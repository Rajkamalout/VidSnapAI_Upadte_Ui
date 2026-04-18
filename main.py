from flask import Flask, render_template, request, redirect, url_for, flash
import uuid
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "secret123"

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    myid = uuid.uuid1()

    if request.method == "POST":
        rec_id = request.form.get("uuid")
        desc = request.form.get("text")
        input_files = []

        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], str(rec_id))
        os.makedirs(folder_path, exist_ok=True)

        for key in request.files:
            file = request.files[key]
            if file and file.filename != "":
                filename = secure_filename(file.filename)
                file.save(os.path.join(folder_path, filename))
                input_files.append(filename)

        # description file
        with open(os.path.join(folder_path, "desc.txt"), "w") as f:
            f.write(desc if desc else "")

        # input.txt for ffmpeg
        for fl in input_files:
            with open(os.path.join(folder_path, "input.txt"), "a") as f:
                f.write(f"file '{fl}'\nduration 1\n")

    return render_template("create.html", myid=myid)


@app.route("/home")
def dashboard():
    return render_template("index.html")


@app.route("/gallery")
def gallery():
    reels_folder = "static/reels"
    os.makedirs(reels_folder, exist_ok=True)
    reels = os.listdir(reels_folder)
    return render_template("gallery.html", reels=reels)


@app.route("/login")
def login():
    return render_template("auth/login.html")


@app.route("/register")
def register():
    return render_template("auth/register.html")


@app.before_request
def check_login():
    allowed = ["/login", "/register", "/"]
    if request.path.startswith("/static"):
        return

    if request.path not in allowed:
        return


# DELETE REEL
@app.route("/delete_reel/<reel_name>", methods=["POST"])
def delete_reel(reel_name):
    reel_path = os.path.join("static/reels", reel_name)

    if os.path.exists(reel_path):
        os.remove(reel_path)
        flash("Reel deleted successfully", "success")
    else:
        flash("Reel not found", "error")

    return redirect(url_for("gallery"))


# 🔥 IMPORTANT FOR RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
