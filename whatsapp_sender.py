import requests

def send_whatsapp_pdf_report(recipient_number, file_path):
    access_token = "EAAVPHE1PDkgBPM1wMFaZBfhxN61ObvY5R7yZA1cFZB4dx3gsgZATiZB1ZAZAY8p0bWhbjKLZCJXVFZAQBpD90TelpRqTZC9UWJcimIqu7rtJjYkHLtS6ZA5P6RO4U8X3wwswqs0U0tSwKSlRERKC6YPI8ZCtm2mTq7WZCyHO4KZAy96YsXO2ZCz4t2OwIUgWZAa7ci9jnjNVIVVhQ5FD17AVfhnBWBiFng03ZAE7VfpqyzbnPxtkZBZBpZCZC5gZDZD"
    phone_number_id = "645771728630723"
    filename = "Nusrat_Daily_Report.pdf"

    # Step 1: Upload media
    upload_url = f"https://graph.facebook.com/v19.0/{phone_number_id}/media"
    headers_upload = {
        "Authorization": f"Bearer {access_token}"
    }
    files = {
        "file": (filename, open(file_path, "rb"), "application/pdf")
    }
    data = {
        "messaging_product": "whatsapp",
        "type": "application/pdf"
    }

    upload_response = requests.post(upload_url, headers=headers_upload, files=files, data=data)
    if upload_response.status_code != 200:
        print("❌ Upload failed:", upload_response.text)
        return

    media_id = upload_response.json().get("id")
    print("✅ Media uploaded, ID:", media_id)

    # Step 2: Send message
    message_url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers_message = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_number,
        "type": "document",
        "document": {
            "id": media_id,
            "filename": filename
        }
    }

    send_response = requests.post(message_url, headers=headers_message, json=payload)
    print("📨 Send response:", send_response.json())
