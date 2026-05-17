import smtplib
from email.message import EmailMessage

SENDER_EMAIL = "testsam360@gmail.com"
SENDER_PASSWORD = "rddwmbynfcbgpywf"

msg = EmailMessage()
msg.set_content("Testing smtplib")
msg['Subject'] = "Test Email"
msg['From'] = SENDER_EMAIL
msg['To'] = "testsam360@gmail.com"

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)
    print("Email sent successfully with smtplib!")
except Exception as e:
    print(f"smtplib failed: {e}")
