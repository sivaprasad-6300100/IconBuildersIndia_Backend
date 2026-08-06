import requests
from django.conf import settings
from .models import OTPStore

BASE_URL = 'https://cpaas.messagecentral.com'


def send_otp(phone):
    phone = phone.replace(' ', '').replace('-', '').replace('+91', '').replace('+', '')
    if phone.startswith('91'):
        phone = phone[2:]  # bare 10-digit number

    try:
        resp = requests.post(f'{BASE_URL}/verification/v3/send', params={
            'countryCode': '91',
            'customerId': settings.MESSAGE_CENTRAL_CUSTOMER_ID,
            'flowType': 'SMS',
            'mobileNumber': phone,
            'otpLength': 6,
        }, headers={'authToken': settings.MESSAGE_CENTRAL_AUTH_TOKEN}, timeout=10)

        data = resp.json()
        print("MC SEND RESPONSE:", data)  # TEMP: watch your terminal for this

        if resp.status_code == 200 and data.get('responseCode') == 200:
            verification_id = data['data']['verificationId']
            OTPStore.objects.filter(phone='91' + phone, is_used=False).delete()
            OTPStore.objects.create(phone='91' + phone, otp=verification_id)
            return {'success': True, 'message': f'OTP sent to +91 {phone}'}

        return {'success': False, 'message': data.get('message', 'Failed to send OTP')}

    except Exception as e:
        return {'success': False, 'message': f'SMS provider error: {e}'}








def verify_otp(phone, otp):
    phone = phone.replace(' ', '').replace('-', '').replace('+91', '').replace('+', '')
    if phone.startswith('91'):
        phone = phone[2:]

    print("VERIFY LOOKUP phone:", '91' + phone, "otp given:", otp)
    print("ALL ROWS:", list(OTPStore.objects.filter(phone='91' + phone).values('phone', 'otp', 'is_used', 'created_at', 'expires_at')))

    try:
        record = OTPStore.objects.filter(phone='91' + phone, is_used=False).latest('created_at')
    except OTPStore.DoesNotExist:
        return {'success': False, 'message': 'OTP not found. Please request a new OTP.'}

    if not record.is_valid():
        return {'success': False, 'message': 'OTP has expired. Please request a new OTP.'}

    resp = requests.get(f'{BASE_URL}/verification/v3/validateOtp', params={
        'countryCode': '91',
        'mobileNumber': phone,
        'verificationId': record.otp,
        'customerId': settings.MESSAGE_CENTRAL_CUSTOMER_ID,
        'code': otp,
    }, headers={'authToken': settings.MESSAGE_CENTRAL_AUTH_TOKEN}, timeout=10)

    data = resp.json()
    print("MC VERIFY RESPONSE:", data)

    if resp.status_code == 200 and data.get('data', {}).get('verificationStatus') == 'VERIFICATION_COMPLETED':
        record.is_used = True
        record.save()
        return {'success': True, 'message': 'OTP verified successfully'}

    return {'success': False, 'message': 'Invalid OTP. Please try again.'}