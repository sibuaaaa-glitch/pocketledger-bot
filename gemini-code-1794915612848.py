# Inside your /whatsapp-webhook route after Gemini Vision parses 'data':
supabase_url = f"{os.environ.get('SUPABASE_URL')}/rest/v1/transactions"
headers = {
    "apikey": os.environ.get("SUPABASE_KEY"),
    "Authorization": f"Bearer {os.environ.get('SUPABASE_KEY')}",
    "Content-Type": "application/json"
}

payload = {
    "party_name": data["party_name"],
    "bank_stamp": data["bank_stamp_details"],
    "amount": data["amount"],
    "gst_rate": data.get("gst_rate", 0),
    "type": data["transaction_type"],
    "category": data["category"],
    "source": "WhatsApp / Slip Scan"
}
requests.post(supabase_url, headers=headers, json=payload)