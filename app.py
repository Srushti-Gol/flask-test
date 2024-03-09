from flask import Flask,request, jsonify
import joblib
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def hello_world():
    return 'Hello from Srushti'
 
CropRecModel = joblib.load('./models/CropRecModel.joblib')
# @app.route('/predictCrop', methods=['POST'])
# def predict_crop():
#     data = request.get_json()
#     # Convert values to float
#     features = [float(data[key]) for key in ['Nitrogen', 'Phosphorous', 'Potassium', 'Temperature', 'Humidity', 'ph', 'Rainfall']]
    
#     # Print the features
#     print("Features:", features)

#     # Make prediction
#     prediction = CropRecModel.predict([features])
    
#     return jsonify({"Prediction" : prediction[0]}), 200
