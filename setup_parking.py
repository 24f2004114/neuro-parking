from app import app, db, ParkingLot, Spot

with app.app_context():
    existing = ParkingLot.query.filter_by(name="City Centre Parking").first()
    if existing:
        print("⚠ Parking lot already exists. Skipping creation.")
    else:
        lot = ParkingLot(
            name="City Centre Parking",
            latitude=22.5867,
            longitude=88.4171,
            price=50,
            max_spots=10
        )

        db.session.add(lot)
        db.session.commit()

        spots = [Spot(lot_id=lot.lot_id) for _ in range(10)]
        db.session.add_all(spots)
        db.session.commit()

        print("✅ Parking lot and 10 spots created successfully")
