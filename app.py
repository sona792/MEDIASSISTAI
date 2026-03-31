from flask import Flask, render_template, request, redirect, url_for
import random
import sqlite3

app = Flask(__name__)

# 🗄️ DATABASE INIT
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # USERS TABLE
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT,
            password TEXT
        )
    ''')

    # HISTORY TABLE
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            result TEXT
        )
    ''')

    # DEFAULT USER (ONLY IF NOT EXISTS)
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES ('admin', '123')")

    conn.commit()
    conn.close()


# 🔐 LOGIN PAGE
@app.route('/')
def home():
    return render_template('login.html')


# 🔐 LOGIN LOGIC
@app.route('/login', methods=['POST'])
def login():
    user = request.form['username']
    pwd = request.form['password']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
    result = c.fetchone()

    conn.close()

    if result:
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error="Invalid Login")


# 📊 DASHBOARD
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# 🧠 DIAGNOSIS PAGE
@app.route('/diagnosis')
def diagnosis():
    return render_template('index.html')


# 🎲 RANDOM PROBABILITY
def predict_probability():
    return random.randint(60, 95)


# 🧠 PREDICT
@app.route('/predict', methods=['POST'])
def predict():
    symptoms = request.form['symptoms'].lower()

    if "fever" in symptoms and ("joint" in symptoms or "body pain" in symptoms):
        result = "🦟 Possible Dengue"
        level = "medium"
        reason = "Fever with joint pain is commonly seen in dengue."

    elif ("cough" in symptoms or "cold" in symptoms) and "fever" in symptoms:
        result = "🤧 Possible Flu"
        level = "low"
        reason = "Fever with cough suggests viral flu."

    elif "chest" in symptoms or "heart" in symptoms:
        result = "❤️ Possible Heart Issue"
        level = "high"
        reason = "Chest pain may indicate heart-related problems."

    elif "breath" in symptoms:
        result = "🫁 Breathing Problem"
        level = "high"
        reason = "Breathing difficulty can be serious."

    else:
        result = "🩺 General Infection"
        level = "low"
        reason = "Symptoms are not specific to a major condition."

    prob = predict_probability()
    final_result = f"{result} ({prob}%)"

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (result) VALUES (?)", (final_result,))
    conn.commit()
    conn.close()

    return render_template('result.html', result=final_result, level=level, reason=reason)


# 📜 HISTORY
@app.route('/history')
def show_history():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT result FROM history")
    data = c.fetchall()
    conn.close()

    return render_template('history.html', history=data)


# 🚀 RUN
if __name__ == '__main__':
    init_db()   # 🔥 VERY IMPORTANT
    app.run(host='0.0.0.0', port=10000)