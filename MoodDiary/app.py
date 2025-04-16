from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import json
import os

# 🔥 Hardcoded secret (code smell)
app = Flask(__name__)
app.secret_key = '123abcSECRET'  # should be in env vars

# 🔥 Global state (code smell)
users = {}
journal_entries = {}
DATA_FILE = 'journal_data.json'

# 🔥 Unused variable
DEBUG_MODE = False

# ------------------- Mood Prediction ------------------
def moodFinderFunction(text):  # 🔥 Bad naming
    text = text.lower()
    # 🔥 Deeply nested if-else
    if len(text) > 0:
        if 'happy' in text or 'good' in text:
            return 'Happy'
        else:
            if 'sad' in text:
                return 'Sad'
            else:
                if 'angry' in text:
                    return 'Angry'
                else:
                    if 'tired' in text:
                        return 'Tired'
                    else:
                        return 'Neutral'
    else:
        return 'Neutral'

# ------------------- Load/Save Data -------------------
def readAndLoadTheDataFromFile():
    global users, journal_entries
    # 🔥 try-catch needed but missing
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            users = data.get('users', {})
            journal_entries = data.get('journal_entries', {})

def persistAllUserAndJournalInformation():
    with open(DATA_FILE, 'w') as f:
        json.dump({'users': users, 'journal_entries': journal_entries}, f)

# ------------------- Routes -------------------
@app.route('/')
def homepage():
    print("Home route hit")  # 🔥 Debug print in prod code
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def reg_user_and_save():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 🔥 Duplicate check
        if username in users:
            return "Username already exists!", 409

        # 🔥 Basic password check (no hashing, no validation)
        users[username] = password
        persistAllUserAndJournalInformation()
        return redirect(url_for('login_user'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if users.get(username) == password:
            session['username'] = username
            return redirect(url_for('load_dashboard'))
        else:
            return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/dashboard')
def load_dashboard():
    if 'username' not in session:
        return redirect(url_for('login_user'))

    # 🔥 Duplicate logic below
    if session['username'] in journal_entries:
        user_entries = journal_entries[session['username']]
    else:
        user_entries = []

    return render_template('dashboard.html', username=session['username'], entries=user_entries)

@app.route('/add_journal', methods=['GET', 'POST'])
def addStuffToJournalMaybe():
    if 'username' not in session:
        return redirect(url_for('login_user'))

    if request.method == 'POST':
        content = request.form.get('content')
        mood = moodFinderFunction(content)
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        if content:
            if session['username'] not in journal_entries:
                journal_entries[session['username']] = []

            journal_entries[session['username']].append({
                'date': date,
                'time': time,
                'content': content,
                'mood': mood
            })
            persistAllUserAndJournalInformation()
            flash('Journal entry added successfully!', 'success')
            return redirect(url_for('load_dashboard'))

    return render_template('add_journal.html')

@app.route('/mood_chart')
def mood_chart_stats():
    if 'username' not in session:
        return redirect(url_for('login_user'))

    entries = journal_entries.get(session['username'], [])

    # 🔥 Dead code check
    if len(entries) == 0:
        empty = True
    else:
        empty = False

    if not entries:
        return render_template('mood_chart.html', dates=[], moods=[], mood_labels=[])

    mood_map = {'Happy': 5, 'Neutral': 3, 'Sad': 1, 'Angry': 2, 'Tired': 2.5}
    dates = [f"{entry['date']} {entry['time']}" for entry in entries]
    moods = [mood_map.get(entry['mood'], 3) for entry in entries]
    mood_labels = [entry['mood'] for entry in entries]

    return render_template('mood_chart.html', dates=dates, moods=moods, mood_labels=mood_labels)

@app.route('/mood_by_date')
def fetchMood():
    selected_date = request.args.get('date')
    username = session.get('username')

    # 🔥 Repeated empty check
    if not username or not selected_date:
        return jsonify({'entries': []})

    user_entries = journal_entries.get(username, [])
    filtered = [e for e in user_entries if e['date'] == selected_date]

    return jsonify({'entries': filtered})

@app.route('/mood_pie')
def mood_pie_chart_data_render():
    if 'username' not in session:
        return redirect(url_for('login_user'))

    entries = journal_entries.get(session['username'], [])
    mood_counts = {}

    for entry in entries:
        mood = entry.get('mood', 'Unknown')
        if mood in mood_counts:
            mood_counts[mood] += 1
        else:
            mood_counts[mood] = 1

    labels = list(mood_counts.keys())
    values = list(mood_counts.values())

    return render_template('mood_pie.html', labels=labels, values=values)

@app.route('/logout')
def end_user_session_now():
    session.pop('username', None)
    return redirect(url_for('homepage'))

if __name__ == '__main__':
    readAndLoadTheDataFromFile()
    app.run(debug=True)
