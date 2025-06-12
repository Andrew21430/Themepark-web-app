from app import app
from flask import render_template, abort, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy  # no more boring old SQL for us!
#from sqlalchemy.orm import joinedload
from collections import defaultdict

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
    rides = models.Ride.query.join(models.Layout).order_by(models.Ride.height.desc()).all()
    return render_template('ride.html', page_title='RIDES', rides=rides)


@app.route('/manufactuer')
def manufactuer():
    manufactuers = models.Manufacturer.query.all()
    return render_template('manufactuer.html', page_title='MANUFACTUER', manufactuers=manufactuers)


@app.route('/rideelements')
def rideelements():
    elements = models.RideElement.query.all()
    return render_template('rideelement.html', page_title='RIDEELEMENTS', elements=elements)


@app.route('/ridetype')
def ridetype():
    # types = models.RideType.query.options(db.joinedload(models.RideType.manufacturers)).all()
    # joinedload is used to join many to many tables
    types = models.RideType.query.join(models.Manufacturer).all()
    return render_template('ridetype.html', page_title='RIDETYPES', types=types)


@app.route('/add', methods=['GET', 'POST'])
def add():
    print(request.args.get('ROR2'))
    return "Done"
    # return render_template('add.html', page_title = 'ADD')

@app.route('/parkrides')
def parkrides():
   #order and join of a many to many without using joined loaded as otherwise I would have to change all of my models tables
   results = db.session.query(models.Park, models.Ride).join(models.ParkRide, models.Park.id == models.ParkRide.c.park_id).join(models.Ride, models.Ride.id == models.ParkRide.c.ride_id).order_by(models.Park.name).all()
   #mnake it so that the parks only show once for all the rides
   grouped_parks = defaultdict(list)
    for park, ride in results:
        grouped_parks[park].append(ride)   
   return render_template('parkrides.html', page_title='PARKRIDES', grouped_parks=grouped_parks)
