import sqlite3
from getpass import getpass

DB = "mental_health.db"

# ----------------- ADMIN LOGIN -----------------
def admin_login():
    print("=== Admin Login ===")
    username = input("Username: ")
    password = getpass("Password: ")

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM users
        WHERE username=? AND password=? AND is_admin=1
    """, (username, password))
    user = cur.fetchone()
    conn.close()

    if user:
        print(f"Welcome, {username}!")
        return True
    else:
        print("Invalid admin credentials.")
        return False

# ----------------- VIEW USERS -----------------
def view_users():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, phone FROM users WHERE is_admin=0")
    users = cur.fetchall()
    conn.close()

    if not users:
        print("No users found.")
        return

    print("\n--- Users ---")
    for u in users:
        print(f"ID: {u[0]}, Username: {u[1]}, Email: {u[2]}, Phone: {u[3]}")
    print("------------\n")

# ----------------- ADD USER -----------------
def add_user():
    username = input("Enter username: ")
    email = input("Enter email: ")
    phone = input("Enter phone: ")
    password = getpass("Enter password: ")

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Check for duplicate email
    cur.execute("SELECT * FROM users WHERE email=?", (email,))
    if cur.fetchone():
        print("User with this email already exists!")
        conn.close()
        return

    cur.execute(
        "INSERT INTO users(username,email,phone,password) VALUES(?,?,?,?)",
        (username, email, phone, password)
    )
    conn.commit()
    conn.close()
    print("User added successfully!")

# ----------------- DELETE USER -----------------
def delete_user():
    user_id = input("Enter user ID to delete: ")
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=? AND is_admin=0", (user_id,))
    conn.commit()
    conn.close()
    print("User deleted successfully!")

# ----------------- UPDATE USER -----------------
def update_user():
    user_id = input("Enter user ID to update: ")

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=? AND is_admin=0", (user_id,))
    user = cur.fetchone()
    if not user:
        print("User not found.")
        conn.close()
        return

    print("Leave field empty to keep current value.")
    username = input(f"Username ({user[1]}): ") or user[1]
    email = input(f"Email ({user[2]}): ") or user[2]
    phone = input(f"Phone ({user[3]}): ") or user[3]
    password = getpass("Password (hidden): ") or user[4]

    cur.execute("""
        UPDATE users
        SET username=?, email=?, phone=?, password=?
        WHERE id=? AND is_admin=0
    """, (username, email, phone, password, user_id))
    conn.commit()
    conn.close()
    print("User updated successfully!")

# ----------------- VIEW SPECIFIC USER PREDICTIONS -----------------
def view_predictions():
    username = input("Enter the username to view predictions: ")

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username=? AND is_admin=0", (username,))
    user = cur.fetchone()
    if not user:
        print("User not found.")
        conn.close()
        return

    user_id = user[0]
    cur.execute("""
        SELECT addiction_score, addiction_level, health_risk, created_at
        FROM predictions
        WHERE user_id=?
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print(f"No predictions found for user '{username}'.")
        return

    print(f"\n--- Predictions for {username} ---")
    for r in rows:
        print(f"Score: {r[0]}, Level: {r[1]}, Health: {r[2]}, Date: {r[3]}")
    print("-------------------------------\n")

# ----------------- MAIN MENU -----------------
def admin_menu():
    while True:
        print("\n--- Admin Menu ---")
        print("1. View users")
        print("2. Add user")
        print("3. Delete user")
        print("4. Update user")
        print("5. View a user's predictions")
        print("6. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            view_users()
        elif choice == "2":
            add_user()
        elif choice == "3":
            delete_user()
        elif choice == "4":
            update_user()
        elif choice == "5":
            view_predictions()
        elif choice == "6":
            print("Exiting admin panel.")
            break
        else:
            print("Invalid choice, try again.")

# ----------------- RUN ADMIN -----------------
if __name__ == "__main__":
    if admin_login():
        admin_menu()