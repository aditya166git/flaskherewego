from flask import Flask, render_template, url_for, flash, redirect, request,jsonify
from flask.json import JSONEncoder
from forms import RegistrationForm, LoginForm, VenueForm,StartEventForm,DeleteEventForm,DeleteVenueForm,DeleteUserForm,SearchEventForm
app = Flask(__name__)
import os
import pymysql
import datetime 
import json
from datetime import time
from datetime import timedelta

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

global username

app.config['SECRET_KEY'] ='381892'

class Database:
    def __init__(self):     
        host = "127.0.0.1"
        user = "root"
        password = ""
        db = "herewegomysql"
        self.con = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.con.cursor()

# class CustomJSONEncoder(JSONEncoder):

#     def default(self, obj):
#         try:
#             if isinstance(obj, (datetime,datetime.date,datetime.datetime.time,datetime.timedelta)):
#                 return obj.isoformat()
#             iterable = iter(obj)
#         except TypeError:
#             pass
#         else:
#             return list(iterable)
#         return JSONEncoder.default(self, obj)

# app.json_encoder = CustomJSONEncoder



posts =[
    {
        'author':'Aditya',
        'title':'Soccer at Rainey?',
        'content':'Sports'
    },
    {
        'author':'Shivang',
        'title':'Board Games this weekend',
        'content':'Fun Activity'
    }
]


'''start with db connection'''
def db_con():
        # When deployed to App Engine, the `GAE_ENV` environment variable will be
    # set to `standard`
    if os.environ.get('GAE_ENV') == 'standard':
        # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        cnx = pymysql.connect(user=db_user, password=db_password,
                             unix_socket=unix_socket, db=db_name)
         
        return cnx
    else:
        # If running locally, use the TCP connections instead
        # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
        # so that your application can use 127.0.0.1:3306 to connect to your
        # Cloud SQL instance
        host = '127.0.0.1'
        cnx = pymysql.connect(user='root', password='herewego',
                              host=host, db='herewegoDB')
        return cnx
'''end with db connection'''

#Helper function
def get_user_role(username):
    conn = db_con()
    with conn.cursor() as cursor:
        role=""
        cursor.execute("select user_role from users where username=%s",username)
        res = cursor.fetchone()
        if res:
            return res[0]
        else:
            flash("User does not exist. Please check you entered the correct login credentials")
            return 'user'

    return res[0]

#Helper function to check if user exists
def auth_user(username,password):
    conn = db_con()
    with conn.cursor() as cursor:
        rows_count = cursor.execute("select username,password From users where username = %s and password=%s",[username,password])
        if rows_count>0:
            return 'Y'
        else:
            print("invalid user")
            return 'X'

#check event capacity
def check_capacity(event_id):
    conn = db_con()
    with conn.cursor() as cursor:
        cursor.execute("select event_capacity FRom events where event_id=%s",event_id)
        res = cursor.fetchall()
        return res[0][0]




@app.route('/apijoinevent/<event_id>/<username>',methods=['GET'])
def apijoinevent(event_id,username):
    try:
        event_cap = check_capacity(event_id)
        if event_cap>0:
            conn = db_con()
            with conn.cursor() as cursor:
                sql = "INSERT INTO user_events(username,event_id) VALUES (%s, %s)"
                val = username,event_id
                cursor.execute(sql, val)
                cursor.execute("update events set event_capacity = event_capacity-1 where event_id=%s",event_id)
                conn.commit()
                return jsonify(
                event_join="True"
                )
        else:
            return jsonify(
                event_join="capacity"
                )
    except:
        return jsonify(
                event_join="False"
                )




#Add user
def add_user(username,first_name,last_name,age,email,user_role,user_phone,password):
    conn = db_con()
    try:
        with conn.cursor() as cursor:
                creation_date = datetime.datetime.now().strftime("%Y-%m-%d")
                sql = "INSERT INTO users (username,first_name,last_name,age,email,user_role,user_phone,creation_date,password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = username, first_name,last_name,age,email,user_role,user_phone,creation_date,password
                cursor.execute(sql, val) 
                conn.commit()
                cursor.execute("SELECT username FROM users WHERE username=%s",username)
                value = cursor.fetchone()
                if value:
                    return True
                else:
                    return False
                #conn.close()                       
    except TypeError as e:
        print(e)
        return None
#Add Venue
def add_venue(user_account,venue_name,venue_open,venue_close,zip_code,city,address):
    conn = db_con()
    with conn.cursor() as cursor:       
        try:
            cursor.execute('''
            insert into venues(venue_name,venue_open,venue_close,zip_code,city,address)
            values(%s,%s,%s,%s,%s,%s)
            ''',(venue_name,venue_open,venue_close,zip_code,city,address))
            conn.commit()
            cursor.execute("SELECT * FROM venues WHERE venue_name=%s",(venue_name,))
            all_venues = cursor.fetchall()
            for p in all_venues:
                print(p)                
        except pymysql.InternalError as e:
             print("Error {" + str(e.args[0]) + "}")
    

def get_venue_id(venue_name):
    conn = db_con()
    with conn.cursor() as cursor:
        try:
            cursor.execute('''
                SELECT venue_id 
                FROM venues
                WHERE venue_name = %s
                ''',(venue_name,))
            result = cursor.fetchone()
            if result is None:
                return "Venue not found"
            else:
                return int(result[0])
        except pymysql.InternalError as e:
            print("Error {" + str(e.args[0]) + "}")


#Checks if a particular venue is available with a given venue id, start time and Date of event
def venue_available(venue_id,start_time,event_date):
    conn = db_con()
    with conn.cursor() as cursor:
        try:
            cursor.execute('''
                            SELECT venue_id
                            FROM events
                            WHERE venue_id = %s AND event_start = %s AND event_date = %s
            ''',(venue_id,start_time,event_date))
            
            result = cursor.fetchone()
            if result is None:
                return True
            else:
                return False
        except pymysql.InternalError as e:
                print("Error {" + str(e.args[0]) + "}")


#Start an event

def start_event(name,city,event_type,start_time,capacity,venue_id,username,description,event_date):
    conn = db_con()
    with conn.cursor() as cursor:
        try:
            end_time = start_time + datetime.timedelta(hours=1)
            creation_date = datetime.datetime.now().strftime("%Y-%m-%d")
            if venue_available(venue_id,start_time,event_date):
                cursor.execute('''
                    INSERT INTO events(event_name,event_city,event_type,event_start,event_end,event_capacity,venue_id,creation_date,username,event_description,event_date)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)                         
                    ''',(name,city,event_type,start_time,end_time,capacity,venue_id,creation_date,username,description,event_date))
                conn.commit()
                cursor.execute('''SELECT * FROM events WHERE event_name = %s''', (name,))
                events = cursor.fetchall()
                for event in events:
                    print(event)
            else:
                flash(f'Event created for this time is unavailable. Please pick a different time', 'success')
                return redirect(url_for('startevent'))
        except pymysql.InternalError as e:
            print("Error {"+ str(e.args[0]) +"}")


#search for existence of a user
def check_events(eventname,startevent):
    conn = db_con()
    with conn.cursor() as cursor:
        try:
            cursor.execute('''
                            SELECT event_id from events WHERE event_name = %s AND event_start = %s
                ''',(eventname,startevent))
            user_results = cursor.fetchone()
            print("*****Event Id id*****")
                    
            if user_results:
                id = user_results[0]
                return id
            else:
                return 0
        except pymysql.InternalError as e:
            print("Error {"+ str(e.args[0]) +"}")

#Delete a user from a registered event
def delete_event(eventname,starttime):
    conn = db_con()
    with conn.cursor() as cursor:   
        #msg = "User removed from the event succesfully"
        e_id = check_events(eventname,starttime)
        print(starttime)
        try:    
            #if check_events(eventname,starttime):
            if e_id!=0:
                cursor.execute("delete from user_events where event_id=%s",e_id)
                cursor.execute("delete from events where event_id=%s",e_id)

                conn.commit()
                conn.close()
                flash("Event " + eventname + " has been successfully deleted from this event")
            else:
                flash("Event does not exist. Please check you entered the correct event name and time") 
        except pymysql.InternalError as e:
            print("Error {"+ str(e.args[0]) +"}")



def check_venue(venuename):
    conn = db_con()
    with conn.cursor() as cursor:
        try:
            cursor.execute('''
                            SELECT venue_id from venues WHERE venue_name = %s
                ''',(venuename,))
            user_results = cursor.fetchone()
            if user_results:
                return True
            else:
                return False
        except pymysql.InternalError as e:
            print("Error {"+ str(e.args[0]) +"}")

#Delete a user from a registered event
def delete_venue(venuename):
    conn = db_con()
    with conn.cursor() as cursor:   
        success_msg = "Venue " + str(venuename) + " has been successfully deleted!"
        failure_msg = "Venue " + str(venuename) + " does not exist, please check venue name is entered correctly and try again!"
        try:    
            if check_venue(venuename):      
                cursor.execute('''DELETE from venues WHERE venue_name =%s
                               ''',(venuename,))

                conn.commit()
                conn.close()
                flash(success_msg,'success')
            else:
                flash(failure_msg,'error') 
        except pymysql.InternalError as e:
            flash(failure_msg,'error')
            return render_template('about.html', title='About')

def check_user(username):
    conn = db_con()
    with conn.cursor() as cursor:
        try:
            cursor.execute('''
                            SELECT username from users WHERE username = %s
                ''',(username,))
            user_results = cursor.fetchone()
            if user_results:
                return True
            else:
                return False
        except pymysql.InternalError as e:
            print("Error {"+ str(e.args[0]) +"}")

#Delete a user from a registered event
def delete_user(username):
    conn = db_con()
    with conn.cursor() as cursor:   
        success_msg = "User " + str(username) + " has been successfully deleted!"
        failure_msg = "User " + str(username) + " does not exist, please check user name is entered correctly and try again!"
        try:    
            if check_user(username):        
                cursor.execute('''DELETE from users WHERE username =%s
                               ''',(username,))

                conn.commit()
                conn.close()
                flash(success_msg,'success')
            else:
                flash(failure_msg,'error') 
        except pymysql.InternalError as e:
            print("Error {"+ str(e.args[0]) +"}")


def events_exist(eventname,event_date):
    conn = db_con()
    with conn.cursor() as cursor:
        try:
            cursor.execute('''
                            SELECT * from events WHERE event_name = %s AND event_date = %s
                ''',(eventname,event_date))
            user_results = cursor.fetchall()
            if user_results:
                return True
            else:
                return False
        except pymysql.InternalError as e:
            print("Error {"+ str(e.args[0]) +"}")

def event_exist(eventname):
    conn = db_con()
    with conn.cursor() as cursor:
        try:
            cursor.execute('''
                            SELECT * from events WHERE event_name = %s
                ''',(eventname,))
            user_results = cursor.fetchall()
            if user_results:
                return True
            else:
                return False
        except pymysql.InternalError as e:
            print("Error {"+ str(e.args[0]) +"}")


def delete_user(username):
    conn = db_con()
    with conn.cursor() as cursor:   
        success_msg = "User " + str(username) + " has been successfully deleted!"
        failure_msg = "User " + str(username) + " does not exist, please check user name is entered correctly and try again!"
        try:    
            if check_user(username):        
                cursor.execute('''DELETE from users WHERE username =%s
                               ''',(username,))

                conn.commit()
                conn.close()
                flash(success_msg,'success')
            else:
                flash(failure_msg,'error') 
        except pymysql.InternalError as e:
            print("Error {"+ str(e.args[0]) +"}")


@app.route('/')
@app.route('/home')
def hello():
    #name = request.args.get("name", "World")
    #return f'Hello, {escape(name)}!'
    conn = db_con()
    with conn.cursor() as cursor:
        cursor.execute('SELECT username from users;')
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    #name = request.args.get("name", "World")
    #return f'Hello, {escape(name)}!'
    #return render_template('about.html')
    return render_template('about.html', title='About')

@app.route('/findevents')
def findevents():
    return render_template('eventsearch.html')


@app.route('/apisearchevent',methods=['POST'])
def apisearchevent():
    data = request.get_json()
    print(data)
    eventname = data['event_name']
    conn = db_con()
    with conn.cursor() as cursor:
        if event_exist(eventname):
            cursor.execute("SELECT e.event_name,e.event_city,e.event_type,e.event_start,e.event_end,v.venue_name,v.address FROM events e, venues v WHERE event_name = %s AND e.venue_id = v.venue_id "
                            ,eventname)

            results = cursor.fetchall()
            time = results[0][3]
            start_time = time.strftime('%H:%M')
            end_time= results[0][4].strftime('%H:%M')
            if results:
                return jsonify(
                    eventname=results[0][0],
                    eventtype=results[0][1],
                    eventcity=results[0][2],
                    eventstart=start_time,
                    eventend=end_time,
                    venuename=results[0][5],
                    venueaddress=results[0][6],
                    event_found="True"
                    )
        else:
            return jsonify(
                event_found="False"
                )



@app.route('/searchevents',methods=['GET', 'POST'])
def searchevents():
    form = SearchEventForm()
    eventname = form.event_name.data
    event_date = form.event_date.data
    conn = db_con()
    with conn.cursor() as cursor:
        if  form.validate_on_submit():
            if events_exist(eventname,event_date):                  
                cursor.execute('''
                                SELECT e.event_name,e.event_city,e.event_type,TIME(e.event_start),TIME(e.event_end),v.venue_name,v.address FROM events e, venues v WHERE event_name = %s AND event_date = %s AND e.venue_id = v.venue_id
                    ''',(eventname,event_date))
                results = cursor.fetchall()
                events = [list(x) for x in results]
                return render_template('eventsearch.html',len = len(events),events=events)
            else:
                flash(f'No events found for this date!')
    return render_template('searchevents.html',title='Search events',form=form)



@app.route('/userpage')
def userpage():
    conn = db_con()
    with conn.cursor() as cursor:
        #global username
        print("*******")
        user = username
        print(user)
        cursor.execute("SELECT e.event_id,e.event_name,v.venue_name,v.zip_code,e.event_city,e.event_type,e.event_start,e.event_end,e.event_capacity from events e,venues v where e.venue_id = v.venue_id and e.event_date >= CURDATE() and not exists ( select ue.event_id from user_events ue where username = %s and ue.event_id = e.event_id)",user)
        data = cursor.fetchall()
        b = [list(x) for x in data]
        #cursor.execute("SELECT * from user_events where username = %s",user)
        cursor.execute("select ue.username,e.event_id,e.event_name,v.venue_name,v.zip_code,e.event_city,e.event_type,e.event_start,e.event_end from events e, user_events ue,venues v where ue.event_id = e.event_id and e.venue_id = v.venue_id and ue.username= %s",user)
        data2 = cursor.fetchall()
        c= [list(x) for x in data2]
        return render_template('newevents.html', x=b,y =c)
    #name = request.args.get("name", "World")
    #return f'Hello, {escape(name)}!'
    #return render_template('about.html')

@app.route('/admin')
def admin():
    x = "success"
    return render_template('admin_home.html', title='Admin')



@app.route('/info')
def info():
    #role = add_user("david", "david","Sharma",26,"david.sharma@utexas.edu","user","9802287819","CHANGEME")
    x ="success"
    
#User Joins an Event
@app.route('/joinevent',methods=['GET', 'POST'])
def join_event():
    event_id = request.form['eventid']
    print (username)
    print(event_id)
    event_cap = check_capacity(event_id)
    if event_cap>0:
        conn = db_con()
        with conn.cursor() as cursor:
            sql = "INSERT INTO user_events(username,event_id) VALUES (%s, %s)"
            val = username,event_id
            cursor.execute(sql, val)
            cursor.execute("update events set event_capacity = event_capacity-1 where event_id=%s",event_id)
            conn.commit()
            flash(f'You have succesfully joined the event')
            conn.close()
            return redirect(url_for('userpage'))
    else:
        flash(f'The event is at full capacity')
        return redirect(url_for('about'))   

#User quits an Event
@app.route('/quitevent',methods=['GET', 'POST'])
def quit_event():
    event_id = request.form['eventid']
    print("########")
    print("inside quit")
    print(event_id)
    user = username
    conn = db_con()
    print("connected to DB")
    with conn.cursor() as cursor:
        cursor.execute("delete from user_events where username=%s and event_id=%s",[user,event_id])
        print("Inside DB")
        cursor.execute("update events set event_capacity = event_capacity+1 where event_id=%s",event_id)
        conn.commit()
        conn.close()
        flash(f'You have succesfully quit the event')
        return redirect(url_for('userpage'))

@app.route('/processjoin')
def process_join():
    return username

@app.route('/apiregister',methods=['POST'])
def apiregister():
    data = request.get_json()
    username = data['username']
    firstname = data['firstname']
    lastname = data['lastname']
    age = data['age']
    email = data['email']
    password = data['password']
    user_phone = data['user_phone']
    if add_user(username,firstname,lastname,age,email,"user",user_phone,"CHANGEME"):
        return jsonify(
            username=username,
            first_name = firstname,
            last_name = lastname,
            age=age,
            email=email,
            user_phone=user_phone,
            register_status = "success"
            )
    else:
        return jsonify(
            register_success = "failure",
            )



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        add_user(form.username.data,form.firstname.data,form.lastname.data,form.age.data,form.email.data,"user",form.user_phone.data,"CHANGEME")        
        return redirect(url_for('about'))
    return render_template('register.html', title='Register', form=form)

@app.route('/startevent',methods=['GET','POST'])
def startevent():
    form = StartEventForm()
    venue_name = form.venue_name.data
    venue_id = get_venue_id(venue_name)
    #start_events = convert_hours(form.event_start.data)
    time = form.event_start.data
    print("Inside Start Event")

    if form.validate_on_submit():
        start_event(form.event_name.data,form.event_city.data,form.event_type.data,time,form.event_capacity.data,venue_id,form.username.data,form.event_description.data,form.event_date.data)
        flash(f'You have successfully created this event', 'success')
        return redirect(url_for('about'))
    print(form.errors)
    return render_template('start_event.html', title='Start Event', form=form)

@app.route('/deletevent',methods=['GET','POST'])
def deletevent():
    form = DeleteEventForm()
    start_time = form.event_start.data
    if form.validate_on_submit():
        delete_event(form.event_name.data,start_time)
        return redirect(url_for('hello'))
    print(form.errors)
    return render_template('deleteevent.html', title='Delete Event', form=form)

@app.route('/deletevenue',methods=['GET','POST'])
def deletevenue():
    form = DeleteVenueForm()
    if form.validate_on_submit():
        delete_venue(form.venue_name.data)
        return redirect(url_for('hello'))
    return render_template('deletevenue.html', title='Delete Venue', form=form)

@app.route('/deleteuser',methods=['GET','POST'])
def deleteuser():
    form = DeleteUserForm()
    if form.validate_on_submit():
        delete_user(form.username.data)
        return redirect(url_for('hello'))
    return render_template('deleteuser.html', title='Delete User', form=form)


@app.route('/addvenue',methods=['GET','POST'])
def addvenue():
    form = VenueForm()
    if form.validate_on_submit():
        add_venue('aditya166',str(form.venue_name.data),form.venue_open.data,form.venue_close.data,str(form.zip_code.data),str(form.city.data),str(form.address.data))
        flash(f'Venue has been successfully added', 'success')
        return redirect(url_for('about'))
    return render_template('addvenue.html', title='Add Venue', form=form)


@app.route('/apilogin/<username>/<password>',methods=['GET'])
def apilogin(username,password):
    try:
        if auth_user(username,password) == 'Y':
            return jsonify(
                user_authenticated = "Success",
                username=username  
                )
        else:
            return jsonify(
                user_authenticated = "Failure"
                )
    except pymysql.InternalError:
        return jsonify(
                user_authenticated="Exists"
            )



@app.route('/userpagejson',methods=['GET', 'POST'])
def userpagejson():
    conn = db_con()
    with conn.cursor() as cursor:
        
        data = request.get_json()
        print('****Printing Data****')
        if data:
            print('has inputs')
            user = data['user']
        else:
            user = 'ritika'
        #cursor.execute("SELECT e.event_id,e.event_name,v.venue_name,v.zip_code,e.event_city,e.event_type,e.event_start,e.event_end,e.event_capacity from events e,venues v where e.venue_id = v.venue_id and e.event_date >= CURDATE() and not exists ( select ue.event_id from user_events ue where username = %s and ue.event_id = e.event_id)",user)
        cursor.execute("select e.event_id,e.event_name,v.venue_name,e.event_start,e.event_end FRom events e, venues v, user_events ue where e.venue_id = v.venue_id and ue.event_id = e.event_id and e.event_date>=CURDATE() and ue.username=%s",user)
        results = cursor.fetchall()
        print(results)
        items = []
        for row in results:
            #items.append({'event_id':row[0],'event_name':row[1],'venue_name':row[2]})
            items.append({'event_id':row[0],'event_name':row[1],'venue_name':row[2],'event_start':row[3],'event_end':row[4]})

        return jsonify(items)


@app.route('/apishowevents',methods=['GET'])
def apishowevents():
    conn = db_con()
    with conn.cursor() as cursor:
        try:
            events = []
            cursor.execute('''
                SELECT event_name,event_city,event_type,event_start,event_end,event_capacity,venue_name,event_description,event_date,event_id
                FROM events,venues WHERE event_date <= CURDATE() AND events.venue_id = venues.venue_id
                ''')
            results = cursor.fetchall()
            print(len(results))
            if results:
                for i in range(len(results)):
                    events.append({'event_name':results[i][0],
                            'event_city':results[i][1],
                            'event_type':results[i][2],
                            'event_start':results[i][3].strftime('%H:%M'),
                            'event_end':results[i][4].strftime('%H:%M'),
                            'event_capacity':results[i][5],
                            'venue_name':results[i][6],
                            'event_description':results[i][7],
                            'event_date':results[i][8].strftime('%m/%d/%Y'),
                            'event_id':results[i][9],
                            'event_status':'True' 
                        })
                return jsonify(events)
            else:
                return jsonify(event_status="False")
        except pymysql.InternalError as e:
            print("Error {"+ str(e.args[0]) +"}")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    global username
    
    if request.method == 'POST':
        username = request.form['username']
        user_role = get_user_role(username)
        password = request.form['password']
        auth_user(username,password)

    if form.validate_on_submit():
        #conn = db_con()
        is_valid = auth_user(username,password)     
        if is_valid=='Y':
            if user_role == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('userpage'))
        else:
            flash('Login Unsuccessful')
    return render_template('login.html', title='Login', form = form)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)