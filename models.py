from flask_sqlalchemy import SQLAlchemy

from constants import STRFTIME_FORMAT

db = SQLAlchemy()


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

    shows = db.relationship('Show', backref='venue', lazy='joined',
                            cascade="all, delete")


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

    shows = db.relationship('Show', backref='artist', lazy='joined',
                            cascade="all, delete")


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
            'venue_image_link': self.venue.image_link,
            'artist_image_link': self.artist.image_link,
            'start_time': self.start_time.strftime(STRFTIME_FORMAT)
        }
