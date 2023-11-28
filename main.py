# Public API endpoint
# 1. login
# 2. get schedules
# 3. show seats
# 4. take seats
# 5. checkout booking
# 6. create payment
# 7. show all bookings
# 8. show ongoing payment
# 9. validate payment
# 10. show payment history

from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Uptream services endpoint
auth_service_url = os.getenv('AUTH_SERVICE_URL')
account_service_url = os.getenv('ACCOUNT_SERVICE_URL')
data_service_url = os.getenv('DATA_SERVICE_URL')
booking_service_url = os.getenv('BOOKING_SERVICE_URL')
payment_service_url = os.getenv('PAYMENT_SERVICE_URL')

# Middleware for JWT token validation
@app.before_request
def before_request():
    # Exclude token validation for the login endpoint
    if request.endpoint == 'login':
        return
    
    # Validate JWT token with the auth service
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    validation_response = validate_token(token)
    
    if validation_response.status_code != 200:
        return jsonify({'message': 'Token is invalid'}), 401

# Function to validate token by calling the auth service
def validate_token(token):
    response = requests.get(auth_service_url+'/validate', headers={'Authorization': token})
    return response

# Login endpoint (no token validation)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    r = requests.post(auth_service_url+'/login', json=dict(**data))

    return r.json(), r.status_code

@app.route('/schedules', methods=['GET'])
def schedules():
    r = requests.get(data_service_url+'/schedules')
    return r.json(), r.status_code

@app.route('/show-seats/<schedule_id>/<schedule_date>', methods=['GET'])
def show_seats(schedule_id, schedule_date):
    r = requests.get(f'{data_service_url}/show-seats/{schedule_id}/{schedule_date}')
    return r.json(), r.status_code

@app.route('/take-seats/<schedule_id>/<schedule_date>', methods=['POST'])
def take_seats(schedule_id, schedule_date):
    r = requests.post(f'{data_service_url}/take-seats/{schedule_id}/{schedule_date}', json=request.get_json())
    return r.json(), r.status_code

@app.route('/checkout', methods=['POST'])
def checkout():
    r = requests.post(f'{booking_service_url}/checkout', json=request.get_json())
    return r.json(), r.status_code

@app.route("/user-booking/<email>", methods=["GET"])
def get_user_booking(email):
    r = requests.get(f'{booking_service_url}/user-booking/{email}')
    return r.json(), r.status_code

@app.route('/create-payment', methods=['POST'])
def create_payment():
    r = requests.post(f'{payment_service_url}/', json=request.get_json())
    return r.json(), r.status_code

@app.route('/ongoing-payment/<email>', methods=['GET'])
def ongoing_payment(email):
    r = requests.get(f'{payment_service_url}/ongoing/{email}')
    return r.json(), r.status_code

@app.route('/validate-payment', methods=['POST'])
def validate_payment():
    r = requests.post(f'{payment_service_url}/validate', json=request.get_json())
    print(r.text)
    return jsonify({}), r.status_code

@app.route('/history-payment/<email>', methods=['GET'])
def history_payment(email):
    r = requests.get(f'{payment_service_url}/history/{email}')
    return r.json(), r.status_code

if __name__ == '__main__':
    app.run(debug=True, port=8000)