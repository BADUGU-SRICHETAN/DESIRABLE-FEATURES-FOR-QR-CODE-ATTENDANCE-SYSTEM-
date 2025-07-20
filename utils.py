import base64
import json
import hashlib
from datetime import datetime
import math
from functools import wraps
import jwt
import qrcode
import io
from PIL import Image
from flask import current_app, request


def generate_qr_data(creator_id, title, expiration_time):
    """Generate encrypted data for QR code"""
    data = {
        'creator_id': creator_id,
        'title': title,
        'expiration': expiration_time.timestamp(),
        'created_at': datetime.utcnow().timestamp()
    }
    return jwt.encode(data, current_app.config['SECRET_KEY'], algorithm='HS256')


def generate_qr_code_image(data):
    """Generate QR code image and return as base64 encoded string"""
    # Create a QR code using the qrcode library
    try:
        # Generate QR code
        img = qrcode.make(data)
        
        # Save to BytesIO object
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # Return base64 encoded image
        return base64.b64encode(img_io.getvalue()).decode()
    except Exception as e:
        print(f"Error generating QR code: {e}")
        # Return a simple placeholder if QR generation fails
        return ""


def verify_qr_data(qr_data):
    """Verify and decrypt QR code data"""
    try:
        # Decode the JWT token using the app's secret key
        data = jwt.decode(qr_data, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        
        # Check expiration
        expiration = datetime.fromtimestamp(data['expiration'])
        if expiration < datetime.utcnow():
            return None
        
        return data
    except Exception as e:
        print(f"Error verifying QR data: {e}")
        return None


def get_client_ip():
    """Get the client's IP address"""
    # Check for forwarded IP (if behind proxy)
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr


def is_valid_location(current_location, required_location, max_distance_meters=100):
    """
    Validate if the current location is within acceptable distance of required location
    """
    try:
        # Parse locations (assumed format: "latitude,longitude")
        current_lat, current_lng = map(float, current_location.split(','))
        required_lat, required_lng = map(float, required_location.split(','))
        
        # Calculate distance (Haversine formula)
        R = 6371e3  # Earth radius in meters
        φ1 = math.radians(current_lat)
        φ2 = math.radians(required_lat)
        Δφ = math.radians(required_lat - current_lat)
        Δλ = math.radians(required_lng - current_lng)
        
        a = (math.sin(Δφ/2) * math.sin(Δφ/2) +
             math.cos(φ1) * math.cos(φ2) *
             math.sin(Δλ/2) * math.sin(Δλ/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = R * c  # Distance in meters
        
        return d <= max_distance_meters
    except Exception as e:
        print(f"Error validating location: {e}")
        return False
