import pg8000  # type: ignore

def get_connection():
    try:
        conn = pg8000.connect(
            database="photon",
            user="postgres",
            password="student",
            host="127.0.0.1",
            port=5432,
        )
        return conn
    except Exception as e:
        print("Error connecting to PostgreSQL:", e)
        return False

def clear_players_table():
    """
    Drops the players table if it exists.
    """
    conn = get_connection()
    if not conn:
        print("Failed to establish connection for clearing players table.")
        return
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS players;")
    conn.commit()
    cursor.close()
    conn.close()
    print("Players table cleared.")

def add_column_if_missing(cursor, table_name, column_name, definition):
    """
    Checks if a column exists in a table, and if not, alters the table to add it.
    """
    check_query = """
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = %s AND column_name = %s;
    """
    cursor.execute(check_query, (table_name, column_name))
    result = cursor.fetchone()
    if not result:
        alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition};"
        cursor.execute(alter_query)
        print(f"Added column '{column_name}' with definition '{definition}' to {table_name}.")

def create_players_table():
    """
    Creates the players table if it doesn't exist, and alters it to ensure required columns exist.
    This preserves existing data.
    """
    conn = get_connection()
    if not conn:
        print("Failed to establish connection for table creation.")
        return
    cursor = conn.cursor()

    # Create the table if it doesn't exist.
    create_query = """
    CREATE TABLE IF NOT EXISTS players (
        id SERIAL PRIMARY KEY,
        player_id VARCHAR(50) UNIQUE,
        name VARCHAR(100),
        equipment_id INTEGER UNIQUE
    );
    """
    cursor.execute(create_query)
    conn.commit()  # Ensure table exists before checking columns

    # Check for missing columns and add them if needed.
    try:
        add_column_if_missing(cursor, "players", "team", "VARCHAR(50)")
        add_column_if_missing(cursor, "players", "name", "VARCHAR(100)")
    except Exception as e:
        print("Error altering table to add missing columns:", e)

    conn.commit()
    cursor.close()
    conn.close()
    print("Players table ensured and updated in database.")

def get_player_code_name(player_id):
    """
    Returns the code name associated with the given player_id,
    or None if the player is not found.
    """
    conn = get_connection()
    if not conn:
        print("Failed to establish connection for retrieving player code name.")
        return None
    cursor = conn.cursor()
    query = "SELECT name FROM players WHERE player_id = %s;"
    cursor.execute(query, (player_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result[0]
    return None

def get_player_count(team):
    """
    Returns the number of players already registered for the given team.
    """
    conn = get_connection()
    if not conn:
        return 0
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM players WHERE team = %s;"
    cursor.execute(query, (team,))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count

def player_exists(player_id):
    """
    Returns True if a player with the given player_id exists in the database.
    """
    conn = get_connection()
    if not conn:
        print("Failed to establish connection to check player ID uniqueness.")
        return False
    cursor = conn.cursor()
    query = "SELECT id FROM players WHERE player_id = %s;"
    cursor.execute(query, (player_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None

def insert_player(player_id, name, equipment_id, team):
    """
    Inserts a new player record.
    Equipment ID is checked for uniqueness.
    Assumes equipment_id can be converted to an integer.
    """
    try:
        equipment_id_int = int(equipment_id)
    except ValueError:
        print(f"Invalid equipment_id '{equipment_id}'. It must be an integer.")
        return

    conn = get_connection()
    if not conn:
        print("Failed to establish connection for inserting player.")
        return
    cursor = conn.cursor()
    # Check if equipment_id is already in use.
    check_query = "SELECT id FROM players WHERE equipment_id = %s;"
    cursor.execute(check_query, (equipment_id_int,))
    result = cursor.fetchone()
    if result:
        print(f"Equipment ID {equipment_id_int} is already in use. Insertion aborted.")
        cursor.close()
        conn.close()
        return

    insert_query = """
    INSERT INTO players (player_id, name, equipment_id, team)
    VALUES (%s, %s, %s, %s);
    """
    cursor.execute(insert_query, (player_id, name, equipment_id_int, team))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Inserted player {player_id} into database on team {team} with equipment ID {equipment_id_int}.")

def update_equipment_id(player_id, equipment_id):
    """
    Updates the equipment_id for an existing player.
    """
    try:
        equipment_id_int = int(equipment_id)
    except ValueError:
        print(f"Invalid equipment_id '{equipment_id}'. It must be an integer.")
        return

    conn = get_connection()
    if not conn:
        print("Failed to establish connection for updating player.")
        return
    cursor = conn.cursor()
    # Ensure the new equipment_id is not used by another player.
    query = "SELECT id FROM players WHERE equipment_id = %s AND player_id <> %s;"
    cursor.execute(query, (equipment_id_int, player_id))
    result = cursor.fetchone()
    if result:
        print(f"Equipment ID {equipment_id_int} is already in use by another player. Update aborted.")
        cursor.close()
        conn.close()
        return
    update_query = "UPDATE players SET equipment_id = %s WHERE player_id = %s;"
    cursor.execute(update_query, (equipment_id_int, player_id))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Updated player {player_id} with equipment ID {equipment_id_int}.")

if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("Connection to PostgreSQL established successfully.")
    else:
        print("Connection to PostgreSQL encountered an error.")
    
    # Uncomment the line below to clear the players table if needed.
    # clear_players_table()
    
    # This call will create the table if it doesn't exist and update missing columns.
    create_players_table()
