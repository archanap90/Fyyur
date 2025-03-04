#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from models import setup_db, Venue, Artist, Show
import models
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db = setup_db(app)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  cities = Venue.query.with_entities(Venue.city,Venue.state).distinct()
  for city in cities:
    venues = Venue.query.filter(Venue.city==city.city).all()
    new_venues_data = []
    for venue in venues:
      num_upcoming_shows = Show.query.filter(Show.venue_id==venue.id).count()
      new_venues_data.append({
        "id":venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      })
    data.append(  
      {"city":city.city,
      "state": city.state,
      "venues": new_venues_data
      }
    )
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  search_term = "%" + request.form.get('search_term') + "%"
  data = Venue.query.filter(Venue.name.ilike(search_term)).all()
  response = {
    "count" : len(data),
    "data" : data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id

  venue = Venue.query.get(venue_id)
  current_datetime = datetime.now()
  venue_shows = Show.query.filter_by(venue_id=venue_id)
  past_shows = []
  upcoming_shows = []
  for show in venue_shows:
    show_artist = Artist.query.get(show.artist_id)
    if(show.start_time < current_datetime):
      past_shows.append({
        'artist_id': show_artist.id,
        'artist_name': show_artist.name,
        'artist_image_link': show_artist.image_link,
        'start_time': show.start_time.strftime("%d-%m-%Y %H:%M:%S")
      })
    else:
      upcoming_shows.append({
        'artist_id': show_artist.id,
        'artist_name': show_artist.name,
        'artist_image_link': show_artist.image_link,
        'start_time': show.start_time.strftime("%d-%m-%Y %H:%M:%S")
      })      
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    #s"website": venue.website,
    "facebook_link": venue.facebook_link,
    #"seeking_talent": venue.seeking_talent,
    #"seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  data['genres'] = data['genres'].split(',')
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False

  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  genres = ",".join(request.form.getlist('genres'))
  facebook_link = request.form['facebook_link']

  venue = Venue(name=name,city=city,state=state,phone=phone,genres=genres,facebook_link=facebook_link)
  try:
    db.session.add(venue)
    db.session.commit()
  except:
    error =True
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
      abort(400)
    else:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['POST','DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  Venue.query.filter_by(id=venue_id).delete()
  db.session.commit()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  search_term = "%" + request.form.get('search_term') + "%"
  data = Artist.query.filter(Artist.name.ilike(search_term)).all()
  response ={
    "count" : len(data),
    "data" : data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  current_datetime = datetime.now()
  artist_shows = Show.query.filter_by(artist_id=artist.id)
  past_shows = []
  upcoming_shows =[]
  for show in artist_shows:
    venue = Venue.query.get(show.venue_id)
    if show.start_time < current_datetime:
      past_shows.append({
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': show.start_time.strftime("%d-%m-%Y %H:%M:%S")
      })
    else:
      upcoming_shows.append({
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': show.start_time.strftime("%d-%m-%Y %H:%M:%S")
      })
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "image_link": artist.image_link,
    "facebook_link": artist.facebook_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows
  }
  data['genres'] = data['genres'].split(',')
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id).__dict__
  form = ArtistForm(data=artist)

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  data = {
    "name": request.form['name'],
    "state": request.form['state'],
    "city": request.form['city'],
    "phone": request.form['phone'],
    "genres": ",".join(request.form.getlist('genres')),
    "facebook_link": request.form['facebook_link']
  }
  print(request.form['genres'])
  db.session.query(Artist).filter(Artist.id == artist_id).update(data)
  db.session.commit()
  db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id).__dict__
  form = VenueForm(data=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  data = {
    "name": request.form['name'],
    "state": request.form['state'],
    "city": request.form['city'],
    "address": request.form['address'],
    "phone": request.form['phone'],
    "genres": ",".join(request.form.getlist('genres')),
    "facebook_link": request.form['facebook_link']
  }
  #print(",".join(request.form.getlist('genres')))
  db.session.query(Venue).filter_by(id=venue_id).update(data)
  db.session.commit()
  db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = request.form['name']
  state = request.form['state']
  city = request.form['city']
  phone = request.form['phone']
  genres = ",".join(request.form.getlist('genres'))
  facebook_link = request.form['facebook_link']
  error = False
  try:
    artist = Artist(name=name,state=state,city=city,phone=phone,genres=genres,facebook_link=facebook_link)
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    print(sys.exc_info)
    
  finally:
    db.session.close()
    if error == True:
      flash('An error occurred. Artist ' + name + ' could not be listed.')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on  number of upcoming shows per venue.
  shows = Show.query.all() 
  data = []
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    data.append({
      "venue_id" : show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    })
 
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']

  try:
    show = Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    print(sys.exc_info)
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Show could not be listed.')
      abort(400)
    else:
      # on successful db insert, flash success
      flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
