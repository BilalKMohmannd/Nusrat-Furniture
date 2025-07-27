import schedule
import time
from report_generator import generate_daily_pdf_report
from whatsapp_sender import send_whatsapp_pdf_report
from datetime import datetime

# List of recipients
recipients = [
    "923295833339",  # Brother or father
    "923222600075",  # Add more numbers here (if added to WhatsApp API test list)
]

def job():
    print(f"📅 Running job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_file = generate_daily_pdf_report()
    for recipient in recipients:
        send_whatsapp_pdf_report(recipient, report_file)

# Schedule at 9 PM daily
schedule.every().day.at("21:00").do(job)

print("📆 Scheduler started... will run daily at 9 PM.\n")

while True:
    schedule.run_pending()
    time.sleep(60)
