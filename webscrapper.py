import requests
from bs4 import BeautifulSoup
import re

def scrape_emails(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Get visible text + HTML
        text = soup.get_text() + response.text

        # Regex for emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+'
        emails = set(re.findall(email_pattern, text))

        return emails

    except Exception as e:
        print("Error:", e)
        return []

# --- User input ---
link = input("Enter public website link: ")

results = scrape_emails(link)

print("\nEmails found:")
for email in results:
    print(email)
