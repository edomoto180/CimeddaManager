# security.py

import os
import sys
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet, InvalidToken
import base64
from colorama import init, Fore, Style
import getpass
from db_setup import get_db_connection


VERIFICATION_TOKEN = b"This is a verification token."
MAX_ATTEMPTS = 3  # Maximum allowed attempts for entering the correct password

# Initialize Colorama
init(autoreset=True)

def derive_key(password: bytes, salt: bytes, iterations: int = 100000) -> bytes:
    kdf_func = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    key = kdf_func.derive(password)
    return key

def load_or_create_salt(salt_path='salt.bin') -> bytes:
    if os.path.exists(salt_path):
        with open(salt_path, 'rb') as f:
            return f.read()
    else:
        new_salt = os.urandom(16)
        with open(salt_path, 'wb') as f:
            f.write(new_salt)
        return new_salt

def store_verification(cipher: Fernet, verify_path='verify.bin'):
    token_encrypted = cipher.encrypt(VERIFICATION_TOKEN)
    with open(verify_path, 'wb') as f:
        f.write(token_encrypted)

def verify_master_password(key: bytes, verify_path='verify.bin') -> bool:
    fernet_key = base64.urlsafe_b64encode(key[:32])
    cipher = Fernet(fernet_key)
    try:
        with open(verify_path, 'rb') as f:
            encrypted_token = f.read()
        decrypted_token = cipher.decrypt(encrypted_token)
        return decrypted_token == VERIFICATION_TOKEN
    except (InvalidToken, FileNotFoundError):
        return False




def get_master_key():
    salt = load_or_create_salt()

    # First execution: set master password
    if not os.path.exists('verify.bin'):
        print(Fore.RED + "No master password set. Please create one."+ Style.RESET_ALL)
        while True:
            # Flush prints to ensure they appear before prompt
            master_password = getpass.getpass(Fore.YELLOW + "Create a master password: "+ Style.RESET_ALL).encode()
            confirm_password = getpass.getpass(Fore.YELLOW + "Confirm master password: "+ Style.RESET_ALL).encode()
            if master_password == confirm_password:
                key = derive_key(master_password, salt)
                fernet_key = base64.urlsafe_b64encode(key[:32])
                cipher = Fernet(fernet_key)
                store_verification(cipher)
                print(Fore.GREEN + "Master password set and verification token created."+ Style.RESET_ALL)
                return key
            else:
                print(Fore.RED + "Passwords do not match. Please try again."+ Style.RESET_ALL)

    # Subsequent executions: verify master password with limited attempts
    attempts = 0
    while attempts < MAX_ATTEMPTS:
        sys.stdout.flush()
        master_password = getpass.getpass(Fore.YELLOW + "Enter your master password: "+ Style.RESET_ALL).encode()
        key = derive_key(master_password, salt)
        if verify_master_password(key):
            print(Fore.GREEN + "Master password verified."+ Style.RESET_ALL)
            return key
        else:
            attempts += 1
            print(Fore.RED + f"Incorrect master password. Attempts remaining: {MAX_ATTEMPTS - attempts}"+ Style.RESET_ALL)

    print(Fore.RED + "Maximum password attempts exceeded. Access blocked."+ Style.RESET_ALL)
    exit(1)


def change_master_password(cipher):
    print(Fore.YELLOW + "You are about to change the master password." + Style.RESET_ALL)

    # Verify current master password
    current_key = get_master_key()  # Initializes and validates the current master password

    # Prompt for the new master password
    while True:
        new_password = getpass.getpass(Fore.YELLOW + "Enter new master password: " + Style.RESET_ALL).encode()
        confirm_password = getpass.getpass(Fore.YELLOW + "Confirm new master password: " + Style.RESET_ALL).encode()

        if new_password != confirm_password:
            print(Fore.RED + "Passwords do not match. Try again." + Style.RESET_ALL)
            continue

        break

    # Derive new key
    salt = load_or_create_salt()  # Use the same salt
    new_key = derive_key(new_password, salt)

    # Create a new cipher with the new key
    new_fernet_key = base64.urlsafe_b64encode(new_key[:32])
    new_cipher = Fernet(new_fernet_key)

    # Re-encrypt all database credentials
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, url, notes FROM credentials")
    rows = cursor.fetchall()

    for row in rows:
        record_id = row[0]

        # Decrypt using the old cipher
        username = cipher.decrypt(row[1]).decode() if row[1] else ""
        password = cipher.decrypt(row[2]).decode()
        url = cipher.decrypt(row[3]).decode() if row[3] else ""
        notes = cipher.decrypt(row[4]).decode() if row[4] else ""

        # Re-encrypt with the new cipher
        new_encrypted_username = new_cipher.encrypt(username.encode()) if username else b""
        new_encrypted_password = new_cipher.encrypt(password.encode())
        new_encrypted_url = new_cipher.encrypt(url.encode()) if url else b""
        new_encrypted_notes = new_cipher.encrypt(notes.encode()) if notes else b""

        # Update the database
        cursor.execute('''
            UPDATE credentials
            SET username = ?, password = ?, url = ?, notes = ?
            WHERE id = ?
        ''', (new_encrypted_username, new_encrypted_password, new_encrypted_url, new_encrypted_notes, record_id))

    conn.commit()
    conn.close()

    # Update the verification token with the new cipher
    store_verification(new_cipher)
    print(Fore.GREEN + "Master password changed successfully!" + Style.RESET_ALL)

    return new_key