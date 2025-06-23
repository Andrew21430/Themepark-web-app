from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired



class RideSearchForm(FlaskForm):
    search = StringField("Search Rides", validators=[DataRequired()])
    submit = SubmitField("Search")

