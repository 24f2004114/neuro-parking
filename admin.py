from app import db, Admin, app

with app.app_context():
    admin = Admin(
        firebase_uid="2CB6KwrAZ9OnSWBrz03Vf6QjTtq1",
        email="chitrakshigulia@gmail.com"
    )
    db.session.add(admin)
    db.session.commit()

print("Admin added")
