import pyodbc
import pandas as pd

print(pyodbc.drivers())
# Define connection string (Modify as per your server details)
conn_str = "Provider=MSOLAP.8;Integrated Security=SSPI;Persist Security Info=True;Initial Catalog=Azure Dashboard;Data Source=AzureDashBoardAS;MDX Compatibility=1;Safety Options=2;MDX Missing Member Mode=Error;Update Isolation Level=2"

# Connect to the Analysis Services Database
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Define MDX Query to get Top 10 Azure Consume Revenue
mdx_query = """
SELECT 
    NON EMPTY { [Measures].[Azure Consume Revenue] } ON COLUMNS,
    NON EMPTY { TOPCOUNT([Customer].[Customer Name].MEMBERS, 10, [Measures].[Azure Consume Revenue]) } ON ROWS
FROM [Your_Cube_Name]
"""

# Execute the query
cursor.execute(mdx_query)

# Fetch and display results
columns = [column[0] for column in cursor.description]
data = cursor.fetchall()

# Convert to DataFrame for easy display
df = pd.DataFrame(data, columns=columns)

# Display top 10 records
print(df)

# Close connection
cursor.close()
conn.close()
