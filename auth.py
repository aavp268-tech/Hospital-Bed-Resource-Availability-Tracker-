"""Admin registration and login, linked to a hospital.

Fix over the previous version: register_admin() did not store which hospital
the admin belongs to, and login_admin() did not return it either — so the
admin dashboard had no way to know whose numbers to show or update.

Usage:
    ok, message = register_admin("kem_admin", "secret123", "KEM Hospital")
    ok, result  = login_admin("kem_admin", "secret123")
    # result is either an error message (ok=False) or
    # {"username": ..., "hospital_name": ...} (ok=True)
"""
import bcrypt

from config.db import ADMINS, HOSPITALS, get_db

admins_collection = get_db()[ADMINS]
hospitals_collection = get_db()[HOSPITALS]


def register_admin(username, password, hospital_name):
    """Create an admin account tied to one hospital.

    Returns (True, message) on success, (False, message) on failure.
    Known limitation: anyone can register as any hospital, with no approval
    step. Fine for a student demo; would need an invite code or an approval
    step for real use.
    """
    if not username or not password:
        return False, "Username and password are required"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    if admins_collection.find_one({"username": username}):
        return False, "Username already exists"

    if not hospitals_collection.find_one({"hospital_name": hospital_name}):
        return False, f"Unknown hospital: {hospital_name}"

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    admins_collection.insert_one({
        "username": username,
        "password_hash": password_hash,
        "hospital_name": hospital_name,
    })
    return True, "Admin registered successfully"


def login_admin(username, password):
    """Check credentials.

    Returns (True, {"username": ..., "hospital_name": ...}) on success,
    (False, message) on failure.
    """
    admin = admins_collection.find_one({"username": username})
    if not admin:
        return False, "Admin not found"

    if not bcrypt.checkpw(password.encode("utf-8"), admin["password_hash"]):
        return False, "Incorrect password"

    return True, {"username": admin["username"], "hospital_name": admin["hospital_name"]}