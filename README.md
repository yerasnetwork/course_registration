# Course Registration System 📚

A robust and user-friendly web application built with **Django** designed to streamline the academic enrollment process. This system manages course catalogs, student registrations, and schedule validations with a focus on data integrity.

## 🌟 Key Features

* **User Authentication**: Dedicated registration and login system tailored for students.
* **Smart Course Catalog**: Dynamic listing of courses showing real-time availability and schedules.
* **Automated Validations**:
    * **Seat Limit Control**: Automatically prevents enrollment once the maximum capacity of a course is reached.
    * **Schedule Conflict Detection**: Backend logic prevents students from registering for multiple courses that overlap in time.
* **Student Dashboard**: A personalized "My Schedule" view for students to track their enrolled classes and timings.
* **Admin Management**: Full-featured administrative interface for managing courses, students, and enrollments.

## 🛠 Tech Stack

* **Backend**: Python / Django 6.0
* **Database**: SQLite (local development)
* **Frontend**: HTML5, CSS3 (Responsive Design)
* **Version Control**: Git / GitHub

## 🚀 Getting Started

### Prerequisites
* Python 3.10 or higher
* pip (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yerasnetwork/course_registration.git](https://github.com/yerasnetwork/course_registration.git)
    cd course_registration
    ```

2.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install django
    ```

4.  **Run migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser (Admin):**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Launch the development server:**
    ```bash
    python manage.py runserver
    ```

The application will be available at `http://127.0.0.1:8000/`.

---
*Developed as a part of a Django learning project focusing on database relationships and backend validation logic.*
