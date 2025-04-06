from datetime import datetime
from flask_login import UserMixin
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """User model representing both drivers and riders."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    ride_offers = db.relationship('RideOffer', backref='driver', lazy='dynamic', cascade='all, delete-orphan')
    ride_requests = db.relationship('RideRequest', backref='rider', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'is_verified': self.is_verified
        }
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class RideOffer(db.Model):
    """Model for ride offers created by drivers."""
    __tablename__ = 'ride_offers'
    
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    origin = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    ride_matches = db.relationship('RideMatch', backref='ride_offer', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'driver_id': self.driver_id,
            'driver_name': self.driver.full_name if self.driver else None,
            'origin': self.origin,
            'destination': self.destination,
            'departure_time': self.departure_time.isoformat(),
            'available_seats': self.available_seats,
            'description': self.description
        }

class RideRequest(db.Model):
    """Model for ride requests created by riders."""
    __tablename__ = 'ride_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    rider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    origin = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    ride_matches = db.relationship('RideMatch', backref='ride_request', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'rider_id': self.rider_id,
            'rider_name': self.rider.full_name if self.rider else None,
            'origin': self.origin,
            'destination': self.destination,
            'departure_time': self.departure_time.isoformat()
        }

class RideMatch(db.Model):
    """Model for matching ride offers with ride requests."""
    __tablename__ = 'ride_matches'
    
    id = db.Column(db.Integer, primary_key=True)
    ride_offer_id = db.Column(db.Integer, db.ForeignKey('ride_offers.id', ondelete='CASCADE'), nullable=False)
    ride_request_id = db.Column(db.Integer, db.ForeignKey('ride_requests.id', ondelete='CASCADE'), nullable=False)
    pending = db.Column(db.Boolean, default=True)
    confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ride_offer_id': self.ride_offer_id,
            'ride_request_id': self.ride_request_id,
            'pending': self.pending,
            'confirmed': self.confirmed
        }
