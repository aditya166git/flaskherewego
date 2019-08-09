from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	firstname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
	lastname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
	age = StringField('Age', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password  = PasswordField('Password',validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
	#user_role = StringField('User Role', validators=[DataRequired(), Length(min=2, max=20)])
	user_phone = StringField('Phone Number', validators=[DataRequired(), Length(min=2, max=20)])
	submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	#email = StringField('Email', validators=[DataRequired(), Email()])
	password  = PasswordField('Password',validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Log In')
