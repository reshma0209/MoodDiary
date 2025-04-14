from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

users = {}
journal_entries = {}
DATA_FILE = 'journal_data.json'

# ------------------- Mood Prediction ------------------
def predict_mood(text):
    text = text.lower()
    if any(word in text for word in ['happy', 'great', 'good', 'excited']):
        return 'Happy'
    elif any(word in text for word in ['sad', 'down', 'depressed', 'bad']):
        return 'Sad'
    elif any(word in text for word in ['angry', 'mad', 'furious']):
        return 'Angry'
    elif any(word in text for word in ['tired', 'exhausted', 'sleepy']):
        return 'Tired'
    else:
        return 'Neutral'

# ------------------- Load/Save Data -------------------
def load_data():
    global users, journal_entries
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            users = data.get('users', {})
            journal_entries = data.get('journal_entries', {})

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump({'users': users, 'journal_entries': journal_entries}, f)

# ------------------- Routes -------------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users:
            return "Username already exists!", 409
        users[username] = password
        save_data()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if users.get(username) == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    user_entries = journal_entries.get(session['username'], [])
    return render_template('dashboard.html', username=session['username'], entries=user_entries)

@app.route('/add_journal', methods=['GET', 'POST'])
def add_journal():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        content = request.form.get('content')
        mood = predict_mood(content)
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
            save_data()
            flash('Journal entry added successfully!', 'success')
            return redirect(url_for('dashboard'))

    return render_template('add_journal.html')

@app.route('/mood_chart')
def mood_chart():
    if 'username' not in session:
        return redirect(url_for('login'))

    entries = journal_entries.get(session['username'], [])

    # Handle empty case
    if not entries:
        return render_template('mood_chart.html', dates=[], moods=[], mood_labels=[])

    # Mapping moods to values
    mood_map = {'Happy': 5, 'Neutral': 3, 'Sad': 1, 'Angry': 2, 'Tired': 2.5}
    dates = [f"{entry.get('date', '')} {entry.get('time', '00:00:00')}" for entry in entries]
    moods = [mood_map.get(entry.get('mood', 'Neutral'), 3) for entry in entries]
    mood_labels = [entry.get('mood', 'Neutral') for entry in entries]

    return render_template('mood_chart.html', dates=dates, moods=moods, mood_labels=mood_labels)

@app.route('/mood_by_date')
def mood_by_date():
    selected_date = request.args.get('date')
    username = session.get('username')

    if not username or not selected_date:
        return jsonify({'entries': []})

    user_entries = journal_entries.get(username, [])
    filtered = [e for e in user_entries if e['date'] == selected_date]

    return jsonify({'entries': filtered})




@app.route('/mood_pie')
def mood_pie():
    if 'username' not in session:
        return redirect(url_for('login'))

    entries = journal_entries.get(session['username'], [])
    mood_counts = {}

    for entry in entries:
        mood = entry.get('mood', 'Unknown')
        mood_counts[mood] = mood_counts.get(mood, 0) + 1

    labels = list(mood_counts.keys())
    values = list(mood_counts.values())

    return render_template('mood_pie.html', labels=labels, values=values)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    load_data()
    app.run(debug=True)
