import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from utils.detector import HerdDetector, ensure_dirs

import exifread

APP_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(APP_DIR, "uploads")
OUTPUT_DIR = os.path.join(APP_DIR, "outputs")
ensure_dirs(UPLOAD_DIR, OUTPUT_DIR)

ALLOWED_IMG = {"jpg", "jpeg", "png"}
ALLOWED_VID = {"mp4", "avi", "mov", "mkv"}

app = Flask(__name__)
app.secret_key = "amna-secret-key"

detector = HerdDetector(model_path="yolov8n.pt", device=None)  # cpu by default

def ext_ok(filename, allowed):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed

def dms_to_decimal(dms, ref):
    # dms: [deg, min, sec] where each is Ratio
    deg = float(dms[0].num) / float(dms[0].den)
    minute = float(dms[1].num) / float(dms[1].den)
    sec = float(dms[2].num) / float(dms[2].den)
    dec = deg + (minute / 60.0) + (sec / 3600.0)
    if ref in ["S", "W"]:
        dec = -dec
    return dec

def extract_gps_from_image(path):
    """
    If image has EXIF GPS, returns (lat, lon). Else returns (None, None).
    """
    try:
        with open(path, "rb") as f:
            tags = exifread.process_file(f, details=False)

        lat_tag = tags.get("GPS GPSLatitude")
        lat_ref = tags.get("GPS GPSLatitudeRef")
        lon_tag = tags.get("GPS GPSLongitude")
        lon_ref = tags.get("GPS GPSLongitudeRef")

        if not (lat_tag and lat_ref and lon_tag and lon_ref):
            return None, None

        lat = dms_to_decimal(lat_tag.values, str(lat_ref.values))
        lon = dms_to_decimal(lon_tag.values, str(lon_ref.values))
        return lat, lon
    except Exception:
        return None, None

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/detect", methods=["POST"])
def detect():
    file = request.files.get("file")
    if not file or file.filename.strip() == "":
        flash("Please choose an image/video file.")
        return redirect(url_for("index"))

    # Optional location (manual or browser geolocation)
    lat = request.form.get("lat") or ""
    lon = request.form.get("lon") or ""
    lat = float(lat) if lat.strip() != "" else None
    lon = float(lon) if lon.strip() != "" else None

    filename = file.filename
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
    uid = str(uuid.uuid4()).replace("-", "")
    in_name = f"{uid}.{ext}"
    in_path = os.path.join(UPLOAD_DIR, in_name)
    file.save(in_path)

    is_image = ext in ALLOWED_IMG
    is_video = ext in ALLOWED_VID
    if not (is_image or is_video):
        os.remove(in_path)
        flash("Unsupported file type. Use image (jpg/png) or video (mp4/avi/mov/mkv).")
        return redirect(url_for("index"))

    # If user did not provide location, try EXIF GPS (images only)
    if (lat is None or lon is None) and is_image:
        exif_lat, exif_lon = extract_gps_from_image(in_path)
        if exif_lat is not None and exif_lon is not None:
            lat, lon = exif_lat, exif_lon

    out_ext = "jpg" if is_image else "mp4"
    out_name = f"{uid}_out.{out_ext}"
    out_path = os.path.join(OUTPUT_DIR, out_name)

    if is_image:
        animals, herds = detector.process_image_file(in_path, out_path)
        media_type = "image"
    else:
        animals, herds = detector.process_video_file(in_path, out_path)
        media_type = "video"

    # Alert rule (you can change it): if herds >= 1 OR animals >= 5
    alert = (herds >= 1) or (animals >= 5)

    return render_template(
        "result.html",
        media_type=media_type,
        output_file=out_name,
        animals=animals,
        herds=herds,
        alert=alert,
        lat=lat,
        lon=lon
    )

@app.route("/outputs/<path:filename>")
def outputs(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)