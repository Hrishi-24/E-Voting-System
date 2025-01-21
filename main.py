from user_management import register_user, login_user
from voting_system import cast_vote, get_results

def main():
    print("Welcome to the E-Voting System!")
    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            username = input("Enter username: ")
            password = input("Enter password: ")
            register_user(username, password)
        elif choice == "2":
            username = input("Enter username: ")
            password = input("Enter password: ")
            user_id = login_user(username, password)

            if user_id:
                print("\n1. Cast Vote\n2. View Results\n3. Logout")
                action = input("Enter your choice: ")

                if action == "1":
                    candidate_id = input("Enter candidate ID to vote for: ")
                    cast_vote(user_id, int(candidate_id))
                elif action == "2":
                    get_results()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
