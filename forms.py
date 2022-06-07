from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, URL, Optional, Regexp
from enums import *

phone_regexp_validator = Regexp("^[0-9]*$", message="Phone number should only contain digits")


def coerce_for_enum(target_enum):
    def coerce(value):
        if isinstance(value, target_enum):
            return value
        try:
            if target_enum[value] is not None:
                return value
        except KeyError:
            raise ValueError(value)

    return coerce


class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )


class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices(),
        coerce=coerce_for_enum(State)
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[phone_regexp_validator]
    )
    image_link = StringField(
        'image_link', validators=[URL()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=Genre.choices(),
        coerce=coerce_for_enum(Genre)
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(), Optional()]
    )
    website_link = StringField(
        'website_link', validators=[URL(), Optional()]
    )

    seeking_talent = BooleanField('seeking_talent')

    seeking_description = StringField(
        'seeking_description'
    )


class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices(),
        coerce=coerce_for_enum(State)
    )
    phone = StringField(
        'phone', validators=[phone_regexp_validator]
    )
    image_link = StringField(
        'image_link', validators=[URL()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=Genre.choices(),
        coerce=coerce_for_enum(Genre)
    )
    facebook_link = StringField(
        # TODO implement enum restriction
        # Enum restriction for URL??????????
        'facebook_link', validators=[URL(), Optional()]
    )

    website_link = StringField(
        'website_link', validators=[URL(), Optional()]
    )

    seeking_venue = BooleanField('seeking_venue')

    seeking_description = StringField(
        'seeking_description'
    )
