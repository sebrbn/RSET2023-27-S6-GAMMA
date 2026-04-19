# ---------------------------------------------------
# SECURITY — FINAL WORKING VERSION
# ---------------------------------------------------
print("security file loaded")
import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ---------------------------------------------------
# HASH PASSWORD
# ---------------------------------------------------
def hash_password(password: str) -> str:

    if len(password) < 6:
        raise ValueError(
            "Password must be at least 6 characters."
        )

    

    return pwd_context.hash(password)


# ---------------------------------------------------
# VERIFY PASSWORD
# ---------------------------------------------------
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    

    return pwd_context.verify(
        plain_password,
        hashed_password
    )