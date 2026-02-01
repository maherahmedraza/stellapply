from keycloak import KeycloakAdmin
from src.core.config import settings


def init_keycloak():
    print(f"Connecting to Keycloak at {settings.keycloak.URL}...")

    # 1. Connect to master to manage realms
    master_admin = KeycloakAdmin(
        server_url=settings.keycloak.URL,
        username=settings.keycloak.ADMIN_USER,
        password=settings.keycloak.ADMIN_PASSWORD,
        realm_name="master",
        verify=True,
    )

    realms = [r["realm"] for r in master_admin.get_realms()]
    if settings.keycloak.REALM not in realms:
        print(f"Creating realm {settings.keycloak.REALM}...")
        master_admin.create_realm({"realm": settings.keycloak.REALM, "enabled": True})

    # 2. Connect specifically to the target realm to manage its clients
    # Even if we use master admin, we target the realm
    admin = KeycloakAdmin(
        server_url=settings.keycloak.URL,
        username=settings.keycloak.ADMIN_USER,
        password=settings.keycloak.ADMIN_PASSWORD,
        realm_name=settings.keycloak.REALM,
        user_realm_name="master",
        verify=True,
    )

    clients = admin.get_clients()
    client = next(
        (c for c in clients if c["clientId"] == settings.keycloak.CLIENT_ID), None
    )

    client_config = {
        "clientId": settings.keycloak.CLIENT_ID,
        "enabled": True,
        "publicClient": False,
        "directAccessGrantsEnabled": True,
        "standardFlowEnabled": True,
        "webOrigins": ["*"],
        "redirectUris": ["*"],
    }

    if not client:
        print(
            f"Creating confidental client {settings.keycloak.CLIENT_ID} in realm {settings.keycloak.REALM}..."
        )
        admin.create_client(client_config)
        client = [
            c
            for c in admin.get_clients()
            if c["clientId"] == settings.keycloak.CLIENT_ID
        ][0]
    else:
        print(
            f"Updating client {settings.keycloak.CLIENT_ID} in realm {settings.keycloak.REALM}..."
        )
        admin.update_client(client["id"], client_config)

    # Get secret
    secret = admin.get_client_secrets(client["id"])["value"]
    print(f"NEW_CLIENT_SECRET={secret}")

    print("Keycloak initialization complete.")


if __name__ == "__main__":
    init_keycloak()
