# Student Information System - Supabase Setup Guide

## Prerequisites
- Python 3.8 or higher
- Supabase account and project

## Step 1: Supabase Project Setup

1. Go to [Supabase](https://supabase.com) and create a new project
2. Note down your project URL and anon key from the API settings
3. Go to the SQL Editor in your Supabase dashboard
4. Copy and paste the contents of `supabase_schema.sql` into the SQL editor
5. Run the SQL script to create all tables and policies

## Step 2: Environment Configuration

Create a `.env` file in the project root with the following content:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-url.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# Flask Configuration
FLASK_SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=development

# Database Configuration (Optional - for direct database access)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.your-project-url.supabase.co:5432/postgres
```

**Important Security Notes:**
- Never commit your `.env` file to version control
- Use a strong, unique secret key for production
- Keep your Supabase credentials secure
- Consider using environment variables in production

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Database Schema

The SQL schema creates the following tables:

- **users**: User accounts with roles (principal, teacher, student)
- **students**: Student information including face data
- **teachers**: Teacher information
- **marks**: Student marks by subject
- **grades**: Student grades by subject
- **attendance**: Daily attendance records with face data

## Step 5: Row Level Security (RLS)

The schema includes comprehensive RLS policies:

- **Principals**: Full access to all data
- **Teachers**: Can view and manage students, marks, grades, and attendance
- **Students**: Can only view their own data and mark their own attendance

## Step 6: Default Users

The schema creates these default users for testing:

- **Username**: `principal`, **Password**: `principal123`, **Role**: principal
- **Username**: `teacher`, **Password**: `teacher123`, **Role**: teacher
- **Username**: `student1`, **Password**: `student123`, **Role**: student

## Step 7: Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Security Features

1. **Password Hashing**: All passwords are hashed using Werkzeug's security functions
2. **Row Level Security**: Database-level access control
3. **Session Management**: Secure session handling with Flask
4. **Input Validation**: Server-side validation for all inputs
5. **SQL Injection Protection**: Using parameterized queries through Supabase

## Production Deployment

For production deployment:

1. Set `FLASK_ENV=production` in your environment
2. Use a strong, unique `FLASK_SECRET_KEY`
3. Enable HTTPS
4. Set up proper logging
5. Consider using a production WSGI server like Gunicorn
6. Set up monitoring and backup strategies

## Troubleshooting

### Common Issues:

1. **Connection Errors**: Verify your Supabase URL and anon key
2. **Permission Errors**: Check that RLS policies are properly configured
3. **Import Errors**: Ensure all dependencies are installed
4. **Face Data Issues**: Check that face data is being properly encoded/decoded

### Debug Mode:

Set `FLASK_ENV=development` to enable debug mode for detailed error messages.

## API Documentation

The application provides RESTful endpoints for:

- User authentication and management
- Student CRUD operations
- Teacher CRUD operations
- Marks and grades management
- Attendance tracking with face recognition
- Comprehensive reporting and analytics

## Data Migration

If you have existing data, you can migrate it by:

1. Exporting your current data
2. Transforming it to match the new schema
3. Using the database service methods to import data
4. Verifying data integrity after migration

## Backup and Recovery

- Supabase provides automatic backups
- Consider setting up additional backup strategies
- Test your recovery procedures regularly
- Keep backup copies of your environment configuration

## Monitoring and Logging

- Monitor application performance
- Set up error tracking
- Log important events (logins, data changes, etc.)
- Monitor database performance and usage

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the Supabase documentation
3. Check Flask and Python documentation
4. Consider community support channels 