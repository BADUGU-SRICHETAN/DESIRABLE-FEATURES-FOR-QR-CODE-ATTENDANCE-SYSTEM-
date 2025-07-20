from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' or 'teacher' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attendance_records = db.relationship('AttendanceRecord', back_populates='user', lazy='dynamic')
    sessions_created = db.relationship('AttendanceSession', back_populates='creator', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class AttendanceSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    qr_data = db.Column(db.String(256))
    location = db.Column(db.String(100))  # Format: "latitude,longitude"
    expiration_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    creator = db.relationship('User', back_populates='sessions_created')
    attendance_records = db.relationship('AttendanceRecord', back_populates='session', lazy='dynamic')

    def __repr__(self):
        return f'<AttendanceSession {self.title}>'


class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_session.id'), nullable=False)
    location = db.Column(db.String(100))  # Format: "latitude,longitude"
    ip_address = db.Column(db.String(45))  # IPv6 addresses can be up to 45 characters
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='attendance_records')
    session = db.relationship('AttendanceSession', back_populates='attendance_records')

    def __repr__(self):
        return f'<AttendanceRecord {self.user.username} - {self.session.title}>'
