"""
CampusDeck - Main Flask Application Backend
--------------------------------------------------------------------------
This is the main Python script for our college web application.
It runs a Flask web server, handles user login/register sessions, and acts as
the backend by saving and loading data to simple local JSON files.

=== EDUCATIONAL ARCHITECTURE EXPLANATIONS ===

1. FLASK ROUTES (@app.route):
   Flask uses decorators like `@app.route('/')` to connect browser URLs to Python functions.
   When a user goes to a URL, Flask runs the matching function and returns HTML or redirects.

2. TEMPLATE RENDERING (render_template):
   We return HTML files using `render_template('index.html')`. Flask compiles these using
   the Jinja2 engine, replacing template tags like {{ stats.cgpa }} with actual variables.

3. SESSIONS & COOKIES (session):
   We use the `session` dictionary to keep users logged in. Flask signs session cookies
   with our `app.secret_key` so the browser cannot tamper with them.

4. DATABASE OPERATION (load_data / save_data):
   Instead of SQL, we use simple JSON text files. Python's `json` library translates these
   text files directly into standard Python lists and dictionaries we can easily append to.
"""

import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

# 1. Initialize Flask
# ------------------
# Creates our web application object. Flask uses __name__ to find static/templates directories.
app = Flask(__name__)

# Secret key is required to securely encrypt cookies for session state tracking and flash alert messages.
app.secret_key = 'campusdeck_student_portfolio_secret_key'

# 2. Database File Configurations
# ------------------------------
# Define the absolute directory where our data folder resides
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Create the data directory folder if it is missing
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 3. Database Helper Functions
# ----------------------------
def load_data(filename):
    """
    JSON Read Function:
    Loads a JSON database file and returns its data as a Python list.
    If the file does not exist, it creates it with an empty list [].
    """
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        # Create file with an empty list if it's missing
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4)
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If the file is corrupted or empty, reset it to an empty list
        return []

def save_data(filename, data):
    """
    JSON Write Function:
    Saves a Python list/dictionary to a JSON file.
    This overwrites the previous file content with the updated database state.
    """
    file_path = os.path.join(DATA_DIR, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def calculate_deadline_info(date_str, item_status):
    """
    Smart Deadline Visibility Logic.
    Calculates the days remaining until a deadline and returns a color label and human-readable text.
    """
    if item_status == 'Completed':
        return {'label': 'Completed', 'color': 'deadline-muted', 'days': -1}
    
    if not date_str:
        return {'label': 'No deadline', 'color': 'default', 'days': 9999}
        
    try:
        # Assuming date format is YYYY-MM-DD
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        days_left = (target_date - today).days
        
        if days_left < 0:
            return {'label': 'Overdue', 'color': 'deadline-red', 'days': days_left}
        elif days_left == 0:
            return {'label': 'Due Today', 'color': 'deadline-red', 'days': days_left}
        elif days_left == 1:
            return {'label': 'Due Tomorrow', 'color': 'deadline-red', 'days': days_left}
        elif days_left <= 3:
            return {'label': f'Due in {days_left} Days', 'color': 'deadline-red', 'days': days_left}
        elif days_left <= 7:
            return {'label': f'Due in {days_left} Days', 'color': 'deadline-orange', 'days': days_left}
        else:
            return {'label': f'Due in {days_left} Days', 'color': 'default', 'days': days_left}
    except ValueError:
        return {'label': 'Invalid date', 'color': 'default', 'days': 9999}

# =========================================================================
# Flask Router & Route Handlers
# =========================================================================

@app.route('/')
def index():
    """
    Landing Page Route:
    Renders the homepage. This route accepts default GET requests to view the page.
    """
    return render_template('index.html')

# -------------------------------------------------------------------------
# User Authentication Section (Register, Login, Logout)
# -------------------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    User Registration:
    - GET: User clicks "Register" link. We show register.html.
    - POST: User submits registration form. We validate and save user data.
    """
    # If the user is already logged in, redirect them directly to their dashboard
    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    # Check if the form was submitted (which sends a POST request)
    if request.method == 'POST':
        # Retrieve form values using their HTML 'name' attribute
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Simple validation: ensure no empty fields
        if not name or not email or not password or not confirm_password:
            flash('All registration fields are required!', 'error')
            return redirect(url_for('register'))

        # Ensure passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))

        users = load_data('users.json')
        # Check if email is already taken
        if any(u.get('email') == email for u in users):
            flash('An account with this email is already registered!', 'error')
            return redirect(url_for('register'))

        # Encrypt (hash) the password. We never save raw plain-text passwords!
        hashed_pw = generate_password_hash(password)
        new_user = {
            'id': str(uuid.uuid4()), # Generate a unique ID string for this user
            'name': name,
            'email': email,
            'password': hashed_pw
        }
        users.append(new_user)
        save_data('users.json', users)

        # Log the user in automatically by saving their ID in the secure session cookie
        session['user_id'] = new_user['id']
        session['user_name'] = new_user['name']
        flash('Account created successfully! Welcome to your dashboard.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User Sign-In:
    - GET: User goes to /login. We render the login page.
    - POST: User submits credentials. We verify passwords using security checks.
    """
    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please fill in both fields!', 'error')
            return redirect(url_for('login'))

        users = load_data('users.json')
        # Find user dictionary by matching email
        user = next((u for u in users if u.get('email') == email), None)

        # Verify hashed password using Werkzeug security utility
        if user and check_password_hash(user['password'], password):
            # Save user session details in cookie
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash(f"Welcome back, {user['name']}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again!', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    User Sign-Out:
    Clears the session cookie data, logging the user out.
    """
    # Delete all session keys
    session.clear()
    flash('You have successfully signed out.', 'success')
    return redirect(url_for('index'))

# -------------------------------------------------------------------------
# Dashboard Section (Protected)
# -------------------------------------------------------------------------

@app.route('/dashboard')
def dashboard():
    """
    Dashboard Home:
    Aggregates user-specific metrics and displays previews of logs/notes.
    """
    # Guard check: redirect user if they are not logged in
    if not session.get('user_id'):
        flash('Please sign in to access your dashboard!', 'error')
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    # Load records and filter so users only see their own marks/goals/etc.
    goals = [g for g in load_data('goals.json') if g.get('user_id') == user_id]
    resources = [r for r in load_data('resources.json') if r.get('user_id') == user_id]
    opportunities = [o for o in load_data('opportunities.json') if o.get('user_id') == user_id]
    notes = [n for n in load_data('notes.json') if n.get('user_id') == user_id]
    marks = [m for m in load_data('marks.json') if m.get('user_id') == user_id]

    # Calculate Cumulative GPA (CGPA) based on GPA Tracker marks
    total_gp_credits = sum(float(m.get('gp', 0)) * float(m.get('credits', 0)) for m in marks)
    total_credits = sum(float(m.get('credits', 0)) for m in marks)
    cgpa = total_gp_credits / total_credits if total_credits > 0 else 0.0

    # Package metric numbers into a statistics dictionary
    stats = {
        'total_goals': len(goals),
        'total_resources': len(resources),
        'total_opportunities': len(opportunities),
        'cgpa': cgpa
    }

    # Fetch up to 3 most recent notes (newest first)
    recent_notes = sorted(notes, key=lambda x: x.get('created_at', ''), reverse=True)[:3]
    
    # Fetch up to 3 upcoming active goals
    active_goals = sorted([g for g in goals if g.get('status') != 'Completed'], key=lambda x: x.get('target_date', ''))[:3]

    # Smart Deadline - Aggregate Next 5 Upcoming Deadlines
    upcoming_items = []
    
    for g in goals:
        if g.get('status') != 'Completed' and g.get('target_date'):
            dl_info = calculate_deadline_info(g.get('target_date'), g.get('status'))
            if dl_info['days'] >= 0: # Only upcoming
                upcoming_items.append({
                    'title': g.get('title'),
                    'type': 'Goal',
                    'target_date': g.get('target_date'),
                    'days_left': dl_info['days'],
                    'deadline_info': dl_info
                })
            
    for o in opportunities:
        if o.get('status') != 'Completed' and o.get('deadline'):
            dl_info = calculate_deadline_info(o.get('deadline'), o.get('status'))
            if dl_info['days'] >= 0: # Only upcoming
                upcoming_items.append({
                    'title': o.get('name'),
                    'type': 'Opportunity',
                    'target_date': o.get('deadline'),
                    'days_left': dl_info['days'],
                    'deadline_info': dl_info
                })
            
    # Sort by closest deadline, take top 5
    upcoming_deadlines = sorted(upcoming_items, key=lambda x: x['days_left'])[:5]

    return render_template('dashboard.html', stats=stats, recent_notes=recent_notes, active_goals=active_goals, upcoming_deadlines=upcoming_deadlines)

# -------------------------------------------------------------------------
# Study Goals Section (Protected)
# -------------------------------------------------------------------------

@app.route('/goals', methods=['GET', 'POST'])
def goals():
    """
    Study Goals Route.
    """
    if not session.get('user_id'):
        flash('Please sign in to manage study goals!', 'error')
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    all_goals = load_data('goals.json')

    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        target_date = request.form.get('target_date')
        status = request.form.get('status', 'Not Started')
        description = request.form.get('description', '')
        priority = request.form.get('priority', 'Medium')
        progress = request.form.get('progress', '0')

        if not title or not category or not target_date:
            flash('Please fill out all required goal fields!', 'error')
            return redirect(url_for('goals'))
            
        try:
            progress_val = int(progress)
            if progress_val < 0 or progress_val > 100:
                progress_val = 0
        except ValueError:
            progress_val = 0

        new_goal = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,  # Link entry to logged-in user
            'title': title,
            'category': category,
            'target_date': target_date,
            'status': status,
            'description': description,
            'priority': priority,
            'progress': progress_val
        }

        # Save to database
        all_goals.append(new_goal)
        save_data('goals.json', all_goals)
        flash('New study goal added successfully!', 'success')
        return redirect(url_for('goals'))

    # Load and sort only user's goals
    user_goals = [g for g in all_goals if g.get('user_id') == user_id]
    
    # Add smart deadline labels
    for g in user_goals:
        g['deadline_info'] = calculate_deadline_info(g.get('target_date', ''), g.get('status', ''))
        
    user_goals = sorted(user_goals, key=lambda x: (x.get('status') == 'Completed', x.get('target_date', '')))
    return render_template('goals.html', goals=user_goals)

@app.route('/goals/toggle/<goal_id>', methods=['POST'])
def toggle_goal(goal_id):
    """
    Toggle Goal Status.
    """
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    all_goals = load_data('goals.json')
    
    for goal in all_goals:
        # Check both ID and ownership
        if goal['id'] == goal_id and goal.get('user_id') == user_id:
            current_status = goal.get('status', 'Not Started')
            if current_status == 'Not Started':
                goal['status'] = 'In Progress'
            elif current_status == 'In Progress':
                goal['status'] = 'Completed'
            else:
                goal['status'] = 'Not Started'
            break
    
    save_data('goals.json', all_goals)
    flash('Goal status updated!', 'success')
    return redirect(url_for('goals'))

@app.route('/goals/delete/<goal_id>', methods=['POST'])
def delete_goal(goal_id):
    """
    Delete Goal.
    """
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    all_goals = load_data('goals.json')
    # Filter out target goal only if it belongs to current user
    updated_list = [g for g in all_goals if not (g['id'] == goal_id and g.get('user_id') == user_id)]
    
    save_data('goals.json', updated_list)
    flash('Study goal deleted.', 'success')
    return redirect(url_for('goals'))

# -------------------------------------------------------------------------
# Resource Vault Section (Protected)
# -------------------------------------------------------------------------

@app.route('/resources', methods=['GET', 'POST'])
def resources():
    """
    Resource Vault Route.
    """
    if not session.get('user_id'):
        flash('Please sign in to access the Resource Vault!', 'error')
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    all_resources = load_data('resources.json')

    if request.method == 'POST':
        title = request.form.get('title')
        res_type = request.form.get('type')
        link = request.form.get('link')
        subject = request.form.get('subject')
        description = request.form.get('description')

        if not title or not res_type or not link or not subject:
            flash('Please fill out all required resource fields!', 'error')
            return redirect(url_for('resources'))

        if not link.startswith(('http://', 'https://')):
            link = 'https://' + link

        new_resource = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': title,
            'type': res_type,
            'link': link,
            'subject': subject,
            'description': description
        }

        all_resources.append(new_resource)
        save_data('resources.json', all_resources)
        flash('Resource saved successfully!', 'success')
        return redirect(url_for('resources'))

    user_resources = [r for r in all_resources if r.get('user_id') == user_id]
    return render_template('resources.html', resources=user_resources)

@app.route('/resources/delete/<resource_id>', methods=['POST'])
def delete_resource(resource_id):
    """
    Delete Resource.
    """
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    all_resources = load_data('resources.json')
    updated_list = [r for r in all_resources if not (r['id'] == resource_id and r.get('user_id') == user_id)]
    
    save_data('resources.json', updated_list)
    flash('Resource removed from vault.', 'success')
    return redirect(url_for('resources'))

# -------------------------------------------------------------------------
# Opportunity Tracker Section (Protected)
# -------------------------------------------------------------------------

@app.route('/opportunities', methods=['GET', 'POST'])
def opportunities():
    """
    Opportunity Tracker Route.
    """
    if not session.get('user_id'):
        flash('Please sign in to track opportunities!', 'error')
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    all_opps = load_data('opportunities.json')

    if request.method == 'POST':
        name = request.form.get('name')
        opp_type = request.form.get('type')
        deadline = request.form.get('deadline')
        status = request.form.get('status', 'Saved')
        link = request.form.get('link')
        notes = request.form.get('notes')
        category = request.form.get('category', 'Events') # Default if empty

        if not name or not opp_type or not deadline:
            flash('Opportunity name, type, and deadline are required!', 'error')
            return redirect(url_for('opportunities'))

        if link and not link.startswith(('http://', 'https://')):
            link = 'https://' + link

        new_opp = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': name,
            'type': opp_type,
            'deadline': deadline,
            'status': status,
            'link': link,
            'notes': notes,
            'category': category
        }

        all_opps.append(new_opp)
        save_data('opportunities.json', all_opps)
        flash('Opportunity tracked!', 'success')
        return redirect(url_for('opportunities'))

    user_opps = [o for o in all_opps if o.get('user_id') == user_id]
    
    # Add smart deadline labels
    for o in user_opps:
        o['deadline_info'] = calculate_deadline_info(o.get('deadline', ''), o.get('status', ''))
        
    user_opps = sorted(user_opps, key=lambda x: (x.get('status') == 'Completed', x.get('deadline', '')))
    return render_template('opportunities.html', opportunities=user_opps)

@app.route('/opportunities/delete/<opp_id>', methods=['POST'])
def delete_opportunity(opp_id):
    """
    Delete Opportunity.
    """
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    all_opps = load_data('opportunities.json')
    updated_list = [o for o in all_opps if not (o['id'] == opp_id and o.get('user_id') == user_id)]
    
    save_data('opportunities.json', updated_list)
    flash('Opportunity tracker entry deleted.', 'success')
    return redirect(url_for('opportunities'))



# -------------------------------------------------------------------------
# Quick Notes Section (Protected)
# -------------------------------------------------------------------------

@app.route('/notes', methods=['GET', 'POST'])
def notes():
    """
    Quick Notes Canvas Route.
    """
    if not session.get('user_id'):
        flash('Please sign in to open notes board!', 'error')
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    all_notes = load_data('notes.json')

    # Automatically assign IDs to old notes that might not have one.
    # This prevents errors during deletion and updates legacy JSON data.
    # Note IDs are unique strings (UUIDs) that allow us to identify exactly which note to delete.
    needs_save = False
    for note in all_notes:
        if 'id' not in note:
            note['id'] = str(uuid.uuid4())
            needs_save = True
    if needs_save:
        save_data('notes.json', all_notes)

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category')
        color = request.form.get('color', 'yellow')

        if not title or not content or not category:
            flash('Please enter all notes fields!', 'error')
            return redirect(url_for('notes'))

        new_note = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': title,
            'content': content,
            'category': category,
            'color': color,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

        all_notes.append(new_note)
        save_data('notes.json', all_notes)
        flash('Quick note posted!', 'success')
        return redirect(url_for('notes'))

    user_notes = [n for n in all_notes if n.get('user_id') == user_id]
    return render_template('notes.html', notes=user_notes)

@app.route('/notes/delete/<note_id>', methods=['POST'])
def delete_note(note_id):
    """
    Delete Note.
    """
    # 1. Verify that the user is logged in
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    
    # 2. Load the current database of notes from JSON
    all_notes = load_data('notes.json')
    
    # 3. Filter out the note to be deleted.
    # Flask handles the POST request to this route, passing the note_id from the URL.
    # We rebuild the list, keeping only notes that DO NOT match both the target note_id and the current user_id.
    # We use note.get('id') to safely handle any legacy notes that might not have an 'id'.
    updated_list = [note for note in all_notes if not (note.get('id') == note_id and note.get('user_id') == user_id)]
    
    # 4. Save the updated list back to the JSON file, permanently removing the note
    save_data('notes.json', updated_list)
    flash('Quick note discarded.', 'success')
    return redirect(url_for('notes'))

# -------------------------------------------------------------------------
# Marks Tracker & GPA Calculator Section (Protected)
# -------------------------------------------------------------------------

@app.route('/marks', methods=['GET', 'POST'])
def marks():
    """
    Marks Tracker & GPA Calculator Route.
    """
    if not session.get('user_id'):
        flash('Please sign in to track academic grades!', 'error')
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    all_marks = load_data('marks.json')

    if request.method == 'POST':
        course_name = request.form.get('course_name')
        semester = request.form.get('semester')
        credits = request.form.get('credits')
        mtt1 = request.form.get('mtt1')
        mtt2 = request.form.get('mtt2')
        ica = request.form.get('ica')
        term_end = request.form.get('term_end')

        if not course_name or not semester or not credits or not mtt1 or not mtt2 or not ica or not term_end:
            flash('Please fill out all required fields!', 'error')
            return redirect(url_for('marks'))

        try:
            credits_val = int(credits)
            mtt1_val = float(mtt1)
            mtt2_val = float(mtt2)
            ica_val = float(ica)
            term_end_val = float(term_end)
            semester_val = int(semester)
        except ValueError:
            flash('Credits, semester, and marks must be numerical values!', 'error')
            return redirect(url_for('marks'))

        # Verify marks ranges (MTT 1 & 2: max 10, ICA: max 30, Term End TEE: max 100)
        if not (0 <= mtt1_val <= 10) or not (0 <= mtt2_val <= 10) or not (0 <= ica_val <= 30) or not (0 <= term_end_val <= 100):
            flash('Marks must be in their specified ranges (MTT1: 0-10, MTT2: 0-10, ICA: 0-30, Term End: 0-100)!', 'error')
            return redirect(url_for('marks'))

        # Scale Term End Exam (TEE) down to 50
        scaled_term_end = term_end_val * 0.5
        total_marks = mtt1_val + mtt2_val + ica_val + scaled_term_end

        # Grade Point (GP) mapping
        if total_marks >= 90:
            gp = 10
            grade = 'O'
        elif total_marks >= 80:
            gp = 9
            grade = 'A+'
        elif total_marks >= 70:
            gp = 8
            grade = 'A'
        elif total_marks >= 60:
            gp = 7
            grade = 'B+'
        elif total_marks >= 50:
            gp = 6
            grade = 'B'
        elif total_marks >= 40:
            gp = 5
            grade = 'C'
        else:
            gp = 0
            grade = 'F'

        new_course = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'course_name': course_name,
            'semester': semester_val,
            'credits': credits_val,
            'mtt1': mtt1_val,
            'mtt2': mtt2_val,
            'ica': ica_val,
            'term_end': term_end_val,
            'total': total_marks,
            'grade': grade,
            'gp': gp
        }

        all_marks.append(new_course)
        save_data('marks.json', all_marks)
        flash('Academic marks record added successfully!', 'success')
        return redirect(url_for('marks'))

    # Grouping logic for GET
    user_marks = [m for m in all_marks if m.get('user_id') == user_id]
    
    grouped_data = {}
    for sem in range(1, 9):
        grouped_data[sem] = {
            'courses': [],
            'total_gp_credits': 0.0,
            'total_credits': 0,
            'sgpa': 0.0
        }

    for course in user_marks:
        sem = course.get('semester')
        if 1 <= sem <= 8:
            grouped_data[sem]['courses'].append(course)
            grouped_data[sem]['total_gp_credits'] += float(course.get('gp', 0)) * float(course.get('credits', 0))
            grouped_data[sem]['total_credits'] += int(course.get('credits', 0))

    # Compute SGPA for each semester
    for sem in range(1, 9):
        tot_credits = grouped_data[sem]['total_credits']
        if tot_credits > 0:
            grouped_data[sem]['sgpa'] = grouped_data[sem]['total_gp_credits'] / tot_credits

    # Compute overall CGPA
    total_gp_credits = sum(grouped_data[sem]['total_gp_credits'] for sem in range(1, 9))
    total_credits = sum(grouped_data[sem]['total_credits'] for sem in range(1, 9))
    cgpa = total_gp_credits / total_credits if total_credits > 0 else 0.0

    return render_template('marks.html', grouped_data=grouped_data, cgpa=cgpa)

@app.route('/marks/delete/<course_id>', methods=['POST'])
def delete_marks(course_id):
    """
    Delete Course Marks.
    """
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    all_marks = load_data('marks.json')
    updated_list = [m for m in all_marks if not (m['id'] == course_id and m.get('user_id') == user_id)]
    
    save_data('marks.json', updated_list)
    flash('Course marks deleted.', 'success')
    return redirect(url_for('marks'))

# -------------------------------------------------------------------------
# Explanatory Guide Section (Public)
# -------------------------------------------------------------------------

@app.route('/how-it-works')
def how_it_works():
    """
    Explanatory Page:
    Documents details of web app components in a student-friendly format.
    """
    return render_template('how_it_works.html')

# -------------------------------------------------------------------------
# Calendar View Section (Protected)
# -------------------------------------------------------------------------

@app.route('/calendar')
def calendar():
    """
    Calendar Route.
    Displays deadlines and events on a monthly grid.
    """
    if not session.get('user_id'):
        flash('Please sign in to view the calendar!', 'error')
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    
    # Load user data
    goals = [g for g in load_data('goals.json') if g.get('user_id') == user_id]
    opportunities = [o for o in load_data('opportunities.json') if o.get('user_id') == user_id]
    
    return render_template('calendar.html', goals=goals, opportunities=opportunities)

# =========================================================================
# Application Entry Point
# =========================================================================
if __name__ == '__main__':
    # Run the server locally on port 5000 with interactive debugger active.
    app.run(host='127.0.0.1', port=5000, debug=True)
