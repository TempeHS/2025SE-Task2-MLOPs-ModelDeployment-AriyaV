import csv  # Import the csv module
from flask import Flask, request, jsonify, render_template
from flask_wtf.csrf import CSRFProtect
import logging
import pickle
import numpy as np

# Configure logging to write to security_log.log
logging.basicConfig(
    filename="security_log.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
)

app = Flask(__name__)
app.secret_key = b"_53oi3uriq9pifpff;apl"
csrf = CSRFProtect(app)

# Load the saved model
with open('ML/my_saved_model.sav', 'rb') as model_file:
    model = pickle.load(model_file)

if not model:
    app.logger.error("Model not loaded properly.")

# Ensure the CSV file exists and has a header
csv_file = 'predictions_log.csv'
with open(csv_file, mode='a', newline='') as file:
    writer = csv.writer(file)
    file.seek(0, 2)  # Move to the end of the file
    if file.tell() == 0:  # If the file is empty, write the header
        writer.writerow(['Weight', 'Cholesterol', 'Prediction'])

@app.route('/')
def index():
    app.logger.info("Index page accessed.")
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
@csrf.exempt  # Disable CSRF protection for this route
def predict():
    app.logger.info("Predict endpoint triggered.")
    try:
        # Get weight and cholesterol from the form
        weight = float(request.form['weight'])
        cholesterol = float(request.form['cholesterol'])

        # Prepare input for the model
        features = np.array([[weight, cholesterol]])

        # Make prediction
        prediction = model.predict(features)
        result = "High risk of Cardiovascular Disease (CVD)" if prediction[0] == 1 else "Low risk of Cardiovascular Disease (CVD)"

        # Log the prediction to the CSV file
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([weight, cholesterol, result])

        app.logger.info(f"Prediction result: {result}")
        # Return the result to the frontend
        return render_template('index.html', prediction_text=result)
    except Exception as e:
        app.logger.error(f"Error during prediction: {str(e)}")
        return render_template('index.html', prediction_text=f"Error: {str(e)}")

# Endpoint for logging CSP violations
@app.route("/csp_report", methods=["POST"])
@csrf.exempt
def csp_report():
    app.logger.critical(f"CSP violation reported: {request.data.decode()}")
    return "done"

if __name__ == '__main__':
    app.logger.info("Starting the application...")
    app.run(debug=True, host="0.0.0.0", port=5000)
