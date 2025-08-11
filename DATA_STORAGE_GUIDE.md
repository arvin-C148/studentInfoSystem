# Data Storage Implementation Guide

## Current Implementation (In-Memory Storage)

The current system uses in-memory storage for demonstration purposes. This means:
- Data is lost when the server restarts
- Not suitable for production use
- Limited scalability

## Recommended Data Storage Solutions

### 1. SQLite Database (Recommended for Small-Medium Scale)

**Advantages:**
- No server setup required
- File-based storage
- ACID compliance
- Easy to backup and migrate

**Implementation:**

```python
# Install required packages
pip install flask-sqlalchemy

# app.py modifications
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_info.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    class_name = db.Column(db.String(10), nullable=False)
    section = db.Column(db.String(5), nullable=False)
    face_data = db.Column(db.Text, nullable=True)  # Base64 encoded image
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    marks = db.relationship('Mark', backref='student', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    face_data = db.Column(db.Text, nullable=True)  # Base64 encoded image

class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    marks = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(2), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
```

### 2. PostgreSQL Database (Recommended for Production)

**Advantages:**
- Robust and scalable
- Advanced features
- Better performance for large datasets
- Built-in JSON support for face data

**Implementation:**

```python
# Install required packages
pip install flask-sqlalchemy psycopg2-binary

# app.py configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/student_info_db'

# Enhanced models for PostgreSQL
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    class_name = db.Column(db.String(10), nullable=False)
    section = db.Column(db.String(5), nullable=False)
    face_data = db.Column(db.Text, nullable=True)  # Base64 encoded image
    face_encoding = db.Column(db.JSON, nullable=True)  # Face recognition encodings
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 3. File-Based Storage for Face Images

**Option A: Local File System**

```python
import os
import uuid
from PIL import Image
import base64
import io

class FaceStorage:
    def __init__(self, storage_path="face_images"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def save_face_image(self, base64_data, student_id):
        """Save face image to file system"""
        try:
            # Remove data URL prefix
            if base64_data.startswith('data:image'):
                base64_data = base64_data.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(image_data))
            
            # Generate unique filename
            filename = f"student_{student_id}_{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(self.storage_path, filename)
            
            # Save image
            image.save(filepath, 'JPEG', quality=85)
            
            return filename
        except Exception as e:
            print(f"Error saving face image: {e}")
            return None
    
    def get_face_image_path(self, filename):
        """Get full path to face image"""
        return os.path.join(self.storage_path, filename)
```

**Option B: Cloud Storage (AWS S3, Google Cloud Storage)**

```python
import boto3
from botocore.exceptions import NoCredentialsError

class S3FaceStorage:
    def __init__(self, bucket_name, aws_access_key, aws_secret_key):
        self.bucket_name = bucket_name
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
    
    def save_face_image(self, base64_data, student_id):
        """Save face image to S3"""
        try:
            # Remove data URL prefix
            if base64_data.startswith('data:image'):
                base64_data = base64_data.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_data)
            
            # Generate unique filename
            filename = f"faces/student_{student_id}_{uuid.uuid4().hex}.jpg"
            
            # Upload to S3
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=image_data,
                ContentType='image/jpeg'
            )
            
            return filename
        except NoCredentialsError:
            print("AWS credentials not found")
            return None
        except Exception as e:
            print(f"Error saving to S3: {e}")
            return None
    
    def get_face_image_url(self, filename, expires_in=3600):
        """Generate presigned URL for face image"""
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': filename},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            print(f"Error generating URL: {e}")
            return None
```

### 4. Redis for Caching and Session Management

```python
import redis
import json

class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
    
    def cache_student_data(self, student_id, data, expire=3600):
        """Cache student data in Redis"""
        key = f"student:{student_id}"
        self.redis_client.setex(key, expire, json.dumps(data))
    
    def get_cached_student_data(self, student_id):
        """Get cached student data"""
        key = f"student:{student_id}"
        data = self.redis_client.get(key)
        return json.loads(data) if data else None
    
    def cache_face_data(self, student_id, face_data, expire=7200):
        """Cache face data separately"""
        key = f"face:{student_id}"
        self.redis_client.setex(key, expire, face_data)
```

## Complete Implementation Example

### 1. Updated app.py with Database Integration

```python
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import base64
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_info.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Initialize face storage
face_storage = FaceStorage()

# Database Models (as defined above)
# ... (User, Student, Attendance, Mark, Teacher models)

@app.route('/attendance/mark', methods=['GET', 'POST'])
def mark_attendance():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    
    student_id = users[session['username']]['student_id']
    student = Student.query.get(student_id)
    today = date.today()
    
    if request.method == 'POST':
        face_data = request.form.get('face_data')
        
        if face_data and len(face_data) > 100:
            try:
                # Save face image to file system
                filename = face_storage.save_face_image(face_data, student_id)
                
                # Create attendance record
                attendance = Attendance(
                    student_id=student_id,
                    date=today,
                    face_data=face_data  # Keep base64 for immediate display
                )
                
                # Update student's face data
                student.face_data = face_data
                student.face_image_path = filename
                
                db.session.add(attendance)
                db.session.commit()
                
                flash('Attendance marked successfully! Face image captured and stored.', 'success')
                
            except Exception as e:
                db.session.rollback()
                flash('Error processing attendance. Please try again.', 'danger')
        else:
            flash('No valid face image captured. Please ensure your camera is working and try again.', 'danger')
        
        return redirect(url_for('dashboard_student'))
    
    return render_template('mark_attendance.html', student=student, today=today)

# Database initialization
def init_db():
    with app.app_context():
        db.create_all()
        
        # Create default users if they don't exist
        if not User.query.filter_by(username='teacher').first():
            teacher_user = User(
                username='teacher',
                password_hash=generate_password_hash('teacher123'),
                role='teacher'
            )
            db.session.add(teacher_user)
        
        if not User.query.filter_by(username='principal').first():
            principal_user = User(
                username='principal',
                password_hash=generate_password_hash('principal123'),
                role='principal'
            )
            db.session.add(principal_user)
        
        db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
```

### 2. Requirements Update

```txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Werkzeug==2.3.7
Pillow==10.0.1
redis==5.0.1
boto3==1.34.0
psycopg2-binary==2.9.7
```

### 3. Environment Configuration

```python
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///student_info.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Face storage configuration
    FACE_STORAGE_PATH = os.environ.get('FACE_STORAGE_PATH') or 'face_images'
    
    # AWS S3 configuration (optional)
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
    
    # Redis configuration (optional)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
```

## Migration Strategy

### Step 1: Backup Current Data
```python
def backup_current_data():
    """Backup current in-memory data"""
    backup = {
        'students': students,
        'teachers': teachers,
        'users': users
    }
    
    with open('backup_data.json', 'w') as f:
        json.dump(backup, f, indent=2)
```

### Step 2: Migrate to Database
```python
def migrate_to_database():
    """Migrate in-memory data to database"""
    with app.app_context():
        # Load backup data
        with open('backup_data.json', 'r') as f:
            backup = json.load(f)
        
        # Migrate students
        for student_data in backup['students']:
            student = Student(
                name=student_data['name'],
                age=student_data['age'],
                class_name=student_data['class'],
                section=student_data['section'],
                face_data=student_data.get('face_data')
            )
            db.session.add(student)
        
        # Migrate teachers
        for teacher_data in backup['teachers']:
            teacher = Teacher(
                name=teacher_data['name'],
                subject=teacher_data['subject']
            )
            db.session.add(teacher)
        
        db.session.commit()
```

## Security Considerations

1. **Face Data Encryption**: Encrypt face data before storage
2. **Access Control**: Implement proper role-based access
3. **Data Retention**: Set up automatic data cleanup policies
4. **Backup Strategy**: Regular database and file backups
5. **GDPR Compliance**: Implement data deletion and export features

## Performance Optimization

1. **Image Compression**: Compress face images before storage
2. **Caching**: Use Redis for frequently accessed data
3. **Database Indexing**: Add indexes on frequently queried fields
4. **CDN**: Use CDN for serving face images in production
5. **Connection Pooling**: Configure database connection pooling

This comprehensive data storage solution provides scalability, security, and performance for your Student Info System. 