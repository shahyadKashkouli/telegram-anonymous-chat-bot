import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OWNER_USER_ID = int(os.getenv('OWNER_USER_ID', 0))

def is_owner(user_id):
    """Check if user is owner"""
    return user_id == OWNER_USER_ID