from flask import Flask,request, jsonify
import joblib
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import timedelta
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import io

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client.get_default_database()

@app.route('/')
def hello_world():
    return 'Hello from Srushti'

auth_collection = db['user']
# Initialize JWTManager
app.config['JWT_SECRET_KEY'] = 'super-secret'  
jwt = JWTManager(app)

# Function to get user identity for JWT token
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user['email']

@app.route('/protected', methods=['GET'])
@jwt_required()  # This will protect the route with JWT token authentication
def protected():
    # Access the current user identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Login route with JWT token creation
@app.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = auth_collection.find_one({'email': email})

    if user:
        if user['password'] == password:
            custom_expiration_time = timedelta(days=1)
            access_token = create_access_token(identity=user,expires_delta=custom_expiration_time)
            user['_id'] = str(user['_id'])  # Convert ObjectId to string
            return jsonify({'message': 'Login successful', 'access_token': access_token , 'user' : {'_id':user['_id'],  'name': user['name']}})
        else:
            return jsonify({'message': 'Incorrect password'}), 401
    else:
        return jsonify({'message': 'User not found'}), 404
    
#for Signup
@app.route('/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    user = {
        'name': name,
        'email': email,
        'password': password
    }
    
    auth_collection.insert_one(user)
    access_token = create_access_token(identity=user)
    user['_id'] = str(user['_id'])
    return jsonify({'message': 'Signup successful', 'access_token': access_token , 'user' : {'_id':user['_id'],  'name': user['name']}})

 
CropRecModel = joblib.load('./models/CropRecModel.joblib')
@app.route('/predictCrop', methods=['POST'])
def predict_crop():
    data = request.get_json()
    # Convert values to float
    features = [float(data[key]) for key in ['Nitrogen', 'Phosphorous', 'Potassium', 'Temperature', 'Humidity', 'ph', 'Rainfall']]
    
    # Print the features
    print("Features:", features)

    # Make prediction
    prediction = CropRecModel.predict([features])
    
    return jsonify({"Prediction" : prediction[0]}), 200

loaded_model = load_model('./models/plantDisease_model')
class_names = ['brown spots', 'deficiency calcium', 'xanthomonas', 'stemphylium solani', 'mosaic vena kuning', 'virus king keriting']
@app.route('/predictDisease', methods=['POST'])
def predict_disease():
    try:
        file = request.files['image']
        img_bytes = file.read()
        img = image.load_img(io.BytesIO(img_bytes), target_size=(150, 150)) 
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0  
        predictions = loaded_model.predict(img_array)
        print(predictions)
        predicted_class_index = np.argmax(predictions)
        predicted_class_name = class_names[predicted_class_index]
        
        return jsonify({"Prediction" : predicted_class_name}), 200
    
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
