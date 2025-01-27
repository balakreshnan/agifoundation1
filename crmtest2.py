from sys import path
path.append('C:\\Program Files\\Microsoft.NET\\ADOMD.NET\\160')

from pyadomd import Pyadomd

# https://github.com/S-C-O-U-T/Pyadomd

conn_str = 'Provider=MSOLAP;Data Source=AzureDashBoardAS;Catalog=Azure Dashboard;'
# query = """EVALUATE Product"""
query = """EVALUATE TPAccountFact"""
#query = """EVALUATE AzureDashBoardAS"""

# query = """
# SELECT 
#     NON EMPTY { [Measures].[Azure Consume Revenue] } ON COLUMNS,
#     NON EMPTY { TOPCOUNT([Customer].[Customer Name].MEMBERS, 10, [Measures].[Azure Consume Revenue]) } ON ROWS
# FROM [Azure Dashboard Model]
# """

with Pyadomd(conn_str) as conn:
    with conn.cursor().execute(query) as cur:
        print(cur.fetchall())