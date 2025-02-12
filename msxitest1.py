import pyodbc
import pandas as pd
from typing import List, Optional

class SemanticModelConnector:
    def __init__(self, server: str, database: str):
        """
        Initialize connection to semantic model using pyodbc
        
        Parameters:
        server (str): Server name (e.g., 'your-server.analysis.windows.net')
        database (str): Database name
        """
        self.server = server
        self.database = database
        self.conn = None
        
    def connect(self, timeout: int = 30) -> None:
        """
        Establish connection to the database using Windows authentication
        
        Parameters:
        timeout (int): Connection timeout in seconds
        """
        connection_string = (
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server={self.server};"
            f"Database={self.database};"
            "Trusted_Connection=yes;"
            "Encrypt=yes;"  # Added for Azure connections
            "TrustServerCertificate=yes;"  # Allows self-signed certificates
            f"Timeout={timeout};"
        )
        
        try:
            self.conn = pyodbc.connect(connection_string)
            print(f"Successfully connected to {self.database}")
        except pyodbc.InterfaceError as e:
            raise Exception(f"Interface error: {str(e)}")
        except pyodbc.DatabaseError as e:
            raise Exception(f"Database error: {str(e)}")
        except pyodbc.Error as e:
            raise Exception(f"Failed to connect: {str(e)}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")

    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute a query and return results as a pandas DataFrame
        
        Parameters:
        query (str): SQL or DAX query to execute
        
        Returns:
        pandas.DataFrame: Query results
        """
        if not self.conn:
            raise Exception("Not connected. Call connect() first.")
            
        try:
            return pd.read_sql(query, self.conn)
        except pyodbc.Error as e:
            raise Exception(f"Query execution failed: {str(e)}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")

    def get_tables(self) -> List[str]:
        """
        Get list of available tables in the database
        
        Returns:
        List[str]: List of table names
        """
        if not self.conn:
            raise Exception("Not connected. Call connect() first.")
            
        cursor = self.conn.cursor()
        tables = []
        
        try:
            # Query for table names
            for row in cursor.tables():
                if row.table_type == 'TABLE':
                    tables.append(row.table_name)
        except pyodbc.Error as e:
            raise Exception(f"Failed to retrieve tables: {str(e)}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")
        finally:
            cursor.close()
            
        return tables

    def get_table_columns(self, table_name: str) -> List[str]:
        """
        Get list of columns for a specific table
        
        Parameters:
        table_name (str): Name of the table
        
        Returns:
        List[str]: List of column names
        """
        if not self.conn:
            raise Exception("Not connected. Call connect() first.")
            
        cursor = self.conn.cursor()
        columns = []
        
        try:
            # Query for column names
            for row in cursor.columns(table=table_name):
                columns.append(row.column_name)
        except pyodbc.Error as e:
            raise Exception(f"Failed to retrieve columns for table {table_name}: {str(e)}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")
        finally:
            cursor.close()
            
        return columns

    def close(self) -> None:
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            print("Connection closed")

def main():
    # Configuration
    config = {
        'server': 'MSXIConsumptionAzBz.analysis.windows.net',
        'database': 'MXSIAnalyst-Consumption'
    }
    
    # Initialize connector
    connector = SemanticModelConnector(**config)
    
    try:
        # Connect to the database
        connector.connect()
        
        # Example 1: List available tables
        print("\nAvailable tables:")
        tables = connector.get_tables()
        for table in tables:
            print(f"- {table}")
        
        # Example 2: Get columns for a specific table
        if tables:
            sample_table = tables[0]
            print(f"\nColumns in {sample_table}:")
            columns = connector.get_table_columns(sample_table)
            for column in columns:
                print(f"- {column}")
        
        # Example 3: Execute some queries
        queries = [
            """
            SELECT TOP 10 
                Product.ProductName,
                SUM(Sales.Amount) as TotalSales
            FROM Sales
            JOIN Product ON Sales.ProductID = Product.ProductID
            GROUP BY Product.ProductName
            ORDER BY TotalSales DESC
            """,
            """
            SELECT 
                Customer.Region,
                COUNT(DISTINCT Customer.CustomerID) as CustomerCount
            FROM Customer
            GROUP BY Customer.Region
            """
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\nExecuting query {i}...")
            df = connector.execute_query(query)
            
            print(f"Results shape: {df.shape}")
            print("\nFirst few rows:")
            print(df.head())
            
            # Optional: Save to CSV
            output_file = f"query_results_{i}.csv"
            df.to_csv(output_file, index=False)
            print(f"Results saved to {output_file}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        
    finally:
        # Always close the connection
        connector.close()

if __name__ == "__main__":
    main()