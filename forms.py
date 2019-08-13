from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,DateTimeField,IntegerField,TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo
import datetime
from pytz import timezone
import time

tz = timezone('America/Chicago')

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


class VenueForm(FlaskForm):
	venue_name = StringField('Venue Name', validators=[DataRequired(), Length(min=2, max=50)])
	address = StringField('Venue Address', validators=[DataRequired(),Length(min=2, max=100)])
	city = StringField('City', validators=[DataRequired(), Length(min=2, max=50)])
	zip_code = StringField('Zip Code', validators=[DataRequired(), Length(min=2, max=50)])
	venue_open = DateTimeField('Open time(CST)',format = "%H:%M",validators=[DataRequired()],
		default= datetime.datetime.now(tz))
	venue_close = DateTimeField('Venue Close time(CST)',format = "%H:%M",validators=[DataRequired()],
		default= datetime.datetime.now(tz))
	submit = SubmitField('Add Venue')

class StartEventForm(FlaskForm):
	event_name = StringField('Event Name', validators=[DataRequired(), Length(min=2, max=50)])
	event_type = StringField('Event Type', validators=[DataRequired(), Length(min=2, max=50)])
	event_description = StringField('City where event will be held', validators=[DataRequired(),Length(min=2, max=80)])
	venue_name = StringField('Venue Name', validators=[DataRequired(), Length(min=2, max=50)])
	event_city = StringField('Description of event (Very brief description of event)', validators=[DataRequired(),Length(min=2, max=100)])
	event_date = DateTimeField('Event Date',format = "%m/%d/%Y",validators=[DataRequired()],
		default= datetime.datetime.now(tz))
	event_start = DateTimeField('Event Start',format = "%H:%M",validators=[DataRequired()],
		default= datetime.datetime.now(tz))
	event_capacity = IntegerField('Specify Event Capacity')
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
	submit = SubmitField('Start Event')

class DeleteEventForm(FlaskForm):
	event_name = StringField('Event Name', validators=[DataRequired(), Length(min=2, max=50)])
	event_start = DateTimeField('Event Start',format = "%H:%M",validators=[DataRequired()],
		default= datetime.datetime.now(tz))
	submit = SubmitField('Delete Event')


class DeleteVenueForm(FlaskForm):
	venue_name = StringField('Venue Name', validators=[DataRequired(), Length(min=2, max=50)])
	submit = SubmitField('Delete Venue')

class DeleteUserForm(FlaskForm):
	username = StringField('User Name', validators=[DataRequired(), Length(min=2, max=50)])
	submit = SubmitField('Delete User')