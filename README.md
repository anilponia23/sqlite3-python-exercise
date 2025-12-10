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

Verify installation:

python --version

sqlite3 --version

Clone the repository:

git clone https://github.com/anilponia23/sqlite3-python-exercise.git

cd sqlite3-python-exercise

How to Run

Initialize the database:

python src/setup_db.py

Run demo (queries + DAL):

python src/app.py

Expected Output
Below are examples of what you should see when running python src/app.py:
SQL Queries Section


<img width="1890" height="453" alt="Screenshot 2025-12-10 154203" src="https://github.com/user-attachments/assets/9ecaf7a0-31b0-48cd-af21-5c04de0f7af5" />



<img width="1895" height="791" alt="Screenshot 2025-12-10 154306" src="https://github.com/user-attachments/assets/6b41bc28-9c16-4409-becf-19af35514ec9" />



<img width="1903" height="626" alt="Screenshot 2025-12-10 154358" src="https://github.com/user-attachments/assets/87e46c8e-a171-4101-9b82-d98dfa258cd3" />


 Project Structure

<img width="582" height="257" alt="Screenshot 2025-12-10 154545" src="https://github.com/user-attachments/assets/c9edcc69-aeb9-49b6-a254-34554822a31f" />


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
