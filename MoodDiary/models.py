# models.py
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    ...

class MoodEntry(db.Model):
    ...
