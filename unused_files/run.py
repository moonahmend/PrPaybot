import requests
import json

url = 'https://api.oxapay.com/v1/payment/invoice'

data = {
   "amount": 100,
   "currency": "USD",
   "lifetime": 30,
   "fee_paid_by_payer": 1,
   "under_paid_coverage": 2.5,
   "to_currency": "USDT",
   "auto_withdrawal": False,
   "mixed_payment": True,
   "callback_url": "https://429b-103-178-187-102.ngrok-free.app/oxapay_callback",
   "return_url": "https://t.me/RaidX24_bot/success",
   "order_id": "123456789_250",
   "thanks_message": "Thanks message",
   "description": "Order #12345",
   "sandbox": True
}

headers = {
   'merchant_api_key': 'ESEMQP-WBNPDP-JUEL5R-FNG0GL',
   'Content-Type': 'application/json'
}

response = requests.post(url, data=json.dumps(data), headers=headers)
result = response.json()
print(result)