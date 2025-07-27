import imaplib
import email
import smtplib
from email.mime.text import MIMEText

# Credentials
EMAIL_ADDRESS = 'test.bot.sender@gmail.com'
EMAIL_PASSWORD = 'kpsq hqhr emix ysua'

# Keywords to department mapping
ROUTING_KEYWORDS = {
    'hr': 'HR',
    'developer': 'Developer',
    'client': 'Client'
}

ROUTING_RESPONSES = {
    'HR': "Thanks for contacting HR support. We’ll get back to you shortly.",
    'Developer': "Developer support has received your issue.",
    'Client': "Client support team will assist you soon."
}

def check_and_route_emails():
    print("\nChecking new emails...\n")

    # Connect to Gmail IMAP
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    imap.select("inbox")

    # Search unseen emails
    status, response = imap.search(None, '(UNSEEN)')
    email_ids = response[0].split()

    for eid in email_ids:
        status, msg_data = imap.fetch(eid, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])

        from_address = email.utils.parseaddr(msg.get("From"))[1]
        from_name = email.utils.parseaddr(msg.get("From"))[0]
        subject = msg.get("Subject", "")
        body = ""

        # Extract plain text body
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")

        print("New Email Received")
        print("---------------------------")
        print(f"From   : {from_name} <{from_address}>")
        print(f"Subject: {subject}")
        print(f"Body   : {body.strip()[:150]}")
        print("---------------------------")

        # Routing logic
        assigned_team = None
        for keyword, team in ROUTING_KEYWORDS.items():
            if keyword.lower() in body.lower():
                assigned_team = team
                break

        if assigned_team:
            send_reply(from_address, assigned_team)
            print(f"Routed to {assigned_team} team. Reply sent.\n")
        else:
            print("No valid keyword found. No reply sent.\n")

    imap.logout()

def send_reply(to_address, team):
    response = ROUTING_RESPONSES.get(team, "Thanks for contacting us.")
    msg = MIMEText(response)
    msg["Subject"] = f"{team} Support Team"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_address

    # Send via SMTP
    smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)
    smtp.quit()

if __name__ == "__main__":
    check_and_route_emails()
