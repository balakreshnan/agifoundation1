import pandas as pd
from sys import path
path.append('\\Program Files\\Microsoft.NET\\ADOMD.NET\\160')
from pyadomd import Pyadomd

# Define connection parameters
model_name = 'Azure Dashboard'
server_name = 'AzureDashBoardAS'

# Create connection string
connection_string = f'Provider=MSOLAP;Data Source={server_name};Catalog={model_name};'

# Define DAX query
dax_query = """
SELECT 
    [CATALOG_NAME] AS [Database], 
    [CUBE_NAME] AS [Cube], 
    [MEASUREGROUP_NAME] AS [Table] 
FROM $SYSTEM.MDSCHEMA_MEASUREGROUPS
"""

# Execute query and fetch results
with Pyadomd(connection_string) as conn:
    cursor = conn.cursor()
    result = cursor.execute(dax_query)
    df = pd.DataFrame(result.fetchone())

# Rename columns and display results
df.rename(columns={0: 'Category', 1: 'Total Sales'}, inplace=True)
print(df)
