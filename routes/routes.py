from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import DataRequired
from models import RideOffer
from utils.route_optimization import RouteOptimization
from app import db
import os
from datetime import datetime, timedelta

routes_bp = Blueprint('routes', __name__, template_folder='templates')

# Initialize the route optimizer with credentials
PROJECT_ID = os.environ.get('PROJECT_ID')
OAUTH_TOKEN = os.environ.get('OAUTH_TOKEN')
route_optimizer = RouteOptimization(PROJECT_ID, OAUTH_TOKEN)

class SearchForm(FlaskForm):
    origin = StringField('Origin (Place ID)', validators=[DataRequired()])
    origin_display = StringField('Origin (Display Name)', validators=[DataRequired()])
    destination = StringField('Destination (Place ID)', validators=[DataRequired()])
    destination_display = StringField('Destination (Display Name)', validators=[DataRequired()])
    departure_date = DateField('Departure Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Search Rides')

@routes_bp.route('/search', methods=['GET', 'POST'])
def search_rides():
    form = SearchForm()
    
    if form.validate_on_submit():
        # Convert date to string format expected by the backend
        departure_date = form.departure_date.data.strftime('%Y-%m-%d')
        
        # Redirect to results page with search parameters
        return redirect(url_for('routes.search_results', 
                               origin=form.origin.data,
                               destination=form.destination.data,
                               departure_date=departure_date))
    
    return render_template('search_rides.html', title='Search Rides', form=form)

@routes_bp.route('/search_results')
def search_results():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    departure_date = request.args.get('departure_date')
    
    if not all([origin, destination, departure_date]):
        flash('Please provide all search parameters', 'warning')
        return redirect(url_for('routes.search_rides'))
    
    # Query ride offers for the given date
    ride_offers = RideOffer.query.filter(
        db.func.date(RideOffer.departure_time) == departure_date,
        RideOffer.available_seats > 0
    ).all()
    
    if not ride_offers:
        flash('No ride offers found for the selected date', 'info')
        return render_template('search_results.html', 
                              title='Search Results', 
                              ride_offers=[], 
                              origin=origin, 
                              destination=destination, 
                              departure_date=departure_date)
    
    # Format departure time for the route optimization API
    departure_time = f"{departure_date}T00:00:00Z"
    passenger_waypoint = (origin, destination)
    
    optimized_ride_offers = []
    for offer in ride_offers:
        try:
            # Get confirmed ride requests for this offer to include in route optimization
            rider_waypoints = []
            for match in offer.ride_matches:
                if match.confirmed:
                    req = match.ride_request
                    rider_waypoints.append((req.origin, req.destination))
            
            # Add current passenger's waypoint
            rider_waypoints.append(passenger_waypoint)
            
            # Call route optimization
            vehicle_waypoint = (offer.origin, offer.destination)
            route_result = route_optimizer.optimize_tours(vehicle_waypoint, rider_waypoints, departure_time)
            
            # Combine ride offer data with route optimization results
            offer_dict = {
                'id': offer.id,
                'driver_id': offer.driver_id,
                'driver_name': offer.driver.full_name,
                'origin': offer.origin,
                'destination': offer.destination,
                'departure_time': offer.departure_time.isoformat(),
                'available_seats': offer.available_seats,
                'description': offer.description,
                'total_duration': route_result['total_duration'],
                'total_distance': route_result['total_distance'],
                'polyline': route_result['polyline']
            }
            
            optimized_ride_offers.append(offer_dict)
        
        except Exception as e:
            # Log the error and continue with the next offer
            print(f"Error optimizing route for offer {offer.id}: {str(e)}")
            continue
    
    # Sort ride offers by total duration (shortest first)
    optimized_ride_offers.sort(key=lambda x: x['total_duration'])
    
    return render_template('search_results.html', 
                          title='Search Results', 
                          ride_offers=optimized_ride_offers, 
                          origin=origin, 
                          destination=destination, 
                          departure_date=departure_date)

@routes_bp.route('/ride_details/<int:ride_offer_id>')
def ride_details(ride_offer_id):
    ride_offer = RideOffer.query.get_or_404(ride_offer_id)
    
    # If the user is logged in, check for optimization with their route
    optimized_data = None
    if current_user.is_authenticated:
        user_requests = current_user.ride_requests.order_by(RideRequest.created_at.desc()).first()
        
        if user_requests:
            try:
                # Format departure time for the route optimization API
                departure_time = ride_offer.departure_time.strftime('%Y-%m-%dT%H:%M:%SZ')
                
                # Get confirmed ride requests for this offer to include in route optimization
                rider_waypoints = []
                for match in ride_offer.ride_matches:
                    if match.confirmed:
                        req = match.ride_request
                        rider_waypoints.append((req.origin, req.destination))
                
                # Add current user's waypoint
                passenger_waypoint = (user_requests.origin, user_requests.destination)
                rider_waypoints.append(passenger_waypoint)
                
                # Call route optimization
                vehicle_waypoint = (ride_offer.origin, ride_offer.destination)
                optimized_data = route_optimizer.optimize_tours(vehicle_waypoint, rider_waypoints, departure_time)
            
            except Exception as e:
                # Log the error and continue
                print(f"Error optimizing route for details view: {str(e)}")
    
    return render_template('ride_details.html', 
                          title='Ride Details', 
                          ride_offer=ride_offer, 
                          optimized_data=optimized_data)
