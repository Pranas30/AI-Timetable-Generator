from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Teacher, SubjectEntry
import random # We'll use this to shuffle days

app = Flask(__name__)
app.secret_key = "your-super-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///timetable.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


@app.route('/')
def home():
    return render_template('login.html')


# ** NEW ROUTE TO SHOW THE REGISTER PAGE **
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')


# ** MODIFIED /register (POST) ROUTE **
@app.route('/register', methods=['POST'])
def register():
    
    name = request.form['name']
    department = request.form['department']
    password = request.form['password']

    hashed_pw = generate_password_hash(password)
    teacher = Teacher(name=name, department=department, password_hash=hashed_pw)
    db.session.add(teacher)
    db.session.commit()

    # ** MODIFIED: Log the user in immediately after registering **
    session['teacher_id'] = teacher.id
    flash("Registration successful! Welcome.", "success")
    
    # ** MODIFIED: Redirect to dashboard (your 'new page with 3 boxes') **
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['POST'])
def login():
    name = request.form['name']
    department = request.form['department']
    password = request.form['password']

    teacher = Teacher.query.filter_by(name=name, department=department).first()

    if teacher and check_password_hash(teacher.password_hash, password):
        session['teacher_id'] = teacher.id
        flash(f"Welcome back, {teacher.name}!", "success")
        # ** This correctly takes you to the dashboard as you wanted **
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid login details.", "error")
        return redirect(url_for('home'))


@app.route('/dashboard')
def dashboard():
    if 'teacher_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('home'))
        
    # ** MODIFIED: Get the teacher's info to display on the dashboard **
    # This was missing before, which would cause an error on the template
    teacher = db.session.get(Teacher, session['teacher_id'])
    if not teacher:
        # Failsafe in case session is valid but teacher was deleted
        session.pop('teacher_id', None)
        flash("Could not find your user. Please log in again.", "error")
        return redirect(url_for('home'))

    return render_template('dashboard.html', teacher=teacher)

def create_empty_grid():
    """Helper function to create a blank grid structure."""
    return {
        "Monday": [None] * 7,
        "Tuesday": [None] * 7,
        "Wednesday": [None] * 7,
        "Thursday": [None] * 7,
        "Friday": [None] * 7,
        "Saturday": [None] * 4  # Saturday half-day
    }


#
# REPLACE your old generate_timetable function with this one
#
#
# REPLACE your old generate_timetable function with this new one
#
def generate_timetable():
    # 1. Define your grid structure
    period_timings = [
        "8:30 - 9:25", "9:25 - 10:20", "10:35 - 11:30", "11:30 - 12:25",
        "1:15 - 2:10", "2:10 - 3:05", "3:05 - 4:00"
    ]
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    # 2. Fetch ALL subjects from the DB
    subjects = SubjectEntry.query.all()
    
    # 3. Create "booking schedules"
    all_teachers = list(set(
        sub.teacher_name.strip().title() 
        for sub in subjects if sub.teacher_name.strip()
    ))
    all_semesters = list(set(sub.semester for sub in subjects))

    teacher_schedule = {teacher: create_empty_grid() for teacher in all_teachers}
    semester_schedule = {sem: create_empty_grid() for sem in all_semesters}
    final_grids = {sem: create_empty_grid() for sem in all_semesters}

    # 4. Create the full list of "classes to be scheduled"
    classes_to_schedule = []
    for sub in subjects:
        normalized_tname = sub.teacher_name.strip().title()
        if not normalized_tname:
            continue
        
        class_details = {
            'subject_obj': sub,
            'teacher': normalized_tname,
            'semester': sub.semester,
            'priority': sub.priority
        }
        
        for _ in range(sub.hours_per_week):
            classes_to_schedule.append(class_details.copy()) 

    # 5. Sort the list by priority
    classes_to_schedule.sort(key=lambda x: x['priority'])

    # 6. The V3 Placement Loop (with consecutive check)
    unplaced_classes = [] 

    for class_to_place in classes_to_schedule:
        placed = False
        
        teacher = class_to_place['teacher']
        semester = class_to_place['semester']
        original_subject_obj = class_to_place['subject_obj']

        random.shuffle(days_of_week) 
        
        for day in days_of_week:
            if placed: break
            
            num_periods = len(semester_schedule[semester][day])
            
            for period_index in range(num_periods):
                
                # --- !! CHECK 1 & 2: Teacher & Semester Free !! ---
                is_teacher_free = not teacher_schedule[teacher][day][period_index]
                is_semester_free = not semester_schedule[semester][day][period_index]

                # --- !! NEW CHECK 3: Not Consecutive !! ---
                is_consecutive = False
                if period_index > 0: # Can't be consecutive if it's the first period
                    # Get the class from the PREVIOUS slot *for this semester*
                    previous_class_obj = final_grids[semester][day][period_index - 1]
                    
                    if previous_class_obj:
                        # Get the normalized name of the previous teacher
                        previous_teacher_name = previous_class_obj.teacher_name.strip().title()
                        if previous_teacher_name == teacher:
                            is_consecutive = True # Found a consecutive class!

                # --- !! FINAL PLACEMENT !! ---
                if is_teacher_free and is_semester_free and not is_consecutive:
                    
                    # Book the resources
                    teacher_schedule[teacher][day][period_index] = True
                    semester_schedule[semester][day][period_index] = True
                    
                    # Place the class in the final grid
                    final_grids[semester][day][period_index] = original_subject_obj 
                    
                    placed = True
                    break # Move to the next class
        
        if not placed:
            unplaced_classes.append(original_subject_obj)

    if unplaced_classes:
        subjects = ", ".join(list(set(c.subject_name for c in unplaced_classes)))
        flash(f"Warning: Could not find slots for all classes. Unplaced subjects: {subjects}", "error")

    return final_grids, period_timings


@app.route('/save_subjects', methods=['POST'])
def save_subjects():
    if 'teacher_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('home'))
        
    teacher_info = db.session.get(Teacher, session['teacher_id'])
    current_department = teacher_info.department if teacher_info else 'Unknown'

    semesters = ['Sem1', 'Sem2', 'Sem3']
    new_subjects_to_add = []
    
    for sem in semesters:
        subjects = request.form.getlist(f'{sem}_subject_name')
        codes = request.form.getlist(f'{sem}_subject_code')
        priorities = request.form.getlist(f'{sem}_priority')
        teachers = request.form.getlist(f'{sem}_teacher_name')
        hours_list = request.form.getlist(f'{sem}_hours_per_week') 

        for sname, scode, prio, tname, hours in zip(subjects, codes, priorities, teachers, hours_list):
            if sname.strip() and hours.strip():
                
                # --- !! THE REAL FIX !! ---
                # Cleans all whitespace AND normalizes case
                # "  shashi " -> "Shashi"
                normalized_tname = tname.strip().title()

                entry = SubjectEntry(
                    semester=sem,
                    subject_name=sname.strip(),
                    subject_code=scode.strip(),
                    priority=int(prio) if prio else 1,
                    teacher_name=normalized_tname, # Use the clean name
                    hours_per_week=int(hours)
                )
                new_subjects_to_add.append(entry)

    # Overwrite old subjects for these semesters
    SubjectEntry.query.filter(SubjectEntry.semester.in_(semesters)).delete()
    db.session.commit()
    
    # Add all the new subjects
    db.session.add_all(new_subjects_to_add)
    db.session.commit() 

    flash("Subjects saved! Generating all timetables...", "success")
    generated_grids, period_timings = generate_timetable()
    
    return render_template(
        'timetable.html', 
        generated_grids=generated_grids,
        timings=period_timings,
        semesters=list(generated_grids.keys())
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)