-- Student Information System Database Schema
-- Run this in your Supabase SQL Editor

-- ALTER DATABASE postgres SET "app.jwt_secret" TO 'your-jwt-secret';

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('principal', 'teacher', 'student')),
    student_id BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create students table
CREATE TABLE IF NOT EXISTS students (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    class VARCHAR(10) NOT NULL,
    section VARCHAR(5) NOT NULL,
    face_data TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create teachers table
CREATE TABLE IF NOT EXISTS teachers (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create marks table
CREATE TABLE IF NOT EXISTS marks (
    id BIGSERIAL PRIMARY KEY,
    student_id BIGINT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject VARCHAR(50) NOT NULL,
    mark INTEGER NOT NULL CHECK (mark >= 0 AND mark <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(student_id, subject)
);

-- Create grades table
CREATE TABLE IF NOT EXISTS grades (
    id BIGSERIAL PRIMARY KEY,
    student_id BIGINT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject VARCHAR(50) NOT NULL,
    grade VARCHAR(2) NOT NULL CHECK (grade IN ('A', 'B', 'C', 'D', 'E', 'F')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(student_id, subject)
);

-- Create attendance table
CREATE TABLE IF NOT EXISTS attendance (
    id BIGSERIAL PRIMARY KEY,
    student_id BIGINT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    face_data TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(student_id, date)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_students_class_section ON students(class, section);
CREATE INDEX IF NOT EXISTS idx_marks_student_id ON marks(student_id);
CREATE INDEX IF NOT EXISTS idx_grades_student_id ON grades(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_student_id ON attendance(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE teachers ENABLE ROW LEVEL SECURITY;
ALTER TABLE marks ENABLE ROW LEVEL SECURITY;
ALTER TABLE grades ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for users table
CREATE POLICY "Users can view their own data" ON users
    FOR SELECT USING (auth.uid()::text = username);

CREATE POLICY "Principals can view all users" ON users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role = 'principal'
        )
    );

CREATE POLICY "Principals can insert users" ON users
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role = 'principal'
        )
    );

CREATE POLICY "Principals can update users" ON users
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role = 'principal'
        )
    );

CREATE POLICY "Principals can delete users" ON users
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role = 'principal'
        )
    );

-- Create RLS policies for students table
CREATE POLICY "Principals and teachers can view all students" ON students
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role IN ('principal', 'teacher')
        )
    );

CREATE POLICY "Students can view their own data" ON students
    FOR SELECT USING (
        id = (
            SELECT student_id FROM users 
            WHERE username = auth.uid()::text
        )
    );

CREATE POLICY "Principals and teachers can insert students" ON students
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role IN ('principal', 'teacher')
        )
    );

CREATE POLICY "Principals and teachers can update students" ON students
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role IN ('principal', 'teacher')
        )
    );

CREATE POLICY "Principals and teachers can delete students" ON students
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role IN ('principal', 'teacher')
        )
    );

-- Create RLS policies for teachers table
CREATE POLICY "Principals can view all teachers" ON teachers
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role = 'principal'
        )
    );

CREATE POLICY "Principals can insert teachers" ON teachers
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role = 'principal'
        )
    );

CREATE POLICY "Principals can update teachers" ON teachers
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role = 'principal'
        )
    );

CREATE POLICY "Principals can delete teachers" ON teachers
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role = 'principal'
        )
    );

-- Create RLS policies for marks table
CREATE POLICY "Principals and teachers can view all marks" ON marks
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role IN ('principal', 'teacher')
        )
    );

CREATE POLICY "Students can view their own marks" ON marks
    FOR SELECT USING (
        student_id = (
            SELECT student_id FROM users 
            WHERE username = auth.uid()::text
        )
    );

CREATE POLICY "Principals and teachers can insert marks" ON marks
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role IN ('principal', 'teacher')
        )
    );

CREATE POLICY "Principals and teachers can update marks" ON marks
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role IN ('principal', 'teacher')
        )
    );

CREATE POLICY "Principals and teachers can delete marks" ON marks
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role IN ('principal', 'teacher')
        )
    );

-- Create RLS policies for grades table
CREATE POLICY "Principals and teachers can view all grades" ON grades
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role IN ('principal', 'teacher')
        )
    );

CREATE POLICY "Students can view their own grades" ON grades
    FOR SELECT USING (
        student_id = (
            SELECT student_id FROM users 
            WHERE username = auth.uid()::text
        )
    );

CREATE POLICY "Principals and teachers can insert grades" ON grades
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role IN ('principal', 'teacher')
        )
    );

CREATE POLICY "Principals and teachers can update grades" ON grades
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role IN ('principal', 'teacher')
        )
    );

CREATE POLICY "Principals and teachers can delete grades" ON grades
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role IN ('principal', 'teacher')
        )
    );

-- Create RLS policies for attendance table
CREATE POLICY "Principals and teachers can view all attendance" ON attendance
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role IN ('principal', 'teacher')
        )
    );

CREATE POLICY "Students can view their own attendance" ON attendance
    FOR SELECT USING (
        student_id = (
            SELECT student_id FROM users 
            WHERE username = auth.uid()::text
        )
    );

CREATE POLICY "Students can insert their own attendance" ON attendance
    FOR INSERT WITH CHECK (
        student_id = (
            SELECT student_id FROM users 
            WHERE username = auth.uid()::text
        )
    );

CREATE POLICY "Students can update their own attendance" ON attendance
    FOR UPDATE USING (
        student_id = (
            SELECT student_id FROM users 
            WHERE username = auth.uid()::text
        )
    );

CREATE POLICY "Principals and teachers can delete attendance" ON attendance
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE username = auth.uid()::text 
            AND role IN ('principal', 'teacher')
        )
    );

-- Insert default users for testing
INSERT INTO users (username, password_hash, role) VALUES
('principal', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.sUu.G', 'principal'),
('teacher', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.sUu.G', 'teacher');

-- Insert sample students
INSERT INTO students (name, age, class, section) VALUES
('Alice Smith', 15, '10', 'A'),
('Bob Johnson', 16, '11', 'B');

-- Insert sample teachers
INSERT INTO teachers (name, subject) VALUES
('Mr. Brown', 'Math'),
('Ms. Green', 'Science');

-- Create student user for testing
INSERT INTO users (username, password_hash, role, student_id) VALUES
('student1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.sUu.G', 'student', 1);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teachers_updated_at BEFORE UPDATE ON teachers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_attendance_updated_at BEFORE UPDATE ON attendance
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); 