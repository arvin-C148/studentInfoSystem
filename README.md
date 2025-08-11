# Student Information System

A comprehensive web-based Student Information System built with Flask and Supabase, featuring face recognition attendance tracking, grade management, and detailed reporting.

## Features

### 🔐 **Secure Authentication**
- Role-based access control (Principal, Teacher, Student)
- Password hashing and secure session management
- Row Level Security (RLS) for database protection

### 👥 **User Management**
- **Principals**: Full system access, user management, comprehensive reporting
- **Teachers**: Student management, grade entry, attendance monitoring
- **Students**: View personal data, mark attendance with face recognition

### 📊 **Student Management**
- Complete CRUD operations for student records
- Class and section organization
- Face data storage for attendance tracking
- Academic performance tracking

### 📚 **Academic Management**
- Subject-wise marks and grades
- Automatic grade calculation (A-F scale)
- Performance analytics and reporting
- Class-wise academic statistics

### 📅 **Attendance System**
- Face recognition-based attendance marking
- Daily attendance tracking
- Attendance percentage calculations
- Face data management for teachers

### 📈 **Comprehensive Reporting**
- Student performance reports
- Class-wise analytics
- Attendance reports with filtering
- Academic performance dashboards
- System-wide statistics

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth with RLS
- **Face Recognition**: OpenCV
- **Frontend**: HTML, CSS, Bootstrap
- **Security**: Row Level Security, Password Hashing

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Supabase account and project

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd StudentInfoSystem
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Supabase Database**
   - Create a new Supabase project
   - Run the SQL script from `supabase_schema.sql` in your Supabase SQL Editor
   - Note your project URL and anon key

4. **Configure Environment**
   Create a `.env` file:
   ```env
   SUPABASE_URL=https://your-project-url.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   FLASK_SECRET_KEY=your-super-secret-key-change-this-in-production
   FLASK_ENV=development
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open http://localhost:5000
   - Login with default credentials:
     - **Principal**: `principal` / `principal123`
     - **Teacher**: `teacher` / `teacher123`
     - **Student**: `student1` / `student123`

## Database Schema

The system uses the following Supabase tables:

- **users**: User accounts with roles and authentication
- **students**: Student information and face data
- **teachers**: Teacher information and subjects
- **marks**: Subject-wise student marks
- **grades**: Subject-wise student grades
- **attendance**: Daily attendance records with face data

## Security Features

### 🔒 **Row Level Security (RLS)**
- Database-level access control
- Role-based data access policies
- Secure data isolation between users

### 🛡️ **Authentication & Authorization**
- Secure password hashing
- Session-based authentication
- Role-based route protection

### 🔐 **Data Protection**
- Encrypted face data storage
- Secure API endpoints
- Input validation and sanitization

## API Endpoints

### Authentication
- `GET/POST /login` - User login
- `GET /logout` - User logout

### Student Management
- `GET /students` - List all students
- `GET/POST /students/add` - Add new student
- `GET/POST /students/edit/<id>` - Edit student
- `POST /students/delete/<id>` - Delete student

### Teacher Management
- `GET /teachers` - List all teachers
- `GET/POST /teachers/add` - Add new teacher
- `GET/POST /teachers/edit/<id>` - Edit teacher
- `POST /teachers/delete/<id>` - Delete teacher

### Academic Management
- `GET/POST /marks/select` - Select class for marks
- `GET/POST /marks/enter/<class>/<section>` - Enter marks and grades

### Attendance
- `GET/POST /attendance/mark` - Mark attendance with face recognition
- `GET/POST /faces/manage` - Manage student face data
- `GET /faces/view/<id>` - View student face data
- `POST /faces/delete/<id>` - Delete student face data

### Reporting
- `GET /reports` - Reports dashboard
- `GET /reports/student/<id>` - Individual student report
- `GET /reports/class/<class>/<section>` - Class report
- `GET /reports/attendance` - Attendance report
- `GET /reports/academic` - Academic report

## Deployment

### Development
```bash
python app.py
```

### Production
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed production deployment instructions.

## Configuration

### Environment Variables
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anon key
- `FLASK_SECRET_KEY`: Secret key for Flask sessions
- `FLASK_ENV`: Environment (development/production)

### Database Configuration
The system uses Supabase as the backend database with:
- Automatic backups
- Real-time subscriptions
- Built-in authentication
- Row Level Security

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Security Considerations

### For Production Deployment
- Change default passwords
- Use strong, unique secret keys
- Enable HTTPS
- Set up proper logging
- Configure firewall rules
- Regular security audits

### Data Privacy
- Face data is stored securely
- User data is protected by RLS
- Regular data backups
- Compliance with privacy regulations

## Support

For issues and questions:
1. Check the [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. Review the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
3. Check Supabase documentation
4. Review Flask documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Supabase for the backend infrastructure
- Flask for the web framework
- OpenCV for face recognition capabilities
- Bootstrap for the UI framework

---

**Note**: This system is designed for educational institutions and includes comprehensive security measures for handling student data. Always ensure compliance with local data protection regulations when deploying in production. 