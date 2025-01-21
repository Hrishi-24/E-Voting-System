import mysql.connector
import bcrypt

def connect_to_db():
    """Establish a connection to the MySQL database."""
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with MySQL username
        password="--------",  # Replace with MySQL password
        database="evoting"  # Replace with database name
    )

def register_user(username, password):
    """Register a new user in the database with hashed password."""
    conn = None
    cursor = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        # Check if the username already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result[0] > 0:
            return "Username already exists. Please choose a different username."
        
        # Hash the password and insert the new user
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        return "User registered successfully!"
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def login_user(username, password):
    """Authenticate a user and return their user_id if successful."""
    conn = None
    cursor = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result:
            # Ensure result[1] (hashed password) is treated as bytes
            stored_hashed_password = result[1]

            if isinstance(stored_hashed_password, str):
                # Convert it back to bytes if it is returned as a string
                stored_hashed_password = stored_hashed_password.encode('utf-8')

            # Compare the input password with the stored hashed password
            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                return result[0]  # Return the user_id
        return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()