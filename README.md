
# E-VOTING SYSTEM

The E-Voting System is a software application designed to facilitate secure and efficient voting processes electronically. This project is implemented using Python as the primary programming language, with MySQL serving as the database management system for storing and retrieving election-related data. The system ensures user-friendly interfaces and robust backend functionalities for managing voters, candidates, elections, and voting processes.


# Key Features

## Voter Management:
- Add New Voters: Add new voters with details such as name, email, phone number, and voter ID.
- Update Voter Information: Modify voter details, such as contact information, when required.
- Delete Voters: Remove voters from the system when necessary.
## Candidate Management:
- Add Candidates: Add candidates with details like name, party, and biography.
- View Candidates: Display a list of all candidates participating in the election.
## Election Setup:
- Create and Configure Elections: Set up an election with details such as election name, start date, and end date.
- Update Election Details: Modify election configurations when required.
## Voting:
- Cast Votes: Allow registered voters to cast their votes for their preferred candidates.
- Secure Voting: Ensure each voter can only cast one vote using authentication mechanisms.
## Results and Analytics:
- View Live Results: Display real-time voting results, showing the votes received by each candidate.
- Election Analytics: Provide detailed statistics about the election, including voter turnout and percentage breakdowns of votes.
## Authentication and Authorization:
- User Registration and Login: Enable voters to register and log in using secure authentication mechanisms.
- Admin Login: Allow administrators to access advanced functionalities like managing voters, candidates, and elections.
- OTP Verification: Secure the registration process with one-time password (OTP) verification.
## Security and Validation:
- Implement validation for user inputs to ensure the integrity of stored data.
- Provide secure authentication for voters and admins to prevent unauthorized access.
## Reporting:
- Generate reports related to election outcomes, voter activity, and voting patterns.

# Technologies Used

**Backend::** Python, Flask

**Database:** MySQL

**Frontend:** HTML, CSS


# Routes Overview
 

| **Route**                      | **Description**                                |  
|--------------------------------|------------------------------------------------|  
| `/`                            | Home page with options to log in or register. |  
| `/register`                    | Voter registration page with OTP verification. |  
| `/verify-otp`                  | Verify OTP for voter registration. |  
| `/login`                       | Voter login page. |  
| `/vote`                        | Page to cast votes for candidates. |  
| `/confirm_vote`                | Displays vote confirmation message. |  
| `/results`                     | Displays live election results. |  
| `/analytics`                   | Election analytics and statistics page. |  
| `/admin/login`                 | Admin login page. |  
| `/admin_dashboard`             | Admin dashboard for managing the system. |  
| `/voter_management`            | Manage voters (add, update, delete voters). |  
| `/admin/candidates`            | Manage candidates (add, view candidates). |  
| `/add_voter`                   | Page to add a voter to the system. |  
| `/update_voter/<voter_id>`     | Update details of a specific voter. |  
| `/delete_voter/<voter_id>`     | Delete a voter from the system. |  
| `/view_users`                  | View all registered users. |  
| `/admin/election`              | Election setup and configuration page. |  
| `/admin/logout`                | Log out from the admin account. |  
| `/logout`                      | Log out from the voter account. |  

# Setup Instructions

Follow the steps below to set up and run the E-Voting System project on your local machine:

### Prerequisites
1. **Python**: Ensure you have Python 3.x installed. [Download Python](https://www.python.org/downloads/)
2. **MySQL**: Install MySQL Server and MySQL Workbench. [Download MySQL](https://dev.mysql.com/downloads/)
3. **Required Python Libraries**: Install the necessary Python packages using `pip`.

## Installation Steps

#### 1. Clone the Repository
Clone this repository to your local machine:

    git clone https://github.com/Hrishi-24/E-Voting-System.git

### 2. Navigate to the project directory
Move into the project folder:

    cd e-voting-system
### 3. Install dependencies
Install the required Python packages using pip:

    pip install -r requirements.txt
### 4. Set up the MySQL database
- Create a new database named evoting:

- Import the schema.sql file to set up the necessary tables:

### 5. Run the application
Start the Flask application:

    python app.py
### 6. Access the application
Open your web browser and navigate to:

    http://127.0.0.1:5000








