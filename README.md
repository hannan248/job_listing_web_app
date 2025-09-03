Job Listing Web App

A full-stack web application for managing and displaying job listings, featuring a React frontend, Flask backend API, and an automated web scraper for actuarial job data.

1. Features

Job Management – Full CRUD operations for job listings.

Advanced Filtering & Sorting – Filter by job type, location, tags, and search terms.

Responsive UI – Modern React interface with intuitive components.

RESTful API – Flask API with comprehensive, well-documented endpoints.

Automated Scraping – Selenium-based scraper for actuarial job listings from ActuaryList.com.

Database Integration – SQLite database using SQLAlchemy ORM.

CORS Support – Seamless frontend-backend communication.

2. Tech Stack
Backend

Python 3.x

Flask (Web framework)

Flask-SQLAlchemy (Database ORM)

Flask-CORS (Cross-origin resource sharing)

SQLite (Database)

Frontend

React 18 (UI library)

JavaScript (Logic)

CSS (Styling)

Scraper

Selenium (Web automation)

Chrome WebDriver (Browser automation)

Requests (HTTP library)

3. Prerequisites

Python 3.8+

Node.js 14+

Google Chrome browser (for scraping)

Git

4. Installation & Setup
Step 1. Clone the Repository
git clone <repository-url>
cd job-listing-web-app

Step 2. Backend Setup
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py


Backend runs on http://localhost:5000.

Step 3. Frontend Setup
cd frontend

# Install dependencies
npm install

# Start React app
npm start


Frontend runs on http://localhost:3000.

Step 4. Scraper Setup
cd Scraper

# Install dependencies
pip install -r requirements.txt

# Run scraper
python scrape.py

5. Usage
Running the Application

Start the backend server (python app.py).

Start the frontend development server (npm start).

Visit http://localhost:3000 in your browser.

Using the Scraper

The scraper automatically:

Navigates to actuarylist.com.

Extracts job listings (company, title, location, tags).

Sends data to the Flask API.

Saves output to scraped_jobs.json.

Run:

cd Scraper
python scrape.py

6. Documentation
Setup & Run Instructions

Backend, frontend, and scraper setup explained above.

Run backend first → frontend second → scraper last (if needed).

API base URL: http://localhost:5000/api.

Assumptions / Shortcuts

SQLite is used for simplicity (easily replaceable with PostgreSQL/MySQL).

Scraper is configured for Chrome only (can be extended to Firefox).

Jobs are refreshed manually by running scrape.py (no cron scheduling included).

Project Structure & Technology Decisions

Flask was chosen for its lightweight, easy-to-integrate REST API.

React 18 used for a modern, component-driven frontend.

SQLite selected as a zero-config development database.

Selenium chosen for dynamic job site scraping where static HTML parsing isn’t enough.

CORS enabled to simplify local development between React (3000) and Flask (5000).

7. API Documentation

Base URL:

http://localhost:5000/api

Endpoints

GET /api/jobs – Retrieve jobs (filterable, sortable).

Parameters:

job_type (Full-time, Part-time, Contract, Internship)

location (case-insensitive partial match)

tag (case-insensitive partial match)

search (search title/company)

sort (posting_date_desc, posting_date_asc, title_asc, company_asc)

GET /api/jobs/{id} – Get job by ID
POST /api/jobs – Create a new job
PUT /api/jobs/{id} – Update an existing job
DELETE /api/jobs/{id} – Delete a job

Utility Endpoints:

GET /api/health – Check server health

GET /api/jobs/job-types – Get unique job types

GET /api/jobs/locations – Get unique locations

GET /api/jobs/tags – Get unique tags

Response format:

{
  "success": true,
  "data": {...},
  "count": 1,
  "message": "string",
  "error": "string",
  "errors": ["array"]
}

8. Project Structure
job-listing-web-app/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── db.py
│   ├── models/
│   │   └── job.py
│   ├── routes/
│   │   └── job_routes.py
│   ├── requirements.txt
│   └── instance/
│       └── jobs.db
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AddEditJob.js
│   │   │   ├── DeleteJob.js
│   │   │   └── FilterSortJob.js
│   │   ├── api.js
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── public/
├── Scraper/
│   ├── scrape.py
│   ├── setup_driver.py
│   ├── requirements.txt
│   └── scraped_jobs.json
└── README.md

9. Acknowledgments

ActuaryList.com – For providing actuarial job listings.

Flask & React communities – For excellent documentation.

Selenium – For powerful web automation tools