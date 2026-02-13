from flask import Flask, render_template, request, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import json
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///appointments.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

# Database model
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    id_number = db.Column(db.String(50), nullable=True)
    service = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()
    

@app.route('/')
def home():
    current_year = datetime.now().year
    return render_template('index.html', current_year=current_year)

@app.route('/view-appointments')
def view_appointments():
    # Simple password protection
    password = request.args.get('password')
    
    if password != 'therapy123':
        return '''
        <h2>Admin Login Required</h2>
        <form>
            <input type="password" name="password" placeholder="Enter password">
            <button type="submit">Login</button>
        </form>
        '''
    
    current_year = datetime.now().year
    appointments = Appointment.query.all()
    return render_template('admin.html', appointments=appointments, current_year=current_year)

@app.route('/booking-simple')
def booking_simple():
    return render_template('booking-simple.html')

@app.route('/test-redirect')
def test_redirect():
    flash('Redirect test worked!')
    return redirect('/')
     
@app.route('/update-status/<int:appointment_id>', methods=['POST'])
def update_status(appointment_id):
    """Update appointment status (completed, no-show, etc.)"""
    try:
        data = request.get_json()
        print(f"Updating appointment {appointment_id} to status: {data['status']}")
        
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'success': False, 'error': 'Appointment not found'}), 404
        
        appointment.status = data['status']
        db.session.commit()
        
        print(f"Successfully updated appointment {appointment_id}")
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error updating status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/reschedule/<int:appointment_id>', methods=['POST'])
def reschedule(appointment_id):
    """Reschedule an appointment to new date/time"""
    try:
        data = request.get_json()
        print(f"Rescheduling appointment {appointment_id} to {data.get('new_date')} {data.get('new_time')}")
        
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'success': False, 'error': 'Appointment not found'}), 404
        
        appointment.date = data['new_date']
        appointment.time = data['new_time']
        appointment.status = 'postponed'
        db.session.commit()
        
        print(f"Successfully rescheduled appointment {appointment_id}")
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error rescheduling: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/about')
def about():
    now = datetime.now()
    current_year = now.year
    return render_template('about.html', current_year=current_year)

# Calendar route
@app.route('/calendar')
def calendar():
    current_year = datetime.now().year
    return render_template('calendar.html', current_year=current_year)

# API: Get blocked dates (fully booked)
@app.route('/api/blocked-dates')
def get_blocked_dates():
    appointments = Appointment.query.filter_by(status='scheduled').all()
    
    date_counts = {}
    for apt in appointments:
        date_counts[apt.date] = date_counts.get(apt.date, 0) + 1
    
    blocked_dates = []
    max_per_day = 3
    
    for date_str, count in date_counts.items():
        if count >= max_per_day:
            blocked_dates.append(date_str)
    
    return jsonify({'blocked_dates': blocked_dates})

# API: Get available time slots for a specific date
@app.route('/api/available-slots')
def get_available_slots():
    date_str = request.args.get('date')
    
    if not date_str:
        return jsonify({'slots': []})
    
    booked_appointments = Appointment.query.filter_by(
        date=date_str,
        status='scheduled'
    ).all()
    
    booked_times = [apt.time for apt in booked_appointments]
    
    all_slots = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
    available_slots = [slot for slot in all_slots if slot not in booked_times]
    
    return jsonify({'slots': available_slots})

# Booking route with calendar support
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    current_year = datetime.now().year
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        id_number = request.form['id_number']
        service = request.form['service']
        date = request.form['date']
        time = request.form['time']
        
        new_appointment = Appointment(
            name=name,
            email=email,
            phone=phone,
            id_number=id_number,
            service=service,
            date=date,
            time=time,
            status='scheduled'
        )
        
        db.session.add(new_appointment)
        db.session.commit()
        
        flash('Appointment booked successfully! We will contact you soon.')
        return redirect('/')
    
    prefill_date = request.args.get('date', '')
    prefill_time = request.args.get('time', '')
    
    return render_template('booking.html', 
                         current_year=current_year,
                         prefill_date=prefill_date,
                         prefill_time=prefill_time)

@app.route('/faq')
def faq():
    current_year = datetime.now().year
    return render_template('faq.html', current_year=current_year)

@app.route('/resources')
def resources():
    current_year = datetime.now().year
    return render_template('resources.html', current_year=current_year)

@app.route('/services')
def services():
    current_year = datetime.now().year
    return render_template('services.html', current_year=current_year)

@app.route('/debug-routes')
def debug_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(str(rule))
    return "<br>".join(routes)

@app.route('/contact')
def contact():
    current_year = datetime.now().year
    return render_template('contact.html', current_year=current_year)

@app.route('/contact-submit', methods=['POST'])
def contact_submit():
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    subject = request.form.get('subject')
    message = request.form.get('message')
    
    # For now, just flash a success message
    flash('Thank you for your message! We will get back to you within 24 hours.')
    
    # Later we can add email notification here
    # send_contact_notification(name, email, phone, subject, message)
    
    return redirect('/contact')
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

