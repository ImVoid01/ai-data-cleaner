import os
import tempfile
import zipfile
from flask import Flask, request, send_file, render_template, redirect, url_for, flash
import pandas as pd

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")  # Never hardcode in production

UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

def ai_process_csv(input_path, output_folder):
    """Simulated AI processing on CSV - fills NaNs and saves basic reports"""
    df = pd.read_csv(input_path)

    # Example: Replace missing values
    df_cleaned = df.fillna('N/A')

    # Create required subfolders
    os.makedirs(os.path.join(output_folder, "data"), exist_ok=True)
    os.makedirs(os.path.join(output_folder, "insight"), exist_ok=True)
    os.makedirs(os.path.join(output_folder, "report"), exist_ok=True)

    # Save cleaned data
    cleaned_path = os.path.join(output_folder, "data", "cleaned_data.csv")
    df_cleaned.to_csv(cleaned_path, index=False)

    # Write dummy insights
    with open(os.path.join(output_folder, "insight", "insights.txt"), "w") as f:
        f.write(f"Data insight:\n- Rows: {df_cleaned.shape[0]}\n- Columns: {df_cleaned.shape[1]}\n")

    # Write dummy report
    with open(os.path.join(output_folder, "report", "change_report.txt"), "w") as f:
        f.write("Change report:\n- Replaced missing values with 'N/A' in all columns.\n")

    return cleaned_path

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No file selected")
            return redirect(request.url)

        if file and file.filename.lower().endswith(".csv"):
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, file.filename)
            file.save(file_path)

            # Process file
            ai_process_csv(file_path, temp_dir)

            # Zip result
            zip_path = os.path.join(temp_dir, "output.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for folder in ["data", "report", "insight"]:
                    folder_path = os.path.join(temp_dir, folder)
                    for root, _, files in os.walk(folder_path):
                        for fname in files:
                            full_path = os.path.join(root, fname)
                            arcname = os.path.relpath(full_path, temp_dir)
                            zipf.write(full_path, arcname=arcname)

            return send_file(zip_path, as_attachment=True)

        flash("Please upload a valid CSV file.")
        return redirect(request.url)

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
