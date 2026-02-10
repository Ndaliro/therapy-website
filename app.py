from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime  # <-- ADD THIS IMPORT
import os

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
    service = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    current_year = datetime.now().year  # <-- ADD THIS
    return render_template('index.html', current_year=current_year)  # <-- PASS IT HERE

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    current_year = datetime.now().year
    
    if request.method == 'POST':
        print("=== FORM SUBMITTED ===")  # Debug message
        print(f"Form data: {request.form}")  # Debug message
        
        # Get form data with error handling
        try:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            service = request.form['service']
            date = request.form['date']
            
            print(f"Name: {name}, Email: {email}")  # Debug message
            
            # Save to database
            new_appointment = Appointment(
                name=name,
                email=email,
                phone=phone,
                service=service,
                date=date
            )
            
            db.session.add(new_appointment)
            db.session.commit()
            print("=== SAVED TO DATABASE ===")  # Debug message
            
            flash('Appointment booked successfully! We will contact you soon.')
            return redirect('/')
            
        except Exception as e:
            print(f"ERROR: {e}")  # Debug message
            flash(f'Error: {e}')
            return redirect('/booking')
    
    return render_template('booking.html', current_year=current_year)

@app.route('/view-appointments')
def view_appointments():
    current_year = datetime.now().year  # <-- ADD THIS
    appointments = Appointment.query.all()
    return render_template('admin.html', appointments=appointments, current_year=current_year)  # <-- PASS IT HERE

@app.route('/booking-simple')
def booking_simple():
    return render_template('booking-simple.html')

@app.route('/test-redirect')
def test_redirect():
    flash('Redirect test worked!')
    return redirect('/')
     
     
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)