import yagmail

SENDER_EMAIL = "mohan1204p@gmail.com"
SENDER_PASSWORD = "egiytgqxooehtanr"

try:
    yag = yagmail.SMTP(SENDER_EMAIL, SENDER_PASSWORD)
    yag.send(
        to="testsam360@gmail.com",
        subject="Test Email",
        contents="Testing yagmail"
    )
    print("Email sent successfully!")
except Exception as e:
    print(f"Email failed: {e}")
