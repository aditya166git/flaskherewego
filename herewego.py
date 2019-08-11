from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm, VenueForm
app = Flask(__name__)
import os
import pymysql
import datetime 
from datetime import time

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

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
		unix_socket = '/cloudsql/herewegoadi:us-central1:herewego'
		cnx = pymysql.connect(user='root', password='root',
							 unix_socket=unix_socket, db="herewego")
		 
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
	print(res)
	return(res)

#define add user
def add_user(username,first_name,last_name,age,email,user_role,user_phone,password):
	conn = db_con()
	try:
		with conn.cursor() as cursor:
				creation_date = datetime.datetime.now().strftime("%Y-%m-%d")
				sql = "INSERT INTO users (username,first_name,last_name,age,email,user_role,user_phone,creation_date,password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
				val = (username, first_name,last_name,age,email,user_role,user_phone,creation_date,password)
				cursor.execute(sql, val)
				conn.commit()
		
	except TypeError as e:
		print(e)
		return None

#define venues
def add_venue(user_account,venue_name,venue_open,venue_close,zip_code,city,address):
	conn = db_con()
	with conn.cursor() as cursor:		
	    user_role = get_user_role(user_account)
	    try:
	        if user_role =='admin':
	            print("Got here")
	        else:            
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
	         print("Error {" + e.args[0] + "}")


@app.route('/addvenue',methods=['GET','POST'])
def addvenue():
	form = VenueForm()	
	if form.validate_on_submit():
		add_venue('aditya166',str(form.venue_name.data),form.venue_open.data,form.venue_close.data,str(form.zip_code.data),str(form.city.data),str(form.address.data))
		flash(f'Venue has been successfully added', 'success')
		return redirect(url_for('about'))
	return render_template('addvenue.html', title='Add Venue', form=form)


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


@app.route('/info')
def info():
	role = add_user("shivang", "shivang","Sharma",26,"shivang.sharma@utexas.edu","user","9802287819","CHANGEME")
	x ="success"
	return x

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		flash(f'Account created for {form.username.data}!', 'success')
		return redirect(url_for('about'))
	return render_template('register.html', title='Register', form=form)




@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		conn = db_con()
		if form.username.data == 'aditya166' and form.password.data == 'password':
			flash('You have been logged in !', 'success')
			return redirect(url_for('about'))
		else:
			flash('Login Unsuccessful')
	return render_template('login.html', title='Login', form = form)

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True)