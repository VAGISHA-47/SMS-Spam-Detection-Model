#!/usr/bin/env python3
"""Create a test user directly in MongoDB for the SMS Spam app.

Usage:
  python scripts/create_test_user.py --username alice --password secret

It reads `MONGO_URI` from the environment or falls back to mongodb://localhost:27017
"""
import os
import argparse
from datetime import datetime

import pymongo
from werkzeug.security import generate_password_hash


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--username', required=True)
    p.add_argument('--password', required=True)
    args = p.parse_args()

    mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
    client = pymongo.MongoClient(mongo_uri)
    db = client.get_database('sms_spam_app')
    users = db.get_collection('users')

    if users.find_one({'username': args.username}):
        print(f"User {args.username} already exists")
        return

    users.insert_one({
        'username': args.username,
        'password_hash': generate_password_hash(args.password),
        'created_at': datetime.utcnow(),
    })
    print(f"Created user {args.username}")


if __name__ == '__main__':
    main()
