from snowflake_client import get_connection

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
row = cursor.fetchone()
print(f"User:      {row[0]}")
print(f"Role:      {row[1]}")
print(f"Warehouse: {row[2]}")
conn.close()