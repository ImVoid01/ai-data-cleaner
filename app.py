from flask import Flask, render_template, request
import openai
import os

app = Flask(__name__)

# Set your OpenAI API key here or via environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")  # Prefer environment variable for security

def ai_strengthen_password(password_idea):
    prompt = (
        f"I have this password idea: '{password_idea}'. "
        "Please transform it into a strong, secure, but still memorable password. "
        "Make sure to mix uppercase, lowercase, numbers, and symbols, "
        "but keep it easy enough to remember for the user."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.7,
        )
        generated_password = response.choices[0].message.content.strip()
        return generated_password
    except Exception as e:
        return f"Error generating password: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        pw_idea = request.form.get("password", "")
        if pw_idea:
            result = ai_strengthen_password(pw_idea)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
