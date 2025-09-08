#!/usr/bin/env python3
"""
Seed database with dummy users for testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.db import SessionLocal
from backend.app.models import User, Role
from backend.app.security import get_password_hash

def seed_database():
    db = SessionLocal()
    
    try:
        # Create roles if they don't exist
        roles = ['patient', 'consultant', 'admin']
        for role_name in roles:
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(name=role_name)
                db.add(role)
        
        db.commit()
        
        # Get role objects
        patient_role = db.query(Role).filter(Role.name == 'patient').first()
        consultant_role = db.query(Role).filter(Role.name == 'consultant').first()
        admin_role = db.query(Role).filter(Role.name == 'admin').first()
        
        # Create dummy users if they don't exist
        dummy_users = [
            {
                'username': 'patient1',
                'email': 'patient1@test.com',
                'password': 'password123',
                'role': patient_role
            },
            {
                'username': 'consultant1',
                'email': 'consultant1@test.com',
                'password': 'password123',
                'role': consultant_role
            },
            {
                'username': 'admin1',
                'email': 'admin1@test.com',
                'password': 'password123',
                'role': admin_role
            }
        ]
        
        for user_data in dummy_users:
            existing_user = db.query(User).filter(User.username == user_data['username']).first()
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    hashed_password=get_password_hash(user_data['password']),
                    role_id=user_data['role'].id
                )
                db.add(user)
                print(f"Created user: {user_data['username']} ({user_data['role'].name})")
            else:
                print(f"User already exists: {user_data['username']}")
        
        db.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()