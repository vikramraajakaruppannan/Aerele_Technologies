# 📅 Event Scheduling & Resource Allocation System

A **Flask-based web application** that allows organizations to **schedule events**, **manage shared resources**, **allocate resources to events**, and **prevent scheduling conflicts**.  
The system also provides **resource utilization reporting** within a selected date range.

This project was developed as part of a **technical hiring assignment** to demonstrate backend logic, database design, conflict handling, and clean UI integration.

---

## 🚀 Features

### 🔹 Event Management
- Create, view, edit, and delete events
- Each event has:
  - Title
  - Start time
  - End time
  - Description

### 🔹 Resource Management
- Manage shared resources such as:
  - Rooms
  - Instructors
  - Equipment
- Full CRUD support (Create, View, Edit, Delete)

### 🔹 Resource Allocation
- Allocate resources to events
- Supports **many-to-many relationships**
- Ensures:
  - No resource is double-booked
  - Time overlaps are handled correctly

### 🔹 Conflict Detection
- Prevents allocation if:
  - The same resource is already assigned to another overlapping event
- Handles edge cases:
  - Partial overlaps
  - Nested time intervals
  - Start/end boundary conflicts

### 🔹 Resource Utilization Report
- Generate reports based on a selected date range
- Shows:
  - Resource name
  - Total hours utilized
  - Upcoming event bookings

### 🔹 Modern UI
- Clean, responsive UI using **Bootstrap**
- Subtle action icons (Edit/Delete) without disturbing layout
- Confirmation prompts for destructive actions
- Dashboard view with key metrics

---

## 🧠 System Design

### Database Tables

#### 1. Event
| Field | Description |
|------|------------|
| event_id | Primary Key |
| title | Event title |
| start_time | Start datetime |
| end_time | End datetime |
| description | Optional details |

#### 2. Resource
| Field | Description |
|------|------------|
| resource_id | Primary Key |
| resource_name | Name of resource |
| resource_type | room / instructor / equipment |

#### 3. EventResourceAllocation
| Field | Description |
|------|------------|
| allocation_id | Primary Key |
| event_id | Foreign Key → Event |
| resource_id | Foreign Key → Resource |

Relationships:
- One event → many resources
- One resource → many events

---

## ⚙️ Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Frontend:** HTML, Jinja2, Bootstrap, Font Awesome
- **Architecture:** Flask Application Factory Pattern

---
