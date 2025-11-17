"""
HIVE - Innovation and Entrepreneurship Management System
Sri Ramakrishna Institute of Technology
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hive-sri-ramakrishna-2024-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hive_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create upload directories
os.makedirs('uploads/events', exist_ok=True)
os.makedirs('uploads/reports', exist_ok=True)
os.makedirs('uploads/photos', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('static/guidelines', exist_ok=True)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    events = db.relationship('Event', backref='coordinator', lazy=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    quarter = db.Column(db.String(10), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    activity_category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(50), nullable=False)
    venue = db.Column(db.String(200), nullable=False)
    participants_expected = db.Column(db.Integer)
    resource_person = db.Column(db.Text)
    objectives = db.Column(db.Text)
    student_development = db.Column(db.Text)
    institution_development = db.Column(db.Text)
    budget = db.Column(db.Float, default=0)
    coordinator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Planned')
    checklist_confirmed = db.Column(db.Boolean, default=False)
    
    # Report submission fields
    report_submitted = db.Column(db.Boolean, default=False)
    submission_date = db.Column(db.DateTime)
    male_participants = db.Column(db.Integer, default=0)
    female_participants = db.Column(db.Integer, default=0)
    internal_participants = db.Column(db.Integer, default=0)
    external_participants = db.Column(db.Integer, default=0)
    faculty_participants = db.Column(db.Integer, default=0)
    year_wise_data = db.Column(db.Text)
    department_wise_data = db.Column(db.Text)
    sdg_goals = db.Column(db.Text)
    summary = db.Column(db.Text)
    youtube_link = db.Column(db.String(500))
    social_media_links = db.Column(db.Text)
    expense_statement = db.Column(db.Text)

class EventPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    photo_type = db.Column(db.String(50))  # geotagged, normal
    file_path = db.Column(db.String(500))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class EventDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    document_type = db.Column(db.String(100))  # poster, report, attendance, etc.
    file_path = db.Column(db.String(500))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper Functions
def generate_random_password(length=8):
    """Generate a random password"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def send_credentials_email(email, username, password):
    """Send email with login credentials"""
    try:
        # Configure your SMTP settings here
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "hive@sritcbe.ac.in"  # Replace with your email
        sender_password = ""  # Replace with your app password
        
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email
        message["Subject"] = "Welcome to HIVE - Your Login Credentials"
        
        body = f"""
        Welcome to HIVE - Innovation and Entrepreneurship Management System
        Sri Ramakrishna Institute of Technology
        
        Your login credentials are:
        Username: {username}
        Password: {password}
        
        Please login at: http://your-server-address/login
        
        For security, please change your password after your first login.
        
        Best Regards,
        HIVE Team
        """
        
        message.attach(MIMEText(body, "plain"))
        
        # Uncomment these lines when you have configured SMTP
        # server = smtplib.SMTP(smtp_server, smtp_port)
        # server.starttls()
        # server.login(sender_email, sender_password)
        # server.send_message(message)
        # server.quit()
        
        print(f"Email would be sent to {email} with credentials")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def admin_required(f):
    """Decorator for admin-only routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    """Home page with login options"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for both admin and ambassadors"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check for admin login
        if username == 'hive' and password == 'hive':
            # Create admin user if not exists
            admin = User.query.filter_by(email='hive@admin.com').first()
            if not admin:
                admin = User(
                    email='hive@admin.com',
                    name='Admin',
                    password_hash=generate_password_hash('hive'),
                    department='Administration',
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        
        # Check for regular user login
        user = User.query.filter_by(email=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('user_dashboard'))
        
        flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    users = User.query.filter_by(is_admin=False).all()
    events = Event.query.all()
    return render_template('admin_dashboard.html', users=users, events=events)

@app.route('/admin/register_user', methods=['GET', 'POST'])
@admin_required
def register_user():
    """Register new innovation ambassador"""
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        department = request.form.get('department')
        phone = request.form.get('phone')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('User with this email already exists', 'error')
            return redirect(url_for('register_user'))
        
        # Generate random password
        password = generate_random_password()
        
        # Create new user
        new_user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password),
            department=department,
            phone=phone,
            is_admin=False
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Send credentials via email
        send_credentials_email(email, email, password)
        
        flash(f'User registered successfully. Credentials sent to {email}', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('register_user.html')

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    """User dashboard for innovation ambassadors"""
    user_events = Event.query.filter_by(coordinator_id=current_user.id).all()
    return render_template('user_dashboard.html', events=user_events)

@app.route('/user/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    """Create new event"""
    if request.method == 'POST':
        # Get form data
        event_data = {
            'title': request.form.get('title'),
            'event_type': request.form.get('event_type'),
            'quarter': request.form.get('quarter'),
            'academic_year': request.form.get('academic_year'),
            'semester': request.form.get('semester'),
            'level': request.form.get('level'),
            'activity_category': request.form.get('activity_category'),
            'date': datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
            'time': request.form.get('time'),
            'venue': request.form.get('venue'),
            'participants_expected': int(request.form.get('participants_expected', 0)),
            'resource_person': request.form.get('resource_person'),
            'objectives': request.form.get('objectives'),
            'student_development': request.form.get('student_development'),
            'institution_development': request.form.get('institution_development'),
            'budget': float(request.form.get('budget', 0)),
            'coordinator_id': current_user.id,
            'checklist_confirmed': 'checklist' in request.form
        }
        
        # Create new event
        new_event = Event(**event_data)
        db.session.add(new_event)
        db.session.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    
    return render_template('create_event.html')

@app.route('/user/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect', 'error')
            return redirect(url_for('change_password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return redirect(url_for('change_password'))
        
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    
    return render_template('change_password.html')

@app.route('/user/submit_report/<int:event_id>', methods=['GET', 'POST'])
@login_required
def submit_report(event_id):
    """Submit event report"""
    event = Event.query.get_or_404(event_id)
    
    if event.coordinator_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        # Update event with report data
        event.male_participants = int(request.form.get('male_participants', 0))
        event.female_participants = int(request.form.get('female_participants', 0))
        event.internal_participants = int(request.form.get('internal_participants', 0))
        event.external_participants = int(request.form.get('external_participants', 0))
        event.faculty_participants = int(request.form.get('faculty_participants', 0))
        event.year_wise_data = request.form.get('year_wise_data')
        event.department_wise_data = request.form.get('department_wise_data')
        event.sdg_goals = request.form.get('sdg_goals')
        event.summary = request.form.get('summary')
        event.youtube_link = request.form.get('youtube_link')
        event.social_media_links = request.form.get('social_media_links')
        event.expense_statement = request.form.get('expense_statement')
        event.report_submitted = True
        event.submission_date = datetime.utcnow()
        event.status = 'Completed'
        
        # Handle file uploads
        # Geotagged photos
        if 'geotagged_photos' in request.files:
            for file in request.files.getlist('geotagged_photos'):
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join('uploads/photos', f'geo_{event_id}_{filename}')
                    file.save(filepath)
                    photo = EventPhoto(event_id=event_id, photo_type='geotagged', file_path=filepath)
                    db.session.add(photo)
        
        # Normal photos
        if 'normal_photos' in request.files:
            for file in request.files.getlist('normal_photos'):
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join('uploads/photos', f'normal_{event_id}_{filename}')
                    file.save(filepath)
                    photo = EventPhoto(event_id=event_id, photo_type='normal', file_path=filepath)
                    db.session.add(photo)
        
        # Documents
        doc_types = ['poster', 'detailed_report', 'attendance_sheet', 'resource_person_profile']
        for doc_type in doc_types:
            if doc_type in request.files:
                file = request.files[doc_type]
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join('uploads/reports', f'{doc_type}_{event_id}_{filename}')
                    file.save(filepath)
                    document = EventDocument(event_id=event_id, document_type=doc_type, file_path=filepath)
                    db.session.add(document)
        
        db.session.commit()
        flash('Event report submitted successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    
    return render_template('submit_report.html', event=event)

@app.route('/download_guidelines')
@login_required
def download_guidelines():
    """Download guidelines PDF"""
    # You can place your guidelines PDF in the static/guidelines folder
    guidelines_path = 'static/guidelines/iic_guidelines.pdf'
    if os.path.exists(guidelines_path):
        return send_file(guidelines_path, as_attachment=True, download_name='IIC_Guidelines.pdf')
    else:
        flash('Guidelines file not found', 'error')
        return redirect(request.referrer or url_for('user_dashboard'))

@app.route('/generate_report/<int:event_id>')
@login_required
def generate_report(event_id):
    """Generate PDF report for an event"""
    event = Event.query.get_or_404(event_id)
    
    if event.coordinator_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=TA_CENTER
    )
    
    # Add header with letterhead (you would need to add your letterhead image)
    # logo = Image('static/images/letterhead.png', width=6*inch, height=1.5*inch)
    # elements.append(logo)
    
    elements.append(Paragraph("SRI RAMAKRISHNA INSTITUTE OF TECHNOLOGY", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("HIVE - Innovation and Entrepreneurship Cell", styles['Heading2']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("EVENT REPORT", styles['Heading1']))
    elements.append(Spacer(1, 24))
    
    # Event details
    event_data = [
        ['Event Title:', event.title],
        ['Event Type:', event.event_type],
        ['Date:', event.date.strftime('%d/%m/%Y')],
        ['Time:', event.time],
        ['Venue:', event.venue],
        ['Quarter:', event.quarter],
        ['Academic Year:', event.academic_year],
        ['Semester:', event.semester],
        ['Level:', event.level],
        ['Activity Category:', event.activity_category],
        ['Coordinator:', current_user.name],
        ['Department:', current_user.department],
    ]
    
    # Create table
    table = Table(event_data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 24))
    
    # Objectives
    elements.append(Paragraph("Objectives:", styles['Heading2']))
    elements.append(Paragraph(event.objectives or "Not specified", styles['BodyText']))
    elements.append(Spacer(1, 12))
    
    # If report submitted, add additional details
    if event.report_submitted:
        elements.append(Paragraph("Event Statistics:", styles['Heading2']))
        stats_data = [
            ['Male Participants:', str(event.male_participants)],
            ['Female Participants:', str(event.female_participants)],
            ['Total Participants:', str(event.male_participants + event.female_participants)],
            ['Internal Participants:', str(event.internal_participants)],
            ['External Participants:', str(event.external_participants)],
            ['Faculty Participants:', str(event.faculty_participants)],
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 12))
        
        # Summary
        elements.append(Paragraph("Event Summary:", styles['Heading2']))
        elements.append(Paragraph(event.summary or "Not provided", styles['BodyText']))
        elements.append(Spacer(1, 12))
        
        # SDG Goals
        if event.sdg_goals:
            elements.append(Paragraph("Sustainable Development Goals Addressed:", styles['Heading2']))
            elements.append(Paragraph(event.sdg_goals, styles['BodyText']))
            elements.append(Spacer(1, 12))
    
    # Signature section
    elements.append(Spacer(1, 48))
    sig_data = [
        ['', '', ''],
        ['Faculty Coordinator', 'HOD', 'Principal'],
        ['Signature', 'Signature', 'Signature'],
    ]
    
    sig_table = Table(sig_data, colWidths=[2*inch, 2*inch, 2*inch])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elements.append(sig_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'Event_Report_{event.title}_{datetime.now().strftime("%Y%m%d")}.pdf',
        mimetype='application/pdf'
    )

@app.route('/api/events')
@login_required
def api_events():
    """API endpoint to get events data"""
    if current_user.is_admin:
        events = Event.query.all()
    else:
        events = Event.query.filter_by(coordinator_id=current_user.id).all()
    
    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'title': event.title,
            'date': event.date.strftime('%Y-%m-%d'),
            'status': event.status,
            'level': event.level,
            'coordinator': event.coordinator.name
        })
    
    return jsonify(events_data)

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()
    
    # Create admin user if not exists
    admin = User.query.filter_by(email='hive@admin.com').first()
    if not admin:
        admin = User(
            email='hive@admin.com',
            name='Admin',
            password_hash=generate_password_hash('hive'),
            department='Administration',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)