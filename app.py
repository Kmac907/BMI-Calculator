from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Define BMI categories and corresponding information
bmi_categories = {
    "Underweight": {
        "risk": "Increased risk of malnutrition and weakened immune system.",
        "benefit": "May have better endurance and be less prone to joint problems.",
        "recommendation": "Consult with a healthcare professional for a balanced diet and exercise plan to gain healthy weight.",
    },
    "Normal Weight": {
        "risk": "Lower risk of health problems associated with weight.",
        "benefit": "Better overall health and reduced risk of chronic diseases.",
        "recommendation": "Maintain a balanced diet and regular physical activity to stay healthy.",
    },
    "Overweight": {
        "risk": "Increased risk of heart disease, diabetes, and other health issues.",
        "benefit": "May have more strength but higher risk of joint problems.",
        "recommendation": "Focus on weight management through diet and exercise. Consult with a healthcare professional for guidance.",
    },
    "Obese": {
        "risk": "Significantly increased risk of various health problems.",
        "benefit": "May benefit from weight loss for overall health improvement.",
        "recommendation": "Seek medical advice for a comprehensive weight management plan and lifestyle changes.",
    },
}

# Wger Exercise API endpoint and your API key
wger_api_endpoint = "https://wger.de/api/v2/exercise/?format=json"
wger_api_key = "677cbea8eaf93f95a19be665a8f810439f059ac6"

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/bmi", methods=["POST"])
def calculate():
    try:
        selected_unit = request.form.get("unit")

        if selected_unit == "imperial":
            weight_conversion_factor = 0.453592  # 1 lb = 0.453592 kg
            height_conversion_factor = 2.54       # 1 inch = 2.54 cm
        else:
            weight_conversion_factor = 1.0
            height_conversion_factor = 1.0

        w = float(request.form.get("weight")) * weight_conversion_factor
        h = float(request.form.get("height")) * height_conversion_factor

        if w and h:
            bmi = round(w / ((h / 100) ** 2), 3)

            # Determine BMI category
            if bmi < 18.5:
                category = "Underweight"
            elif 18.5 <= bmi < 25:
                category = "Normal Weight"
            elif 25 <= bmi < 30:
                category = "Overweight"
            else:
                category = "Obese"

            # Retrieve health information and recommendation based on BMI category
            risk = bmi_categories[category]["risk"]
            benefit = bmi_categories[category]["benefit"]
            recommendation = bmi_categories[category]["recommendation"]

            # Fetch exercise recommendations from the Wger Exercise API
            exercise_recommendations = get_exercise_recommendations(category)

            return render_template(
                "index.html",
                bmi=bmi,
                category=category,
                risk=risk,
                benefit=benefit,
                recommendation=recommendation,
                exercise_recommendations=exercise_recommendations,
            )
    except ValueError as error:
        error = "Please enter all the values"
        return render_template("index.html", error=error)

def get_exercise_recommendations(bmi_category):
    # Prepare query parameters for the API request
    params = {"format": "json", "limit": 5}  # Adjust the limit as needed

    # Make the API request to fetch exercise recommendations based on the BMI category
    headers = {"Authorization": f"Token {wger_api_key}"}
    response = requests.get(wger_api_endpoint, params=params, headers=headers)

    if response.status_code == 200:
        exercise_data = response.json()
        # Filter exercise recommendations based on the BMI category
        filtered_exercises = [
            exercise for exercise in exercise_data["results"] if bmi_category in exercise["description"]
        ]
        return exercise_data
    else:
        return []

if __name__ == "__main__":
    app.run(debug=True)
