import asyncio
import os
import sys

# Add the backend directory to sys.path to allow imports from 'app'
# Assuming this script is in backend/app/tests/test_retell_connection.py
# We want to be able to import from 'app.core.config' etc.
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
app_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(backend_dir)
sys.path.append(app_dir)

# Now we can import using the structure 'app.core.config'
try:
    from app.core.config import settings
    from app.services.voice_provider.retell import RetellProvider
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

async def test_retell_connection():
    print("\n" + "="*50)
    print("RETELL AI CONNECTION TEST")
    print("="*50)
    
    if settings.RETELL_API_KEY == "your-retell-api-key" or not settings.RETELL_API_KEY:
        print("[ERROR] RETELL_API_KEY not found in .env or is set to default.")
        return

    print(f"[OK] Using API Key: {settings.RETELL_API_KEY[:8]}...")
    
    retell = RetellProvider(api_key=settings.RETELL_API_KEY)
    
    # 1. Test List Agents
    print("\n--- 1. Testing List Agents ---")
    agents = await retell.list_agents()
    if agents:
        print(f"[OK] Successfully retrieved {len(agents)} agents.")
        for agent in agents[:3]:
            print(f"   - {agent.get('agent_name', 'Unnamed')} (ID: {agent.get('agent_id')})")
    else:
        print("[WARN] No agents found or error occurred during listing.")

    # 2. Test Get Specific Agent (if ID provided)
    agent_id = settings.RETELL_AGENT_ID
    if agent_id:
        print(f"\n--- 2. Testing Get Agent Details (ID: {agent_id}) ---")
        agent_details = await retell.get_agent_details(agent_id)
        if agent_details and agent_details.get("agent_id"):
            print(f"[OK] Successfully retrieved details for agent: {agent_details.get('agent_name', 'Unnamed')}")
            print(f"   Response: {agent_details}")
        else:
            print(f"[ERROR] Failed to retrieve details for agent ID: {agent_id}")
    else:
        print("\n--- 2. Skipping Get Agent Details (RETELL_AGENT_ID not set in .env) ---")

    # 3. Test Create Web Call Session (Mocked or real depending on agent availability)
    if agent_id:
        print(f"\n--- 3. Testing Create Web Call Session ---")
        session = await retell.create_session(agent_id=agent_id, metadata={"test": "true"})
        if session and session.get("access_token"):
            print(f"[OK] Successfully created web call session!")
            print(f"   Access Token: {session.get('access_token')[:20]}...")
            print(f"   Call ID: {session.get('call_id')}")
        else:
            print("[ERROR] Failed to create web call session.")
    
    print("\n" + "="*50)
    print("TEST COMPLETE")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(test_retell_connection())
