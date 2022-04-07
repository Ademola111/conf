from re import M
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField

from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    username = StringField("Your Email: ", validators=[DataRequired(), Email()])
    pwd = PasswordField("Enter Password")
    loginbtn = SubmitField('Login')

class ContactusForm(FlaskForm):
    fullname=StringField("Fullname", validators=[DataRequired()])
    email=StringField("Your email")
    message=TextAreaField("Message here ", validators=[DataRequired()])
    btn=SubmitField("Send")