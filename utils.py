from datetime import datetime


def get_venue_page_payload(venue):
    past_shows = []
    upcoming_shows = []

    for show in venue.shows:
        if show.start_time <= datetime.now():
            past_shows.append(show.format())
        else:
            upcoming_shows.append(show.format())

    return {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'city': venue.city,
        'state': venue.state,
        'address': venue.address,
        'phone': venue.phone,
        'image_link': venue.image_link,
        'website_link': venue.website_link,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }


def get_artist_page_payload(artist):
    past_shows = []
    upcoming_shows = []

    for show in artist.shows:
        if show.start_time <= datetime.now():
            past_shows.append(show.format())
        else:
            upcoming_shows.append(show.format())


    return {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'image_link': artist.image_link,
        'website_link': artist.website_link,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
