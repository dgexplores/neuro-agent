#!/usr/bin/env python3
"""
Generate JWT tokens for NeuroAgent API authentication
"""

import jwt
import datetime
import sys

# JWT Secret Key (matches backend configuration)
JWT_SECRET_KEY = "REDACTED"
JWT_ALGORITHM = "HS256"


def generate_token(user_id="demo-physician", hours=24):
    """
    Generate a JWT token valid for specified hours

    Args:
        user_id (str): User identifier
        hours (int): Token validity duration in hours

    Returns:
        str: JWT token
    """
    payload = {
        'user_id': user_id,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=hours)
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def main():
    print("=" * 60)
    print("NeuroAgent JWT Token Generator")
    print("=" * 60)
    print()

    # Get user input
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
    else:
        user_id = input("Enter user_id (default: demo-physician): ").strip() or "demo-physician"

    if len(sys.argv) > 2:
        hours = int(sys.argv[2])
    else:
        hours_input = input("Token validity in hours (default: 24): ").strip()
        hours = int(hours_input) if hours_input else 24

    # Generate token
    token = generate_token(user_id, hours)

    # Display results
    print()
    print(f"[OK] Token generated successfully!")
    print()
    print(f"User ID: {user_id}")
    print(f"Valid for: {hours} hours")
    print(f"Expires at: {datetime.datetime.utcnow() + datetime.timedelta(hours=hours)}")
    print()
    print("=" * 60)
    print("JWT TOKEN (copy below)")
    print("=" * 60)
    print()
    print(token)
    print()
    print("=" * 60)
    print("AUTHORIZATION HEADER (copy below)")
    print("=" * 60)
    print()
    print(f"Bearer {token}")
    print()
    print("=" * 60)
    print("CURL EXAMPLE")
    print("=" * 60)
    print()
    print("curl -X POST https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/api/v1/diagnosis \\")
    print(f'  -H "Authorization: Bearer {token}" \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d @data/demo_cases.json')
    print()


if __name__ == "__main__":
    main()
