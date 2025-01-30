from sys import path
path.append('C:\\Program Files\\Microsoft.NET\\ADOMD.NET\\160')

from pyadomd import Pyadomd

# https://github.com/S-C-O-U-T/Pyadomd

conn_str = 'Provider=MSOLAP;Data Source=MSXIConsumptionAzBz;Catalog=MXSIAnalyst-Consumption;'
# query = """EVALUATE Product"""
# query = """EVALUATE TPAccountFact"""
#query = """EVALUATE AzureDashBoardAS"""
print('----------------- All Databases, Cube, Tables')
query = """
SELECT 
    [CATALOG_NAME] AS [Database], 
    [CUBE_NAME] AS [Cube], 
    [MEASUREGROUP_NAME] AS [Table] 
FROM $SYSTEM.MDSCHEMA_MEASUREGROUPS
"""

with Pyadomd(conn_str) as conn:
    with conn.cursor().execute(query) as cur:
        # print(cur.fetchall())
        for row in cur.fetchall():
            print(row)

print('----------------- measures')
query = """
SELECT 
    [MEASUREGROUP_NAME], 
    [MEASURE_NAME]
FROM $SYSTEM.MDSCHEMA_MEASURES
WHERE [MEASUREGROUP_NAME] = 'Azure Consumed Revenue'
"""

with Pyadomd(conn_str) as conn:
    with conn.cursor().execute(query) as cur:
        # print(cur.fetchall())
        for row in cur.fetchall():
            print(row)

print('----------------- dimensions for Cube Model')
query = """
SELECT 
    *
FROM $SYSTEM.MDSCHEMA_DIMENSIONS
WHERE [CUBE_NAME] = 'Model'
"""

with Pyadomd(conn_str) as conn:
    with conn.cursor().execute(query) as cur:
        # print(cur.fetchall())
        for row in cur.fetchall():
            print(row)

print('----------------- Total Revenue data')

# query = """
# SELECT 
#     { 
#         [Measures].[Azure Consumed Revenue MoM $], 
#         [Measures].[Azure Consumed Revenue MoM %] 
#     } ON COLUMNS, 
#     TOPCOUNT(
#         [Account Information].[ATU Group Manager].Members, 
#         10, 
#         [Measures].[Azure Consumed Revenue MoM %]
#     ) ON ROWS
# FROM [Model]
# """

query = """
SELECT 
    { 
        [Measures].[Azure Consumed Revenue MoM $], 
        [Measures].[Azure Consumed Revenue MoM %]
    } ON COLUMNS
FROM [Model]
WHERE ([Account Information].[TPID].["830434"])
"""
# WHERE ([Account Information].[TPAccountName] == 'Accenture')
# WHERE ([Account Information].[Sales Unit].&["USA - West & Midwest"])

with Pyadomd(conn_str) as conn:
    with conn.cursor().execute(query) as cur:
        print(cur.fetchall())
        # for row in cur.fetchall():
        #     print(row)