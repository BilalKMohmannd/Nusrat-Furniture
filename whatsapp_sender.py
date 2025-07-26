import requests

def send_whatsapp_document(phone_number, file_path):
    token = "YOUR_META_CLOUD_API_TOKEN"
    phone_id = "YOUR_PHONE_NUMBER_ID"
    url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Upload media first
    media_res = requests.post(
        f"https://graph.facebook.com/v19.0/{phone_id}/media",
        headers=headers,
        files={"file": open(file_path, "rb")},
        data={"messaging_product": "whatsapp", "type": "application/pdf"}
    )
    media_id = media_res.json().get("id")

    # Send document
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "document",
        "document": {
            "id": media_id,
            "filename": "daily_report.pdf"
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print(response.json())
