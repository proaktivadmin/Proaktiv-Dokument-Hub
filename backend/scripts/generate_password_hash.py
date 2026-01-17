#!/usr/bin/env python3
"""
Generate a bcrypt password hash for use with APP_PASSWORD_HASH.

Usage:
    python scripts/generate_password_hash.py

You will be prompted to enter a password.
The output is the bcrypt hash to set as APP_PASSWORD_HASH.
"""

import bcrypt
import getpass


def generate_hash(password: str) -> str:
    """Generate a bcrypt hash for the given password."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def main():
    print("=== Password Hash Generator ===")
    print()
    
    # Get password securely
    password = getpass.getpass("Enter your password: ")
    confirm = getpass.getpass("Confirm password: ")
    
    if password != confirm:
        print("\n❌ Passwords do not match!")
        return
    
    if len(password) < 8:
        print("\n⚠️  Warning: Password is less than 8 characters!")
    
    # Generate hash
    hash_value = generate_hash(password)
    
    print()
    print("=" * 60)
    print("✅ Password hash generated successfully!")
    print()
    print("Add this to Railway environment variables:")
    print()
    print(f"APP_PASSWORD_HASH={hash_value}")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
