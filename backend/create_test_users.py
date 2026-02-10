
import requests
import random
import string

BASE_URL = "http://localhost:8000/api/v1"

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_and_login_user(prefix):
    username = f"{prefix}_{generate_random_string()}"
    email = f"{username}@test.com"
    password = "password123"
    
    # Register
    print(f"Registering {username}...")
    reg_resp = requests.post(f"{BASE_URL}/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    
    if reg_resp.status_code not in [200, 201]:
        print(f"Registration failed for {username}: {reg_resp.text}")
        return None

    # Login
    print(f"Logging in {username}...")
    login_resp = requests.post(f"{BASE_URL}/auth/login", data={
        "username": username,
        "password": password
    })
    
    if login_resp.status_code != 200:
        print(f"Login failed for {username}: {login_resp.text}")
        return None
        
    return login_resp.json()

def main():
    user1 = create_and_login_user("testuser1")
    user2 = create_and_login_user("testuser2")
    
    if user1 and user2:
        print("\n--- TOKENS ---")
        print(f"USER1_TOKEN={user1['access_token']}")
        print(f"USER2_TOKEN={user2['access_token']}")
    else:
        print("Failed to create users.")

if __name__ == "__main__":
    main()
