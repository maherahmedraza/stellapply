from src.modules.identity.infrastructure.keycloak import KeycloakProvider
from src.core.config import settings


def manual_create():
    p = KeycloakProvider()
    try:
        uid = p.create_user("manual@example.com", "Password123!", "Manual User")
        print(f"User created with ID: {uid}")
    except Exception as e:
        print(f"Error creating user: {str(e)}")


if __name__ == "__main__":
    manual_create()
