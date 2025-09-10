from app.db.database import SessionLocal, init_db
from app.db import crud

def run():
    init_db()
    db = SessionLocal()

    # 1. Create a user
    user = crud.create_user(db, "alice", "alice@example.com", "hashedpassword123")
    print("Created user:", user.id, user.username)

    # 2. Create a session
    session = crud.create_session(db, user.id)
    print("Started session:", session.id)

    # 3. Add a message
    msg = crud.add_message(db, session.id, sender="user", content="Hello, TherapyBot!")
    print("Message logged:", msg.content)

    # 4. Add wellness log
    log = crud.create_wellness_log(db, user.id, mood="happy", energy_level=8, notes="Great day")
    print("Wellness log:", log.mood, log.energy_level)

    db.close()

if __name__ == "__main__":
    run()

