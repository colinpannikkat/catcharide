from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, SubmitField
from wtforms.validators import DataRequired
from models import RideRequest, RideOffer, RideMatch
from app import db
from datetime import datetime

passengers_bp = Blueprint('passengers', __name__, template_folder='templates')

class RideRequestForm(FlaskForm):
    origin = StringField('Origin (Place ID)', validators=[DataRequired()])
    origin_display = StringField('Origin (Display Name)', validators=[DataRequired()])
    destination = StringField('Destination (Place ID)', validators=[DataRequired()])
    destination_display = StringField('Destination (Display Name)', validators=[DataRequired()])
    departure_time = DateTimeField('Departure Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Create Ride Request')

@passengers_bp.route('/create_request', methods=['GET', 'POST'])
@login_required
def create_request():
    form = RideRequestForm()
    if form.validate_on_submit():
        ride_request = RideRequest(
            rider_id=current_user.id,
            origin=form.origin.data,
            destination=form.destination.data,
            departure_time=form.departure_time.data
        )
        db.session.add(ride_request)
        db.session.commit()
        flash('Your ride request has been created!', 'success')
        return redirect(url_for('passengers.my_requests'))
    
    return render_template('request_ride.html', title='Create Ride Request', form=form)

@passengers_bp.route('/my_requests')
@login_required
def my_requests():
    ride_requests = RideRequest.query.filter_by(rider_id=current_user.id).order_by(RideRequest.departure_time).all()
    return render_template('my_requests.html', title='My Ride Requests', ride_requests=ride_requests)

@passengers_bp.route('/edit_request/<int:ride_request_id>', methods=['GET', 'POST'])
@login_required
def edit_request(ride_request_id):
    ride_request = RideRequest.query.get_or_404(ride_request_id)
    
    # Check if the current user is the owner of the ride request
    if ride_request.rider_id != current_user.id:
        flash('You can only edit your own ride requests!', 'danger')
        return redirect(url_for('passengers.my_requests'))
    
    form = RideRequestForm()
    
    if form.validate_on_submit():
        ride_request.origin = form.origin.data
        ride_request.destination = form.destination.data
        ride_request.departure_time = form.departure_time.data
        db.session.commit()
        flash('Your ride request has been updated!', 'success')
        return redirect(url_for('passengers.my_requests'))
    elif request.method == 'GET':
        form.origin.data = ride_request.origin
        form.destination.data = ride_request.destination
        form.departure_time.data = ride_request.departure_time
    
    return render_template('edit_request.html', title='Edit Ride Request', form=form)

@passengers_bp.route('/delete_request/<int:ride_request_id>', methods=['POST'])
@login_required
def delete_request(ride_request_id):
    ride_request = RideRequest.query.get_or_404(ride_request_id)
    
    # Check if the current user is the owner of the ride request
    if ride_request.rider_id != current_user.id:
        flash('You can only delete your own ride requests!', 'danger')
        return redirect(url_for('passengers.my_requests'))
    
    try:
        # First, delete all ride matches associated with this request
        matches = RideMatch.query.filter_by(ride_request_id=ride_request_id).all()
        for match in matches:
            # If the match was confirmed, increase available seats
            if match.confirmed:
                ride_offer = RideOffer.query.get_or_404(match.ride_offer_id)
                ride_offer.available_seats += 1
            db.session.delete(match)
        
        # Then delete the ride request
        db.session.delete(ride_request)
        db.session.commit()
        flash('Your ride request has been deleted!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the ride request: {str(e)}', 'danger')
    
    return redirect(url_for('passengers.my_requests'))

@passengers_bp.route('/apply_ride/<int:ride_offer_id>', methods=['GET', 'POST'])
@login_required
def apply_ride(ride_offer_id):
    ride_offer = RideOffer.query.get_or_404(ride_offer_id)
    
    # Check if there are available seats
    if ride_offer.available_seats <= 0:
        flash('No more seats available for this ride!', 'warning')
        return redirect(url_for('routes.search_rides'))
    
    # Check if user has already applied to this ride
    existing_match = RideMatch.query.join(RideRequest).filter(
        RideMatch.ride_offer_id == ride_offer_id,
        RideRequest.rider_id == current_user.id
    ).first()
    
    if existing_match:
        flash('You have already applied to this ride!', 'warning')
        return redirect(url_for('routes.search_rides'))
    
    form = RideRequestForm()
    
    if form.validate_on_submit():
        # Create a new ride request
        ride_request = RideRequest(
            rider_id=current_user.id,
            origin=form.origin.data,
            destination=form.destination.data,
            departure_time=form.departure_time.data
        )
        db.session.add(ride_request)
        db.session.flush()  # Get the ID without committing
        
        # Create a ride match
        ride_match = RideMatch(
            ride_offer_id=ride_offer_id,
            ride_request_id=ride_request.id,
            pending=True,
            confirmed=False
        )
        db.session.add(ride_match)
        db.session.commit()
        
        flash('You have successfully applied for this ride!', 'success')
        return redirect(url_for('passengers.my_applications'))
    elif request.method == 'GET':
        form.origin.data = ride_offer.origin
        form.destination.data = ride_offer.destination
        form.departure_time.data = ride_offer.departure_time
    
    return render_template('apply_ride.html', 
                           title='Apply for Ride', 
                           form=form, 
                           ride_offer=ride_offer)

@passengers_bp.route('/my_applications')
@login_required
def my_applications():
    # Get all ride matches for the current user's ride requests
    ride_matches = RideMatch.query.join(RideRequest).filter(
        RideRequest.rider_id == current_user.id
    ).order_by(RideMatch.created_at.desc()).all()
    
    return render_template('my_applications.html', 
                           title='My Applications', 
                           ride_matches=ride_matches)

@passengers_bp.route('/cancel_application/<int:match_id>', methods=['POST'])
@login_required
def cancel_application(match_id):
    ride_match = RideMatch.query.get_or_404(match_id)
    
    # First get the ride_request_id before we delete the match (to prevent using None)
    ride_request_id = ride_match.ride_request_id
    
    if not ride_request_id:
        flash('Unable to find the associated ride request!', 'danger')
        return redirect(url_for('passengers.my_applications'))
    
    ride_request = RideRequest.query.get_or_404(ride_request_id)
    
    # Check if the current user is the owner of the ride request
    if ride_request.rider_id != current_user.id:
        flash('You can only cancel your own applications!', 'danger')
        return redirect(url_for('passengers.my_applications'))
    
    try:
        # If the match was confirmed, increase available seats
        if ride_match.confirmed:
            ride_offer = RideOffer.query.get_or_404(ride_match.ride_offer_id)
            ride_offer.available_seats += 1
        
        # Delete the match first, then the request
        db.session.delete(ride_match)
        db.session.flush()  # Apply the deletion without committing
        
        db.session.delete(ride_request)
        db.session.commit()
        
        flash('Your application has been canceled!', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while canceling the application: {str(e)}', 'danger')
    
    return redirect(url_for('passengers.my_applications'))
