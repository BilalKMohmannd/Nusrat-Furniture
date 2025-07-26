import schedule
import time
from report_generator import generate_daily_pdf_report
from whatsapp_sender import send_whatsapp_document

def job():
    report_file = generate_daily_pdf_report()
    send_whatsapp_document("923295833339", report_file)

schedule.every().day.at("22:00").do(job)

print("Scheduler started... will run daily at 9 PM.")
while True:
    schedule.run_pending()
    time.sleep(60)
