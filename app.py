from flask import render_template,request,redirect
import requests
from flask_bcrypt import Bcrypt
import matplotlib.pyplot as plt
from matplotlib import use 
use('Agg')
from models import *
from api import *

bcrypt = Bcrypt(app)
BASE = "http://127.0.0.1:5000/"

@app.route('/')
def land():
    return render_template('landing.html')

@app.route('/login', methods= ["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template('login.html')
    if request.method == "POST":
        un, pw= request.form['u_name'], request.form['pswd']
        userInfo= User.query.filter_by(user_name= un).all()
        if(len(userInfo)==0):
            return render_template('login.html', error= "No user found")
        for i in userInfo:
            if(bcrypt.check_password_hash(i.password, pw)):
                uid= userInfo[0].user_id
                return redirect(f'/{uid}/{un}/dashboard')
        return render_template('login.html', error= "Wrong password")

#ROUTE: REGISTER
@app.route('/register', methods= ["GET", "POST"] )
def register():
    if request.method == "POST":
        un, fn= request.form['u_name'], request.form['f_name']
        ln, pw= request.form['l_name'], request.form['pswd']
        pw_hash= bcrypt.generate_password_hash(pw).decode('utf-8')
        addUser= User(user_name=un, first_name=fn, last_name=ln, password=pw_hash)
        db.session.add(addUser)
        db.session.commit()
        return redirect('/login')
    if request.method == "GET":
       return render_template('register.html')

#ROUTES: TRACKER CRUD
#ROUTE: TRACKER READ
@app.route('/<int:user_id>/<user_name>/dashboard')
def dash(user_id, user_name):
    tList = requests.get(BASE + str(user_id)+ "/trackers", {'tracker_type': 'Boolean', 'tracker_name': 'helping', 'description': 'counting days of helping '})
    tDict= tList.json()
    l= []
    for r in tDict:
        tid= r['tracker_id']
        tid=str(tid)
        tlog= requests.get(f"{BASE}{user_id}/{tid}/tracker_logs")
        tlogDict= tlog.json()
        if(len(tlogDict)>0):
            for i in tlogDict:
                l.append(i['tracker_timestamp'])
    j=0
    for i in tDict:
        if(len(l)>j):
            s=l[j].split(' ')
            i['logs']= s[0]
            j+=1
        else:
            i['logs']= 'No logs found'
    # print(tDict)
    #return str(len(tDict))
    return render_template('dashboard.html', tDict=tDict, user_name=user_name, user_id= user_id)

#ROUTE: TRACKER CREATE
@app.route('/<int:user_id>/<user_name>/add_tracker', methods= ["GET","POST"])
def addT(user_id, user_name):
    if request.method == 'POST':
        tn, td= request.form['tName'], request.form['tDesc']
        tt= request.form['ttypes']
        requests.post(BASE + str(user_id)+ "/trackers", {'tracker_type': tt, 'tracker_name': tn, 'description': td})
        return redirect(f'/{user_id}/{user_name}/dashboard')
    elif request.method == 'GET':
        return render_template('add-tracker.html', user_name=user_name, user_id= user_id)

#ROUTE: TRACKER UPDATE
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/update_tracker' , methods= ["GET","POST"])
def upT(user_id, user_name, tracker_id):
    #return render_template('update1.html' , user_name=user_name, user_id= user_id, tracker_id= tracker_id)
    if request.method == 'POST':
       tn, td= request.form['tName'], request.form['tDesc']
       requests.put(BASE + str(user_id)+ "/tracker/" +str(tracker_id), {'tracker_name': tn, 'description': td })
       return redirect(f'/{user_id}/{user_name}/dashboard')
    elif request.method == 'GET':
        t=Tracker.query.filter_by(tracker_id=tracker_id).first()
        trac_n= t.tracker_name
        trac_d= t.description
        trac_t= t.tracker_type
        return render_template('update-tracker.html' , user_name=user_name, user_id= user_id, tracker_id= tracker_id, trac_n= trac_n, tracker_desc= trac_d, tracker_type= trac_t)

#ROUTE: TRACKER DELETE
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/delete_tracker')
def delT(user_id, user_name, tracker_id):
    requests.delete(BASE + str(user_id) +"/tracker/"+ str(tracker_id))
    return redirect(f'/{user_id}/{user_name}/dashboard')


#TRACKER LOGS: CRUD,  ROUTES
#READ LOGS, ROUTES
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/<tracker_name>/tracker_logs', methods= ["GET","POST"])
def viewT(user_id, user_name, tracker_id, tracker_name):
    logL= requests.get(BASE + str(user_id)+"/" + str(tracker_id)+ "/tracker_logs")
    logListJson= logL.json()
    response = requests.get(f"{BASE}{str(user_id)}/trackers")
    td= response.json()
    s=""
    for r in td:
        if r['tracker_id']== tracker_id:
            tt= r['tracker_type']
            s=tt
    tracker_values=[]
    tracker_log=[]
    for i in logListJson:
        ts= i['tracker_timestamp']
        ts= ts.split(' ')
        tracker_log.append(ts[0])
        tracker_values.append(i['tracker_value'])
    plt.clf()
    plt.scatter(tracker_log, tracker_values)
    plt.savefig('./static/hist.png')
    for i in range(len(logListJson)):
        time_change= logListJson[i]['tracker_timestamp']
        l=time_change.split('.')
        logListJson[i]['tracker_timestamp']= l[0]
    return render_template('view-tracker.html', user_id= user_id, user_name=user_name, tracker_id= tracker_id, tracker_name=tracker_name, logListJson= logListJson,tracker_type= s)

#ADD A LOG, ROUTE
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/<tracker_name>/add_log', methods= ["GET","POST"])
def addLog(user_id, user_name, tracker_id, tracker_name):
    #response = requests.post(BASE + user_id+"/" +tracker_id +"/tracker_logs", {'tracker_value':True, 'tracker_note':'new log'})
    if request.method == 'POST':
       val, nts= request.form['value'], request.form['notes']
       requests.post(BASE + str(user_id) +"/" +str(tracker_id)+ "/tracker_logs", {'tracker_value':val, 'tracker_note':nts})
       return redirect(f'/{user_id}/{user_name}/{tracker_id}/{tracker_name}/tracker_logs')
    elif request.method == 'GET':
       return render_template('add-logs.html', user_id= user_id, user_name=user_name, tracker_id= tracker_id, tracker_name=tracker_name)

#UPDATE A LOG, ROUTE
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/<tracker_name>/<int:log_id>/update_log' , methods= ["GET","POST"])
def updateLog(user_id, user_name, tracker_id, log_id, tracker_name):
    if request.method == 'POST':
       val, nts= request.form['value'], request.form['notes']
       requests.put(f'{BASE}{user_id}/{tracker_id}/tracker_log/{log_id}', {'tracker_value':val, 'tracker_note':nts})
       return redirect(f'/{user_id}/{user_name}/{tracker_id}/{tracker_name}/tracker_logs')
    elif request.method == 'GET':
        response = requests.get(f"{BASE}{user_id}/{tracker_id}/tracker_logs")
        tlogs=response.json()
        for r in tlogs:
            if r['log_id']== log_id:
               lv= r['tracker_value']
               ln= r['tracker_note']
               ltime= r['tracker_timestamp']
        return render_template('update-log.html', user_id= user_id, user_name=user_name, tracker_id= tracker_id, tracker_name=tracker_name, log_id=log_id, lv=lv, ln=ln, ltime=ltime)

#DELETE A LOG, ROUTE
@app.route('/<int:user_id>/<user_name>/<int:tracker_id>/<tracker_name>/<int:log_id>/delete_log', methods= ["GET","POST"])
def deleteLog(user_id, user_name, tracker_id, log_id, tracker_name ):
    requests.delete(BASE + str(user_id)+"/" + str(tracker_id)+ "/tracker_log/"+ str(log_id))
    return redirect(f'/{user_id}/{user_name}/{tracker_id}/{tracker_name}/tracker_logs')

if __name__ == '__main__':
    app.run( debug=True)

