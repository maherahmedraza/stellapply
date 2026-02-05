from keycloak import KeycloakAdmin
from src.core.config import settings


def debug_keycloak_isolated():
    print(f"Connecting to {settings.keycloak.URL}...")

    # Get master realms to see what exists
    master_admin = KeycloakAdmin(
        server_url=settings.keycloak.URL,
        username=settings.keycloak.ADMIN_USER,
        password=settings.keycloak.ADMIN_PASSWORD,
        realm_name="master",
        verify=True,
    )
    realms = [r["realm"] for r in master_admin.get_realms()]
    print(f"Existing realms: {realms}")

    for r_name in realms:
        print(f"\n--- Realm: {r_name} ---")
        try:
            admin = KeycloakAdmin(
                server_url=settings.keycloak.URL,
                username=settings.keycloak.ADMIN_USER,
                password=settings.keycloak.ADMIN_PASSWORD,
                realm_name=r_name,
                user_realm_name="master",
                verify=True,
            )
            users = admin.get_users()
            print(f"Users: {[u['username'] for u in users]}")

            clients = admin.get_clients()
            target_ids = [
                c["clientId"]
                for c in clients
                if c["clientId"] == settings.keycloak.CLIENT_ID
            ]
            if target_ids:
                client = [
                    c for c in clients if c["clientId"] == settings.keycloak.CLIENT_ID
                ][0]
                print(
                    f"Client {settings.keycloak.CLIENT_ID} FOUND with ID: {client['id']}"
                )
            else:
                print(f"Client {settings.keycloak.CLIENT_ID} NOT FOUND")
        except Exception as e:
            print(f"Error accessing realm {r_name}: {str(e)}")


if __name__ == "__main__":
    debug_keycloak_isolated()
