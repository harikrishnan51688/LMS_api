# Library Management System
A web-based library management api using Flask. This application allows users to manage books, patrons, and transactions, providing an easy interface for librarians and library members to interact with.

Frontend: https://github.com/harikrishnan51688/LMS-frontend  <br>

## Features

- **Book Management**: Add, update, delete, and view books in the library catalog.
- **Transaction Management**: Issue and return books, track overdue items, and view transaction history.
- **Search Functionality**: Search for books and patrons using various filters.
- **User Authentication**: Secure login and registration system for librarians and members.

## Technologies Used

- **Backend**: Flask, Redis, Celery
- **Frontend**: VueJS, HTML, CSS, JavaScript
- **Database**: SQLite, Redis for caching
- **Other**: Flask-Login for authentication, SQLAlchemy for ORM, Celery for background tasks, Mailhog for monitoring test mails

## Installation
Note: Works only in linux (due to the celery dependency)
1. **Clone the repository**:

   ```bash
   git clone https://github.com/harikrishnan51688/LMS_api.git
   cd LMS_api
   python -m venv venv
   source /venv/bin/activate
   pip install -r requirements.txt
   flask --app main run
2. **Clone frontend repository**:

   ```bash
   git clone https://github.com/harikrishnan51688/LMS-frontend
   cd LMS-frontend
   npm install
   npm run dev
