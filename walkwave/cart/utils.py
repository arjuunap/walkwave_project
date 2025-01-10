import hmac
import hashlib
from django.conf import settings

def verify_razorpay_signature(data):
    """
    Verify the Razorpay signature using the secret key.
    """
    razorpay_signature = data.get('razorpay_signature')
    order_id = data.get('razorpay_order_id')
    payment_id = data.get('razorpay_payment_id')

    if not (razorpay_signature and order_id and payment_id):
        raise ValueError("Missing required Razorpay parameters.")

    secret = settings.RAZORPAY_KEY_SECRET
    msg = f"{order_id}|{payment_id}".encode('utf-8')
    generated_signature = hmac.new(secret.encode('utf-8'), msg, hashlib.sha256).hexdigest()

    if generated_signature != razorpay_signature:
        raise ValueError("Invalid Razorpay signature.")
