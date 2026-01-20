from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os,json
from sqlalchemy import func

import firebase_admin
from firebase_admin import credentials, auth

# ================== APP SETUP ==================

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.sqlite3")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ================== FIREBASE ==================

if not firebase_admin._apps:
    cred = credentials.Certificate(
    json.loads(os.environ["FIREBASE_KEY_JSON"])
)
    firebase_admin.initialize_app(cred)

# ================== MODELS ==================

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), nullable=False)

class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), nullable=False)

class ParkingLot(db.Model):
    lot_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    price = db.Column(db.Float)
    max_spots = db.Column(db.Integer)
    spots = db.relationship("Spot", backref="lot", lazy=True, cascade="all, delete")

class Spot(db.Model):
    spot_id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lot.lot_id"))
    is_occupied = db.Column(db.Boolean, default=False)

class Booking(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)
    user_uid = db.Column(db.String(200), nullable=False)
    spot_id = db.Column(db.Integer, nullable=False)
    vehicle_number = db.Column(db.String(20))

    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration_hours = db.Column(db.Float)
    cost = db.Column(db.Float)

    payment_status = db.Column(db.String(20), default="PENDING")

# ================== DB INIT ==================

with app.app_context():
    db.create_all()

# ================== HELPERS ==================

def verify_token(req):
    auth_header = req.headers.get("Authorization")
    if not auth_header:
        return None
    try:
        token = auth_header.replace("Bearer ", "")
        return auth.verify_id_token(token)
    except Exception as e:
        print("Token error:", e)
        return None

def is_admin(token_data):
    return Admin.query.filter_by(firebase_uid=token_data["uid"]).first() is not None

# ================== ROUTES ==================

@app.route("/")
def home():
    return jsonify({"status": "Backend running"})

# ---------- WHO AM I ----------

@app.route("/api/whoami")
def whoami():
    token_data = verify_token(request)
    if not token_data:
        return jsonify({"error": "Unauthorized"}), 401

    uid = token_data["uid"]

    if Admin.query.filter_by(firebase_uid=uid).first():
        return jsonify({"role": "admin"})

    if User.query.filter_by(firebase_uid=uid).first():
        return jsonify({"role": "user"})

    return jsonify({"role": "unknown"})

# ---------- SYNC USER ----------

@app.route("/api/sync-user", methods=["POST"])
def sync_user():
    token_data = verify_token(request)
    if not token_data:
        return jsonify({"error": "Unauthorized"}), 401

    uid = token_data["uid"]
    email = token_data.get("email", "")

    if Admin.query.filter_by(firebase_uid=uid).first():
        return jsonify({"message": "Admin synced"})

    if not User.query.filter_by(firebase_uid=uid).first():
        db.session.add(User(firebase_uid=uid, email=email))
        db.session.commit()

    return jsonify({"message": "User synced"})

# ---------- PARKING LOCATIONS ----------

@app.route("/api/parking-locations")
def parking_locations():
    lots = ParkingLot.query.all()
    result = []

    for lot in lots:
        occupied = sum(1 for s in lot.spots if s.is_occupied)
        result.append({
            "lot_id": lot.lot_id,
            "name": lot.name,
            "lat": lot.latitude,
            "lng": lot.longitude,
            "price": lot.price,
            "total": len(lot.spots),
            "available": len(lot.spots) - occupied
        })

    return jsonify(result)

# ---------- BOOK SPOT ----------

@app.route("/api/book", methods=["POST"])
def book_spot():
    token_data = verify_token(request)
    if not token_data:
        return jsonify({"error": "Unauthorized"}), 401

    uid = token_data["uid"]
    data = request.json

    if Booking.query.filter_by(user_uid=uid, end_time=None).first():
        return jsonify({"message": "Please release your current booking first"}), 400

    spot = Spot.query.filter_by(
        lot_id=data["lot_id"],
        is_occupied=False
    ).first()

    if not spot:
        return jsonify({"message": "No free spot"}), 400

    spot.is_occupied = True

    booking = Booking(
        user_uid=uid,
        spot_id=spot.spot_id,
        vehicle_number=data["vehicle_number"]
    )

    db.session.add(booking)
    db.session.commit()

    return jsonify({
        "message": "Spot booked successfully",
        "booking_id": booking.booking_id
    })

# ---------- ACTIVE BOOKING ----------

@app.route("/api/active-booking")
def active_booking():
    token_data = verify_token(request)
    if not token_data:
        return jsonify({"error": "Unauthorized"}), 401

    booking = Booking.query.filter_by(
        user_uid=token_data["uid"],
        end_time=None
    ).first()

    if not booking:
        return jsonify({"active": False})

    return jsonify({
        "active": True,
        "booking_id": booking.booking_id,
        "start_time": booking.start_time.isoformat()
    })

# ---------- BOOKING HISTORY ----------

@app.route("/api/my-bookings")
def my_bookings():
    token_data = verify_token(request)
    if not token_data:
        return jsonify({"error": "Unauthorized"}), 401

    bookings = (
        db.session.query(
            Booking,
            ParkingLot.name.label("parking_lot")
        )
        .join(Spot, Spot.spot_id == Booking.spot_id)
        .join(ParkingLot, ParkingLot.lot_id == Spot.lot_id)
        .filter(Booking.user_uid == token_data["uid"])
        .order_by(Booking.start_time.desc())
        .all()
    )

    result = []
    for booking, lot_name in bookings:
        result.append({
            "booking_id": booking.booking_id,
            "parking_lot": lot_name,
            "vehicle_number": booking.vehicle_number,
            "active": booking.end_time is None,
            "start_time": booking.start_time.isoformat(),
            "end_time": booking.end_time.isoformat() if booking.end_time else None,
            "duration": booking.duration_hours,
            "cost": booking.cost,
            "payment_status": booking.payment_status,
        })

    return jsonify(result)

# ---------- RELEASE SPOT ----------

@app.route("/api/release/<int:booking_id>", methods=["POST"])
def release_spot(booking_id):
    token_data = verify_token(request)
    if not token_data:
        return jsonify({"error": "Unauthorized"}), 401

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_uid != token_data["uid"]:
        return jsonify({"error": "Forbidden"}), 403

    if booking.end_time:
        return jsonify({
            "message": "Already released",
            "duration_hours": booking.duration_hours,
            "cost": booking.cost
        })

    spot = Spot.query.get_or_404(booking.spot_id)
    lot = ParkingLot.query.get_or_404(spot.lot_id)

    booking.end_time = datetime.utcnow()
    duration = (booking.end_time - booking.start_time).total_seconds() / 3600
    booking.duration_hours = round(duration, 2)
    booking.cost = round(duration * lot.price, 2)
    booking.payment_status = "PAID"

    spot.is_occupied = False
    db.session.commit()

    return jsonify({
        "message": "Spot released",
        "duration_hours": booking.duration_hours,
        "cost": booking.cost
    })

# ================== ADMIN ROUTES ==================

@app.route("/api/admin/analytics")
def admin_analytics():
    token_data = verify_token(request)
    if not token_data or not is_admin(token_data):
        return jsonify({"error": "Admin only"}), 403

    revenue = sum(b.cost for b in Booking.query.filter(Booking.cost != None).all())
    active = Booking.query.filter_by(end_time=None).count()

    return jsonify({
        "total_bookings": Booking.query.count(),
        "active_bookings": active,
        "revenue": round(revenue, 2)
    })

@app.route("/api/admin/revenue-daily")
def revenue_daily():
    token_data = verify_token(request)
    if not token_data or not is_admin(token_data):
        return jsonify({"error": "Admin only"}), 403

    data = (
        db.session.query(
            func.date(Booking.start_time),
            func.sum(Booking.cost)
        )
        .filter(Booking.cost != None)
        .group_by(func.date(Booking.start_time))
        .all()
    )

    return jsonify([
        {"date": str(d), "revenue": r}
        for d, r in data
    ])

@app.route("/api/admin/add-lot", methods=["POST"])
def add_parking_lot():
    token_data = verify_token(request)
    if not token_data or not is_admin(token_data):
        return jsonify({"error": "Admin only"}), 403

    data = request.json

    lot = ParkingLot(
        name=data["name"],
        latitude=data["lat"],
        longitude=data["lng"],
        price=data["price"],
        max_spots=data["spots"]
    )

    db.session.add(lot)
    db.session.commit()

    spots = [Spot(lot_id=lot.lot_id) for _ in range(data["spots"])]
    db.session.add_all(spots)
    db.session.commit()

    return jsonify({"message": "Parking lot added successfully"})

@app.route("/api/admin/update-lot/<int:lot_id>", methods=["PUT"])
def update_parking_lot(lot_id):
    token_data = verify_token(request)
    if not token_data or not is_admin(token_data):
        return jsonify({"error": "Admin only"}), 403

    price = request.json.get("price")
    if price is None:
        return jsonify({"error": "Price required"}), 400

    lot = ParkingLot.query.get_or_404(lot_id)
    lot.price = float(price)
    db.session.commit()

    return jsonify({"message": "Parking lot updated"})

@app.route("/api/admin/delete-lot/<int:lot_id>", methods=["DELETE"])
def delete_parking_lot(lot_id):
    token_data = verify_token(request)
    if not token_data or not is_admin(token_data):
        return jsonify({"error": "Admin only"}), 403

    lot = ParkingLot.query.get_or_404(lot_id)
    db.session.delete(lot)
    db.session.commit()

    return jsonify({"message": "Parking lot deleted"})

# ================== RUN ==================

if __name__ == "__main__":
    app.run()
