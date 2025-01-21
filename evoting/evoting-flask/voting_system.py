import mysql.connector

from db_config import get_db_connection

def cast_vote(user_id, candidate_id):
    db = get_db_connection()
    cursor = db.cursor()



    try:
        # Check if the user has already voted
        cursor.execute("SELECT has_voted FROM users WHERE id = %s", (user_id,))
        if cursor.fetchone()[0]:
            print("You have already voted.")
            return

        # Update the candidate's vote count
        cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE id = %s", (candidate_id,))
        
        # Mark the user as having voted
        cursor.execute("UPDATE users SET has_voted = TRUE WHERE id = %s", (user_id,))
        
        db.commit()
        print("Vote cast successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        db.close()

def get_results():
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT name, votes FROM candidates ORDER BY votes DESC")
        results = cursor.fetchall()

        print("Election Results:")
        for candidate in results:
            print(f"{candidate[0]}: {candidate[1]} votes")
    finally:
        cursor.close()
        db.close()
