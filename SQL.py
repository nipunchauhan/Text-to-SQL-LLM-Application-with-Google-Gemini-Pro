import sqlite3
import os 

database_file = "database.sqlite"

if not os.path.exists(database_file):
    print(f"Error: Database file {database_file} not found.")
    exit()

try:
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"Found {len(tables)} tables:")
    for table in tables:
        print(f"- {table[0]}")
    
    print("\nTop 5 results from each table:")
    print("=" * 50)   
    # Show top 5 from each table
    for table in tables:
        table_name = table[0]
        print(f"\n{table_name}:")
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
            
    connection.commit()

except sqlite3.Error as e:
    print(f"Error: {e}")

finally:
    if 'connection' in locals() and connection:
        connection.close()