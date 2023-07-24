import requests
import hashlib
import re
import base64


class Paytring:

    # Providing API Key and Secret 
    def __init__(self):
        self.key = 'test_cDfh9'
        self.secret = 'fBAVZ2yGPE'
        self.endpoint = 'https://api.paytring.com/api/v1/'


class Order (Paytring) :
    
    def Create(self, receipt_id, amount, callback_url,customer_info):
        """Create order"""
        try:
            self.vaidate_customer_info(customer_info)
            self.validate_email(customer_info['email'])
            self.validate_phone(customer_info['phone'])
            self.validate_amount(amount)
            self.validate_callback_url(callback_url)
            self.validate_receipt(receipt_id)
            
            endpoint = self.endpoint + 'order/create'

            payload = {
                "key": self.key,
                "receipt_id": receipt_id,
                "amount": amount,
                "callback_url": callback_url,
                "cname": customer_info['cname'],
                "email": customer_info['email'],
                "phone": customer_info['phone'],
            }

            hash = self.create_hash(payload)
            payload['hash'] = hash

            response = requests.post(endpoint, payload)
            response =  response.json()
            response['hash'] = hash
            if response['status'] == True:
                if 'url' in response.keys():
                    response['url'] = base64.b64decode(response['url']).decode('utf-8')
                return {"response": response}
            return {"response": response}
        except Exception as e:
            return {"response": str(e)}

    def Fetch(self, id):
        """Fetch order"""
        try:
            if not isinstance(id, str):
                raise Exception('Invalid Order ID')
            endpoint = self.endpoint + 'order/fetch'
            payload = {
                "key": self.key,
                "id": id
            }
            hash = self.create_hash(payload)
            payload['hash'] = hash
            response = requests.post(endpoint, payload)
            response = response.json()
            if response['status'] == True:
                return {"response": response}
            return {"response": response}
        except Exception as e:
            return {"response": str(e)}

    def create_hash(self, body):
        """Create hash for the body and key"""
        try:
            if len(body.keys()) != 0:
                keys = sorted(body.keys())
                value = [body[key] for key in keys]
                value = '|'.join(value) + '|'
                value += self.secret
                return hashlib.sha512(value.encode('utf-8')).hexdigest()
            else:
                raise Exception('Invalid Payload')
        except Exception as e:
            raise Exception(str(e))


    def validate_email(self, email):
        if not isinstance(email, str):
            raise Exception('Invalid email')
        
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if(re.search(regex, email)):
            return True
        raise Exception('Invalid email')

    def validate_amount(self, amount):
        if not isinstance(amount, str):
            raise Exception('Invalid amount')
        
        if amount.isnumeric():
            return True
        raise Exception('Invalid amount')

    def validate_phone(self, phone):
        if not isinstance(phone, str):
            raise Exception('Invalid phone number')
        
        regex = re.compile("(0|91)?[6-9][0-9]{9}")
        if regex.match(phone):
            return True
        raise Exception('Invalid phone number')

    def validate_callback_url(self, callback_url):
        if isinstance(callback_url, str):
            return True
        raise Exception('Invalid callback url')

    def validate_notes(self, notes):
        if isinstance(notes, dict):
            return True
        raise Exception('Invalid notes')

    def vaidate_customer_info(self, customer_info):
        if customer_info.keys() == {'cname', 'email', 'phone'}:
            return True
        raise Exception('Insufficient customer info')

    def validate_receipt(self, receipt_id):
        if isinstance(receipt_id, str):
            return True
        raise Exception('Invalid receipt id')
