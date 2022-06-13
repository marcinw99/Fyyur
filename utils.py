def get_venue_page_payload(venue, past_shows, upcoming_shows):
    past_shows_length = len(past_shows)
    upcoming_shows_length = len(upcoming_shows)
    formatted_past_shows = []
    formatted_upcoming_shows = []

    if past_shows_length > 0:
        formatted_past_shows = [show.format() for show in past_shows]

    if upcoming_shows_length > 0:
        formatted_upcoming_shows = [show.format() for show in upcoming_shows]

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
        "past_shows": formatted_past_shows,
        "upcoming_shows": formatted_upcoming_shows,
        "past_shows_count": past_shows_length,
        "upcoming_shows_count": upcoming_shows_length,
    }


def get_artist_page_payload(artist, past_shows, upcoming_shows):
    past_shows_length = len(past_shows)
    upcoming_shows_length = len(upcoming_shows)
    formatted_past_shows = []
    formatted_upcoming_shows = []

    if past_shows_length > 0:
        formatted_past_shows = [show.format() for show in past_shows]

    if upcoming_shows_length > 0:
        formatted_upcoming_shows = [show.format() for show in upcoming_shows]

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
        "past_shows": formatted_past_shows,
        "upcoming_shows": formatted_upcoming_shows,
        "past_shows_count": past_shows_length,
        "upcoming_shows_count": upcoming_shows_length,
    }
