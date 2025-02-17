import psycopg2
from psycopg2 import sql

# Define connection parameters
connection_params = {
    'dbname': 'photon',
    'user': 'student',
    'password': 'student',
    'host': 'localhost',
    'port': '7501'
}

cursor = None
conn = None

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(**connection_params)
    cursor = conn.cursor()

    # Execute a query 
    cursor.execute("SELECT version();")

    # Fetch and display the result
    version = cursor.fetchone()
    print(f"Connected to - {version}")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                codename VARCHAR(30),
            );
        ''')

    # Insert sample data
    cursor.execute('''
        INSERT INTO players (id, codename)
        VALUES (%s, %s);
    ''', ('500', 'BhodiLi'))

    # Commit the changes
    conn.commit()

    # Fetch and display data from the table
    cursor.execute("SELECT * FROM players;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
except Exception as error:
    print(f"Error connecting to PostgreSQL database: {error}")

finally:
    # Close the cursor and connection
    if cursor:
        cursor.close()
    if conn:
        conn.close()