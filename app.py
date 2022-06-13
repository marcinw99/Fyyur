# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import collections
import collections.abc

collections.Callable = collections.abc.Callable
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from utils import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)

# ----------------------------------------------------------------------------#
# Constants.
# ----------------------------------------------------------------------------#

STRFTIME_FORMAT = "%m/%d/%Y, %H:%M:%S"


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False, default=[])
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    website_link = db.Column(db.String(120), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean(), nullable=False)
    seeking_description = db.Column(db.String(500), nullable=True)

    shows = db.relationship('Show', backref='venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False, default=[])
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    website_link = db.Column(db.String(120), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean(), nullable=False)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='artist', lazy=True)


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    start_time = db.Column(db.DateTime, nullable=False)

    def format(self):
        return {
            'id': self.id,
            'artist_id': self.artist_id,
            'venue_id': self.venue_id,
            'start_time': self.start_time.strftime(STRFTIME_FORMAT)
        }


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

date_formats = {
    'full': "EEEE MMMM, d, y 'at' h:mma",
    'medium': "EE MM, dd, y h:mma"
}


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    computed_format = date_formats[format]
    return babel.dates.format_datetime(date, format=computed_format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    areas_query = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).order_by(
        Venue.state).all()

    areas = []

    for area in areas_query:
        venues_query = Venue.query.filter_by(state=area.state, city=area.city).order_by(Venue.name).all()

        area_venues = []
        for venue in venues_query:
            num_upcoming_shows = db.session.query(func.count(Show.id)).filter_by(venue_id=venue.id).all()[0][0]

            area_venues.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': num_upcoming_shows
            })

        areas.append({
            'city': area.city,
            'state': area.state,
            'venues': area_venues
        })

    return render_template('pages/venues.html', areas=areas)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')

    venues_query = db.session.query(Venue.id, Venue.name).filter(Venue.name.ilike(f'%{search_term}%')).all()

    formatted_venues = []

    for venue in venues_query:
        num_upcoming_shows = db.session.query(func.count(Show.id)).filter_by(venue_id=venue.id).all()[0][0]

        formatted_venues.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming_shows
        })

    results = {
        "count": len(formatted_venues),
        "data": formatted_venues
    }
    return render_template('pages/search_venues.html', results=results,
                           search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    time_now = datetime.now()

    venue = Venue.query.filter(Venue.id == venue_id).one_or_none()

    if venue is None:
        abort(404)

    past_shows = db.session.query(Show).join(Venue).filter(
        Show.venue_id == venue_id,
        Show.start_time < time_now
    ).all()

    upcoming_shows = db.session.query(Show).join(Venue).filter(
        Show.venue_id == venue_id,
        Show.start_time >= time_now
    ).all()

    return render_template('pages/show_venue.html', venue=get_venue_page_payload(
        venue=venue,
        past_shows=past_shows,
        upcoming_shows=upcoming_shows
    ))


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    errorMessages = []
    context = {}
    try:
        name = request.form.get('name')
        context['name'] = name
        form = VenueForm(request.form)
        if not form.validate():
            for formError in form.errors:
                errorMessages.append(formError + ': ' + form.errors[formError][0])
            raise ValueError('Form values are incorrect')
        newVenue = Venue(
            name=name,
            genres=request.form.getlist('genres'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            phone=request.form.get('phone'),
            website_link=request.form.get('website_link'),
            facebook_link=request.form.get('facebook_link'),
            seeking_talent=request.form.get('seeking_talent') == 'y',
            seeking_description=request.form.get('seeking_description'),
            image_link=request.form.get('image_link')
        )
        db.session.add(newVenue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            if len(errorMessages) > 0:
                for message in errorMessages:
                    flash(message)
            else:
                flash('An error occurred. Venue ' + context['name'] + ' could not be added.')
            return redirect(request.url)
        else:
            flash('Venue ' + context['name'] + ' was successfully added!')
            return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists_query = db.session.query(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=artists_query)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')

    artists_query = db.session.query(Artist.id, Artist.name).filter(Artist.name.ilike(f'%{search_term}%')).all()

    formatted_artists = []

    for artist in artists_query:
        num_upcoming_shows = db.session.query(func.count(Show.id)).filter_by(artist_id=artist.id).all()[0][0]

        formatted_artists.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming_shows
        })

    results = {
        "count": len(formatted_artists),
        "data": formatted_artists
    }

    return render_template('pages/search_artists.html', results=results,
                           search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    time_now = datetime.now()

    artist = Artist.query.filter(Artist.id == artist_id).one_or_none()

    if artist is None:
        abort(404)

    past_shows = db.session.query(Show).join(Artist).filter(
        Show.artist_id == artist_id,
        Show.start_time < time_now
    ).all()

    upcoming_shows = db.session.query(Show).join(Artist).filter(
        Show.artist_id == artist_id,
        Show.start_time >= time_now
    ).all()

    return render_template('pages/show_artist.html', artist=get_artist_page_payload(
        artist=artist,
        past_shows=past_shows,
        upcoming_shows=upcoming_shows
    ))


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    fetchedArtist = Artist.query.get(artist_id)

    parsedArtistData = {
        "id": artist_id,
        "name": fetchedArtist.name,
        "genres": fetchedArtist.genres,
        "city": fetchedArtist.city,
        "state": fetchedArtist.state,
        "phone": fetchedArtist.phone,
        "website_link": fetchedArtist.website_link,
        "facebook_link": fetchedArtist.facebook_link,
        "seeking_venue": fetchedArtist.seeking_venue,
        "seeking_description": fetchedArtist.seeking_description,
        "image_link": fetchedArtist.image_link,
    }
    form = ArtistForm(data=parsedArtistData)
    return render_template('forms/edit_artist.html', form=form, artist=parsedArtistData)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    errorMessages = []
    context = {}

    try:
        artist = Artist.query.get(artist_id)
        if artist is None:
            abort(404)

        context['oldName'] = artist.name
        newName = request.form.get('name')
        context['newName'] = newName

        form = ArtistForm(request.form)
        if not form.validate():
            for formError in form.errors:
                errorMessages.append(formError + ': ' + form.errors[formError][0])
            raise ValueError('Form values are incorrect')

        artist.name = newName
        artist.genres = request.form.getlist('genres')
        artist.address = request.form.get('address')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.website_link = request.form.get('website_link')
        artist.facebook_link = request.form.get('facebook_link')
        artist.seeking_venue = request.form.get('seeking_venue') == 'y'
        artist.seeking_description = request.form.get('seeking_description')
        artist.image_link = request.form.get('image_link')

        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            if len(errorMessages) > 0:
                for message in errorMessages:
                    flash(message)
            else:
                flash('An error occurred. Artist ' + context['oldName'] + ' could not be edited.')
            return redirect(request.url)
        else:
            flash('Artist ' + context['newName'] + ' was successfully edited!')
            return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    fetchedVenue = Venue.query.get(venue_id)

    if fetchedVenue is None:
        abort(404)

    parsedVenueData = {
        "id": venue_id,
        "name": fetchedVenue.name,
        "genres": fetchedVenue.genres,
        "address": fetchedVenue.address,
        "city": fetchedVenue.city,
        "state": fetchedVenue.state,
        "phone": fetchedVenue.phone,
        "website_link": fetchedVenue.website_link,
        "facebook_link": fetchedVenue.facebook_link,
        "seeking_talent": fetchedVenue.seeking_talent,
        "seeking_description": fetchedVenue.seeking_description,
        "image_link": fetchedVenue.image_link,
    }
    form = VenueForm(data=parsedVenueData)
    return render_template('forms/edit_venue.html', form=form, venue=parsedVenueData)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    errorMessages = []
    context = {}

    try:
        venue = Venue.query.get(venue_id)
        if venue is None:
            abort(404)

        context['oldName'] = venue.name
        newName = request.form.get('name')
        context['newName'] = newName

        form = VenueForm(request.form)
        if not form.validate():
            for formError in form.errors:
                errorMessages.append(formError + ': ' + form.errors[formError][0])
            raise ValueError('Form values are incorrect')

        venue.name = newName
        venue.genres = request.form.getlist('genres')
        venue.address = request.form.get('address')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.phone = request.form.get('phone')
        venue.website_link = request.form.get('website_link')
        venue.facebook_link = request.form.get('facebook_link')
        venue.seeking_talent = request.form.get('seeking_talent') == 'y'
        venue.seeking_description = request.form.get('seeking_description')
        venue.image_link = request.form.get('image_link')

        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            if len(errorMessages) > 0:
                for message in errorMessages:
                    flash(message)
            else:
                flash('An error occurred. Venue ' + context['oldName'] + ' could not be edited.')
            return redirect(request.url)
        else:
            flash('Venue ' + context['newName'] + ' was successfully edited!')
            return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    errorMessages = []
    context = {}
    try:
        name = request.form.get('name')
        context['name'] = name
        form = ArtistForm(request.form)
        if not form.validate():
            for formError in form.errors:
                errorMessages.append(formError + ': ' + form.errors[formError][0])
            raise ValueError('Form values are incorrect')
        newArtist = Artist(
            name=name,
            genres=request.form.getlist('genres'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            phone=request.form.get('phone'),
            website_link=request.form.get('website_link'),
            facebook_link=request.form.get('facebook_link'),
            seeking_venue=request.form.get('seeking_venue') == 'y',
            seeking_description=request.form.get('seeking_description'),
            image_link=request.form.get('image_link')
        )
        db.session.add(newArtist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            if len(errorMessages) > 0:
                for message in errorMessages:
                    flash(message)
            else:
                flash('An error occurred. Artist ' + context['name'] + ' could not be added.')
            return redirect(request.url)
        else:
            flash('Artist ' + context['name'] + ' was successfully added!')
            return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    query = db.session.query(Show, Artist, Venue).join(Artist).filter(
        Show.artist_id == Artist.id,
        Show.venue_id == Venue.id
    ).all()

    formatted_shows = []

    for item in query:
        show = item[0]
        artist = item[1]
        venue = item[2]

        formatted_shows.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime(STRFTIME_FORMAT)
        })

    return render_template('pages/shows.html', shows=formatted_shows)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    errorMessages = []
    try:
        form = ShowForm(request.form)
        if not form.validate():
            for formError in form.errors:
                errorMessages.append(formError + ': ' + form.errors[formError][0])
            raise ValueError('Form values are incorrect')
        newShow = Show(
            artist_id=request.form.get('artist_id'),
            venue_id=request.form.get('venue_id'),
            start_time=datetime.fromisoformat(request.form.get('start_time'))
        )
        db.session.add(newShow)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        if error:
            if len(errorMessages) > 0:
                for message in errorMessages:
                    flash(message)
            else:
                flash('An error occurred. Show could not be listed.')
            return redirect(request.url)
        else:
            flash('Show was successfully added!')
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
