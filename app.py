from flask import Flask, render_template, request, redirect, session, url_for, flash, get_flashed_messages, Response
from user_management import register_user, login_user
from voting_system import cast_vote, get_results
from werkzeug.security import check_password_hash
import bcrypt

from functools import wraps
from twilio.rest import Client
from random import randint
import mysql.connector

def connect_to_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='evoting'
    )



def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated_function


def sync_voters_table():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Insert missing voters from `users` into `voters`
        cursor.execute("""
            INSERT INTO voters (name, email, phone, voter_id)
            SELECT username, email, phone, voter_id
            FROM users
            WHERE voter_id NOT IN (SELECT voter_id FROM voters);
        """)
        conn.commit()
        print("Voters table synced successfully.")
    except Exception as e:
        print(f"Error syncing voters table: {e}")
    finally:
        cursor.close()
        conn.close()

# Call this function during server startup
sync_voters_table()



def format_phone_number(phone):
    # Add +91 as default country code for India if not included
    if not phone.startswith('+'):
        phone = f"+91{phone}" 
    return phone


def send_otp(phone, otp):
    """
    Sends an OTP to the specified phone number using Twilio SMS API.

    Args:
        phone (str): The recipient's phone number.
        otp (str): The One-Time Password to be sent.

    Returns:
        bool: True if the SMS was sent successfully, False otherwise.
    """
    # Twilio credentials
    account_sid = '---------'  # Replace with Twilio Account SID
    auth_token = '--------'    # Replace with Twilio Auth Token
    client = Client(account_sid, auth_token)
    twilio_phone = '+000000000000'  # Replace with Twilio phone number

    # Initialize the Twilio client
    client = Client(account_sid, auth_token)

    try:
        formatted_phone = format_phone_number(phone)  # Format the phone number
        message = client.messages.create(
            body=f"Your OTP is {otp}. Please do not share it with anyone.",
            from_="+0000000000",  # Replace with Twilio phone number
            to=formatted_phone
        )
        print(f"OTP sent successfully to {formatted_phone}")
        return True
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return False
    

def get_voted_candidate_data():
    candidate_id = session.get('voted_candidate_id')  # Fetch the voted candidate's ID from session

    if not candidate_id:
        return None  # No candidate selected

    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name, party FROM candidates WHERE id = %s", (candidate_id,))
        candidate = cursor.fetchone()

        cursor.close()
        conn.close()

        return candidate
    except Exception as e:
        print(f"Error fetching candidate data: {e}")
        return None


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change to a secure random key in production

@app.route('/')
def home():
    return render_template('index.html')

# Temporary dictionary to store OTPs for verification
otp_store = {}


# Fixed admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Hrishi@24" 


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validate credentials
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect('/admin_dashboard')
        else:
            flash("Invalid username or password.", "error")
            return render_template('admin_login.html')

    return render_template('admin_login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        phone = request.form.get('phone')
        email = request.form.get('email')
        voter_id = request.form.get('voter_id')

        if not username or not password or not phone or not voter_id:
            return render_template('register.html', error="All fields are required.")

        # Generate OTP and store it temporarily
        otp = str(randint(100000, 999999))
        otp_store[phone] = otp

        session['phone'] = phone
        session['email'] = email
        session['username'] = username
        session['password'] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        session['voter_id'] = voter_id

        # Send OTP via Twilio
        send_otp(phone, otp)

        # Redirect to OTP verification page
        return redirect('/verify-otp')

    return render_template('register.html')



@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    phone = session.get('phone')
    if not phone:
        return redirect('/register')  # Redirect back to registration if phone not in session
    
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        
        # Check if OTP matches
        if otp_store.get(phone) == user_otp:
            try:
                # Store user in the database
                conn = connect_to_db()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password, phone, email, voter_id) VALUES (%s, %s, %s, %s, %s)",
                    (session['username'], session['password'], session['phone'], session['email'], session['voter_id']))
                conn.commit()
                
                # Clear OTP after successful registration
                otp_store.pop(phone, None)
                
                return redirect('/login')
            except Exception as e:
                return f"Error: {e}", 500
            finally:
                cursor.close()
                conn.close()
        else:
            return render_template('verify_otp.html', error="Invalid OTP", phone=phone)

    return render_template('verify_otp.html', phone=phone)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        try:
            # Fetch user details from the database
            conn = connect_to_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            # Check if user exists
            if not user:
                return render_template('login.html', error="Invalid username or password.")
            
            # Verify password using bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                session['user_id'] = user['id']
                return redirect('/vote')
            else:
                return render_template('login.html', error="Invalid username or password.")
            
        except Exception as e:
            print(f"Error during login: {e}")
            return render_template('login.html', error="An error occurred during login.")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('login.html')


@app.route('/vote', methods=['GET'])
def vote_page():
    candidates = []
    if request.method == 'POST':
        # Check if 'candidate_id' is in form data
        candidate_id = request.form.get('candidate_id')

        if not candidate_id:
                return render_template('vote.html', candidates=candidates, error="Please select a candidate.")

        voter_id = session.get('user_id')  # Assuming user is logged in
        
        # Proceed with the vote casting logic
        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            
            query = "INSERT INTO votes (candidate_id, voter_id) VALUES (%s, %s)"
            cursor.execute(query, (candidate_id, voter_id))
            conn.commit()
            
            print("Vote successfully inserted!")  # Debugging line
            return redirect('/results')
        except Exception as e:
            print(f"Error casting vote: {e}")
            return "An error occurred while casting your vote.", 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    else:
        # Handle GET request to render voting page with candidates
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM candidates")
        candidates = cursor.fetchall()
        return render_template('vote.html', candidates=candidates)


@app.route('/vote', methods=['POST'])
def vote():
    candidate_id = request.form.get('candidate_id')
    print("Received candidate_id:", candidate_id)


    if not candidate_id:
        flash("No candidate selected. Please try voting again.", "error")
        return redirect('/vote')

    # Store candidate_id in the session
    session['voted_candidate_id'] = candidate_id
    print("Stored candidate_id in session:", session.get('voted_candidate_id'))  # Debugging output

    # Voter details from session
    voter_id = session.get('voter_id')
    name = session.get('username')
    email = session.get('email', 'no_email@example.com')
    phone = session.get('phone')
    print("Voter details:", name, email, phone, voter_id)

    print(f"Inserting vote: Name={name}, Email={email}, Phone={phone}, Voter_ID={voter_id}, Candidate_ID={candidate_id}")

    # Insert vote into database
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO votes (name, email, phone, voter_id, candidate_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, phone, voter_id, candidate_id))
        conn.commit()

        print("Vote successfully inserted.")
    except Exception as e:
        flash(f"Error recording vote: {e}", "error")
        print(f"Error during vote insertion: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect('/confirm_vote')



@app.route('/confirm_vote', methods=['GET', 'POST'])
def vote_confirmation():
    # Get the selected candidate's ID from the session
    candidate_id = session.get('voted_candidate_id')  # Retrieve the selected candidate's ID from session
    
    if not candidate_id:
        return render_template('confirm_vote.html', candidate=None)

    try:
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)

        # Fetch the candidate details using the candidate_id from the session
        cursor.execute("SELECT name, party FROM candidates WHERE id = %s", (candidate_id,))
        candidate = cursor.fetchone()

        if not candidate:
            flash("Invalid candidate selection.", "error")
            candidate = None
    except Exception as e:
        flash(f"Error fetching candidate details: {e}", "error")
        candidate = None
    finally:
        cursor.close()
        conn.close()

    return render_template('confirm_vote.html', candidate=candidate)



@app.route('/results', methods=['GET'])
def results():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    try:
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)

        # Fetch results query
        cursor.execute("""
            SELECT 
                c.name AS candidate_name,
                c.party AS candidate_party,
                COUNT(v.id) AS total_votes
            FROM candidates c
            LEFT JOIN votes v ON c.id = v.candidate_id
            GROUP BY c.id, c.name, c.party;
        """)
        results = cursor.fetchall()
        print("Election Results:", results)  # Debugging output

        if not results:
            flash("No results available. No votes have been recorded yet.", "info")
            results = []

    except Exception as e:
        flash(f"Error fetching results: {e}", "error")
        results = []

    finally:
        cursor.close()
        conn.close()

    return render_template('results.html', results=results)



@app.route('/analytics')
def analytics():
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch total votes
    cursor.execute("SELECT COUNT(*) AS total_votes FROM votes")
    total_votes = cursor.fetchone()['total_votes']
    
    # Fetch votes per candidate
    cursor.execute("""
        SELECT c.name, COUNT(v.candidate_id) AS votes
        FROM candidates c
        LEFT JOIN votes v ON c.id = v.candidate_id
        GROUP BY c.id
    """)
    results = cursor.fetchall()
    
    # Calculate percentages
    for row in results:
        row['percentage'] = round((row['votes'] / total_votes * 100), 2) if total_votes > 0 else 0
    
    cursor.close()
    conn.close()
    
    return render_template('analytics.html', results=results, total_votes=total_votes)



@app.route('/admin_dashboard')
@admin_required  # Ensure only logged-in admins can access
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash("Please log in to access the admin dashboard.", "error")
        return redirect('/admin/login')
    # Render the dashboard with the username
    return render_template('admin_dashboard.html', username=session.get('admin_username'))


@app.route('/voter_management', methods=['GET', 'POST'])
def voter_management():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    voters = []  # List to store combined data

    try:
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)

        # Fetch data from `users` and `voters` tables
        cursor.execute("""
            SELECT 
                u.username AS name,
                u.email AS email,
                u.phone AS phone,
                u.voter_id AS voter_id,
                1 AS is_registered,
                IF(v.voter_id IS NOT NULL, 1, 0) AS has_voted
            FROM users u
            LEFT JOIN voters v ON u.voter_id = v.voter_id
        """)
        voters = cursor.fetchall()
        for voter in voters:
            print(f"Fetched voter: {voter['name']}, {voter['email']}, {voter['phone']}, {voter['voter_id']}")


    except Exception as e:
        print(f"Error fetching voter data: {e}")
        flash(f"Error fetching data: {e}", "error")

    finally:
        cursor.close()
        conn.close()

    return render_template('voter_management.html', voters=voters, flash_messages=get_flashed_messages())



@app.route('/admin/candidates', methods=['GET', 'POST'])
def manage_candidates():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    conn = None
    cursor = None

    try:
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)  # Fetch results as dictionaries for easy template access

        if request.method == 'POST':
            # Add a new candidate
            name = request.form.get('name')
            party = request.form.get('party')
            bio = request.form.get('bio')

            if not name or not party or not bio:
                flash("All fields are required.", "error")
            else:
                try:
                    cursor.execute(
                        "INSERT INTO candidates (name, party, bio) VALUES (%s, %s, %s)",
                        (name, party, bio)
                    )
                    conn.commit()
                    flash("Candidate added successfully!", "success")
                except Exception as e:
                    flash(f"Error adding candidate: {e}", "error")
                return redirect('/admin/candidates')

        # Fetch all candidates
        cursor.execute("SELECT id, name, party, bio FROM candidates")
        candidates = cursor.fetchall()

    except Exception as e:
        flash(f"Error: {e}", "error")
        candidates = []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('candidates.html', candidates=candidates)



@app.route('/add_voter', methods=['GET', 'POST'])
def add_voter():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        voter_id = request.form['voter_id']

        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO voters (name, email, phone, voter_id) VALUES (%s, %s, %s, %s)",
                (name, email, phone, voter_id)
            )
            conn.commit()
            flash("Voter added successfully.", "success")
        except Exception as e:
            flash(f"Error: {e}", "error")
        finally:
            cursor.close()
            conn.close()

    return render_template('add_voter.html')



@app.route('/update_voter/<voter_id>', methods=['GET', 'POST'])
def update_voter(voter_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    try:
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'GET':
            # Fetch voter details for the provided voter_id
            cursor.execute("SELECT username AS name, email, phone, voter_id FROM users WHERE voter_id = %s", (voter_id,))
            voter = cursor.fetchone()
            print(f"Fetched voter for update (voter_id={voter_id}): {voter}")

            if not voter:
                flash(f"Voter with voter_id={voter_id} not found.", "error")
                return redirect('/voter_management')  # Redirect if voter not found

            return render_template('update_voter.html', voter=voter)

        elif request.method == 'POST':
            # Handle update logic
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')

            if not name or not email or not phone:
                flash("All fields are required.", "error")
                return redirect(f'/update_voter/{voter_id}')

            # Update voter details
            cursor.execute("""
                UPDATE users 
                SET username = %s, email = %s, phone = %s 
                WHERE voter_id = %s
            """, (name, email, phone, voter_id))
            conn.commit()

            flash(f"Voter with voter_id={voter_id} updated successfully.", "success")
            print(f"Updated voter with voter_id={voter_id}: Name={name}, Email={email}, Phone={phone}")
            return redirect('/voter_management')

    except Exception as e:
        flash(f"Error updating voter: {e}", "error")
        print(f"Error updating voter (voter_id={voter_id}): {e}")

    finally:
        cursor.close()
        conn.close()

    return redirect('/voter_management')



@app.route('/delete_voter/<voter_id>', methods=['POST'])
def delete_voter(voter_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    try:
        # Connect to the database
        conn = connect_to_db()
        cursor = conn.cursor()

        # Delete voter from the database
        cursor.execute("DELETE FROM users WHERE voter_id = %s", (voter_id,))
        conn.commit()

        # Flash success message
        flash(f"Voter with voter_id={voter_id} deleted successfully.", "success")
        print(f"Deleted voter with voter_id: {voter_id}")  # Debugging
    except Exception as e:
        # Handle errors and flash an error message
        flash(f"Error deleting voter: {e}", "error")
        print(f"Error deleting voter with voter_id={voter_id}: {e}")  # Debugging
    finally:
        cursor.close()
        conn.close()

    return redirect('/voter_management')



@app.route('/view_users', methods=['GET'])
def view_voters():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    try:
        # Connect to the database and fetch users
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, phone, voter_id FROM users")  # Correct column name
        voters = cursor.fetchall()
        print("Fetched voters:", voters)  # Debugging
    except Exception as e:
        print(f"Error fetching voters: {e}")
        voters = []
    finally:
        cursor.close()
        conn.close()

    return render_template('view_users.html', voters=voters)



@app.route('/admin/election', methods=['GET', 'POST'])
def manage_election():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    # If the form is submitted (POST)
    if request.method == 'POST':
        election_name = request.form['election_name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        try:
            conn = connect_to_db()
            cursor = conn.cursor()

            # Make sure to handle any unread results before executing another query
            cursor.execute("""
                INSERT INTO elections (election_name, start_date, end_date)
                VALUES (%s, %s, %s)
            """, (election_name, start_date, end_date))
            conn.commit()

            # Clear any unread results
            cursor.nextset()

            flash("Election created successfully.", "success")
        except Exception as e:
            flash(f"Error creating election: {e}", "error")
        finally:
            cursor.close()
            conn.close()

    # Fetch existing election details
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM elections ORDER BY start_date DESC")
        election = cursor.fetchone()
        cursor.nextset()  # Clear any unread results
    except Exception as e:
        flash(f"Error fetching election details: {e}", "error")
        election = None
    finally:
        cursor.close()
        conn.close()

    return render_template('election.html', election=election)



@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash("Logged out successfully.", "success")
    return redirect('/admin/login')


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()  # Clear all session data to log out
    flash("You have been logged out.", "success")
    return redirect('/login')  # Redirect to the login page


print("Registered Routes:")
for rule in app.url_map.iter_rules():
    print(rule)


if __name__ == '__main__':
    app.run(debug=True)
