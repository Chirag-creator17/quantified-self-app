from flask import *
from flask_sqlalchemy import SQLAlchemy
import datetime
import pytz
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fdb1.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()
tz = pytz.timezone('Asia/Kolkata')


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100))
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return "<User %r>" % self.user_id


class Tracker(db.Model):
    __tablename__ = 'tracker'
    tracker_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracker_type = db.Column(db.String(100), nullable=False)
    tracker_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    settings = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    def __repr__(self):
        return "<Tracker %r" % self.tracker_id


class Tracker_Numerical(db.Model):
    tracker_id = db.Column(db.Integer, db.ForeignKey(
        'tracker.tracker_id'), nullable=False)
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracker_timestamp = db.Column(
        db.DateTime, default=tz.localize(datetime.datetime.now()))
    tracker_value = db.Column(db.Float, nullable=False)
    tracker_note = db.Column(db.String(100))


class Tracker_boolean(db.Model):
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracker_id = db.Column(db.Integer, db.ForeignKey(
        'tracker.tracker_id'), nullable=False)
    tracker_timestamp = db.Column(
        db.DateTime, default=tz.localize(datetime.datetime.now()))
    tracker_value = db.Column(db.String(10), nullable=False)
    tracker_note = db.Column(db.String(100))
