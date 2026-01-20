# Vehicle Parking -MAD 1 Project
A Flask-based parking app with admin and user dashboards.

## Description
This is a vehicle parking app where we have admin and users. So we need to create models for admin , users, lots, spots, bookings etc. Then after this we create routers for rendering html pages in the urls. If any html template needs the data from the database to use in jinja2 formate then we would first query the data from the tables in the database and then passed them to the templates. In case templates do not need them I simply rendered the template only


## Features
1. User and admin login/registration
2. Book and release parking spots
3. View and manage bookings
4. Admin and user charts and summaries
5. SQLite database backend with SQLAlchemy ORM


## Technologies used
1. Python 3 : Core language used to build the app
2. Flask : Framework for routing and rendering templates
3. Flask-SQLAlchemy: For interacting with the SQLite database
4. SQLite: database
5. HTML, Bootstrap : for UI and styling
6. Matplotlib: Used to generate charts

## How to Run the project

### Step 1: 
Extract the ZIP file and open a terminal in the project folder.

### Step 2: Create a virtual environment
python3 -m venv venv
source venv/bin/activate

### Step 3: Install dependencies
pip install -r requirements.txt

### Step 4: Run the application
python3 app.py


then open the browser and go to "http://127.0.0.1:5000"


## Hardcoded values for admin
username=iamadmin
password=addme



eyJhbGciOiJSUzI1NiIsImtpZCI6IjA4MmU5NzVlMDdkZmE0OTYwYzdiN2I0ZmMxZDEwZjkxNmRjMmY1NWI
iLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vbmV1cm8tcGF
ya2luZyIsImF1ZCI6Im5ldXJvLXBhcmtpbmciLCJhdXRoX3RpbWUiOjE3Njg3NjE4MjcsInVzZXJfaWQiOi
JSalZsSVRZZlZ5Y3ZmaDIwbG9yamE0OFF6QjYzIiwic3ViIjoiUmpWbElUWWZWeWN2ZmgyMGxvcmphNDhRe
kI2MyIsImlhdCI6MTc2ODc2MTgyNywiZXhwIjoxNzY4NzY1NDI3LCJlbWFpbCI6ImNoaXRyYWtzaGlndWxp
YUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOns
iZW1haWwiOlsiY2hpdHJha3NoaWd1bGlhQGdtYWlsLmNvbSJdfSwic2lnbl9pbl9wcm92aWRlciI6InBhc3
N3b3JkIn19.uTmqGiXdjFUfuCrXvD4VwXg22svZpysI5MZM0QgMNB4u8utwxobVo6UZgZ0-igO9NHs-VEeN
KM0HJ8Ns1w8ZQuDfHIC9zJrkfK7XWmzpct99gmexWpDHVpSsNKZkHAeHJKCBVy3BLfP5ehKPPyzM1S-DA94
QgGDgc8fVPBesvbcB8YBBZ0uIb8ModUvXFh7f7WIrMqOANShzqr_7Km0HcbBuwbr2L9UBDMEw15HiWU-rfM
INhIiWYGwz5-ki4FEIv5aJtTjE1tpal52EydOhnwHY7-1CRyLea0xOAD1eEfWQ_g9n77QIB-3VrQR762Dnp
MlDJvO05qtMgaB0ZcpBeg