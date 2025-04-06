from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from models import RideOffer, RideMatch
from app import db
from datetime import datetime

drivers_bp = Blueprint('drivers', __name__, template_folder='templates')

class RideOfferForm(FlaskForm):
    origin = StringField('Origin (Place ID)', validators=[DataRequired()])
    origin_display = StringField('Origin (Display Name)', validators=[DataRequired()])
    destination = StringField('Destination (Place ID)', validators=[DataRequired()])
    destination_display = StringField('Destination (Display Name)', validators=[DataRequired()])
    departure_time = DateTimeField('Departure Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    available_seats = IntegerField('Available Seats', validators=[DataRequired(), NumberRange(min=1, max=8)])
    description = TextAreaField('Description')
    submit = SubmitField('Create Ride Offer')

@drivers_bp.route('/create_offer', methods=['GET', 'POST'])
@login_required
def create_offer():
    form = RideOfferForm()
    if form.validate_on_submit():
        ride_offer = RideOffer(
            driver_id=current_user.id,
            origin=form.origin.data,
            destination=form.destination.data,
            departure_time=form.departure_time.data,
            available_seats=form.available_seats.data,
            description=form.description.data
        )
        db.session.add(ride_offer)
        db.session.commit()
        flash('Your ride offer has been created!', 'success')
        return redirect(url_for('drivers.my_offers'))
    
    return render_template('offer_ride.html', title='Create Ride Offer', form=form)

@drivers_bp.route('/my_offers')
@login_required
def my_offers():
    ride_offers = RideOffer.query.filter_by(driver_id=current_user.id).order_by(RideOffer.departure_time).all()
    return render_template('my_offers.html', title='My Ride Offers', ride_offers=ride_offers)

@drivers_bp.route('/edit_offer/<int:ride_offer_id>', methods=['GET', 'POST'])
@login_required
def edit_offer(ride_offer_id):
    ride_offer = RideOffer.query.get_or_404(ride_offer_id)
    
    # Check if the current user is the owner of the ride offer
    if ride_offer.driver_id != current_user.id:
        flash('You can only edit your own ride offers!', 'danger')
        return redirect(url_for('drivers.my_offers'))
    
    form = RideOfferForm()
    
    if form.validate_on_submit():
        ride_offer.origin = form.origin.data
        ride_offer.destination = form.destination.data
        ride_offer.departure_time = form.departure_time.data
        ride_offer.available_seats = form.available_seats.data
        ride_offer.description = form.description.data
        db.session.commit()
        flash('Your ride offer has been updated!', 'success')
        return redirect(url_for('drivers.my_offers'))
    elif request.method == 'GET':
        form.origin.data = ride_offer.origin
        form.destination.data = ride_offer.destination
        form.departure_time.data = ride_offer.departure_time
        form.available_seats.data = ride_offer.available_seats
        form.description.data = ride_offer.description
    
    return render_template('edit_offer.html', title='Edit Ride Offer', form=form)

@drivers_bp.route('/delete_offer/<int:ride_offer_id>', methods=['POST'])
@login_required
def delete_offer(ride_offer_id):
    ride_offer = RideOffer.query.get_or_404(ride_offer_id)
    
    # Check if the current user is the owner of the ride offer
    if ride_offer.driver_id != current_user.id:
        flash('You can only delete your own ride offers!', 'danger')
        return redirect(url_for('drivers.my_offers'))
    
    try:
        # First, delete all ride matches associated with this offer
        matches = RideMatch.query.filter_by(ride_offer_id=ride_offer_id).all()
        for match in matches:
            db.session.delete(match)
        
        # Then delete the ride offer
        db.session.delete(ride_offer)
        db.session.commit()
        flash('Your ride offer has been deleted!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the ride offer: {str(e)}', 'danger')
    
    return redirect(url_for('drivers.my_offers'))

@drivers_bp.route('/ride_requests/<int:ride_offer_id>')
@login_required
def ride_requests(ride_offer_id):
    ride_offer = RideOffer.query.get_or_404(ride_offer_id)
    
    # Check if the current user is the owner of the ride offer
    if ride_offer.driver_id != current_user.id:
        flash('You can only view requests for your own ride offers!', 'danger')
        return redirect(url_for('drivers.my_offers'))
    
    # Get all pending and confirmed ride matches for this offer
    ride_matches = RideMatch.query.filter_by(ride_offer_id=ride_offer_id).all()
    
    return render_template('ride_requests.html', 
                          title='Ride Requests', 
                          ride_offer=ride_offer, 
                          ride_matches=ride_matches)

@drivers_bp.route('/accept_request/<int:match_id>', methods=['POST'])
@login_required
def accept_request(match_id):
    ride_match = RideMatch.query.get_or_404(match_id)
    ride_offer = RideOffer.query.get_or_404(ride_match.ride_offer_id)
    
    # Check if the current user is the owner of the ride offer
    if ride_offer.driver_id != current_user.id:
        flash('You can only accept requests for your own ride offers!', 'danger')
        return redirect(url_for('drivers.my_offers'))
    
    # Check if there are available seats
    if ride_offer.available_seats <= 0:
        flash('No more seats available for this ride!', 'warning')
        return redirect(url_for('drivers.ride_requests', ride_offer_id=ride_offer.id))
    
    # Update the ride match
    ride_match.pending = False
    ride_match.confirmed = True
    
    # Decrease available seats
    ride_offer.available_seats -= 1
    
    db.session.commit()
    flash('Ride request accepted!', 'success')
    return redirect(url_for('drivers.ride_requests', ride_offer_id=ride_offer.id))

@drivers_bp.route('/decline_request/<int:match_id>', methods=['POST'])
@login_required
def decline_request(match_id):
    ride_match = RideMatch.query.get_or_404(match_id)
    ride_offer = RideOffer.query.get_or_404(ride_match.ride_offer_id)
    
    # Check if the current user is the owner of the ride offer
    if ride_offer.driver_id != current_user.id:
        flash('You can only decline requests for your own ride offers!', 'danger')
        return redirect(url_for('drivers.my_offers'))
    
    # Update the ride match
    ride_match.pending = False
    ride_match.confirmed = False
    
    db.session.commit()
    flash('Ride request declined!', 'info')
    return redirect(url_for('drivers.ride_requests', ride_offer_id=ride_offer.id))
