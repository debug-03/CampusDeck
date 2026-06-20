# CampusDeck

CampusDeck is a student productivity dashboard built using Python and Flask.

I created this project to learn how frontend and backend systems work together while solving a problem I personally face as a student — keeping track of goals, study resources, opportunities, grades, and notes across multiple platforms.

Instead of using a traditional database, CampusDeck uses JSON files to store data, which made it easier for me to understand how data flows through a web application before moving to SQL-based projects.

## Features

* User registration and login
* Goal tracking
* Resource bookmarks
* Opportunity tracker
* Sticky notes
* Study activity tracking
* GPA and grade calculator
* Dashboard with key metrics

## Tech Stack

### Frontend

* HTML
* CSS
* JavaScript
* Jinja2 templates

### Backend

* Python
* Flask

### Data Storage

* JSON files

### Authentication

* Flask sessions
* Werkzeug password hashing

## Project Structure

```text
CampusDeck/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── users.json
│   ├── goals.json
│   ├── resources.json
│   ├── opportunities.json
│   ├── notes.json
│   └── grades.json
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── ...
│
└── static/
    ├── style.css
    ├── script.js
    └── images/
```

## How It Works

The application follows a simple flow:

```text
Browser → Flask Route → Python Logic → JSON Files → Jinja Templates → Browser
```

When a user submits a form, Flask receives the data, processes it, updates the relevant JSON file, and renders the updated information back to the user.

### Registration Flow

```text
User fills the registration form
↓
Flask receives the data
↓
Password is hashed
↓
User information is stored in users.json
↓
User is redirected to the login page
```

### Login Flow

```text
User enters credentials
↓
Flask verifies the user data
↓
Password hash is checked
↓
Session is created
↓
Dashboard is displayed
```

## Why JSON Instead of SQL?

The main goal of this project was learning.

Using JSON files helped me understand:

* How data is stored and retrieved
* CRUD operations
* Form handling
* Authentication flow
* Backend logic in Flask

In future versions, I plan to migrate the project to a proper SQL database.

## Libraries Used

* Flask
* Werkzeug
* json
* uuid
* datetime
* os

## Design Inspiration

The interface is inspired by products like GitHub, LeetCode, and Notion.

The focus was to keep the design:

* Minimal
* Practical
* Student-focused
* Easy to navigate

## Running the Project Locally

Clone the repository:

```bash
git clone https://github.com/debug-03/CampusDeck.git
cd CampusDeck
```

Create and activate a virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

## Future Improvements

* Migrate from JSON to SQL
* Add notifications and reminders
* Improve analytics and insights
* Add search functionality
* Improve mobile responsiveness

## What I Learned

Through this project, I learned:

* Flask routing
* Template rendering with Jinja2
* Form handling
* Session management
* Password hashing
* JSON-based data storage
* Connecting frontend and backend components

Most importantly, this project helped me understand what happens behind the scenes when a user interacts with a web application.
