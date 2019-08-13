from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm, LoginForm, VenueForm,StartEventForm,DeleteEventForm,DeleteVenueForm,DeleteUserForm
app = Flask(__name__)
import os
import pymysql
import datetime 
from datetime import time

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

global username

app.config['SECRET_KEY'] ='381892'

posts =[
	{
		'author':'Aditya',
		'title':'How far can I go?',
		'content':'Ficton'
	},
	{
		'author':'Shivang',
		'title':'How to fall in love with Wendys',
		'content':'Thriller'
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
		cnx = pymysql.connect(user='root', password='',
							  host=host, db='herewegomysql')
		return cnx
'''end with db connection'''

#Helper function
def get_user_role(username):
	conn = db_con()
	with conn.cursor() as cursor:
		role=""
		cursor.execute("select user_role from users where username=%s",username)
		res = cursor.fetchone()
	return res[0]

#Helper function to check if user exists
def auth_user(username,password):
	conn = db_con()
	with conn.cursor() as cursor:
		rows_count = cursor.execute("select username,password From users where username = %s and password=%s",[username,password])
		if rows_count>0:
			return 'Y'
		else:
			return 'X'

#check event capacity
def check_capacity(event_id):
	conn = db_con()
	with conn.cursor() as cursor:
		cursor.execute("select event_capacity FRom events where event_id=%s",event_id)
		res = cursor.fetchall()
		return res[0][0]

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


@app.route('/userpage')
def userpage():
	conn = db_con()
	with conn.cursor() as cursor:
		#global username
		print("*******")
		user = username
		print(user)
		cursor.execute("SELECT e.event_id,e.event_name,v.venue_name,v.zip_code,e.event_city,e.event_type,e.event_start,e.event_end,e.event_capacity from events e,venues v where e.venue_id = v.venue_id and e.event_start >= CURDATE() and not exists ( select ue.event_id from user_events ue where username = %s and ue.event_id = e.event_id)",user)
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

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		flash(f'Account created for {form.username.data}!', 'success')
		add_user(form.username.data,form.firstname.data,form.lastname.data,form.age.data,form.email.data,"user",form.user_phone.data,"CHANGEME")		
		return redirect(url_for('about'))
	return render_template('register.html', title='Register', form=form)


@app.route('/addvenue',methods=['GET','POST'])
def addvenue():
	form = VenueForm()
	if form.validate_on_submit():
		add_venue('aditya166',str(form.venue_name.data),form.venue_open.data,form.venue_close.data,str(form.zip_code.data),str(form.city.data),str(form.address.data))
		flash(f'Venue has been successfully added', 'success')
		return redirect(url_for('about'))
	return render_template('addvenue.html', title='Add Venue', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		#conn = db_con()
		global username
		username = form.username.data
		user_role =get_user_role(form.username.data)	
		is_valid = auth_user(form.username.data,form.password.data)
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