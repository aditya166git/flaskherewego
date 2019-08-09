from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
app = Flask(__name__)

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

@app.route('/')
@app.route('/home')
def hello():
    #name = request.args.get("name", "World")
    #return f'Hello, {escape(name)}!'
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    #name = request.args.get("name", "World")
    #return f'Hello, {escape(name)}!'
    return render_template('about.html')

@app.route('/info')
def info():
	return "info"

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
		if form.username.data == 'aditya166' and form.password.data == 'password':
			flash('You have been logged in !', 'success')
			return redirect(url_for('about'))
		else:
			flash('Login Unsuccessful')
	return render_template('login.html', title='Login', form = form)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)