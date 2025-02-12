import requests
import json
from azure.identity import DefaultAzureCredential

# ----------------------- Configuration -----------------------

# Power BI REST API endpoint
SCOPE = ['https://analysis.windows.net/powerbi/api/.default']

# Power BI dataset details
WORKSPACE_NAME = 'MSXIConsumptionAzBz'  # Name of your workspace
DATASET_ID = 'YOUR_ACTUAL_DATASET_GUID'  # Replace with the valid GUID

# ----------------------- Authentication -----------------------

def get_access_token():
    """Obtain an access token using DefaultAzureCredential."""
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token(*SCOPE)
        return token.token
    except Exception as e:
        raise Exception(f"Failed to obtain access token: {str(e)}")

# ----------------------- Execute Query -----------------------

def execute_dax_query(access_token, dax_query):
    """
    Execute a DAX query against the specified Power BI dataset.

    :param access_token: OAuth2 access token
    :param dax_query: The DAX query string to execute
    :return: Query results as JSON
    """
    url = f'https://api.powerbi.com/v1.0/myorg/datasets/{DATASET_ID}/executeQueries'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    payload = {
        "queries": [
            {
                "query": dax_query
            }
        ],
        "serializerSettings": {
            "includeNulls": True
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed with status code {response.status_code}: {response.text}")

# ----------------------- Main Function -----------------------

def main():
    try:
        # Step 1: Authenticate and get access token
        token = get_access_token()
        print("Access token obtained successfully.")

        # Step 2: Define your DAX query
        dax_query = """
        EVALUATE
        SUMMARIZECOLUMNS(
            'TableName'[Column1],
            'TableName'[Column2],
            "Total Sales", SUM('TableName'[SalesAmount])
        )
        """
        # Verify that 'TableName' columns exist in your dataset.
        # Step 3: Execute the DAX query
        query_result = execute_dax_query(token, dax_query)
        print("Query executed successfully.")

        # Step 4: Process and display the results
        # This assumes a specific structure; adjust according to your query
        for table in query_result.get('results', []):
            for rows in table.get('tables', []):
                columns = rows.get('columns', [])
                data = rows.get('rows', [])
                # Print column headers
                headers = [col.get('name') for col in columns]
                print('\t'.join(headers))
                # Print each row
                for row in data:
                    print('\t'.join(str(item) for item in row))

    except Exception as e:
        print(f"An error occurred: {e}")

# ----------------------- Entry Point -----------------------

if __name__ == '__main__':
    main()