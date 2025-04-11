from flask import Blueprint,request,jsonify,send_file
from lib.model_handler.login_details_handler import Login_handler
from lib.extensions import mongo
from lib.model_handler.report_handler import Report_handler
import tensorflow as tf
import numpy as np
import io
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from lib.model_handler.prediction_handler import PredictionHandler
import requests
from geopy.distance import geodesic
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SENDER_EMAIL = os.getenv("EMAIL_USER")
SENDER_PASSWORD = os.getenv("EMAIL_PASS")
otp_store = {}
def generate_otp():
    return str(random.randint(100000, 999999)) 
api_bp = Blueprint('api',__name__)

MODEL_PATH = "./lib/model/trained_model.keras"
model = tf.keras.models.load_model(MODEL_PATH)

CLASS_LABELS = ["cataract", "diabetic_retinopathy", "glaucoma", "hypertensive_retinopathy", "myopia", "normal"]
@api_bp.route('/')
def index():
    return 'Hello World'

def send_email(to_email, subject, message):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, to_email, text)
        server.quit()
        return True

    except Exception as e:
        print("Error sending email:", e)
        return False
    
@api_bp.route('/user-signup',methods=['POST','GET'])
def user_signup():
    try:
        email = request.args.get('email')   
        password = request.args.get('password')
        data = mongo.db.logindata.find_one({"email":email})
        if data:
            return jsonify({"error": "Email already registered"}), 400
        otp = generate_otp()
        otp_store["email"] = otp  
        if send_email(email, "Your OTP Code", f"Your OTP is: {otp}"):
            return jsonify({
                'otp_sent': True,
                'message': "OTP sent to your registered email"
            }), 200
        else:
            return jsonify({
                'otp_sent': False,
                'message': "Didn’t receive the OTP? Check your spam folder or try a different email."
            }), 500
    except Exception as e:
        return {"success":False},400
    
@api_bp.route('/user-login', methods=['POST'])
def user_login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        login = Login_handler(email, password).login()

        if login['user'] and login['password']:
            return jsonify({
                'uuid':login['uuid'],
                'authenticated': True,
                'message': "Login successful"
            }), 200
        elif not login['user']:
            return jsonify({
                'authenticated': False,
                'message': "User not found"
            }), 401
        elif not login['password']:
            return jsonify({
                'authenticated': False,
                'message': "Incorrect password"
            }), 401
        else:
            return jsonify({
                'authenticated': False,
                'message': "Invalid credentials"
            }), 401

    except Exception as e:
        print("Exception during login:", e)
        return jsonify({"success": False, "error": str(e)}), 400
@api_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.json
        uuid = data.get('email')
        otp_input = data.get('otp')

        if not uuid or not otp_input:
            return jsonify({"error": "UUID and OTP are required"}), 400

        stored_otp = otp_store.get(uuid)

        if stored_otp == otp_input:
            sign = Login_handler(data['email'],data['password']).signup()
            del otp_store[uuid]  # Remove OTP after successful verification
            return jsonify({
                "uuid":sign,
                "authenticated": True,
                "message": "OTP verified successfully"
            }), 200
        else:
            return jsonify({
                "authenticated": False,
                "message": "Invalid or expired OTP"
            }), 401

    except Exception as e:
        print("Exception during OTP verification:", e)
        return jsonify({"success": False, "error": str(e)}), 400


@api_bp.route('/register-patient', methods=['POST'])
def register_patient():
    uuid = request.form.get("uuid")
    name = request.form.get("name")
    age = request.form.get("age")
    gender = request.form.get("gender")
    email = request.form.get("email")
    phone = request.form.get("phone")
    address = request.form.get("address")
    if not (uuid and name and age and gender and email and phone and address):
        return jsonify({"error": "Missing required fields"}), 400
    existing_patient = mongo.db.patientdata.find_one({"uuid": uuid})
    if existing_patient:
        return jsonify({"message": "Patient already registered"}), 409
    patient_data = {
        "uuid": uuid,
        "name": name,
        "age": int(age),
        "gender": gender,
        "email": email,
        "phone": phone,
        "address": address
    }
    mongo.db.patientdata.insert_one(patient_data)

    return jsonify({"message": "Patient registered successfully"}), 201

@api_bp.route("/report", methods=['GET'])
def report():
    try:
        uuid = request.args.get('uuid')
        disease = request.args.get('disease')
        r_h = Report_handler(uuid,disease)
        report = r_h.report_generator()
        print(report)
        pdf_buffer = r_h.generate_pdf(report)
        return send_file(
            pdf_buffer, 
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"report_{uuid}.pdf"
        )

    except Exception as e:
        return {"success": False, "error": str(e)}, 400

@api_bp.route('/predict', methods=['POST'])
def predict():
    uuid = request.form.get("uuid")
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        img = load_img(io.BytesIO(file.read()), target_size=(128, 128))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
      
        
        predictions = model.predict(img_array)
        predicted_class = np.argmax(predictions, axis=1)[0]
        confidence = np.max(predictions)
        PredictionHandler(uuid,CLASS_LABELS[predicted_class]).save_prediction()
        return jsonify({
            "predicted_class": CLASS_LABELS[predicted_class],
            "confidence": float(confidence)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/prediction-history', methods=['GET'])
def prediction_history():
    try:
        uuid = request.args.get('uuid')
        if not uuid:
            return jsonify({"error": "Missing required fields"}), 400
        predictions = mongo.db.prediction.find({"uuid": uuid})
        prediction_list = []
        for prediction in predictions:
            prediction["_id"] = str(prediction["_id"])  
            prediction_list.append(prediction)

        return jsonify(prediction_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@api_bp.route('/nearest_eye_specialists', methods=['GET'])
def get_nearest_specialists():
    try:
        user_lat = float(request.args.get("lat"))
        user_lng = float(request.args.get("lng"))
        speciality = request.args.get("speciality")
        user_location = (user_lat, user_lng)
        doctors = list(mongo.db.doctordata.find({"specialization": speciality}, {"_id": 0}))
        for doctor in doctors:
            doctor["distance_km"] = round(geodesic(user_location, (doctor["lat"], doctor["lng"])).km, 2)
        doctors.sort(key=lambda x: x["distance_km"])
        return jsonify(doctors[:10])

    except Exception as e:
        return jsonify({"error": str(e)})





























# @api_bp.route('/nearby_eye_specialists', methods=['GET'])
# def get_nearby_eye_specialists():
#     lat = request.args.get('lat')
#     lng = request.args.get('lng')

#     osm_url = f"https://nominatim.openstreetmap.org/search?format=json&q=eye%20hospital&lat={lat}&lon={lng}&radius=20000"

#     response = requests.get(osm_url).json()
#     results = [{"name": place["display_name"], "lat": place["lat"], "lng": place["lon"]} for place in response]

#     return jsonify(results[:10])  

#This section has a dependency on the google service which is a paid service so we are not using the same currently 


# GOOGLE_API_KEY = "YOUR_GOOGLE_PLACES_API_KEY"  # Replace with your API key

# @api_bp.route('/nearby_eye_specialists', methods=['GET'])
# def get_nearby_eye_specialists():
#     latitude = request.args.get('lat', default="12.9716") 
#     longitude = request.args.get('lng', default="77.5946")
#     places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
#     params = {
#         "location": f"{latitude},{longitude}",
#         "radius": 5000,  
#         "type": "hospital",
#         "keyword": "eye specialist",
#         "key": GOOGLE_API_KEY
#     }
    
#     response = requests.get(places_url, params=params)
#     data = response.json()
    
#     results = []
#     for place in data.get("results", [])[:10]: 
#         results.append({
#             "name": place.get("name"),
#             "address": place.get("vicinity"),
#             "rating": place.get("rating", "N/A"),
#             "place_id": place.get("place_id"),
#             "maps_link": f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={place.get('place_id')}"
#         })
    
#     return jsonify(results)
