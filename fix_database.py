"""
FIX DATABASE SCRIPT
This will delete and recreate the database with id_number column
"""

import os
import shutil

print("=" * 50)
print("DATABASE FIX SCRIPT")
print("=" * 50)

# Step 1: Delete old database
print("\n1. Checking for old database...")
if os.path.exists("appointments.db"):
    os.remove("appointments.db")
    print("   ✅ Deleted: appointments.db")
else:
    print("   ℹ️  No old database found")

# Step 2: Delete cache folders
print("\n2. Cleaning cache...")
cache_folders = ["__pycache__", "instance"]
for folder in cache_folders:
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"   ✅ Deleted: {folder}/")
    else:
        print(f"   ℹ️  No {folder} folder")

# Step 3: Import and create new database
print("\n3. Creating new database...")
try:
    from app import app, db, Appointment
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("   ✅ Database tables created")
        
        # Test with a sample appointment
        test_appointment = Appointment(
            name="Test Client",
            email="test@example.com",
            phone="1234567890",
            id_number="TEST123456",  # Testing the new column
            service="Test Service",
            date="2026-02-11",
            time="14:00",
            status="scheduled"
        )
        
        db.session.add(test_appointment)
        db.session.commit()
        print("   ✅ Test appointment saved with id_number")
        
        # Verify
        count = Appointment.query.count()
        print(f"   ✅ Total appointments in database: {count}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("\n   TROUBLESHOOTING:")
    print("   1. Make sure app.py has id_number in Appointment class")
    print("   2. Check for syntax errors in app.py")
    print("   3. Restart VSCode if needed")

print("\n" + "=" * 50)
print("SCRIPT COMPLETE!")
print("=" * 50)
print("\n🎉 NEXT STEPS:")
print("1. Run: python app.py")
print("2. Visit: http://localhost:5000")
print("3. Book a test appointment")
print("\nThe id_number column should now work!")