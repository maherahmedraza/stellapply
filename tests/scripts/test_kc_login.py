from keycloak import KeycloakAdmin, KeycloakOpenID
from src.core.config import settings


def test_login():
    print("Testing Keycloak login directly...")
    admin = KeycloakAdmin(
        server_url=settings.keycloak.URL,
        username=settings.keycloak.ADMIN_USER,
        password=settings.keycloak.ADMIN_PASSWORD,
        realm_name="master",
        verify=True,
    )
    admin.realm_name = settings.keycloak.REALM

    email = "debug_test_kcsync_final@example.com"
    password = "Password123!"

    # 1. Ensure user exists
    user = admin.get_users({"email": email})
    if not user:
        print(f"User {email} not found in Keycloak.")
        return

    user_id = user[0]["id"]
    print(f"User ID: {user_id}")

    # 2. Reset password
    print("Resetting password...")
    admin.set_user_password(user_id, password, temporary=False)

    # 3. Try to get token
    print("Trying to get token...")
    openid = KeycloakOpenID(
        server_url=settings.keycloak.URL,
        client_id=settings.keycloak.CLIENT_ID,
        realm_name=settings.keycloak.REALM,
        client_secret_key=settings.keycloak.CLIENT_SECRET,
    )

    try:
        token = openid.token(email, password)
        print("Login SUCCESS!")
        print(f"Access Token exists: {'access_token' in token}")
    except Exception as e:
        print(f"Login FAILED: {str(e)}")


if __name__ == "__main__":
    test_login()
