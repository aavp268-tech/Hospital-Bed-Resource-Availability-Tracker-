import bcrypt
from config.db import get_db, ADMINS

admins_collection = get_db()[ADMINS]


# Admin registration
def register_admin(username, password):

    # Check if username already exists
    existing_admin = admins_collection.find_one({
        "username": username
    })

    if existing_admin:
        return False, "Username already exists"

    # Hash the password
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    # Create admin data
    admin_data = {
        "username": username,
        "password_hash": password_hash
    }

    # Save admin to MongoDB
    admins_collection.insert_one(admin_data)

    return True, "Admin registered successfully"

# Admin login
def login_admin(username, password):

    # Find admin
    admin = admins_collection.find_one({
        "username": username
    })

    if not admin:
        return False, "Admin not found"

    # Check password
    password_matches = bcrypt.checkpw(
        password.encode("utf-8"),
        admin["password_hash"]
    )

    if password_matches:
        return True, "Login successful"

    return False, "Incorrect password"
result = login_admin("testadmin", "test123")
print(result)
