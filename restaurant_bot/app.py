from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Sample data
menu_items = {
    "pizza": "Pizza - Rs. 1200",
    "burger": "Burger - Rs. 650",
    "pasta": "Pasta - Rs. 900",
    "shawarma": "Shawarma - Rs. 400",
    "fries": "Fries - Rs. 300"
}

reservations = {
    "amna": "Your table is reserved for 7:00 PM.",
    "ali": "Your table is reserved for 8:30 PM."
}

orders = {
    "101": "Your order is being prepared.",
    "102": "Your order is out for delivery.",
    "103": "Your order has been delivered."
}


def get_bot_response(user_message):
    msg = user_message.lower().strip()

    # Greetings
    if msg in ["hi", "hello", "hey"]:
        return "Hello! Welcome to our restaurant. You can ask about the menu, reservation status, or order tracking."

    # Menu
    elif "menu" in msg:
        menu_text = "Here is our menu:<br>"
        for item, price in menu_items.items():
            menu_text += f"- {price}<br>"
        return menu_text

    # Specific menu item
    elif any(item in msg for item in menu_items):
        for item in menu_items:
            if item in msg:
                return f"{menu_items[item]}"

    # Reservation
    elif "reservation" in msg:
        words = msg.split()
        for word in words:
            if word in reservations:
                return reservations[word]
        return "Please provide your name with reservation. Example: reservation amna"

    # Order tracking
    elif "order" in msg or "track" in msg:
        words = msg.split()
        for word in words:
            if word in orders:
                return orders[word]
        return "Please provide your order ID. Example: track order 102"

    # Help
    elif "help" in msg:
        return (
            "You can ask:<br>"
            "- Show menu<br>"
            "- Reservation Amna<br>"
            "- Track order 102"
        )

    else:
        return "Sorry, I did not understand that. Type 'help' to see what you can ask."


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    bot_response = get_bot_response(user_message)
    return jsonify({"response": bot_response})


if __name__ == "__main__":
    app.run(debug=True)