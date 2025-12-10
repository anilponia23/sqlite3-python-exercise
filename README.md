Manufacturing Data Platform (Python + SQLite)

Overview
This project implements a small data platform for a fictional manufacturing company using:
Database: SQLite (local file)
Language: Python 3.x
The platform supports:
Normalized schema for products, machines, work orders, and operations
Demo data for realistic queries
SQL queries to answer common business questions
Python Data Access Layer (DAL) functions for programmatic access

  Features
Schema: Multi-plant ready, normalized tables
Seed Data: 3 products, 5 machines, 12 work orders, operations with good vs scrap, downtime events
Queries: Product output by month, WIP orders, machine utilization, scrap drivers
Python Functions: Summaries, WIP, utilization, create work orders

  Prerequisites & Installation
Prerequisites
Python 3.10+ (tested on 3.12)
SQLite (comes pre-installed with Python)
Git (for cloning the repository)
VS Code or any IDE (optional but recommended)
Installation Steps
Clone the repository:


git clone https://github.com/anilponia23/sqlite3-python-exercise.git

cd sqlite3-python-exercise


Show more lines
(If not, ensure Python 3.x is installed; no extra packages are required for sqlite3.)
Verify installation:
python --version

sqlite3 --version

Setup Instructions
Clone the repo:

git clone https://github.com/anilponia23/sqlite3-python-exercise.git
cd sqlite3-python-exercise
Show more lines
Create virtual environment (optional):

python -m venv .venv
.\.venv\Scripts\activate
Show more lines
Install dependencies:

pip install -r requirements.txt
Show more lines
(If no requirements.txt, just ensure Python 3.x is installed.)

How to Run
Initialize the database:

python src/setup_db.py
Show more lines
Run demo (queries + DAL):

python src/app.py
Show more lines

 Project Structure
sqlite3-python-exercise/
├─ sql/
│  ├─ 001_schema.sql      # Database schema
│  ├─ 002_seed.sql        # Demo data
│  └─ queries.sql         # Reference SQL queries
├─ src/
│  ├─ setup_db.py         # Creates DB and seeds data
│  ├─ dal.py              # Python DAL functions
│  ├─ queries.py          # Python wrappers for SQL queries
│  └─ app.py              # Demo runner
└─ README.md

 Design Decisions
Normalized schema: Separate planning (work_orders) from actuals (operations)
WIP definition: status = in_progress OR now within planned window and not completed/cancelled
Utilization metric: runtime hours / available hours; adjusted variant subtracts downtime
Timestamps: ISO 8601 UTC for consistency
Indexes: Added for status and time-range queries

  Assumptions
Single plant seeded; schema supports multiple plants
Downtime events optional but included for realism
Scrap rate = scrap / (good + scrap)

Deliverables
SQL files for schema and seed data
Python scripts for DB setup, queries, and DAL
README with instructions and design notes

Expected Output
Below are examples of what you should see when running python src/app.py:
SQL Queries Section

<img width="1575" height="541" alt="Screenshot 2025-12-10 090747" src="https://github.com/user-attachments/assets/43aadb98-3e06-4467-a49c-c76d685c0e05" />


<img width="1496" height="749" alt="Screenshot 2025-12-10 090737" src="https://github.com/user-attachments/assets/09e75e2d-2f51-48c9-ac60-a1969efd3800" />


<img width="1572" height="634" alt="Screenshot 2025-12-10 090638" src="https://github.com/user-attachments/assets/908e5c16-a678-4322-8c58-8803633650fd" />




 Why This Design?
Normalized schema: Avoids duplication and supports scalability.
Separation of planning vs actuals: Work orders vs operations for accurate reporting.
Multi-plant ready: Future-proof for multiple sites.
Indexes: Improve query performance for status and time-based filters.
Optional downtime: Enables realistic machine utilization metrics.

  How to Check on GitHub
Commit and push the README:

git add README.md
git commit -m "Add polished README"
git push
Show more lines
Go to your repo:
https://github.com/anilponia23/sqlite3-python-exercise

The README will render automatically on the main page.
