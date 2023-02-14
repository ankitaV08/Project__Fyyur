#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import Venue, Artist, Show, app, db

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
 ## In models.py file

# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  venue_data = Venue.query.order_by(Venue.state, Venue.city.asc()).distinct(Venue.city, Venue.state).all()
  print('venue_data ',venue_data)
  data = []
  current_time = datetime.now()

  for venue in venue_data:
    # creating venues list with common state and city values 
    venues = []
    venue_list = Venue.query.order_by(Venue.id).filter(Venue.city == venue.city, Venue.state == venue.state).all()
    for venue_obj in venue_list:
      venue_details={}
      venue_details['id'] = venue_obj.id
      venue_details['name'] = venue_obj.name

      # logic to calculate num_upcoming_shows value
      total_shows = Show.query.filter_by(venue_id=venue_obj.id).all()
      upcoming_shows = 0
      for shows in total_shows:
        if(shows.start_time > current_time):
          upcoming_shows += 1

      venue_details['num_upcoming_shows'] = upcoming_shows
      venues.append(venue_details)
    data.append(
      {
        "city" : venue.city,
        "state" : venue.state,
        "venues" : venues
      }
    )
    print(data)

  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_string = request.form.get('search_term', '')
  venues_list = Venue.query.filter(Venue.name.ilike('%' + search_string.lower() + '%')).all()
  print ('venues: ',venues_list)
  response = {}
  venue_details = []
  count = Venue.query.filter(Venue.name.ilike('%' + search_string.lower() + '%')).count()
  current_time = datetime.now()

  for venue in venues_list:
    # logic to calculate num_upcoming_shows value
    total_shows = Show.query.filter_by(venue_id=venue.id).all()
    upcoming_shows = 0
    for shows in total_shows:
      if(shows.start_time > current_time):
        upcoming_shows += 1
    
    venue_details.append(
      {
        "id" : venue.id,
        "name" : venue.name,
        "num_upcoming_shows" : upcoming_shows
      }
    )
  response = {
    "count" : count,
    "data" : venue_details
  } 
 
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = {}
  # fetching particular venue data based on venue_id
  venue_details = Venue.query.get(venue_id)  
  past_shows = []
  upcoming_shows = []
  present_time = datetime.now()

  past_shows_data = db.session.query(Show).join(Artist).filter(db.and_(present_time > Show.start_time, Show.venue_id == venue_id)).all()
  past_shows_count = len(past_shows_data)
  print('past shoe count : ',past_shows_count)
  print('past_shows_data : ', past_shows_data)
  
  for p in past_shows_data:
    past_show_details = {}
    past_show_details['artist_id'] = p.artist_id
    past_show_details['artist_name'] = p.Artist.name
    past_show_details['artist_image_link'] = p.Artist.image_link
    past_show_details['start_time'] = str(p.start_time)
    past_shows.append(past_show_details)
    print('past shows : ',past_shows)

  upcoming_shows_data = db.session.query(Show).join(Artist).filter(db.and_(present_time < Show.start_time, Show.venue_id == venue_id)).all()
  upcoming_shows_count = len(upcoming_shows_data)
  print(upcoming_shows_count)

  for u in upcoming_shows_data:
    upcoming_show_details = {}
    upcoming_show_details['artist_id'] = u.artist_id
    upcoming_show_details['artist_name'] = u.Artist.name
    upcoming_show_details['artist_image_link'] = u.Artist.image_link
    upcoming_show_details['start_time'] = str(u.start_time)
    upcoming_shows.append(upcoming_show_details)
    print('upcoming_shows: ', upcoming_shows)
  
  data['id'] = venue_details.id
  data['name'] = venue_details.name
  data['genres'] = venue_details.genres
  data['address'] = venue_details.address
  data['city'] = venue_details.city
  data['state'] = venue_details.state
  data['phone'] = venue_details.phone
  data['website'] = venue_details.website
  data['facebook_link'] = venue_details.facebook_link
  data['seeking_talent'] = venue_details.seeking_talent
  data['seeking_description'] = venue_details.seeking_description
  data['image_link'] = venue_details.image_link
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = past_shows_count
  data['upcoming_shows_count'] = upcoming_shows_count


  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  print(data)
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
  form = VenueForm(request.form)
  name = form.name.data.strip()
  print(name)
  city = form.city.data.strip()
  print(city)
  genres = form.genres.data 
  print(genres)
  state = form.state.data
  phone = form.phone.data   
  address = form.address.data.strip() 
  website = form.website_link.data.strip()       
  image_link = form.image_link.data.strip()
  seeking_talent = "seeking_talent" in request.form
  print(seeking_talent)
  seeking_description = form.seeking_description.data.strip()
  facebook_link = form.facebook_link.data.strip()
  try:
    print(form.validate())

    if form.validate():
      form_venue_data = Venue(name=name,genres=genres, city=city, state=state, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link, website=website, seeking_talent=seeking_talent ,seeking_description=seeking_description)
      print(form_venue_data)
      db.session.add(form_venue_data)
      print('session.add completed')
      db.session.commit()
      print('commit completed')
        # on successful db insert, flash success
      flash(f"Venue '{request.form['name']}' was successfully listed!")
    else:
      flash( form.errors )
    return redirect(url_for('show_venue', venue_id=Venue.query.order_by(Venue.id.desc()).first().id))
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash(
        f"Venue 'An error occurred. Venue {request.form['name']}' could not be listed!",  category="error")
    db.session.rollback()
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
    flash(f'Venue {venue_id} deleted successfully')
  except:
    flash(
        f'An error occurred. Venue with id {venue_id} cannot be deleted!', category="error")
    db.session.rollback()

  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists_list = Artist.query.all()
  for artists in artists_list:
    data_dict = {}
    data_dict['id'] = artists.id
    data_dict['name'] = artists.name
    data.append(data_dict)

  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response = {}

  search_string = request.form.get('search_term', '')
  artist_list = Artist.query.filter(Artist.name.ilike('%' + search_string.lower() + '%')).all()
  print ('artists : ',artist_list)
  response = {}
  artist_details = []
  count = len(artist_list)
  current_time = datetime.now()

  for artist in artist_list:
    # logic to calculate num_upcoming_shows value
    total_shows = Show.query.filter_by(artist_id=artist.id).all()
    upcoming_shows = 0
    for shows in total_shows:
      if(shows.start_time > current_time):
        upcoming_shows += 1
    
    artist_details.append(
      {
        "id" : artist.id,
        "name" : artist.name,
        "num_upcoming_shows" : upcoming_shows
      }
    )
  response = {
    "count" : count,
    "data" : artist_details
  } 

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  data = {}
  # fetching particular artist data based on artist_id
  artist_details = Artist.query.get(artist_id)  
  past_shows = []
  upcoming_shows = []
  present_time = datetime.now()

  # logic to calculate past shows
  past_shows_data = db.session.query(Show).join(Venue).filter(db.and_(present_time > Show.start_time, Show.artist_id == artist_id)).all()
  past_shows_count = len(past_shows_data)
  print('past_shows_data : ', past_shows_data)
  
  for p in past_shows_data:
    past_show_details = {}
    past_show_details['venue_id'] = p.venue_id
    past_show_details['venue_name'] = p.Venue.name
    past_show_details['venue_image_link'] = p.Venue.image_link
    past_show_details['start_time'] = str(p.start_time)
    past_shows.append(past_show_details)

  # logic to calculate upcoming shows
  upcoming_shows_data = db.session.query(Show).join(Venue).filter(db.and_(present_time < Show.start_time, Show.artist_id == artist_id)).all()
  upcoming_shows_count = len(upcoming_shows_data)
  print('upcoming_shows_count ', upcoming_shows_count)
  print('upcoming_shows_data ', upcoming_shows_data)

  for u in upcoming_shows_data:
    upcoming_show_details = {}
    upcoming_show_details['venue_id'] = u.venue_id
    upcoming_show_details['venue_name'] = u.Venue.name
    upcoming_show_details['venue_image_link'] = u.Venue.image_link
    upcoming_show_details['start_time'] = str(u.start_time)
    upcoming_shows.append(upcoming_show_details)
    print('upcoming_shows= ', upcoming_shows)
  
  data['id'] = artist_details.id
  data['name'] = artist_details.name
  data['genres'] = artist_details.genres
  data['city'] = artist_details.city
  data['state'] = artist_details.state
  data['phone'] = artist_details.phone
  data['website'] = artist_details.website
  data['facebook_link'] = artist_details.facebook_link
  data['seeking_venue'] = artist_details.seeking_venue
  data['seeking_description'] = artist_details.seeking_description
  data['image_link'] = artist_details.image_link
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = past_shows_count
  data['upcoming_shows_count'] = upcoming_shows_count


  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  print('DATA : ', data)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  print(artist)
  populated_form = ArtistForm(name=artist.name, city=artist.city, state=artist.state, phone=artist.phone, genres=artist.genres, facebook_link=artist.facebook_link, image_link=artist.image_link, website_link=artist.website, seeking_venue=artist.seeking_venue, seeking_description=artist.seeking_description)
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=populated_form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form)
  try:
    if form.validate():
      updated_artist = Artist.query.filter(Artist.id == artist_id)
      updated_artist.name = request.form['name']
      updated_artist.city = request.form['city']
      updated_artist.state = request.form['state']
      updated_artist.phone = request.form['phone']
      updated_artist.genres = request.form.getlist('genres', type=str)
      updated_artist.facebook_link = request.form['facebook_link']
      updated_artist.image_link = request.form['image_link']
      updated_artist.website = request.form['website_link']
      updated_artist.seeking_venue = 'seeking_venue' in request.form
      updated_artist.seeking_description = request.form['seeking_description']
      db.session.commit()
      flash(f"Artist with id {artist_id} updated successfully!")
    else :
      flash(form.errors)
  except:
      flash(f"An error occurred. Artist with id {artist_id} could not be updated.", category="error")
      db.session.rollback()
  finally:
      db.session.close()
      return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  print(venue)
  populated_form = VenueForm(name=venue.name, genres=venue.genres, address=venue.address, city=venue.city, state=venue.state, phone=venue.phone, website_link=venue.website, facebook_link=venue.facebook_link, seeking_talent=venue.seeking_talent, seeking_description=venue.seeking_description, image_link=venue.image_link)
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=populated_form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  try:
    if form.validate():
      updated_venue = Venue.query.filter(Venue.id == venue_id)
      updated_venue.name = request.form['name']
      updated_venue.genres = request.form.getlist('genres', type=str)
      updated_venue.address = request.form['address']
      updated_venue.city = request.form['city']
      updated_venue.state = request.form['state']
      updated_venue.phone = request.form['phone']
      updated_venue.website = request.form['website_link']
      updated_venue.facebook_link = request.form['facebook_link']
      updated_venue.image_link = request.form['image_link']
      updated_venue.seeking_talent = 'seeking_talent' in request.form
      updated_venue.seeking_description = request.form['seeking_description']
      db.session.commit()
      flash(f"Venue with id {venue_id} updated successfully!")
    else :
      flash(form.errors)
  except:
    flash(f"An error occurred. Venue with id {venue_id} could not be updated.", category="error")
    db.session.rollback()
  finally:
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

  form = ArtistForm(request.form)
  try:
    if form.validate():
      new_artist = Artist(name=request.form['name'],genres=request.form.getlist('genres', type=str),state=request.form['state'], city=request.form['city'], phone=request.form['phone'], facebook_link=request.form['facebook_link'], website=request.form['website_link'], seeking_venue='seeking_venue' in request.form, seeking_description=request.form['seeking_description'], image_link=request.form['image_link'])
      db.session.add(new_artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
        flash(form.errors)
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.', category="error")
    db.session.rollback()
  finally:
      db.session.close()
      return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows_list = Show.query.all()
  for shows in shows_list:
    details = {}
    details['venue_id'] = shows.venue_id
    details['venue_name'] = Venue.query.filter(Venue.id == shows.venue_id).first().name
    details['artist_id'] = shows.artist_id
    details['artist_name'] = Artist.query.filter(Artist.id == shows.artist_id).first().name
    details['artist_image_link'] = Artist.query.filter(Artist.id == shows.artist_id).first().image_link
    details['start_time'] = str(shows.start_time)
    data.append(details)
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]

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
  form = ShowForm(request.form)
  try:
    if(form.validate()):
      new_show = Show(artist_id=request.form['artist_id'],venue_id=request.form['venue_id'], start_time=request.form['start_time'])
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    else:
      flash(form.errors)
  except:
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Show could not be listed.')
      db.session.rollback()
  finally:
    db.session.close()
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
