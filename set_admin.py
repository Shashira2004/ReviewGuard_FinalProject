import firebase_admin
from firebase_admin import credentials, auth

# Path to your service account JSON
cred = credentials.Certificate("artifacts/reviewguard-310f6-firebase-adminsdk-fbsvc-7d1e2ee5d6.json")
firebase_admin.initialize_app(cred)

# Replace this with the UID of the user you want to make admin
uid = "Vm7WA4PyF4gel9O9fyAV19zpQCB2"

# Set custom claim
auth.set_custom_user_claims(uid, {'admin': True})

print(f"User {uid} is now an admin.")
