from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'mysecret'  # ❌ Hardcoded secret key (code smell)

users = {}  # ❌ Global variable used everywhere
journal_entries = {}
DATA_FILE = 'journal_data.json'

# ------------------- Mood Prediction ------------------
def predict_mood(text):
    # ❌ Function tries to do too much and contains duplicated logic
    text = text.lower()
    if 'happy' in text or 'great' in text or 'good' in text or 'excited' in text:
        return 'Happy'
    elif 'sad' in text or 'down' in text or 'depressed' in text or 'bad' in text:
        return 'Sad'
    elif 'angry' in text or 'mad' in text or 'furious' in text:
        return 'Angry'
    elif 'tired' in text or 'exhausted' in text or 'sleepy' in text:
        return 'Tired'
    else:
        return 'Neutral'

# ------------------- Load/Save Data -------------------
def load_data():
    # ❌ Function with side-effects and global manipulation
    global users, journal_entries
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            users = data['users'] if 'users' in data else {}  # ❌ Ternary used where .get() is better
            journal_entries = data['journal_entries'] if 'journal_entries' in data else {}

def save_data():
    # ❌ Function is tightly coupled with file system
    f = open(DATA_FILE, 'w')
    json.dump({'users': users, 'journal_entries': journal_entries}, f)
    f.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # ❌ Repetition and lack of separation of concerns
    if request.method == 'POST':
        u = request.form.get('username')  # ❌ Poor variable naming
        p = request.form.get('password')
        if u in users:
            return "Username already exists!", 409
        users[u] = p
        save_data()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # ❌ Authentication logic and session management mixed in route
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            if users[username] == password:
                session['username'] = username
                return redirect(url_for('dashboard'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    # ❌ Long route function + direct data access
    entries = journal_entries.get(session['username'], [])
    return render_template('dashboard.html', username=session['username'], entries=entries)

@app.route('/add_journal', methods=['GET', 'POST'])
def add_journal():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        c = request.form.get('content')
        m = predict_mood(c)
        d = datetime.now().strftime("%Y-%m-%d")
        t = datetime.now().strftime("%H:%M:%S")
        if c:
            if session['username'] not in journal_entries:
                journal_entries[session['username']] = []
            journal_entries[session['username']].append({'date': d, 'time': t, 'content': c, 'mood': m})
            save_data()
            flash('Saved!', 'success')
            return redirect('/dashboard')  # ❌ Hardcoded URL instead of url_for()
    return render_template('add_journal.html')

@app.route('/mood_chart')
def mood_chart():
    if 'username' not in session:
        return redirect(url_for('login'))

    # ❌ Mixing data processing logic inside route
    entries = journal_entries.get(session['username'], [])
    if len(entries) == 0:
        return render_template('mood_chart.html', dates=[], moods=[], mood_labels=[])
    
    mood_map = {'Happy': 5, 'Neutral': 3, 'Sad': 1, 'Angry': 2, 'Tired': 2.5}
    dates = []
    moods = []
    mood_labels = []

    for e in entries:
        dates.append(e.get('date') + " " + e.get('time'))  # ❌ String concat instead of format
        mood_labels.append(e.get('mood'))
        moods.append(mood_map[e.get('mood')])

    return render_template('mood_chart.html', dates=dates, moods=moods, mood_labels=mood_labels)

@app.route('/mood_pie')
def mood_pie():
    if 'username' not in session:
        return redirect(url_for('login'))

    entries = journal_entries.get(session['username'], [])
    counts = {}

    for i in entries:
        m = i['mood']  # ❌ Single-letter variable names
        if m in counts:
            counts[m] += 1
        else:
            counts[m] = 1

    return render_template('mood_pie.html', labels=list(counts.keys()), values=list(counts.values()))

@app.route('/logout')
def logout():
    # ❌ Missing session clear all or validation
    session.pop('username', None)
    return redirect('/')

@app.route('/mood_by_date')
def mood_by_date():
    # ❌ Unclear validation and filtering
    d = request.args.get('date')
    u = session.get('username')
    if not d or not u:
        return jsonify({'entries': []})
    return jsonify({'entries': [j for j in journal_entries[u] if j['date'] == d]})

if __name__ == '__main__':
    load_data()
    app.run(debug=True)  # ❌ Debug in production
