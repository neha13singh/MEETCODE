
import asyncio
import requests
import json
import websockets
import random
import string
import time

BASE_URL = "http://localhost:8000/api/v1"
WS_URL = "ws://localhost:8000/ws"

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
        return None, None

    # Login
    print(f"Logging in {username}...")
    login_resp = requests.post(f"{BASE_URL}/auth/login", data={
        "username": username,
        "password": password
    })
    
    if login_resp.status_code != 200:
        print(f"Login failed for {username}: {login_resp.text}")
        return None, None
        
    data = login_resp.json()
    return data['access_token'], username

async def run_test():
    print("--- STARTING INVITE FLOW VERIFICATION ---")
    
    # 1. Create two users
    token1, user1 = create_and_login_user("sim_creator")
    token2, user2 = create_and_login_user("sim_joiner")
    
    if not token1 or not token2:
        print("Failed to create users. Exiting.")
        return

    invite_code = None
    match_id = None

    # 2. Creator connects and creates private match
    print(f"\n[Creator] Connecting to WebSocket as {user1}...")
    async with websockets.connect(f"{WS_URL}?token={token1}") as ws1:
        print("[Creator] Connected.")
        
        create_payload = {
            "event": "match:create_private",
            "data": {"difficulty": "medium"}
        }
        print(f"[Creator] Sending: {create_payload}")
        await ws1.send(json.dumps(create_payload))
        
        # Wait for code
        response = await ws1.recv()
        data = json.loads(response)
        print(f"[Creator] Received: {data}")
        
        if data['event'] == 'match:private_created':
            invite_code = data['data']['code']
            match_id = data['data']['matchId']
            print(f"[Creator] match created! CODE: {invite_code}, MatchID: {match_id}")
        else:
            print("[Creator] Unexpected creation response.")
            return

        # 3. Joiner connects and joins using code
        print(f"\n[Joiner] Connecting to WebSocket as {user2}...")
        async with websockets.connect(f"{WS_URL}?token={token2}") as ws2:
            print("[Joiner] Connected.")
            
            join_payload = {
                "event": "match:join_private",
                "data": {"code": invite_code}
            }
            print(f"[Joiner] Sending: {join_payload}")
            await ws2.send(json.dumps(join_payload))
            
            # 4. Verify both receive match:found
            print("\n[Verifying] Waiting for match:found events on both clients...")
            
            # Creator should receive match:found
            resp1 = await ws1.recv()
            data1 = json.loads(resp1)
            print(f"[Creator] Received: {data1}")
            
            # Joiner should receive match:found
            resp2 = await ws2.recv()
            data2 = json.loads(resp2)
            print(f"[Joiner] Received: {data2}")
            
            if data1['event'] == 'match:found' and data2['event'] == 'match:found':
                print("\nSUCCESS: Both users received match:found event!")
                print(f"Match ID: {data1['data']['matchId']}")
            else:
                print("\nFAILURE: Did not receive match:found events as expected.")

if __name__ == "__main__":
    asyncio.run(run_test())
