from flask import Flask, request, render_template, redirect, url_for, make_response
import os

UPLOAD_DIR = "uploads"
USER_CREDENTIALS = {'testuser': 'password123'}
LOGGED_IN_USERS = {}

# Ensure upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app = Flask(__name__)

@app.route("/")
def index():
    username = request.cookies.get('username')
    if username in LOGGED_IN_USERS:
        uploaded_files = os.listdir(UPLOAD_DIR)
        return render_template("index.html", username=username, files=uploaded_files)
    return render_template("index.html", username=None)

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            LOGGED_IN_USERS[username] = True
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('username', username)
            return resp
        return render_template("login.html", error="Invalid username or password.")
        """
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if username in USER_CREDENTIALS:
            return render_template("signup.html", error="Username already exists.")
        USER_CREDENTIALS[username] = password
        LOGGED_IN_USERS[username] = True
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('username', username)
        return resp
    return render_template("signup.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    username = request.cookies.get('username')
    if username not in LOGGED_IN_USERS:
        return render_template("access_denied.html")
    
    if request.method == "POST":
        uploaded_file = request.files['file']
        if uploaded_file.filename:
            file_path = os.path.join(UPLOAD_DIR, uploaded_file.filename)
            uploaded_file.save(file_path)
            return render_template("upload_success.html", filename=uploaded_file.filename)
        return render_template("upload.html", error="No file selected for upload.")
    
    return render_template("upload.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    username = request.cookies.get('username')
    if username not in LOGGED_IN_USERS:
        return render_template("access_denied.html")

    if request.method == "POST":
        message = request.form.get('message')
        return render_template("chat.html", username=username, message=message)
    
    return render_template("chat.html", username=username)

@app.route("/events")
def events():
    return render_template("events.html")

@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('username', '', expires=0)
    return resp

if __name__ == "__main__":
    app.run(port=8080)
