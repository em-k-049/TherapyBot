# backend/seed.py (Corrected Version)
import logging
from app.db import SessionLocal
from app.models import Role

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_data():
    db = SessionLocal()
    try:
        # Check if roles already exist
        if db.query(Role).count() == 0:
            logger.info("Seeding initial roles...")

            # Create default roles (without the 'description' field)
            roles = [
                Role(name="patient"),
                Role(name="consultant"),
                Role(name="admin")
            ]

            db.add_all(roles)
            db.commit()
            logger.info("Roles seeded successfully.")
        else:
            logger.info("Roles already exist. No seeding needed.")

    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting database seeding process...")
    seed_data()
    logger.info("Seeding process finished.")