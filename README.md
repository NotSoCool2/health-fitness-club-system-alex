# COMP 3005 Final Project  
## Health & Fitness Club Management System
## Group of 2: Alex Bon and Gloria Li

This project is a **CLI-based Health & Fitness Club Management System** built for COMP 3005 (Fall 2025).  
It uses **PostgreSQL** as the backend DB and **Python (psycopg2)** as the application for UI

The system supports **three roles** as stated in specs:
- **Member**: register, manage profile, track health metrics & goals, and view personal dashboard
- **Trainer**: set availability and look up member progress
- **Admin**: (planned) room/class/billing operations for staff.

Course specs:
- Relational DB in PostgreSQL with **DDL.sql + DML.sql**. :contentReference[oaicite:1]{index=1}  
- At least **4 Member fns**, **2 Trainer fns**, and **2 Admin fns** (for a 2-person group total ≥10 operations). :contentReference[oaicite:2]{index=2}  
- Separate **ERD + mapping + normalization** documented under `/docs`. :contentReference[oaicite:3]{index=3}  

---
## 1. Tech info

- **Language:** Python
- **Database:** PostgreSQL
- **Library:** `psycopg2` for DB connection
- **Interface:** Text-based CLI (menu-driven)

---
## 2. Folder Structure

Project root (what we submit):

```text
Final Project
├── README.md # this file
├── sql
│   ├── DDL.sql # CREATE TABLE + constraints
│   └── DML.sql # sample data (including members, trainers, metrics)
├── app
│   ├── app.py # MAIN CLI entry point, menu + routing
│   ├── auth.py # login + registration functions (registration is a member func.)
│   ├── member.py # member operations (metrics, goals, dashboard, profile)
│   ├── trainer.py # trainer operations (availability, member lookup)
│   ├── db.py # DB connection + resetDB() --> runs DML and DDL
│   ├── state.py
│   └── __pycache__ # Python cache (ignored in git)
└── docs (TO DO)
    ├── ERD.pdf # ER diagram with entities/relationships (to be added)
    ├── Mapping.pdf # ER → Relational mapping (optional or merged w/ ERD.pdf)
    ├── Normalization.pdf # 2NF/3NF proof or integrated in report
    └── Report.pdf # Short written report + assumptions