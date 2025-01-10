# CimeddaManager

**CimeddaManager** is a secure and user-friendly password management application developed in Python. It allows you to store, retrieve, update, and delete your credentials for various services securely using an SQLite database with field-level encryption for sensitive data.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [Command-Line Interface](#command-line-interface)
- [Auto-Lock Feature](#auto-lock-feature)
- [Security Considerations](#security-considerations)
  - [Encryption](#encryption)
  - [Key Management](#key-management)
  - [Access Control](#access-control)
- [Extensibility](#extensibility)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features

- **Secure Storage**: Credentials are stored in an SQLite database with passwords encrypted using field-level encryption.
- **Master Password**: Protects access to your stored credentials. The master password is used to derive a key for encryption and decryption, but it is never stored.
- **CRUD Operations**: Add, retrieve, update, and delete credentials effortlessly.
- **Auto-Lock**: Automatically locks the session after a period of inactivity to enhance security.
- **Timestamp Tracking**: Records creation and last updated timestamps for each credential.
- **Command-Line Interface**: Simple and intuitive CLI for managing your passwords.
- **Extensible Design**: Easily extendable to include GUI interfaces or additional features.

## Prerequisites

- **Operating System**: Windows 10 (instructions applicable for other OSes with minor adjustments)
- **Python**: Python 3.x
- **Python Packages**:
  - `cryptography`
  - `sqlite3` (bundled with Python)
  - `colorama`

Install these packages using:
```bash
pip install -r requirements.txt


Project Structure

    main.py: Entry point of the application with the command-line interface.
    db_setup.py: Handles database connection and initialization.
    security.py: Manages key derivation, encryption, decryption, and master key changes.
    credentials.py: Contains functions to manage credentials, including encryption and decryption.
    salt.bin: Stores the salt used for key derivation (generated on first run).
    secure_passwords.db: SQLite database storing all credentials (with passwords stored encrypted).
    requirements.txt: Lists all Python dependencies.
    README.md: Project documentation.

Usage
Running the Application

    Set Up Environment:
        Install dependencies:

    pip install -r requirements.txt

Run the Application:

    python main.py

    Follow the prompts to set up a master password and start managing your credentials.

Command-Line Interface

The application provides a user-friendly CLI with the following options:

    Add Credential: Add a new service credential.
    Retrieve Credential: Retrieve credentials for a specific service.
    Update Credential: Update existing credentials.
    Delete Credential: Delete credentials for a service.
    Change Master Password: Change the master password.

Auto-Lock Feature

CimeddaManager automatically locks the session after a period of inactivity (default: 5 minutes). This feature enhances security by requiring re-authentication if the application is left idle.
Security Considerations
Encryption

    Algorithm: AES-256 is used for encrypting sensitive data.
    Key Derivation: PBKDF2 with SHA-256 ensures strong key derivation using a unique salt.

Key Management

    The master password is never stored. A derived key is used for encryption and decryption.

Access Control

    The application locks after inactivity and limits attempts for master password verification to prevent unauthorized access.

Extensibility

CimeddaManager is designed to be extensible. Potential enhancements include:

    Adding a GUI using frameworks like Tkinter or PyQt.
    Cloud synchronization for credentials.
    Integration with browser extensions for autofill.

Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository and submit a pull request.
License

This project is licensed under the MIT License. See the LICENSE file for details.
Acknowledgements

    Cryptography: For robust encryption and key management.
    SQLite: Lightweight and powerful database management.
    Colorama: For adding colorful terminal outputs.