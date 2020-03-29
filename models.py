from sqlalchemy import Column, String, create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import json

##database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()
 

def setup_db(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db) # this
    ##db.create_all()
    return db

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'
    __table_args__ = {'schema':'fyyur_app'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'
    __table_args__ = {'schema':'fyyur_app'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
#db.create_all()

class Show(db.Model):
    __tablename__ = 'Show'
    __table_args__ = {'schema':'fyyur_app'}
    venue_id = db.Column(
      db.Integer, 
      db.ForeignKey('fyyur_app.Venue.id',onupdate="CASCADE", ondelete="CASCADE"), 
      primary_key = True)
    artist_id = db.Column(
     db.Integer, 
     db.ForeignKey('fyyur_app.Artist.id',onupdate="CASCADE", ondelete="CASCADE"), 
     primary_key = True)
    start_time = db.Column(db.DateTime)