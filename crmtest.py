from msal import PublicClientApplication
import requests

# Configuration
# TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"
TENANT_ID = "16b3c013-d300-468d-ac64-7eda0820b6d3"
CLIENT_ID = "72c91998-f8a4-4937-bbfa-7091afa3b862"
DYNAMICS_URL = "https://microsoftsales.crm.dynamics.com"
SCOPE = [f"{DYNAMICS_URL}/user_impersonation"]
API_VERSION = "v9.2"

# Get Access Token Interactively
def get_interactive_token():
    app = PublicClientApplication(
        client_id=CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}"
    )
    result = app.acquire_token_interactive(scopes=SCOPE)
    return result["access_token"]

# Fetch Data from Dynamics 365
def fetch_dynamics_data(access_token, entity="accounts"):
    endpoint = f"{DYNAMICS_URL}/api/data/{API_VERSION}/{entity}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    response = requests.get(endpoint, headers=headers)
    return response.json()

# Use the token to call Dynamics 365 API
access_token = get_interactive_token()
data = fetch_dynamics_data(access_token)  # Reuse fetch_dynamics_data from earlier
print(data)