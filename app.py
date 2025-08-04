from flask import Flask, render_template, request, send_file
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
CLEANED_FOLDER = "cleaned"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)

@app.route("/")
def upload_file():
    return render_template("index.html")

@app.route("/clean", methods=["POST"])
def clean_csv():
    if "file" not in request.files:
        return "No file part"

    file = request.files["file"]
    if file.filename == "":
        return "No selected file"

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Load CSV
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        return f"Error reading the CSV file: {e}"

    # Clean the data
    df.fillna(df.mean(numeric_only=True), inplace=True)  # Use numeric_only to avoid warnings
    df.drop_duplicates(inplace=True)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    cleaned_filename = "cleaned_" + file.filename
    cleaned_path = os.path.join(CLEANED_FOLDER, cleaned_filename)

    try:
        df.to_csv(cleaned_path, index=False)
        print(f"Cleaned file saved to: {cleaned_path}")
    except Exception as e:
        return f"Error saving the cleaned file: {e}"

    # Check if the cleaned file exists before sending it
    if not os.path.exists(cleaned_path):
        return f"Cleaned file does not exist at path: {cleaned_path}"

    # Attempt to send the file
    try:
        return send_file(cleaned_path, as_attachment=True)
    except Exception as e:
        return f"Error sending the cleaned file: {e}"
if __name__ == "__main__":
    app.run(debug=True)