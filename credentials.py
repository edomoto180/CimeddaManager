# credentials.py

from db_setup import get_db_connection
from cryptography.fernet import Fernet, InvalidToken
from security import get_master_key
import base64
# import pandas as pd

# Global variables for security components (initialized later)
_master_key = None
cipher = None

def initialize_credentials():
    global _master_key, cipher
    # Derive the master key and set up the Fernet cipher
    _master_key = get_master_key()
    fernet_key = base64.urlsafe_b64encode(_master_key[:32])
    cipher = Fernet(fernet_key)

def get_cipher():
    global cipher
    return cipher

def reinitialize_cipher(new_key):
    """Reinitialize the cipher with a new key when the master password is changed."""
    global cipher
    fernet_key = base64.urlsafe_b64encode(new_key[:32])
    cipher = Fernet(fernet_key)

def add_credential(service, username, password, url='', notes=''):
    encrypted_password = cipher.encrypt(password.encode())
    encrypted_username = cipher.encrypt(username.encode()) if username else b""
    encrypted_url = cipher.encrypt(url.encode()) if url else b""
    encrypted_notes = cipher.encrypt(notes.encode()) if notes else b""

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
            INSERT INTO credentials (service, username, password, url, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (service, encrypted_username, encrypted_password, encrypted_url, encrypted_notes))
    conn.commit()
    conn.close()

def get_credential(service):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
            SELECT id, service, username, password, url, notes, created_at, updated_at 
            FROM credentials 
            WHERE service = ?
        ''', (service,))
    row = cursor.fetchone()
    conn.close()
    if row:
        # Decrypt fields before returning
        try:
            decrypted_username = cipher.decrypt(row[2]).decode() if row[2] else ""
        except InvalidToken:
            decrypted_username = "Decryption failed"

        try:
            decrypted_password = cipher.decrypt(row[3]).decode()
        except InvalidToken:
            decrypted_password = "Decryption failed"

        try:
            decrypted_url = cipher.decrypt(row[4]).decode() if row[4] else ""
        except InvalidToken:
            decrypted_url = "Decryption failed"

        try:
            decrypted_notes = cipher.decrypt(row[5]).decode() if row[5] else ""
        except InvalidToken:
            decrypted_notes = "Decryption failed"

        # Reconstruct row with decrypted data
        decrypted_row = (
            row[0],  # id
            row[1],  # service
            decrypted_username,  # username
            decrypted_password,  # password
            decrypted_url,  # url
            decrypted_notes,  # notes
            row[6],  # created_at
            row[7]  # updated_at
        )
        return decrypted_row
    return None

def update_credential(service, username=None, password=None, url=None, notes=None):
    fields = []
    values = []

    # Check each field and update only if it's not blank
    if username is not None and username != "":
        encrypted_username = cipher.encrypt(username.encode())
        fields.append("username = ?")
        values.append(encrypted_username)
    if password is not None and password != "":
        encrypted_pass = cipher.encrypt(password.encode())
        fields.append("password = ?")
        values.append(encrypted_pass)
    if url is not None and url != "":
        encrypted_url = cipher.encrypt(url.encode())
        fields.append("url = ?")
        values.append(encrypted_url)
    if notes is not None and notes != "":
        encrypted_notes = cipher.encrypt(notes.encode())
        fields.append("notes = ?")
        values.append(encrypted_notes)

    # If no fields to update, return False
    if not fields:
        return False

    # Add service as the last parameter for the WHERE clause
    values.append(service)
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = f'''
            UPDATE credentials
            SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE service = ?
        '''
    cursor.execute(sql, tuple(values))
    conn.commit()
    rows_updated = cursor.rowcount
    conn.close()
    return rows_updated > 0


def delete_credential(service):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM credentials
        WHERE service = ?
    ''', (service,))
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()
    return rows_deleted > 0

def list_services():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, service FROM credentials")
    services = cursor.fetchall()
    conn.close()
    return services


# def import_from_excel(file_path):
#     """
#     Imports credentials from a non-protected Excel file into the database.
#
#     The Excel file should have:
#       - First row as headers.
#       - Columns: Service, Password, Username, URL, Notes ...
#       - Data starting from the second row.
#     """
#     try:
#
#         # Read the Excel file into a DataFrame using pandas
#         df = pd.read_excel(file_path, engine='openpyxl', dtype=object)
#
#         # Check if the DataFrame has at least 2 columns (Service and Password)
#         if df.shape[1] < 2:
#             raise ValueError("The Excel file does not have the required columns.")
#
#         # Iterate over each row in the DataFrame and insert into the database
#         for index, row in df.iterrows():
#             # Extract values with default empty string if a cell is missing or NaN
#             service = row[0] if not pd.isna(row[0]) else None
#             password = row[1] if not pd.isna(row[1]) else ""
#             username = row[2] if len(row) > 2 and not pd.isna(row[2]) else ""
#             notes = row[3] if len(row) > 3 and not pd.isna(row[3]) else ""
#
#             # Convert password to string if it's not already
#             service = str(service)
#             password = str(password)
#             username = str(username)
#             notes = str(notes)
#
#             if service:  # Proceed only if a service name exists
#                 try:
#                     add_credential(service, username, password, "", notes)
#                     #print(f"Imported credential for service: {service}")
#                 except Exception as e:
#                     print(f"Failed to import credential for {service}: {e}")
#     except Exception as e:
#         print(f"An error occurred during import: {e}")
#         raise  # re-raise exception for further debugging if desired