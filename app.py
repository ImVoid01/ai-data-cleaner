import os
from flask import Flask, request, send_file, render_template, redirect, url_for, flash
import tempfile
import zipfile
import pandas as pd

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")  # Replace "supersecret" in prod!

UPLOAD_FOLDER = tempfile.gettempdir()  # temp folder for uploads
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB limit

# Dummy AI processing function (replace with your real AI integration)
def ai_process_csv(input_path, output_folder):
    df = pd.read_csv(input_path)

    # --- Data cleaning example: fill NaNs with 'N/A' ---
    df_cleaned = df.fillna('N/A')

    # Save cleaned data
    cleaned_path = os.path.join(output_folder, "data", "cleaned_data.csv")
    df_cleaned.to_csv(cleaned_path, index=False)

    # Save dummy insight text
    with open(os.path.join(output_folder, "insight", "insights.txt"), "w") as f:
        f.write(f"Data insight:\n- Rows: {df_cleaned.shape[0]}\n- Columns: {df_cleaned.shape[1]}\n")

    # Save dummy change report
    with open(os.path.join(output_folder, "report", "change_report.txt"), "w") as f:
        f.write("Change report:\n- Replaced missing values with 'N/A' in all columns.\n")

    return cleaned_path

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and file.filename.endswith('.csv'):
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, file.filename)
            file.save(file_path)

            # Create output folders
            for folder in ["data", "report", "insight"]:
                os.makedirs(os.path.join(temp_dir, folder), exist_ok=True)

            # Process CSV with dummy AI function
            ai_process_csv(file_path, temp_dir)

            # Create zip of outputs
            zip_path = os.path.join(temp_dir, "output.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for folder in ["data", "report", "insight"]:
                    folder_path = os.path.join(temp_dir, folder)
                    for root, _, files in os.walk(folder_path):
                        for fname in files:
                            full_path = os.path.join(root, fname)
                            arcname = os.path.join(folder, fname)
                            zipf.write(full_path, arcname=arcname)

            return send_file(zip_path, as_attachment=True)

        else:
            flash('Please upload a CSV file.')
            return redirect(request.url)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
