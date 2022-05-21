from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with, marshal
from models import *
api = Api(app) 

#TRACKERS: CREATE: ARGS
trackers_post_args = reqparse.RequestParser()
trackers_post_args.add_argument("tracker_name", type=str, help="Name of the tracker is required", required=True)
trackers_post_args.add_argument("tracker_type", type=str, help="type  of the tracker is required", required=True)
trackers_post_args.add_argument("description", type=str, help="description of the tracker is required", required=True)
trackers_post_args.add_argument("settings", type=str)

#TRACKERS: UPDATE: ARGS
trackers_update_args = reqparse.RequestParser()
trackers_update_args.add_argument("tracker_name", type=str, help="Name of the tracker is required", required=True)
trackers_update_args.add_argument("description", type=str, help="description of the tracker is required", required=True)
trackers_update_args.add_argument("settings", type=str)

#LOGS, BOOLEAN: POST, PUT: ARGS
bool_args = reqparse.RequestParser()
#logs_post_args.add_argument("tracker_timestamp")
bool_args.add_argument("tracker_value", type=bool,  help="value of the tracker log is required", required=True)
bool_args.add_argument("tracker_note", type=str, help="note for the tracker log is required", required=True)

#LOGS, NUMERICAL: POST, PUT: ARGS
numerical_args = reqparse.RequestParser()
#logs_post_args.add_argument("tracker_timestamp")
numerical_args.add_argument("tracker_value", type=int,  help="value of the tracker log is required", required=True)
numerical_args.add_argument("tracker_note", type=str, help="note for the tracker log is required", required=True)

#LOGS, MULTICHOICE: POST, PUT: ARGS
multi_args = reqparse.RequestParser()
#logs_post_args.add_argument("tracker_timestamp")
multi_args.add_argument("tracker_value", type=str,  help="value of the tracker log is required", required=True)
multi_args.add_argument("tracker_note", type=str, help="note for the tracker log is required", required=True)

#TRACKER: GET: JSON
tracker_json = {
    'tracker_id': fields.Integer,
    'tracker_type': fields.String,
    'tracker_name': fields.String,
    'description': fields.String,
    'settings': fields.String,
    'user_id': fields.Integer
}
tracker_boolean_json= {
    'log_id': fields.Integer,
    'tracker_id': fields.Integer,
    'tracker_timestamp': fields.String,
    'tracker_value': fields.Boolean,
    'tracker_note': fields.String,
}
tracker_numerical_json= {
    'log_id': fields.Integer,
    'tracker_id': fields.Integer,
    'tracker_timestamp': fields.String,
    'tracker_value': fields.Integer,
    'tracker_note': fields.String,
}
tracker_multichoice_json= {
    'log_id': fields.Integer,
    'tracker_id': fields.Integer,
    'tracker_timestamp': fields.String,
    'tracker_value': fields.String,
    'tracker_note': fields.String,
}



#API: TRACKERS: CRUD

class Trackers(Resource):
#API: TRACKER: READ
    @marshal_with(tracker_json)
    def get(self, user_id ):
        allT= Tracker.query.filter_by(user_id=user_id).all()
        return allT
#API: TRACKER: CREATE
    def post(self, user_id):
        args = trackers_post_args.parse_args()
        newT = Tracker(user_id= user_id, tracker_name=args['tracker_name'], tracker_type=args['tracker_type'], description=args['description'])
        db.session.add(newT)
        db.session.commit()

api.add_resource(Trackers, "/<int:user_id>/trackers")

#API: TRACKER: UPDATE
class Tracker_manipulate(Resource):
    def put(self, user_id, tracker_id ):
        args = trackers_update_args.parse_args()
        trackerUpdate= Tracker.query.filter_by(tracker_id= tracker_id).update(dict(tracker_name= args['tracker_name'], description= args['description']))
        db.session.commit()
        return 'succesfully updated'

#API: TRACKER: DELETE
    #@marshal_with(resource_fields)
    def delete(self, user_id, tracker_id):
        Tracker.query.filter_by(tracker_id= tracker_id).delete()
        db.session.commit()
        return 'sucessfully deleted'
api.add_resource(Tracker_manipulate, "/<int:user_id>/tracker/<int:tracker_id>")

type_dict= {'numerical': Tracker_Numerical, 'multiple_choice': Tracker_multi_choice, 'boolean': Tracker_boolean, 'time_duration':Tracker_Numerical }
logs_json_dict= {'numerical': tracker_numerical_json, 'multiple_choice': tracker_multichoice_json, 'boolean': tracker_boolean_json, 'time_duration':tracker_numerical_json }

logType= {Tracker_Numerical: numerical_args, Tracker_multi_choice: multi_args, Tracker_boolean: bool_args}

#API: LOGS: CRUD
#API: LOG: READ, CREATE
class Tracker_logs(Resource):
    def get(self, user_id, tracker_id):
        tType= Tracker.query.filter_by(tracker_id=tracker_id).first().tracker_type
        logClass=type_dict[tType]
        tLogs=logClass.query.filter_by(tracker_id=tracker_id).all()
        return  marshal(tLogs, logs_json_dict[tType])

    def post(self, user_id, tracker_id):
        tType= Tracker.query.filter_by(tracker_id=tracker_id).first().tracker_type
        logClass=type_dict[tType]
        args = logType[logClass].parse_args()
        newLog = logClass(tracker_id=tracker_id, tracker_value=args['tracker_value'], tracker_note=args['tracker_note'])
        db.session.add(newLog)
        db.session.commit()
        return 'new log added '
api.add_resource(Tracker_logs, "/<int:user_id>/<int:tracker_id>/tracker_logs")

#API: LOGS: UPDATE
class log_manipulate(Resource):

    #@marshal_with(logs_json_dict[tType])
    def put(self, user_id, tracker_id, log_id):
        tType= Tracker.query.filter_by(tracker_id=tracker_id).first().tracker_type
        logClass=type_dict[tType]
        args = logType[logClass].parse_args()
        logUpdate=logClass.query.filter_by(tracker_id=tracker_id, log_id=log_id).update(dict(tracker_value=args['tracker_value'], tracker_note=args['tracker_note']))
        db.session.commit()
        return 'tracker_log updated'

#API: LOGS: DELETE
#@marshal_with(resource_fields)
    def delete(self, user_id, tracker_id, log_id):
        tType= Tracker.query.filter_by(tracker_id=tracker_id).first().tracker_type
        logClass=type_dict[tType]
        logClass.query.filter_by(log_id=log_id).delete()
        db.session.commit()
        return 'tracker_log deleted'

api.add_resource(log_manipulate, "/<int:user_id>/<int:tracker_id>/tracker_log/<int:log_id>")
