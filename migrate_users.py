#!/usr/bin/env python3
"""
Migration script to help existing users transition to the new authentication system
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-credentials.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def migrate_existing_users():
    """Migrate existing users from Firestore to Firebase Auth"""
    print("🔄 Starting user migration...")
    
    try:
        # Get all users from Firestore
        users_ref = db.collection('users')
        users = users_ref.stream()
        
        migrated_count = 0
        error_count = 0
        
        for user_doc in users:
            user_id = user_doc.id
            user_data = user_doc.to_dict()
            
            print(f"\n📋 Processing user: {user_id}")
            print(f"   Email: {user_data.get('email', 'No email')}")
            print(f"   Name: {user_data.get('name', 'No name')}")
            
            # Check if user already exists in Firebase Auth
            try:
                # Try to find user by email
                if user_data.get('email'):
                    try:
                        auth_user = auth.get_user_by_email(user_data['email'])
                        print(f"   ✅ User already exists in Firebase Auth: {auth_user.uid}")
                        migrated_count += 1
                        continue
                    except auth.UserNotFoundError:
                        pass
                
                # Create user in Firebase Auth
                if user_data.get('email'):
                    try:
                        # Generate a temporary password (user will need to reset it)
                        temp_password = f"TempPass{user_id[:8]}!"
                        
                        auth_user = auth.create_user(
                            email=user_data['email'],
                            password=temp_password,
                            display_name=user_data.get('name', user_data['email'].split('@')[0])
                        )
                        
                        print(f"   ✅ Created in Firebase Auth: {auth_user.uid}")
                        print(f"   ⚠️  Temporary password: {temp_password}")
                        print(f"   📧 User should reset password via email")
                        
                        migrated_count += 1
                        
                    except Exception as e:
                        print(f"   ❌ Failed to create in Firebase Auth: {e}")
                        error_count += 1
                else:
                    print(f"   ⚠️  No email found, skipping Firebase Auth creation")
                    
            except Exception as e:
                print(f"   ❌ Error processing user: {e}")
                error_count += 1
        
        print(f"\n📊 Migration Summary:")
        print(f"   ✅ Successfully migrated: {migrated_count}")
        print(f"   ❌ Errors: {error_count}")
        
        if migrated_count > 0:
            print(f"\n📧 Next Steps:")
            print(f"   1. Users should check their email for password reset")
            print(f"   2. Or use the temporary password shown above")
            print(f"   3. Users can then login normally")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

def list_all_users():
    """List all users in both Firestore and Firebase Auth"""
    print("📋 Listing all users...")
    
    # List Firestore users
    print("\n🔥 Firestore Users:")
    users_ref = db.collection('users')
    firestore_users = users_ref.stream()
    
    firestore_count = 0
    for user_doc in firestore_users:
        user_data = user_doc.to_dict()
        print(f"   {user_doc.id}: {user_data.get('email', 'No email')} - {user_data.get('name', 'No name')}")
        firestore_count += 1
    
    print(f"   Total Firestore users: {firestore_count}")
    
    # List Firebase Auth users (limited to first 100)
    print("\n🔐 Firebase Auth Users:")
    try:
        auth_users = auth.list_users()
        auth_count = 0
        for user in auth_users.users:
            print(f"   {user.uid}: {user.email} - {user.display_name}")
            auth_count += 1
        print(f"   Total Firebase Auth users: {auth_count}")
    except Exception as e:
        print(f"   ❌ Error listing Firebase Auth users: {e}")

def main():
    """Main function"""
    print("🔄 User Migration Tool")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. List all users")
        print("2. Migrate existing users to Firebase Auth")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            list_all_users()
        elif choice == "2":
            confirm = input("Are you sure you want to migrate users? (y/N): ").strip().lower()
            if confirm == 'y':
                migrate_existing_users()
            else:
                print("Migration cancelled.")
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 