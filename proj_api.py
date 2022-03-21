from flask import Flask, render_template,request,redirect,url_for
import os
from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db1.db'

db = SQLAlchemy(app)



class User(db.Model):
    __tablename__ = 'user'
    user_id=db.Column(db.Integer,primary_key=True, autoincrement=True)
    user_name=db.Column(db.String(100),nullable=False)
    first_name=db.Column(db.String(100), nullable=False)
    last_name=db.Column(db.String(100))
    password=db.Column(db.String(100),nullable=False)
    def __repr__(self):
        return "<User %r>" %self.user_id

class Tracker(db.Model):
    __tablename__ = 'tracker'
    tracker_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracker_type=db.Column(db.String(100), nullable=False)
    tracker_name=db.Column(db.String(100),nullable=False)
    description=db.Column(db.String(100),nullable=False)
    def __repr__(self):
        return "<Tracker %r" %self.tracker_id

class Tracker_Numerical(db.Model):
    tracker_id=db.Column(db.Integer,db.ForeignKey('tracker.tracker_id'), nullable=False, primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'), nullable=False, primary_key=True)
    tracker_timestamp=db.Column(db.DateTime,default=datetime.datetime.utcnow(),primary_key=True)
    tracker_value=db.Column(db.Float,nullable=False)
    tracker_note=db.Column(db.String(100))
class Tracker_multi_choice(db.Model):
    tracker_id=db.Column(db.Integer,db.ForeignKey('tracker.tracker_id'), nullable=False, primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'), nullable=False, primary_key=True)
    tracker_timestamp=db.Column(db.DateTime,default=datetime.datetime.utcnow(),primary_key=True)
    tracker_value=db.Column(db.String(50),nullable=False)
    tracker_note=db.Column(db.String(100))

class Tracker_boolean(db.Model):
    tracker_id=db.Column(db.Integer,db.ForeignKey('tracker.tracker_id'), nullable=False, primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'), nullable=False, primary_key=True)
    tracker_timestamp=db.Column(db.DateTime,default=datetime.datetime.utcnow(), primary_key=True)
    tracker_value=db.Column(db.Boolean,nullable=False)
    tracker_note=db.Column(db.String(100))





class addT(Resource):
    #@marshal_with(resource_fields)
    def get(self):
        return "hello"

    #@marshal_with(resource_fields)
    def post(self):

        return 'post'

api.add_resource(addT, "/add_tracker")

class Trackers(Resource):
    #@marshal_with(resource_fields)
    def get(self):
        return "hello"

    #@marshal_with(resource_fields)
    def post(self):
        return 'post'

api.add_resource(Trackers, "/trackers")

'''class addT(Resource):
    #@marshal_with(resource_fields)
    def get(self):
        return "hello"

    #@marshal_with(resource_fields)
    def post(self):
        return 'post'

api.add_resource(addT, "/add_tracker")'''

