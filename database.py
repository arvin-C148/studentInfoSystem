from supabase import create_client, Client
from werkzeug.security import generate_password_hash
import bcrypt
from datetime import date, datetime
import json
from config import Config

class DatabaseService:
    def __init__(self):
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
    
    # User Management
    def create_user(self, username, password, role, student_id=None):
        """Create a new user in the database"""
        try:
            user_data = {
                'username': username,
                'password_hash': generate_password_hash(password),
                'role': role,
                'created_at': datetime.now().isoformat()
            }
            
            if student_id:
                user_data['student_id'] = student_id
            
            result = self.supabase.table('users').insert(user_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user(self, username):
        """Get user by username"""
        try:
            result = self.supabase.table('users').select('*').eq('username', username).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        user = self.get_user(username)
        if user and user['password_hash'].startswith('$2b$'):
            # bcrypt hash
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return user
        elif user and check_password_hash(user['password_hash'], password):
            # werkzeug hash (fallback)
            return user
        return None
    
    def get_all_users(self):
        """Get all users"""
        try:
            result = self.supabase.table('users').select('*').execute()
            return result.data
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    # Student Management
    def create_student(self, name, age, class_name, section, face_data=None):
        """Create a new student"""
        try:
            student_data = {
                'name': name,
                'age': age,
                'class': class_name,
                'section': section,
                'face_data': face_data,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('students').insert(student_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating student: {e}")
            return None
    
    def get_student(self, student_id):
        """Get student by ID"""
        try:
            result = self.supabase.table('students').select('*').eq('id', student_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting student: {e}")
            return None
    
    def get_all_students(self):
        """Get all students"""
        try:
            result = self.supabase.table('students').select('*').order('name').execute()
            return result.data
        except Exception as e:
            print(f"Error getting students: {e}")
            return []
    
    def update_student(self, student_id, **kwargs):
        """Update student information"""
        try:
            kwargs['updated_at'] = datetime.now().isoformat()
            result = self.supabase.table('students').update(kwargs).eq('id', student_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating student: {e}")
            return None
    
    def delete_student(self, student_id):
        """Delete a student"""
        try:
            result = self.supabase.table('students').delete().eq('id', student_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting student: {e}")
            return False
    
    # Teacher Management
    def create_teacher(self, name, subject):
        """Create a new teacher"""
        try:
            teacher_data = {
                'name': name,
                'subject': subject,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('teachers').insert(teacher_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating teacher: {e}")
            return None
    
    def get_teacher(self, teacher_id):
        """Get teacher by ID"""
        try:
            result = self.supabase.table('teachers').select('*').eq('id', teacher_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting teacher: {e}")
            return None
    
    def get_all_teachers(self):
        """Get all teachers"""
        try:
            result = self.supabase.table('teachers').select('*').order('name').execute()
            return result.data
        except Exception as e:
            print(f"Error getting teachers: {e}")
            return []
    
    def update_teacher(self, teacher_id, **kwargs):
        """Update teacher information"""
        try:
            kwargs['updated_at'] = datetime.now().isoformat()
            result = self.supabase.table('teachers').update(kwargs).eq('id', teacher_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating teacher: {e}")
            return None
    
    def delete_teacher(self, teacher_id):
        """Delete a teacher"""
        try:
            result = self.supabase.table('teachers').delete().eq('id', teacher_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting teacher: {e}")
            return False
    
    # Marks and Grades Management
    def save_marks(self, student_id, marks_data):
        """Save marks for a student"""
        try:
            # First, delete existing marks for this student
            self.supabase.table('marks').delete().eq('student_id', student_id).execute()
            
            # Insert new marks
            marks_records = []
            for subject, mark in marks_data.items():
                marks_records.append({
                    'student_id': student_id,
                    'subject': subject,
                    'mark': mark,
                    'created_at': datetime.now().isoformat()
                })
            
            if marks_records:
                result = self.supabase.table('marks').insert(marks_records).execute()
                return result.data
            return []
        except Exception as e:
            print(f"Error saving marks: {e}")
            return []
    
    def get_student_marks(self, student_id):
        """Get marks for a student"""
        try:
            result = self.supabase.table('marks').select('*').eq('student_id', student_id).execute()
            marks = {}
            for record in result.data:
                marks[record['subject']] = record['mark']
            return marks
        except Exception as e:
            print(f"Error getting marks: {e}")
            return {}
    
    def save_grades(self, student_id, grades_data):
        """Save grades for a student"""
        try:
            # First, delete existing grades for this student
            self.supabase.table('grades').delete().eq('student_id', student_id).execute()
            
            # Insert new grades
            grades_records = []
            for subject, grade in grades_data.items():
                grades_records.append({
                    'student_id': student_id,
                    'subject': subject,
                    'grade': grade,
                    'created_at': datetime.now().isoformat()
                })
            
            if grades_records:
                result = self.supabase.table('grades').insert(grades_records).execute()
                return result.data
            return []
        except Exception as e:
            print(f"Error saving grades: {e}")
            return []
    
    def get_student_grades(self, student_id):
        """Get grades for a student"""
        try:
            result = self.supabase.table('grades').select('*').eq('student_id', student_id).execute()
            grades = {}
            for record in result.data:
                grades[record['subject']] = record['grade']
            return grades
        except Exception as e:
            print(f"Error getting grades: {e}")
            return {}
    
    # Attendance Management
    def mark_attendance(self, student_id, date_str, face_data=None):
        """Mark attendance for a student"""
        try:
            # Check if attendance already exists for this date
            existing = self.supabase.table('attendance').select('*').eq('student_id', student_id).eq('date', date_str).execute()
            
            if existing.data:
                # Update existing attendance with new face data
                result = self.supabase.table('attendance').update({
                    'face_data': face_data,
                    'updated_at': datetime.now().isoformat()
                }).eq('student_id', student_id).eq('date', date_str).execute()
                return result.data[0] if result.data else None
            else:
                # Create new attendance record
                attendance_data = {
                    'student_id': student_id,
                    'date': date_str,
                    'face_data': face_data,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                result = self.supabase.table('attendance').insert(attendance_data).execute()
                return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error marking attendance: {e}")
            return None
    
    def get_student_attendance(self, student_id):
        """Get attendance records for a student"""
        try:
            result = self.supabase.table('attendance').select('*').eq('student_id', student_id).order('date', desc=True).execute()
            return [record['date'] for record in result.data]
        except Exception as e:
            print(f"Error getting attendance: {e}")
            return []
    
    def get_attendance_by_date(self, date_str):
        """Get all attendance records for a specific date"""
        try:
            result = self.supabase.table('attendance').select('*').eq('date', date_str).execute()
            return result.data
        except Exception as e:
            print(f"Error getting attendance by date: {e}")
            return []
    
    # Face Data Management
    def update_student_face(self, student_id, face_data):
        """Update student's face data"""
        try:
            result = self.supabase.table('students').update({
                'face_data': face_data,
                'updated_at': datetime.now().isoformat()
            }).eq('id', student_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating face data: {e}")
            return None
    
    def delete_student_face(self, student_id):
        """Delete student's face data"""
        try:
            result = self.supabase.table('students').update({
                'face_data': None,
                'updated_at': datetime.now().isoformat()
            }).eq('id', student_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error deleting face data: {e}")
            return None
    
    # Statistics and Reports
    def get_statistics(self):
        """Get system statistics"""
        try:
            # Get counts
            students_count = len(self.get_all_students())
            teachers_count = len(self.get_all_teachers())
            users_count = len(self.get_all_users())
            
            # Get students with face data
            students_with_face = self.supabase.table('students').select('id').not_.is_('face_data', 'null').execute()
            face_data_count = len(students_with_face.data)
            
            # Get attendance statistics
            attendance_count = self.supabase.table('attendance').select('id', count='exact').execute()
            total_attendance = attendance_count.count if attendance_count.count else 0
            
            return {
                'total_students': students_count,
                'total_teachers': teachers_count,
                'total_users': users_count,
                'students_with_face_data': face_data_count,
                'total_attendance_records': total_attendance
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def get_class_statistics(self, class_name, section):
        """Get statistics for a specific class"""
        try:
            # Get students in class
            students = self.supabase.table('students').select('*').eq('class', class_name).eq('section', section).execute()
            class_students = students.data
            
            if not class_students:
                return {}
            
            # Calculate statistics
            total_students = len(class_students)
            students_with_face = len([s for s in class_students if s.get('face_data')])
            
            # Get marks and grades for this class
            student_ids = [s['id'] for s in class_students]
            marks_data = self.supabase.table('marks').select('*').in_('student_id', student_ids).execute()
            grades_data = self.supabase.table('grades').select('*').in_('student_id', student_ids).execute()
            
            students_with_marks = len(set([m['student_id'] for m in marks_data.data]))
            students_with_grades = len(set([g['student_id'] for g in grades_data.data]))
            
            # Calculate average marks
            if marks_data.data:
                avg_marks = sum([m['mark'] for m in marks_data.data]) / len(marks_data.data)
            else:
                avg_marks = 0
            
            return {
                'class_name': class_name,
                'section': section,
                'total_students': total_students,
                'students_with_face_data': students_with_face,
                'students_with_marks': students_with_marks,
                'students_with_grades': students_with_grades,
                'average_marks': round(avg_marks, 2),
                'students': class_students
            }
        except Exception as e:
            print(f"Error getting class statistics: {e}")
            return {}

# Global database service instance
db = DatabaseService() 