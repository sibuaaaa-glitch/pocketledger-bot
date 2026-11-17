import os, json, requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai

app = Flask(__name__)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """You are an accounting assistant analyzing bank slips and receipts.
Extract: party_name, bank_stamp_details, amount, transaction_type ('income' or 'expense'), and category.
Prioritize the customer name from the WhatsApp caption. Output STRICT JSON only."""

@app.route("/whatsapp-webhook", methods=["POST"])
def webhook():
    media_url = request.form.get("MediaUrl0")
    caption = request.form.get("Body", "").strip()
    resp = MessagingResponse()

    if not media_url:
        resp.message("Please send a photo of a bank slip or counterfoil.")
        return str(resp)

    # Download slip from Twilio WhatsApp
    img_bytes = requests.get(media_url, auth=(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))).content

    # Ask Gemini Vision AI
    prompt = f"{SYSTEM_PROMPT}\nWhatsApp Caption: '{caption}'"
    ai_res = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": img_bytes}])
    data = json.loads(ai_res.text.strip().replace("```json", "").replace("```", ""))

    # Confirmation reply back to WhatsApp
    reply = (
        f"✓ *Payment Logged!*\n"
        f"• *Party:* {data['party_name']}\n"
        f"• *Amount:* ₹{data['amount']:,.2f}\n"
        f"• *Verified:* {data['bank_stamp_details']}\n"
        f"Thank you!"
    )
    resp.message(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))