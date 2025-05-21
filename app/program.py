from app import app
from flask import render_template, abort, request
from flask_sqlalchemy import SQLAlchemy  # no more boring old SQL for us!
import os


basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "database.db")
db.init_app(app)

import app.models as models


# basic route
@app.route('/')
def root():
    return render_template('home.html', page_title='HOME')


@app.route('/park')
def park():
    parks = models.Park.query.all()
    return render_template('park.html', page_title='PARKS', parks=parks)


@app.route('/ride')
def ride():
    rides = models.Ride.query.join(models.Layout).all()
    return render_template('ride.html', page_title='RIDES', rides=rides)


@app.route('/manufactuer')
def manufactuer():
    manufactuers = models.Manufacturer.query.all()
    return render_template('manufactuer.html', page_title='MANUFACTUER', manufactuers=manufactuers)


@app.route('/rideelements')
def rideelements():
    elements = models.RideElement.query.all()
    return render_template('rideelement.html', page_title ='RIDEELEMENTS', elements=elements)


@app.route('/ridetype')
def ridetype():
    types = models.RideType.query.options(db.joinedload(models.RideType.manufacturers)).all()
    #joinedload is used to join many to many tables
    return render_template('ridetype.html', page_title = 'RIDETYPES', types=types)


@app.route('/add', methods=['GET', 'POST'])
def add():
    print(request.args.get('ROR2'))
    return "Done"
    # return render_template('add.html', page_title = 'ADD')
