import asyncio
import sys
import os
import hashlib
from sqlalchemy import select

# Add project root to path
sys.path.append(os.getcwd())

from src.core.database.connection import AsyncSessionLocal
from src.modules.identity.domain.models import User, SubscriptionTier

# Import Resume to register it with SQLAlchemy for the relationship
from src.modules.resume.domain.models import Resume
from src.modules.identity.infrastructure.keycloak import KeycloakProvider
from src.core.security.encryption import encrypt_data
from src.core.security.hashing import get_password_hash


async def main():
    email = "de-user@stellapply.com"
    password = "Password1234!"

    print(f"Setting up user: {email}")

    # 1. Keycloak Setup
    try:
        kp = KeycloakProvider()
        # Note: getKeycloakAdmin might fail if admin credentials aren't in .env or correct
        # But let's try.
        admin = kp.get_admin_client()

        # Check if user exists
        user_id = admin.get_user_id(email)

        if not user_id:
            print("User not found in Keycloak. Creating...")
            user_id = admin.create_user(
                {
                    "email": email,
                    "username": email,
                    "enabled": True,
                    "firstName": "Demo",
                    "lastName": "User",
                    "credentials": [
                        {"value": password, "type": "password", "temporary": False}
                    ],
                    "emailVerified": True,
                }
            )
            print(f"Created Keycloak user: {user_id}")
        else:
            print(f"Keycloak user exists: {user_id}")
            # Reset password to ensure it matches what verify_user expects
            print("Resetting password...")
            admin.set_user_password(user_id, password, temporary=False)
            print("Password reset.")

    except Exception as e:
        print(f"Keycloak Error: {e}")
        # Proceed to Postgres anyway, although login requires Keycloak

    # 2. Postgres Setup
    try:
        async with AsyncSessionLocal() as session:
            email_hash = hashlib.sha256(email.lower().encode()).hexdigest()
            result = await session.execute(
                select(User).where(User.email_hash == email_hash)
            )
            user = result.scalars().first()

            if not user:
                print("User not found in Postgres. Creating...")
                email_encrypted = encrypt_data(email).encode()
                password_hash = get_password_hash(password)

                new_user = User(
                    email_encrypted=email_encrypted,
                    email_hash=email_hash,
                    password_hash=password_hash,
                    status="active",
                    tier=SubscriptionTier.FREE,
                    governance_metadata={
                        "classification": "restricted",
                        "retention": "permanent",
                        "consent_version": "1.0",
                    },
                )
                session.add(new_user)
                await session.commit()
                print("Created Postgres user.")
            else:
                print("Postgres user exists.")
                # Update password hash just in case
                new_hash = get_password_hash(password)
                if user.password_hash != new_hash:
                    print("Updating password hash in Postgres...")
                    user.password_hash = new_hash
                    await session.commit()
                    print("Updated.")
                else:
                    print("Password hash matches.")

    except Exception as e:
        print(f"Postgres Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
