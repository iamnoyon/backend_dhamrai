from pwdlib import PasswordHash

hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return hash.verify(password, hashed_password)