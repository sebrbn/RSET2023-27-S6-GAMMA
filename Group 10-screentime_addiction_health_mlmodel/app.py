from flask import Flask, render_template, request, redirect, session
from database import create_tables, connect
from model import predict_addiction, predict_health, top6_features, top8_features
from recommendation import generate_recommendation
from chatbot import chat_with_ai
import webbrowser
from threading import Timer

app = Flask(__name__)
app.secret_key = "secret123"

# Ensure DB tables exist
create_tables()


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')

        if not all([username, email, phone, password]):
            return "Please fill all fields"

        # Check if email already exists
        with connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email=?", (email,))
            existing_user = cur.fetchone()
            if existing_user:
                return "User already exists. Please login instead."

            # Insert new user
            cur.execute(
                "INSERT INTO users(username,email,phone,password) VALUES(?,?,?,?)",
                (username, email, phone, password)
            )

        return redirect("/login")

    return render_template("signup.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return "Missing form fields"

        with connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM users WHERE email=? AND password=?",
                (email, password)
            )
            user = cur.fetchone()

        if user:
            session['user_id'] = user[0]
            return redirect("/dashboard")
        else:
            return "Invalid login"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect("/login")

    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT addiction_score, addiction_level, health_risk, created_at
            FROM predictions
            WHERE user_id=?
            ORDER BY created_at DESC
        """, (session['user_id'],))
        rows = cur.fetchall()

    scores = [r[0] for r in rows]
    levels = [r[1] for r in rows]
    health = [r[2] for r in rows]

    return render_template(
        "dashboard.html",
        rows=rows,
        scores=scores,
        levels=levels,
        health=health
    )


# ---------------- PREDICTION ----------------
@app.route("/prediction", methods=["GET", "POST"])
def prediction():
    if 'user_id' not in session:
        return redirect("/login")

    if request.method == "POST":
        # Collect feature values safely
        add_values = [float(request.form.get(f, 0)) for f in top6_features]
        health_values = [float(request.form.get(f, 0)) for f in top8_features]

        # Make predictions
        score, level = predict_addiction(add_values)
        health, prob = predict_health(health_values)
        recommendation = generate_recommendation(score, level, health)

        # Save prediction
        with connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO predictions(user_id,addiction_score,addiction_level,health_risk)
                VALUES(?,?,?,?)
            """, (session['user_id'], score, level, health))

        return render_template(
            "prediction.html",
            score=round(score, 2),
            level=level,
            health=health,
            probability=round(prob, 3),
            recommendation=recommendation,
            features1=top6_features,
            features2=top8_features
        )

    return render_template(
        "prediction.html",
        features1=top6_features,
        features2=top8_features
    )


# ---------------- CHATBOT ----------------
@app.route("/chatbot", methods=["GET","POST"])
def chatbot():

    if "chat_history" not in session:
        session["chat_history"] = []

    if request.method == "POST":

        if "clear" in request.form:
            session["chat_history"] = []
            return redirect("/chatbot")

        question = request.form.get("question")

        if question:

            answer = chat_with_ai(question)

            session["chat_history"].append({
                "user": question,
                "bot": answer
            })

            session.modified = True

    return render_template(
        "chatbot.html",
        chat_history=session["chat_history"]
    )
# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- AUTO OPEN WEBSITE ----------------
def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(debug=True)