# main.py
# --------------------------------------------------------------------------------
from db_setup import initialize_db
from credentials import (
    add_credential,
    get_credential,
    update_credential,
    delete_credential,
    list_services,
    initialize_credentials,
    # import_from_excel,
    get_cipher,
    reinitialize_cipher
)
from colorama import init, Fore, Style
import getpass
import os
from security import change_master_password
import time
import threading


# --------------------------------------------------------------------------------
# Auto-lock settings
LOCK_TIMEOUT = 300 # Auto-lock after 300 seconds (5 minutes)
last_activity_time = time.time()
is_locked = False
stop_last_activity_thread = False  # Global flag to stop the thread

# Initialize Colorama
init(autoreset=True)

# Define the ASCII art logo
LOGO = Fore.CYAN + Style.BRIGHT + r"""

   _____ _                    _     _       __  __                                   
  / ____(_)                  | |   | |     |  \/  |                                  
 | |     _ _ __ ___   ___  __| | __| | __ _| \  / | __ _ _ __   __ _  __ _  ___ _ __ 
 | |    | | '_ ` _ \ / _ \/ _` |/ _` |/ _` | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
 | |____| | | | | | |  __/ (_| | (_| | (_| | |  | | (_| | | | | (_| | (_| |  __/ |   
  \_____|_|_| |_| |_|\___|\__,_|\__,_|\__,_|_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|   
                                                                      __/ |          
                                                                     |___/           

""" + Style.RESET_ALL
# --------------------------------------------------------------------------------
def monitor_activity():
    """Monitor user activity and lock after timeout."""
    global last_activity_time, is_locked, stop_last_activity_thread
    while not stop_last_activity_thread:
        if time.time() - last_activity_time > LOCK_TIMEOUT:
            is_locked = True
            print(Fore.RED + "\n\nSession timed out. Please log in again." + Style.RESET_ALL)
            exit(1)
        time.sleep(1)
# --------------------------------------------------------------------------------
def reset_timer():
    """Reset the inactivity timer."""
    global last_activity_time
    last_activity_time = time.time()
# --------------------------------------------------------------------------------
def service_display_and_selector():
    services = list_services()

    if not services:
        print(Fore.RED + "No credentials available." + Style.RESET_ALL)

    print("\nAvailable Services:")

    for index, (service_id, service_name) in enumerate(services):
        print(f"{index}. {service_name}")

    user_input = input("Enter the number or part of the service name you want: ")
    selected_service = None

    # Attempt numeric selection first
    try:
        selection_index = int(user_input)
        if selection_index < 0 or selection_index >= len(services):
            print(Fore.RED + "Invalid selection." + Style.RESET_ALL)

        selected_service = normalize_str_value(services[selection_index][1])
    except ValueError:
        # Handle as text search if not a valid number
        search_query = user_input.lower()
        matching_services = [
            (idx, service_name) for idx, (_, service_name) in enumerate(services)
            if search_query in service_name.lower()
        ]

        if not matching_services:
            print(Fore.RED + f"No services found matching '{user_input}'." + Style.RESET_ALL)
        elif len(matching_services) == 1:
            # If only one match, select it automatically
            selected_service = normalize_str_value(matching_services[0][1])
        else:
            # Multiple matches found. Let user refine choice.
            print("\nMultiple services found:")
            for idx, service_name in matching_services:
                print(f"{idx}. {service_name}")

            try:
                refined_index = int(input("Multiple matches found. Enter the number of the desired service: "))
                # Validate refined index is among the matching ones
                if any(refined_index == idx for idx, _ in matching_services):
                    selected_service = normalize_str_value(services[refined_index][1])
                else:
                    print(Fore.RED + "Invalid selection among matches." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "Please enter a valid number." + Style.RESET_ALL)

    return selected_service
# --------------------------------------------------------------------------------
def normalize_str_value(val):
    val = str(val)
    if val == "None":
        val = None
    return val
# --------------------------------------------------------------------------------
def main():
    # Start the activity monitor thread
    global is_locked, stop_last_activity_thread
    threading.Thread(target=monitor_activity, daemon=True).start()

    # Print the logo at the top of the console
    os.system('cls')
    print(LOGO)

    initialize_credentials()   # Set up master key and cipher (prompts if needed).
    initialize_db()            # Initialize or verify the database.
    cipher = get_cipher()

    while True:
        # Check if session is locked
        if is_locked:
            # Re-authenticate the user
            print(Fore.YELLOW + "Session locked due to inactivity." + Style.RESET_ALL)
            stop_last_activity_thread = True
            break

        reset_timer()  # Reset the timer after any user activity

        print("\n" + Fore.CYAN + Style.BRIGHT + "---------------------------------------")
        print(Fore.CYAN + Style.BRIGHT + "CimeddaManager - Password Manager")
        print("1. Add Credential")
        print("2. Retrieve Credential")
        print("3. Update Credential")
        print("4. Delete Credential")
        print("5. Change Master Password")
        print("6. Exit")
        # print("7. Import Credentials from Excel")  # New option

        choice = input(Fore.YELLOW + "Select an option (1-5): " + Style.RESET_ALL)

        if choice == '1':
            service_name = normalize_str_value(input(Fore.YELLOW + "Enter service name: "+ Style.RESET_ALL))
            username = normalize_str_value(input(Fore.YELLOW + "Enter username: "+ Style.RESET_ALL))
            password_value = normalize_str_value(getpass.getpass(Fore.YELLOW + "Enter password: "+ Style.RESET_ALL))
            url = normalize_str_value(input(Fore.YELLOW + "Enter URL (optional): "+ Style.RESET_ALL))
            notes = normalize_str_value(input(Fore.YELLOW + "Enter notes (optional): "+ Style.RESET_ALL))
            add_credential(service_name, username, password_value, url, notes)
            print(Fore.GREEN + f"Credential for '{service_name}' added successfully." + Style.RESET_ALL)

        elif choice == '2':
            selected_service = service_display_and_selector()

            # Now retrieve and display the credential if a service was selected
            if selected_service:
                record = get_credential(selected_service)
                if record:
                    print("\n" + Fore.GREEN + "Retrieved Record:" + Style.RESET_ALL)
                    print(Fore.YELLOW + f"ID: {Style.RESET_ALL}{record[0]}")
                    print(Fore.YELLOW + f"Service: {Style.RESET_ALL}{record[1]}")
                    print(Fore.YELLOW + f"Username: {Style.RESET_ALL}{record[2]}")
                    print(Fore.YELLOW + f"Password: {Style.RESET_ALL}{record[3]}")
                    print(Fore.YELLOW + f"URL: {Style.RESET_ALL}{record[4]}")
                    print(Fore.YELLOW + f"Notes: {Style.RESET_ALL}{record[5]}")
                    print(Fore.YELLOW + f"Created At: {Style.RESET_ALL}{record[6]}")
                    print(Fore.YELLOW + f"Updated At: {Style.RESET_ALL}{record[7]}")
                else:
                    print(Fore.RED + f"No record found for service '{selected_service}'." + Style.RESET_ALL)
            else:
                print(Fore.RED + f"Invalid service selected: '{selected_service}'." + Style.RESET_ALL)

        elif choice == '3':
            selected_service = service_display_and_selector()

            # Now retrieve and display the credential if a service was selected
            if selected_service:
                print(f"\nUpdating credential for '{selected_service}'." + Style.RESET_ALL)
                print(Fore.YELLOW + "Enter new values (leave blank to keep current value):" + Style.RESET_ALL)
                username = normalize_str_value(input(Fore.YELLOW + "New username: " + Style.RESET_ALL))
                password_value = normalize_str_value(getpass.getpass(Fore.YELLOW + "New password: " + Style.RESET_ALL))
                url = normalize_str_value(input(Fore.YELLOW + "New URL: " + Style.RESET_ALL))
                notes = normalize_str_value(input(Fore.YELLOW + "New notes: " + Style.RESET_ALL))

                # Only include values in kwargs if they are not empty
                kwargs = {}
                if username.strip():
                    kwargs['username'] = username.strip()
                if password_value.strip():
                    kwargs['password'] = password_value.strip()
                if url.strip():
                    kwargs['url'] = url.strip()
                if notes.strip():
                    kwargs['notes'] = notes.strip()

                success = update_credential(selected_service, **kwargs)
                if success:
                    print(Fore.GREEN + f"Credential for '{selected_service}' updated successfully." + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"Failed to update credential for '{selected_service}'. Make sure it exists." + Style.RESET_ALL)
            else:
                print(Fore.RED + f"Invalid service selected: '{selected_service}'." + Style.RESET_ALL)

        elif choice == '4':
            selected_service = service_display_and_selector()

            # Now retrieve and display the credential if a service was selected
            if selected_service:
                confirm = input(f"Are you sure you want to delete '{selected_service}'? (y/n): ").lower()
                if confirm == 'y':
                    success = delete_credential(selected_service)
                    if success:
                        print(Fore.GREEN + f"Credential for '{selected_service}' deleted successfully." + Style.RESET_ALL)
                    else:
                        print(Fore.RED + f"No credential found for service '{selected_service}'." + Style.RESET_ALL)
                else:
                    print("Deletion canceled.")
            else:
                print(Fore.RED + f"Invalid service selected: '{selected_service}'." + Style.RESET_ALL)

        elif choice == '5':
            new_key = change_master_password(cipher)

            # Reinitialize the global cipher
            reinitialize_cipher(new_key)
            cipher = get_cipher()

        elif choice == '6':
            print(Fore.CYAN + "Exiting CimeddaManager. Goodbye!" + Style.RESET_ALL)
            stop_last_activity_thread = True
            break

        # elif choice == '7':
        #     file_path = input(Fore.YELLOW + "Enter the path to the Excel file: " + Style.RESET_ALL)
        #     try:
        #         import_from_excel(file_path)
        #         print(Fore.GREEN + "Import completed." + Style.RESET_ALL)
        #     except Exception as e:
        #         print(Fore.RED + f"An error occurred during import: {e}" + Style.RESET_ALL)

        else:
            print(Fore.RED + "Invalid option. Please select a valid number." + Style.RESET_ALL)
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
