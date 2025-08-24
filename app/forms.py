from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange, Optional
from app.models import Ride, Park
from flask_wtf.file import FileField, FileAllowed




class RideSearchForm(FlaskForm):
    search = StringField("Search Rides", validators=[DataRequired()])
    submit = SubmitField("Search")


class ParkSearchForm(FlaskForm):
    search = StringField("Search Parks", validators=[DataRequired()])
    submit = SubmitField("Search")



class RegisterForm(FlaskForm):
    # This form is used for user registration
    # It includes fields for username, password, and confirmation
    # and uses validators to ensure the inputs are valid
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm  = PasswordField("Confirm",  validators=[DataRequired(), EqualTo('password')])
    submit   = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit   = SubmitField("Login")



class ReviewForm(FlaskForm):
    content = TextAreaField("Your Review", validators=[DataRequired()])
    rating = IntegerField("Rating (1–5)", validators=[
        DataRequired(),
        NumberRange(min=1, max=5, message="Rating must be between 1 and 5")
    ])

    # Optional dropdown to associate review with either a Ride or a Park
    ride_id = SelectField("Ride", coerce=int, validators=[Optional()])
    park_id = SelectField("Park", coerce=int, validators=[Optional()])

    submit = SubmitField("Submit Review")

    def set_choices(self):
        self.ride_id.choices = [(0, "--- None ---")] + [
            (ride.id, ride.name) for ride in Ride.query.order_by(Ride.name).all()
        ]
        self.park_id.choices = [(0, "--- None ---")] + [
            (park.id, park.name) for park in Park.query.order_by(Park.name).all()
        ]



class ParkForm(FlaskForm):
    name = StringField("Park Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    submit = SubmitField("Add Park")


class RideForm(FlaskForm):
    # This form is used for adding or editing a ride
    # It includes fields for ride details such as name, type, layout, theme, launch type, thrill level, restrictions, constructor, and photo
    name = StringField('Name', validators=[DataRequired()])
    ride_type_id = IntegerField('Ride Type ID', validators=[DataRequired()])
    layout_id = IntegerField('Layout ID', validators=[DataRequired()])
    theme_id = IntegerField('Theme ID', validators=[DataRequired()])
    launch_type_id = IntegerField('Launch Type ID', validators=[DataRequired()])
    #park_id = IntegerField('Park ID', validators=[DataRequired()])
    thrill_level = StringField('Thrill Level', validators=[DataRequired()])
    restriction_id = IntegerField('Restriction ID', validators=[DataRequired()])
    constructor_id = IntegerField('Constructor ID', validators=[DataRequired()])
    photo = FileField('Photo', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    Height = IntegerField('Height (m)', validators=[Optional()])
    submit = SubmitField('Save')