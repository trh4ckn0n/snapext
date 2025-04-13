from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import webbrowser
import time

app = Flask(__name__)

app.secret_key = "trhacknon_super_secret_key"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

def load_snapchat_links():
    file_path = "snapso.txt"
    try:
        with open(file_path, "r") as file:
            return [line.strip() for line in file.readlines() if line.startswith("https://www.snapchat.com/add/")]
    except FileNotFoundError:
        return []

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == "trkn":
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Mot de passe incorrect !")
    return render_template("login.html")

@app.route("/snapchat")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    links = load_snapchat_links()
    return render_template("index.html", links=links)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/open", methods=["POST"])
def open_links():
    if not session.get("logged_in"):
        return jsonify({"status": "error", "message": "Non autorisé"}), 403

    data = request.json
    links = data.get("links", [])

    for link in links:
        webbrowser.open(link)
        time.sleep(1.5)

    return jsonify({"status": "success", "message": f"{len(links)} liens ouverts."})

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
