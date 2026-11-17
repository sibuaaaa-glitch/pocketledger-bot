from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
import json, requests

app = Flask(__name__)
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/whatsapp-webhook", methods=["POST"])
def whatsapp_webhook():
    # 1. Incoming photo URL and optional caption from WhatsApp
    media_url = request.form.get("MediaUrl0")
    caption = request.form.get("Body", "").strip()
    resp = MessagingResponse()

    if not media_url:
        resp.message("Please send a photo of a bank slip or payment receipt.")
        return str(resp)

    # 2. Download slip image from WhatsApp
    img_data = requests.get(media_url).content

    # 3. Ask Gemini Vision to extract the accounting data
    prompt = f"Analyze this bank slip. WhatsApp Caption: '{caption}'"
    ai_response = model.generate_content([
        prompt, 
        {"mime_type": "image/jpeg", "data": img_data}
    ])
    entry = json.loads(ai_response.text)

    # 4. Handle ambiguous party names
    if entry.get("confidence") == "needs_party_clarification":
        reply = f"Detected ₹{entry['amount']} via {entry['bank_stamp_details']}. Whose ledger should I credit this to?"
    else:
        # Save to database (or PocketLedger)
        reply = f"✓ Logged ₹{entry['amount']:,.2f} to {entry['party_name']}!\nVerified: {entry['bank_stamp_details']}"

    resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(port=5000)