from flask import Flask,request, jsonify
import joblib
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import OpenAI


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key = OPENAI_API_KEY)

@app.route('/')
def hello_world():
    return 'Hello from Srushti'

def generate_crop_report(predicted_crop):
    prompt_crop_practices = f"You are an agriculture expert recommending crop practices for the {predicted_crop} crop."
    prompt_irrigation_practices = f"You are an agriculture expert analyzing soil. Based on the predicted crop '{predicted_crop}', recommend suitable irrigation practices."
    prompt_pest_control_methods = f"You are an agriculture expert analyzing soil. Based on the predicted crop '{predicted_crop}', suggest effective pest control methods."
    prompt_fertilizer_recommendation = f"You are an agriculture expert providing fertilizer recommendations for the {predicted_crop} crop."

    response_1 = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Answer the question in less than 40 words based on the content below, and if the question can't be answered based on the content, say \"I don't know\"\n\n"},
            {"role": "user", "content": prompt_crop_practices}
        ],
    )

    response_2 = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Answer the question in less than 40 words based on the content below, and if the question can't be answered based on the content, say \"I don't know\"\n\n"},
            {"role": "user", "content": prompt_irrigation_practices}
        ],
    )

    response_3 = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Answer the question in less than 40 words based on the content below, and if the question can't be answered based on the content, say \"I don't know\"\n\n"},
            {"role": "user", "content": prompt_pest_control_methods}
        ],
    )

    response_4 = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Answer the question in less than 40 words based on the content below, and if the question can't be answered based on the content, say \"urea\"\n\n"},
            {"role": "user", "content": prompt_fertilizer_recommendation}
        ],
    )

    return {
        'predicted_crop': predicted_crop,
        'crop_practices_recommendation': response_1.choices[0].message.content,
        'irrigation_practices_recommendation': response_2.choices[0].message.content,
        'pest_control_methods_recommendation': response_3.choices[0].message.content,
        'fertilizer_recommendation': response_4.choices[0].message.content,
    }

CropRecModel = joblib.load('./models/CropRecModel.joblib')
@app.route('/predictCrop', methods=['POST'])
def predict_crop():
    data = request.get_json()
    
    features = [float(data[key]) for key in ['Nitrogen', 'Phosphorous', 'Potassium', 'Temperature', 'Humidity', 'ph', 'Rainfall']]
    
    print("Features:", features)
    
    # Make prediction
    prediction = CropRecModel.predict([features])

    report = generate_crop_report(prediction[0])
    
    return jsonify(report), 200

