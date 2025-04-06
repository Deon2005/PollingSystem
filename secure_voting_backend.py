from flask import Flask, request, jsonify, send_file from flask_cors import CORS import firebase_admin from firebase_admin import credentials, firestore, auth import random import cv2 import face_recognition import numpy as np import base64 import os

app = Flask(name) CORS(app)

Firebase Admin Initialization

cred = credentials.Certificate("firebase_key.json")  # Place your Firebase service account key here firebase_admin.initialize_app(cred) db = firestore.client()


def generate_otp(): return str(random.randint(100000, 999999))

def save_temp_image(base64_str, filename): img_data = base64.b64decode(base64_str.split(',')[1]) with open(filename, 'wb') as f: f.write(img_data)

def compare_faces(known_image_path, unknown_image_path): try: known_image = face_recognition.load_image_file(known_image_path) unknown_image = face_recognition.load_image_file(unknown_image_path)

known_encoding = face_recognition.face_encodings(known_image)[0]
    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

    results = face_recognition.compare_faces([known_encoding], unknown_encoding)
    return results[0]
except:
    return False



@app.route('/send_otp', methods=['POST']) def send_otp(): data = request.json officer_id = data.get('officer_id') otp = generate_otp()

db.collection('officers').document(officer_id).set({'otp': otp}, merge=True)
print(f"OTP sent to {officer_id}: {otp}")

return jsonify({"message": "OTP sent successfully"})

@app.route('/verify_otp', methods=['POST']) def verify_otp(): data = request.json officer_id = data.get('officer_id') entered_otp = data.get('otp')

doc = db.collection('officers').document(officer_id).get()
if doc.exists and doc.to_dict().get('otp') == entered_otp:
    return jsonify({"status": "success", "message": "OTP verified"})
return jsonify({"status": "fail", "message": "Incorrect OTP"})

@app.route('/upload_face', methods=['POST']) def upload_face(): data = request.json image_data = data.get('image') officer_id = data.get('officer_id') filename = f"known_{officer_id}.jpg" save_temp_image(image_data, filename) return jsonify({"message": "Face image saved"})

@app.route('/verify_face', methods=['POST']) def verify_face(): data = request.json image_data = data.get('image') officer_id = data.get('officer_id')

unknown_path = f"temp_{officer_id}.jpg"
known_path = f"known_{officer_id}.jpg"

save_temp_image(image_data, unknown_path)
match = compare_faces(known_path, unknown_path)

return jsonify({"match": match})

@app.route('/verify_fingerprint', methods=['POST']) def verify_fingerprint(): data = request.json officer_id = data.get('officer_id') # Simulate fingerprint check print(f"Simulating fingerprint scan for officer {officer_id}") return jsonify({"status": "success", "message": "Fingerprint verified"})


if name == 'main': app.run(debug=True)
