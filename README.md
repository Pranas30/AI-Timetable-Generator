# 🗓️ AI-Powered Automated Timetable Generator

A full-stack web application designed to automate the complex task of college scheduling. This system uses a custom constraint-satisfaction algorithm to generate conflict-free timetables for multiple semesters simultaneously.

## 🚀 Key Features
* **Conflict Resolution:** Automatically prevents teacher double-bookings and semester overlaps.
* **Workload Management:** Ensures teachers do not have consecutive classes in the same semester to prevent fatigue.
* **Smart Prioritization:** High-priority subjects are scheduled first to ensure optimal time slots.
* **Dynamic Grid:** Handles variable weekly hours (e.g., 4 hours/week for Theory, 1 hour/week for Library).
* **Cross-Semester Sync:** Manages resources across different batches (Sem 1, Sem 3, etc.) in real-time.

## 🛠️ Tech Stack
* **Backend:** Python, Flask
* **Database:** SQLite with SQLAlchemy (ORM)
* **Frontend:** HTML5, CSS3 (Responsive Design)
* **Version Control:** Git & GitHub

## 📝 How It Works
1. **Data Input:** Departments enter subjects, assigned teachers, and total weekly hours.
2. **Algorithm Processing:** The system shuffles available slots and validates each placement against three rules:
   - Is the teacher free?
   - Is the semester slot empty?
   - Is it non-consecutive for the teacher?
3. **Generation:** A visual, color-coded timetable is rendered for all semesters.

