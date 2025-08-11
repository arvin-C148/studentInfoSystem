from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import cv2
import numpy as np
from datetime import date
import base64
import os
from config import Config
from database import db

app = Flask(__name__)
app.config.from_object(Config)

# Helper functions for ID generation (no longer needed with database)
def get_next_student_id():
    students = db.get_all_students()
    return max([s['id'] for s in students], default=0) + 1

def get_next_teacher_id():
    teachers = db.get_all_teachers()
    return max([t['id'] for t in teachers], default=0) + 1

# Student Management (CRUD)
@app.route('/students')
def list_students():
    if session.get('role') not in ['principal', 'teacher']:
        return redirect(url_for('login'))
    students = db.get_all_students()
    return render_template('students.html', students=students, role=session.get('role'))

@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    if session.get('role') not in ['principal', 'teacher']:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_student = db.create_student(
            name=request.form['name'],
            age=int(request.form['age']),
            class_name=request.form['class'],
            section=request.form['section']
        )
        if new_student:
            flash('Student added successfully!', 'success')
        else:
            flash('Error adding student. Please try again.', 'danger')
        return redirect(url_for('list_students'))
    return render_template('student_form.html', action='Add')

@app.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if session.get('role') not in ['principal', 'teacher']:
        return redirect(url_for('login'))
    student = db.get_student(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('list_students'))
    if request.method == 'POST':
        updated_student = db.update_student(
            student_id,
            name=request.form['name'],
            age=int(request.form['age']),
            class_name=request.form['class'],
            section=request.form['section']
        )
        if updated_student:
            flash('Student updated successfully!', 'success')
        else:
            flash('Error updating student. Please try again.', 'danger')
        return redirect(url_for('list_students'))
    return render_template('student_form.html', action='Edit', student=student)

@app.route('/students/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if session.get('role') not in ['principal', 'teacher']:
        return redirect(url_for('login'))
    if db.delete_student(student_id):
        flash('Student deleted successfully!', 'success')
    else:
        flash('Error deleting student. Please try again.', 'danger')
    return redirect(url_for('list_students'))

# Teacher Management (CRUD, principal only)
@app.route('/teachers')
def list_teachers():
    if session.get('role') != 'principal':
        return redirect(url_for('login'))
    teachers = db.get_all_teachers()
    return render_template('teachers.html', teachers=teachers)

@app.route('/teachers/add', methods=['GET', 'POST'])
def add_teacher():
    if session.get('role') != 'principal':
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_teacher = db.create_teacher(
            name=request.form['name'],
            subject=request.form['subject']
        )
        if new_teacher:
            flash('Teacher added successfully!', 'success')
        else:
            flash('Error adding teacher. Please try again.', 'danger')
        return redirect(url_for('list_teachers'))
    return render_template('teacher_form.html', action='Add')

@app.route('/teachers/edit/<int:teacher_id>', methods=['GET', 'POST'])
def edit_teacher(teacher_id):
    if session.get('role') != 'principal':
        return redirect(url_for('login'))
    teacher = db.get_teacher(teacher_id)
    if not teacher:
        flash('Teacher not found.', 'danger')
        return redirect(url_for('list_teachers'))
    if request.method == 'POST':
        updated_teacher = db.update_teacher(
            teacher_id,
            name=request.form['name'],
            subject=request.form['subject']
        )
        if updated_teacher:
            flash('Teacher updated successfully!', 'success')
        else:
            flash('Error updating teacher. Please try again.', 'danger')
        return redirect(url_for('list_teachers'))
    return render_template('teacher_form.html', action='Edit', teacher=teacher)

@app.route('/teachers/delete/<int:teacher_id>', methods=['POST'])
def delete_teacher(teacher_id):
    if session.get('role') != 'principal':
        return redirect(url_for('login'))
    if db.delete_teacher(teacher_id):
        flash('Teacher deleted successfully!', 'success')
    else:
        flash('Error deleting teacher. Please try again.', 'danger')
    return redirect(url_for('list_teachers'))

# Route for teacher to select class and section
@app.route('/marks/select', methods=['GET', 'POST'])
def select_class_section():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    students = db.get_all_students()
    classes = sorted(set(s['class'] for s in students))
    sections = sorted(set(s['section'] for s in students))
    if request.method == 'POST':
        selected_class = request.form['class']
        selected_section = request.form['section']
        return redirect(url_for('enter_marks', class_name=selected_class, section=selected_section))
    return render_template('select_class_section.html', classes=classes, sections=sections)

# Route to enter marks and grades for students in a class/section
@app.route('/marks/enter/<class_name>/<section>', methods=['GET', 'POST'])
def enter_marks(class_name, section):
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    students = db.get_all_students()
    filtered_students = [s for s in students if s['class'] == class_name and s['section'] == section]
    teachers = db.get_all_teachers()
    subjects = [t['subject'] for t in teachers]  # All subjects in system
    if request.method == 'POST':
        for student in filtered_students:
            marks = {}
            grades = {}
            for subject in subjects:
                mark_key = f"marks_{student['id']}_{subject}"
                mark_val = request.form.get(mark_key)
                if mark_val is not None and mark_val != '':
                    try:
                        mark = int(mark_val)
                        marks[subject] = mark
                        # Grade per subject
                        if mark >= 90:
                            grade = 'A'
                        elif mark >= 80:
                            grade = 'B'
                        elif mark >= 70:
                            grade = 'C'
                        elif mark >= 60:
                            grade = 'D'
                        elif mark >= 40:
                            grade = 'E'
                        else:
                            grade = 'F'
                        grades[subject] = grade
                    except ValueError:
                        pass
            
            # Save marks and grades to database
            if marks:
                db.save_marks(student['id'], marks)
            if grades:
                db.save_grades(student['id'], grades)
        
        flash('Marks and grades updated!', 'success')
        return redirect(url_for('list_students'))
    return render_template('enter_marks.html', students=filtered_students, subjects=subjects, class_name=class_name, section=section)

@app.route('/')
def index():
    if 'username' in session:
        role = session.get('role')
        if role == 'principal':
            return redirect(url_for('dashboard_principal'))
        elif role == 'teacher':
            return redirect(url_for('dashboard_teacher'))
        elif role == 'student':
            return redirect(url_for('dashboard_student'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.verify_user(username, password)
        if user:
            session['username'] = username
            session['role'] = user['role']
            if user['role'] == 'principal':
                return redirect(url_for('dashboard_principal'))
            elif user['role'] == 'teacher':
                return redirect(url_for('dashboard_teacher'))
            elif user['role'] == 'student':
                return redirect(url_for('dashboard_student'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard/principal')
def dashboard_principal():
    if session.get('role') != 'principal':
        return redirect(url_for('login'))
    students = db.get_all_students()
    teachers = db.get_all_teachers()
    return render_template('dashboard_principal.html', username=session.get('username'), students=students, teachers=teachers)

@app.route('/dashboard/teacher')
def dashboard_teacher():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    students = db.get_all_students()
    return render_template('dashboard_teacher.html', username=session.get('username'), students=students)

@app.route('/dashboard/student')
def dashboard_student():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    # Find the student record for this user
    user = db.get_user(session['username'])
    if user and user.get('student_id'):
        student = db.get_student(user['student_id'])
        if student:
            # Get marks and grades for this student
            marks = db.get_student_marks(student['id'])
            grades = db.get_student_grades(student['id'])
            attendance = db.get_student_attendance(student['id'])
            
            # Add marks, grades, and attendance to student data
            student['marks'] = marks
            student['grades'] = grades
            student['attendance'] = attendance
            
            return render_template('dashboard_student.html', student=student, username=session.get('username'))
    flash('Student data not found.', 'danger')
    return redirect(url_for('login'))

@app.route('/attendance/mark', methods=['GET', 'POST'])
def mark_attendance():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    
    user = db.get_user(session['username'])
    if not user or not user.get('student_id'):
        flash('Student data not found.', 'danger')
        return redirect(url_for('dashboard_student'))
    
    student = db.get_student(user['student_id'])
    if not student:
        flash('Student data not found.', 'danger')
        return redirect(url_for('dashboard_student'))
    
    today = date.today().isoformat()
    if request.method == 'POST':
        # Get the face image data from the form
        face_data = request.form.get('face_data')
        print(f"Received face data length: {len(face_data) if face_data else 0}")
        
        if face_data and len(face_data) > 100:  # Basic check that we have actual image data
            try:
                # Mark attendance in database
                attendance_record = db.mark_attendance(student['id'], today, face_data)
                
                if attendance_record:
                    flash('Attendance marked successfully! Face image captured and stored.', 'success')
                    print(f"Attendance marked for student {student['name']} on {today}")
                else:
                    flash('Error marking attendance. Please try again.', 'danger')
            except Exception as e:
                print(f"Error processing attendance: {e}")
                flash('Error processing attendance. Please try again.', 'danger')
        else:
            flash('No valid face image captured. Please ensure your camera is working and try again.', 'danger')
            print("No valid face data received")
        return redirect(url_for('dashboard_student'))
    return render_template('mark_attendance.html', student=student, today=today)

# Face Management Routes for Teachers
@app.route('/faces/manage', methods=['GET', 'POST'])
def manage_student_faces():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    
    students = db.get_all_students()
    classes = sorted(set(s['class'] for s in students))
    sections = sorted(set(s['section'] for s in students))
    
    if request.method == 'POST':
        selected_class = request.form.get('class')
        selected_section = request.form.get('section')
        if selected_class and selected_section:
            filtered_students = [s for s in students if s['class'] == selected_class and s['section'] == selected_section]
            return render_template('manage_faces.html', 
                                students=filtered_students, 
                                classes=classes, 
                                sections=sections,
                                selected_class=selected_class,
                                selected_section=selected_section)
    
    return render_template('manage_faces.html', 
                         students=[], 
                         classes=classes, 
                         sections=sections,
                         selected_class=None,
                         selected_section=None)

@app.route('/faces/view/<int:student_id>')
def view_student_face(student_id):
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    
    student = db.get_student(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('manage_student_faces'))
    
    return render_template('view_student_face.html', student=student)

@app.route('/faces/delete/<int:student_id>', methods=['POST'])
def delete_student_face(student_id):
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
    
    student = db.get_student(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('manage_student_faces'))
    
    updated_student = db.delete_student_face(student_id)
    if updated_student:
        flash('Student face data deleted successfully!', 'success')
    else:
        flash('Error deleting face data. Please try again.', 'danger')
    
    # Get the referrer to redirect back to the appropriate page
    referrer = request.referrer
    if referrer and 'view_student_face' in referrer:
        return redirect(url_for('manage_student_faces'))
    else:
        return redirect(url_for('manage_student_faces'))

# Reporting Routes
@app.route('/reports')
def reports_dashboard():
    if session.get('role') not in ['principal', 'teacher']:
        return redirect(url_for('login'))
    
    # Get statistics from database
    stats = db.get_statistics()
    students = db.get_all_students()
    classes = sorted(set(s['class'] for s in students))
    sections = sorted(set(s['section'] for s in students))
    
    stats.update({
        'total_classes': len(classes),
        'total_sections': len(sections),
        'classes': classes,
        'sections': sections
    })
    
    return render_template('reports_dashboard.html', stats=stats, username=session.get('username'))

@app.route('/reports/student/<int:student_id>')
def student_report(student_id):
    if session.get('role') not in ['principal', 'teacher']:
        return redirect(url_for('login'))
    
    student = db.get_student(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('reports_dashboard'))
    
    # Get marks, grades, and attendance for this student
    marks = db.get_student_marks(student_id)
    grades = db.get_student_grades(student_id)
    attendance = db.get_student_attendance(student_id)
    
    # Calculate attendance percentage
    total_days = 30  # Assuming 30 school days in a month
    attendance_percentage = (len(attendance) / total_days) * 100 if total_days > 0 else 0
    
    # Calculate average marks
    if marks:
        average_marks = sum(marks.values()) / len(marks)
    else:
        average_marks = 0
    
    # Generate grade distribution
    grade_distribution = {}
    if grades:
        for grade in grades.values():
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
    
    report_data = {
        'student': student,
        'attendance_percentage': round(attendance_percentage, 2),
        'average_marks': round(average_marks, 2),
        'grade_distribution': grade_distribution,
        'total_subjects': len(marks) if marks else 0,
        'total_attendance_days': len(attendance)
    }
    
    return render_template('student_report.html', report_data=report_data, username=session.get('username'))

@app.route('/reports/class/<class_name>/<section>')
def class_report(class_name, section):
    if session.get('role') not in ['principal', 'teacher']:
        return redirect(url_for('login'))
    
    class_stats = db.get_class_statistics(class_name, section)
    
    if not class_stats:
        flash('No students found in this class.', 'danger')
        return redirect(url_for('reports_dashboard'))
    
    return render_template('class_report.html', class_stats=class_stats, username=session.get('username'))

@app.route('/reports/attendance')
def attendance_report():
    if session.get('role') not in ['principal', 'teacher']:
        return redirect(url_for('login'))
    
    # Get filter parameters
    selected_class = request.args.get('class')
    selected_section = request.args.get('section')
    
    students = db.get_all_students()
    classes = sorted(set(s['class'] for s in students))
    sections = sorted(set(s['section'] for s in students))
    
    # Filter students based on selection
    filtered_students = students
    if selected_class:
        filtered_students = [s for s in filtered_students if s['class'] == selected_class]
    if selected_section:
        filtered_students = [s for s in filtered_students if s['section'] == selected_section]
    
    # Calculate attendance statistics
    attendance_data = []
    for student in filtered_students:
        attendance = db.get_student_attendance(student['id'])
        attendance_days = len(attendance)
        attendance_percentage = (attendance_days / 30) * 100  # Assuming 30 school days
        attendance_data.append({
            'student': student,
            'attendance_days': attendance_days,
            'attendance_percentage': round(attendance_percentage, 2),
            'has_face_data': bool(student.get('face_data'))
        })
    
    # Sort by attendance percentage (descending)
    attendance_data.sort(key=lambda x: x['attendance_percentage'], reverse=True)
    
    return render_template('attendance_report.html', 
                         attendance_data=attendance_data,
                         classes=classes,
                         sections=sections,
                         selected_class=selected_class,
                         selected_section=selected_section,
                         username=session.get('username'))

@app.route('/reports/academic')
def academic_report():
    if session.get('role') not in ['principal', 'teacher']:
        return redirect(url_for('login'))
    
    # Get filter parameters
    selected_class = request.args.get('class')
    selected_section = request.args.get('section')
    
    students = db.get_all_students()
    classes = sorted(set(s['class'] for s in students))
    sections = sorted(set(s['section'] for s in students))
    
    # Filter students based on selection
    filtered_students = students
    if selected_class:
        filtered_students = [s for s in filtered_students if s['class'] == selected_class]
    if selected_section:
        filtered_students = [s for s in filtered_students if s['section'] == selected_section]
    
    # Calculate academic statistics
    academic_data = []
    for student in filtered_students:
        marks = db.get_student_marks(student['id'])
        grades = db.get_student_grades(student['id'])
        
        if marks:
            avg_marks = sum(marks.values()) / len(marks)
            total_subjects = len(marks)
        else:
            avg_marks = 0
            total_subjects = 0
        
        if grades:
            grade_count = len(grades)
        else:
            grade_count = 0
        
        academic_data.append({
            'student': student,
            'avg_marks': round(avg_marks, 2),
            'total_subjects': total_subjects,
            'grade_count': grade_count,
            'has_marks': bool(marks),
            'has_grades': bool(grades)
        })
    
    # Sort by average marks (descending)
    academic_data.sort(key=lambda x: x['avg_marks'], reverse=True)
    
    return render_template('academic_report.html', 
                         academic_data=academic_data,
                         classes=classes,
                         sections=sections,
                         selected_class=selected_class,
                         selected_section=selected_section,
                         username=session.get('username'))

@app.route('/ai/academic-stats', methods=['GET', 'POST'])
def ai_academic_stats():
    if session.get('role') not in ['principal', 'teacher']:
        return redirect(url_for('login'))
    
    # Get filter parameters
    selected_class = request.args.get('class')
    selected_section = request.args.get('section')
    selected_student = request.args.get('student_id')
    
    students = db.get_all_students()
    classes = sorted(set(s['class'] for s in students))
    sections = sorted(set(s['section'] for s in students))
    
    # Filter students based on selection
    filtered_students = students
    if selected_class:
        filtered_students = [s for s in filtered_students if s['class'] == selected_class]
    if selected_section:
        filtered_students = [s for s in filtered_students if s['section'] == selected_section]
    
    ai_insights = {}
    selected_student_data = None
    
    if selected_student:
        # Get detailed data for selected student
        student = db.get_student(int(selected_student))
        if student:
            marks = db.get_student_marks(student['id'])
            grades = db.get_student_grades(student['id'])
            attendance = db.get_student_attendance(student['id'])
            
            # Calculate comprehensive statistics
            if marks:
                avg_marks = sum(marks.values()) / len(marks)
                max_marks = max(marks.values())
                min_marks = min(marks.values())
                subject_performance = marks
            else:
                avg_marks = 0
                max_marks = 0
                min_marks = 0
                subject_performance = {}
            
            attendance_days = len(attendance) if attendance else 0
            attendance_percentage = (attendance_days / 30) * 100  # Assuming 30 school days
            
            # Generate AI insights
            ai_insights = generate_ai_insights(student, marks, grades, attendance, avg_marks, attendance_percentage)
            
            selected_student_data = {
                'student': student,
                'avg_marks': round(avg_marks, 2),
                'max_marks': max_marks,
                'min_marks': min_marks,
                'subject_performance': subject_performance,
                'attendance_days': attendance_days,
                'attendance_percentage': round(attendance_percentage, 2),
                'grades': grades if grades else {},
                'ai_insights': ai_insights
            }
    
    # Calculate class-wide statistics for comparison
    class_stats = {}
    if filtered_students:
        all_marks = []
        all_attendance = []
        
        for student in filtered_students:
            marks = db.get_student_marks(student['id'])
            attendance = db.get_student_attendance(student['id'])
            
            if marks:
                all_marks.extend(marks.values())
            if attendance:
                all_attendance.append(len(attendance))
        
        if all_marks:
            class_stats['avg_class_marks'] = round(sum(all_marks) / len(all_marks), 2)
            class_stats['max_class_marks'] = max(all_marks)
            class_stats['min_class_marks'] = min(all_marks)
        
        if all_attendance:
            class_stats['avg_attendance'] = round(sum(all_attendance) / len(all_attendance), 2)
    
    return render_template('ai_academic_stats.html',
                         students=filtered_students,
                         classes=classes,
                         sections=sections,
                         selected_class=selected_class,
                         selected_section=selected_section,
                         selected_student_data=selected_student_data,
                         class_stats=class_stats,
                         username=session.get('username'))

def generate_ai_insights(student, marks, grades, attendance, avg_marks, attendance_percentage):
    """Generate AI-powered insights for student performance"""
    insights = {
        'performance_level': '',
        'strengths': [],
        'weaknesses': [],
        'recommendations': [],
        'trend_analysis': '',
        'attendance_impact': '',
        'overall_assessment': ''
    }
    
    # Performance Level Analysis
    if avg_marks >= 90:
        insights['performance_level'] = 'Excellent'
        insights['overall_assessment'] = f"{student['name']} is performing exceptionally well with an average of {avg_marks}%. This student demonstrates strong academic capabilities."
    elif avg_marks >= 80:
        insights['performance_level'] = 'Good'
        insights['overall_assessment'] = f"{student['name']} is performing well with an average of {avg_marks}%. There's room for improvement but overall solid performance."
    elif avg_marks >= 70:
        insights['performance_level'] = 'Average'
        insights['overall_assessment'] = f"{student['name']} has average performance with {avg_marks}%. This student needs additional support to improve."
    elif avg_marks >= 60:
        insights['performance_level'] = 'Below Average'
        insights['overall_assessment'] = f"{student['name']} is struggling academically with {avg_marks}%. Immediate intervention is recommended."
    else:
        insights['performance_level'] = 'Needs Improvement'
        insights['overall_assessment'] = f"{student['name']} requires significant academic support with {avg_marks}%. Urgent attention needed."
    
    # Subject-specific analysis
    if marks:
        best_subject = max(marks.items(), key=lambda x: x[1])
        worst_subject = min(marks.items(), key=lambda x: x[1])
        
        if best_subject[1] >= 85:
            insights['strengths'].append(f"Excels in {best_subject[0]} with {best_subject[1]}%")
        elif best_subject[1] >= 75:
            insights['strengths'].append(f"Shows potential in {best_subject[0]} with {best_subject[1]}%")
        
        if worst_subject[1] < 70:
            insights['weaknesses'].append(f"Struggles in {worst_subject[0]} with {worst_subject[1]}%")
            insights['recommendations'].append(f"Provide additional support in {worst_subject[0]}")
        
        # Subject distribution analysis
        high_performing_subjects = [subject for subject, score in marks.items() if score >= 80]
        low_performing_subjects = [subject for subject, score in marks.items() if score < 70]
        
        if len(high_performing_subjects) > len(low_performing_subjects):
            insights['trend_analysis'] = "Student shows consistent performance across most subjects"
        elif len(low_performing_subjects) > len(high_performing_subjects):
            insights['trend_analysis'] = "Student needs improvement in multiple subjects"
        else:
            insights['trend_analysis'] = "Mixed performance across subjects"
    
    # Attendance impact analysis
    if attendance_percentage >= 95:
        insights['attendance_impact'] = "Excellent attendance - this positively contributes to academic performance"
    elif attendance_percentage >= 85:
        insights['attendance_impact'] = "Good attendance - consistent presence supports learning"
    elif attendance_percentage >= 75:
        insights['attendance_impact'] = "Moderate attendance - irregular attendance may affect performance"
    else:
        insights['attendance_impact'] = "Poor attendance - this significantly impacts academic performance"
        insights['recommendations'].append("Address attendance issues to improve academic outcomes")
    
    # Additional recommendations based on performance
    if avg_marks < 75:
        insights['recommendations'].append("Consider additional tutoring or remedial classes")
        insights['recommendations'].append("Implement regular progress monitoring")
    
    if attendance_percentage < 80:
        insights['recommendations'].append("Develop attendance improvement plan")
    
    if not insights['recommendations']:
        insights['recommendations'].append("Continue current academic support strategies")
        insights['recommendations'].append("Encourage participation in advanced learning opportunities")
    
    return insights

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG']) 