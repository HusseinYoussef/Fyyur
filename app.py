#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
from config import app

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en_US')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues', methods=['GET'])
def venues():

    data = {}
    date = datetime.today()
    all_venues = Venue.query.all()
    for v in all_venues:
        up_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==v.id)\
                                                .filter(Show.start_time>date).all()
        id, name, city, state = v.id, v.name, v.city, v.state
        location = (city, state)
        if location not in data:
            data[location] = {
                'city': city,
                'state': state,
                'venues': []
            }
        data[location]['venues'].append({
            'id': id,
            'name': name,
            'num_upcoming_shows': len(up_shows)
        })
    return render_template('pages/venues.html', areas=[data[k] for k in data.keys()])


@app.route('/venues/search', methods=['POST'])
def search_venues():

    search_term = request.form.get('search_term', '')
    results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(results),
        "data": results
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<venue_id>', methods=['GET'])
def show_venue(venue_id):

    venue = Venue.query.get(venue_id)
    if venue is None:
        flash(f"Venue doesn't exist!")
        return redirect(url_for('index'))
    data = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'city': venue.city,
        'state': venue.state,
        'address': venue.address,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': [],
        'upcoming_shows': [],
        'past_shows_count': 0,
        'upcoming_shows_count': 0,
    }
    date = datetime.today()
    shows = Show.query.filter(Show.venue_id==venue_id).all()
    for show in shows:
        if show.start_time >= date:
            data['upcoming_shows_count'] += 1
            data['upcoming_shows'].append({
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': format_datetime(str(show.start_time))
            })
        else:
            data['past_shows_count'] += 1
            data['past_shows'].append({
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': format_datetime(str(show.start_time))
            })
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    err = False
    try:
        venue = Venue()
        form = VenueForm()
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.genres = form.genres.data
        venue.image_link = form.image_link.data
        venue.facebook_link = form.facebook_link.data
        venue.website = form.website.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
        err = True
        print(sys.exc_info())
    finally:
        db.session.close()
        if err:
            flash('An error occured. Venue ' +
                  form.name.data + ' Could not be listed.')
        else:
            flash('Venue ' + form.name.data + ' was successfully listed!')

    return redirect(url_for('index'))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

    err = False
    venue = Venue.query.get(venue_id)
    name = venue.name
    try:    
        venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        err = True
        print(sys.exc_info())
    finally:
        db.session.close()
        if not err:
            flash(f'Venue {name} was deleted successfully!!')
        else:
            flash(f'An error occurred. Venue {name} could not be deleted.')
    
    return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists', methods=['GET'])
def artists():
    data = db.session.query(Artist.id, Artist.name)
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

    search_term = request.form.get('search_term', '')
    results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(results),
        "data": results
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<artist_id>', methods=['GET'])
def show_artist(artist_id):

    artist = Artist.query.get(artist_id)
    if artist is None:
        flash(f"Artist doesn't exist!")
        return redirect(url_for('index'))
    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,
        'past_shows': [],
        'upcoming_shows': [],
        'past_shows_count': 0,
        'upcoming_shows_count': 0,
    }
    date = datetime.today()
    shows = Show.query.filter(Show.artist_id==artist_id).all()
    for show in shows:
        if show.start_time >= date:
            data['upcoming_shows_count'] += 1
            data['upcoming_shows'].append({
                'venue_id': show.venue.id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'start_time': format_datetime(str(show.start_time))
            })
        else:
            data['past_shows_count'] += 1
            data['past_shows'].append({
                'venue_id': show.venue.id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'start_time': format_datetime(str(show.start_time))
            })
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    if artist is None:
        flash(f"Artist doesn't exist")
        return redirect(url_for('index'))

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    if artist is None:
        flash(f"Artist doesn't exist.")
        return redirect(url_for('index'))
    try:
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.image_link = form.image_link.data
        artist.facebook_link = form.facebook_link.data
        artist.website = form.website.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        db.session.commit()
        flash(f"Artist {artist.name} has been updated successfully!")
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash(f"An error occured. Could not update artist {artist.name}")
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

    form = VenueForm()
    venue = Venue.query.get(venue_id)
    if venue is None:
        flash(f"Venue doesn't exist")
        return redirect(url_for('index'))
    
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    form = VenueForm()
    venue = Venue.query.get(venue_id)
    if venue is None:
        flash(f"Venue doesn't exist")
        return redirect(url_for('index'))

    try:    
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.genres = form.genres.data
        venue.image_link = form.image_link.data
        venue.facebook_link = form.facebook_link.data
        venue.website = form.website.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        db.session.commit()
        flash(f"Venue {venue.name} has been updated successfully!")
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash(f"An error occured, could not update Venue {venue.name}")
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

    err = False
    try:
        artist = Artist()
        form = ArtistForm()
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.image_link = form.image_link.data
        artist.facebook_link = form.facebook_link.data
        artist.website = form.website.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        err = True
        print(sys.exc_info())
    finally:
        db.session.close()
        if err:
            flash('An error occurred. Artist ' +
                  form.name.data + ' could not be listed.')
        else:
            flash('Artist ' + form.name.data + ' was successfully listed!')

    return redirect(url_for('index'))


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):

    err = False
    artist = Artist.query.get(artist_id)
    name = artist.name
    try:    
        artist.query.filter_by(id=artist_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        err = True
        print(sys.exc_info())
    finally:
        db.session.close()
        if not err:
            flash(f'Artist {name} was deleted successfully!!')
        else:
            flash(f'An error occurred. Artist {name} could not be deleted.')
    
    return jsonify({ 'success': True })

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows', methods=['GET'])
def shows():

    shows = Show.query.all()
    data = []
    for show in shows:
        data.append({
            'venue_id': show.venue.id,
            'venue_name': show.venue.name,
            'artist_id': show.artist.id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': format_datetime(str(show.start_time))
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create', methods=['GET'])
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

    err = False
    try:
        form = ShowForm()
        show = Show()
        show.artist_id = form.artist_id.data
        show.venue_id = form.venue_id.data
        show.start_time = form.start_time.data
        db.session.add(show)
        db.session.commit()
    except:
        db.session.rollback()
        err = True
        print(sys.exc_info())
    finally:
        db.session.close()
        if err:
            flash('An error occurred. Show could not be listed.')
        else:
            flash('Show was successfully listed!')

    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
