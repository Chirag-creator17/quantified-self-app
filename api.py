from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with, marshal
from models import *
api = Api(app)

# TRACKER: GET: JSON
tracker_json = {
    'tracker_id': fields.Integer,
    'tracker_type': fields.String,
    'tracker_name': fields.String,
    'description': fields.String,
    'settings': fields.String,
    'user_id': fields.Integer
}
tracker_boolean_json = {
    'log_id': fields.Integer,
    'tracker_id': fields.Integer,
    'tracker_timestamp': fields.String,
    'tracker_value': fields.String,
    'tracker_note': fields.String,
}
tracker_numerical_json = {
    'log_id': fields.Integer,
    'tracker_id': fields.Integer,
    'tracker_timestamp': fields.String,
    'tracker_value': fields.Integer,
    'tracker_note': fields.String,
}
tracker_multichoice_json = {
    'log_id': fields.Integer,
    'tracker_id': fields.Integer,
    'tracker_timestamp': fields.String,
    'tracker_value': fields.String,
    'tracker_note': fields.String,
}
type_dict = {
    'numerical': Tracker_Numerical,
    'multiple_choice': Tracker_multi_choice,
    'boolean': Tracker_boolean
}
logs_json_dict = {
    'numerical': tracker_numerical_json,
    'multiple_choice': tracker_multichoice_json,
    'boolean': tracker_boolean_json
}

# TRACKERS: CREATE: ARGS
tp_args = reqparse.RequestParser()
tp_args.add_argument(
    "tracker_name", type=str, help="Name of the tracker is required", required=True)
tp_args.add_argument(
    "tracker_type", type=str, help="type  of the tracker is required", required=True)
tp_args.add_argument(
    "description", type=str, help="description of the tracker is required", required=True)
tp_args.add_argument("settings", type=str)

# TRACKERS: UPDATE: ARGS
tu_args = reqparse.RequestParser()
tu_args.add_argument(
    "tracker_name", type=str, help="Name of the tracker is required", required=True)
tu_args.add_argument(
    "description", type=str, help="description of the tracker is required", required=True)
tu_args.add_argument("settings", type=str)

# LOGS, BOOLEAN: POST, PUT: ARGS
bool_args = reqparse.RequestParser()
bool_args.add_argument("tracker_value", type=str,
                       help="value of the tracker log is required", required=True)
bool_args.add_argument("tracker_note", type=str,
                       help="note for the tracker log is required", required=True)

# LOGS, NUMERICAL: POST, PUT: ARGS
mum_args = reqparse.RequestParser()
mum_args.add_argument("tracker_value", type=int,
                            help="value of the tracker log is required", required=True)
mum_args.add_argument(
    "tracker_note", type=str, help="note for the tracker log is required", required=True)

# LOGS, MULTICHOICE: POST, PUT: ARGS
multi_args = reqparse.RequestParser()
# logs_post_args.add_argument("tracker_timestamp")
multi_args.add_argument("tracker_value", type=str,
                        help="value of the tracker log is required", required=True)
multi_args.add_argument("tracker_note", type=str,
                        help="note for the tracker log is required", required=True)

logType = {
    Tracker_Numerical: mum_args,
    Tracker_multi_choice: multi_args,
    Tracker_boolean: bool_args
}
# API: TRACKERS: CRUD


class Trackers(Resource):
    # API: TRACKER: READ
    @marshal_with(tracker_json)
    def get(self, user_id):
        allT = Tracker.query.filter_by(user_id=user_id).all()
        return allT
    # API: TRACKER: CREATE
    def post(self, user_id):
        args = tp_args.parse_args()
        new_tracker = Tracker(user_id=user_id, tracker_name=args['tracker_name'],
                       tracker_type=args['tracker_type'], description=args['description'])
        db.session.add(new_tracker)
        db.session.commit()
        
api.add_resource(Trackers, "/<int:user_id>/trackers")

# API: TRACKER: UPDATE

class Tracker_manipulate(Resource):
    def put(self, user_id, tracker_id):
        args = tu_args.parse_args()
        trackerUpdate = Tracker.query.filter_by(tracker_id=tracker_id).update(
            dict(tracker_name=args['tracker_name'], description=args['description']))
        db.session.commit()
        return 'succesfully updated'

# API: TRACKER: DELETE
    # @marshal_with(resource_fields)
    def delete(self, user_id, tracker_id):
        Tracker.query.filter_by(tracker_id=tracker_id).delete()
        db.session.commit()
        return 'sucessfully deleted'

api.add_resource(Tracker_manipulate, "/<int:user_id>/tracker/<int:tracker_id>")


# API: LOGS: CRUD
# API: LOG: READ, CREATE

class Tracker_logs(Resource):
    def get(self, user_id, tracker_id):
        tracker_type = Tracker.query.filter_by(
            tracker_id=tracker_id).first().tracker_type
        logClass = type_dict[tracker_type]
        tLogs = logClass.query.filter_by(tracker_id=tracker_id).all()
        return marshal(tLogs, logs_json_dict[tracker_type])

    def post(self, user_id, tracker_id):
        tracker_type = Tracker.query.filter_by(
            tracker_id=tracker_id).first().tracker_type
        logClass = type_dict[tracker_type]
        args = logType[logClass].parse_args()
        newLog = logClass(
            tracker_id=tracker_id, tracker_value=args['tracker_value'], tracker_note=args['tracker_note'])
        db.session.add(newLog)
        db.session.commit()
        return 'new log added '

api.add_resource(Tracker_logs, "/<int:user_id>/<int:tracker_id>/tracker_logs")

# API: LOGS: UPDATE


class log_manipulate(Resource):

    # @marshal_with(logs_json_dict[tracker_type])
    def put(self, user_id, tracker_id, log_id):
        tracker_type = Tracker.query.filter_by(
            tracker_id=tracker_id).first().tracker_type
        logClass = type_dict[tracker_type]
        args = logType[logClass].parse_args()
        logUpdate = logClass.query.filter_by(tracker_id=tracker_id, log_id=log_id).update(
            dict(tracker_value=args['tracker_value'], tracker_note=args['tracker_note']))
        db.session.commit()
        return 'tracker_log updated'

# API: LOGS: DELETE
# @marshal_with(resource_fields)
    def delete(self, user_id, tracker_id, log_id):
        tracker_type = Tracker.query.filter_by(
            tracker_id=tracker_id).first().tracker_type
        logClass = type_dict[tracker_type]
        logClass.query.filter_by(log_id=log_id).delete()
        db.session.commit()
        return 'tracker_log deleted'


api.add_resource(
    log_manipulate, "/<int:user_id>/<int:tracker_id>/tracker_log/<int:log_id>")
