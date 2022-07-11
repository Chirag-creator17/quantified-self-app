from flask import render_template,request,redirect,jsonify,json
import requests
from flask_bcrypt import Bcrypt
import matplotlib.pyplot as plt
from matplotlib import use 
use('Agg')
from models import *
from api import *

bcrypt = Bcrypt(app)
BASE = "http://127.0.0.1:5000/"

#ROUTE: LANDING PAGE
@app.route('/')
def landing_page():
    return render_template('landing.html')

#ROUTE: LOGIN
@app.route('/login', methods= ["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template('login.html')
    
    if request.method == "POST":
        
        #Getting username and password form form 
        user_name=request.form['u_name']
        user_password=request.form['pswd']
        
        #Checking if user exists
        user_info= User.query.filter_by(user_name= user_name).all()
        
        #Checking if user does not exist if not redirect to signup page
        if(len(user_info)==0):
            return render_template('login.html', error= "No user found")
        
        #Checking if password is correct
        for i in user_info:
            if(bcrypt.check_password_hash(i.password, user_password)):     #Unhashing password and checking if it matches
                u_id= user_info[0].user_id
                return redirect(f'/{u_id}/{user_name}/dashboard')          #Redirecting to dashboard if password is correct
            
        #If password is incorrect redirect to login page
        return render_template('login.html', error= "Wrong password")
    
# Function for backend validation of password  while user will register
def validate(password):
    if(len(password)<=8):
        return "Password must be atleast 8 characters long"
    special_charater_count ,interger_count , upper_case=0,0,0
    special_charaters=['[','@','_','!','#','$','%','^','&','*','(',')','<','>','?','/','|','}','{','~',':',']','+','-',',']
    for i in password:
        if(i in special_charaters):
            special_charater_count+=1
        if(i.isdigit()):
            interger_count+=1
        if(i.isupper()):
            upper_case+=1
    if(special_charater_count==0):
        return "Password must contain atleast one special character"
    if(interger_count==0):
        return "Password must contain atleast one number"
    if(upper_case==0):
        return "Password must contain atleast one uppercase letter"
    if(len(password)-special_charater_count-interger_count-upper_case<=0):
        return "Password must contain atleast one lowercase letter"
    return "valid"

#ROUTE: REGISTER
@app.route('/register', methods= ["GET", "POST"] )
def register():
    if request.method == "POST":
        
        # Getting details form form
        user_name, first_name= request.form['u_name'], request.form['f_name']
        last_name, user_password= request.form['l_name'], request.form['pswd']
        
        # Validating password
        if(validate(user_password)=="valid"):
            user_password_hashed= bcrypt.generate_password_hash(user_password).decode('utf-8')    #Hashing password
            add_user= User(user_name=user_name, first_name=first_name, last_name=last_name, password=user_password_hashed)   #Adding user to database
            db.session.add(add_user)
            db.session.commit()
            return redirect('/login')
        
        #If password is invalid redirect to register page
        return render_template('register.html', error= validate(user_password))
    
    if request.method == "GET":
       return render_template('register.html')

#ROUTES: TRACKER CRUD
#ROUTE: TRACKER READ
@app.route('/<int:user_id>/<user_name>/dashboard')
def dashboardView(user_id, user_name):
    
    # Getting tracker data from database by api
    tracker_list_request= requests.get(BASE + str(user_id)+ "/trackers")
    tracker_list= tracker_list_request.json()
    # print(tracker_list)
    
    # making list of trackers and getting the last log value for each tracker 
    for tracker in tracker_list:
        tlog= requests.get(f"{BASE}{user_id}/{str(tracker['tracker_id'])}/tracker_logs")   #Getting tracker logs
        tlogDict= tlog.json()
        if(len(tlogDict)>0):
            last_log=tlogDict[-1]['tracker_timestamp']
            tracker['logs']=last_log.split('.')[0]
        else:
            tracker['logs']='No logs found'               #If no logs found for a tracker, set it to 'No logs found'
            
    return render_template('dashboard.html', tDict=tracker_list, user_name=user_name, user_id= user_id)

#ROUTE: TRACKER CREATE
@app.route('/<int:user_id>/<user_name>/add_tracker', methods= ["GET","POST"])
def addTracker(user_id, user_name):
    
    if request.method == 'POST':
        # Getting details from form
        tracker_name, tracker_description= request.form['tName'], request.form['tDesc']
        tracker_type= request.form['ttypes']
        
        # adding tracker to database by api
        requests.post(BASE + str(user_id)+ "/trackers", {'tracker_type': tracker_type, 'tracker_name': tracker_name, 'description': tracker_description})
        return redirect(f'/{user_id}/{user_name}/dashboard')
    
    elif request.method == 'GET':
        return render_template('add-tracker.html', user_name=user_name, user_id= user_id)


#ROUTE: TRACKER UPDATE
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/update_tracker' , methods= ["GET","POST"])
def updateTracker(user_id, user_name, tracker_id):
    
    if request.method == 'POST':
        # Getting details from form
       tracker_name, tracker_details= request.form['tName'], request.form['tDesc']
       
       # updating tracker in database by api
       requests.put(BASE + str(user_id)+ "/tracker/" +str(tracker_id), {'tracker_name': tracker_name, 'description': tracker_details })
       return redirect(f'/{user_id}/{user_name}/dashboard')
   
    elif request.method == 'GET':
        # Getting tracker data from database by api
        tracker_list_request= requests.get(BASE + str(user_id)+ "/trackers")
        tracker_list= tracker_list_request.json()
        trac_name= ""
        trac_desc= ""
        trac_type= ""
        for tracker in tracker_list:
            if(tracker['tracker_id']==tracker_id):
                trac_name= tracker['tracker_name']
                trac_desc= tracker['description']
                trac_type= tracker['tracker_type']
                break
        return render_template('update-tracker.html' , user_name=user_name, user_id= user_id, tracker_id= tracker_id, trac_n= trac_name, tracker_desc= trac_desc, tracker_type= trac_type)

#ROUTE: TRACKER DELETE
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/delete_tracker')
def delT(user_id, user_name, tracker_id):
    # deleting tracker from database by api
    requests.delete(BASE + str(user_id) +"/tracker/"+ str(tracker_id))
    return redirect(f'/{user_id}/{user_name}/dashboard')


#TRACKER LOGS: CRUD,  ROUTES
#READ LOGS, ROUTES
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/<tracker_name>/tracker_logs', methods= ["GET","POST"])
def viewT(user_id, user_name, tracker_id, tracker_name):
    logL= requests.get(BASE + str(user_id)+"/" + str(tracker_id)+ "/tracker_logs")
    logListJson= logL.json()
    tracker_values=[]
    tracker_log=[]
    flag=1
    tracker_type=""
    if(len(logListJson)>0):
        if(logListJson[0]['tracker_value']=="False" or logListJson[0]['tracker_value']=="True"):
            tracker_type="boolean"
        else:
            tracker_type="numerical"
        for i in logListJson:
            ts= i['tracker_timestamp'].split(' ')
            tracker_log.append(ts[0])
            tracker_values.append(i['tracker_value'])
        plt.clf()
        if(tracker_type=="boolean"):
            true_value,false_value=0,0
            for i in tracker_values:
                if(i=="True"):
                    true_value+=1
                else:
                    false_value+=1
            if(true_value+false_value==0):
                flag=0
            plt.pie([true_value,false_value],labels=["True","False"], shadow=True, startangle=90)
            plt.legend(loc="lower right")
        else:
            plt.scatter(tracker_log, tracker_values)
        plt.savefig('./static/hist.png')
        
        for i in range(len(logListJson)):
            time_change= logListJson[i]['tracker_timestamp']
            l=time_change.split('.')
            logListJson[i]['tracker_timestamp']= l[0]
    else:
        flag=0
    tracker_name=tracker_name.capitalize()
    return render_template('view-tracker.html', user_id= user_id, user_name=user_name,flag=flag, tracker_id= tracker_id, tracker_name=tracker_name, logListJson= logListJson,tracker_type= tracker_type)

#ADD A LOG, ROUTE
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/<tracker_name>/add_log', methods= ["GET","POST"])
def addLog(user_id, user_name, tracker_id, tracker_name):
    trackers=requests.get(f"{BASE}/{str(user_id)}/trackers")
    tracker_json=trackers.json()
    tracker_type=''
    for i in tracker_json:
        if(i['tracker_id']==tracker_id):
            tracker_type= i['tracker_type']
            break
    tz = pytz.timezone('Asia/Kolkata')
    tr=tz.localize(datetime.datetime.now())
    tracker_time=tr.strftime("%H:%M:%S")
    if request.method == 'POST':
        tracker_value, tracker_note= request.form['value'], request.form['notes']
        requests.post(BASE + str(user_id) +"/" +str(tracker_id)+ "/tracker_logs", {'tracker_value':tracker_value, 'tracker_note':tracker_note})
        return redirect(f'/{user_id}/{user_name}/{tracker_id}/{tracker_name}/tracker_logs')
    elif request.method == 'GET':
        return render_template('add-logs.html', user_id= user_id, user_name=user_name, tracker_id= tracker_id, tracker_name=tracker_name,tracker_type=tracker_type,tracker_time=tracker_time)

#UPDATE A LOG, ROUTE
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/<tracker_name>/<int:log_id>/update_log' , methods= ["GET","POST"])
def updateLog(user_id, user_name, tracker_id, log_id, tracker_name):
    if request.method == 'POST':
       tracker_value, tracker_note= request.form['value'], request.form['notes']
       requests.put(f'{BASE}{user_id}/{tracker_id}/tracker_log/{log_id}', {'tracker_value':tracker_value, 'tracker_note':tracker_note})
       return redirect(f'/{user_id}/{user_name}/{tracker_id}/{tracker_name}/tracker_logs')
    elif request.method == 'GET':
        response = requests.get(f"{BASE}{user_id}/{tracker_id}/tracker_logs")
        tlogs=response.json()
        for r in tlogs:
            if r['log_id']== log_id:
               lv= r['tracker_value']
               ln= r['tracker_note']
               ltime= r['tracker_timestamp']
        test=requests.get(f"{BASE}/{str(user_id)}/trackers")
        test_json=test.json()
        tracker_type=''
        for i in test_json:
            if(i['tracker_id']==tracker_id):
                tracker_type= i['tracker_type']
        return render_template('update-log.html', user_id= user_id, user_name=user_name, tracker_id= tracker_id, tracker_name=tracker_name, log_id=log_id, lv=lv, ln=ln, ltime=ltime, tracker_type=tracker_type)

#DELETE A LOG, ROUTE
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/<tracker_name>/<int:log_id>/delete_log', methods= ["GET","POST"])
def deleteLog(user_id, user_name, tracker_id, log_id, tracker_name ):
    requests.delete(BASE + str(user_id)+"/" + str(tracker_id)+ "/tracker_log/"+ str(log_id))
    return redirect(f'/{user_id}/{user_name}/{tracker_id}/{tracker_name}/tracker_logs')

if __name__ == '__main__':
    app.run( debug=True)

