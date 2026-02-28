import sys
import requests
import getpass

SERVER = "http://127.0.0.1:5000"

def banner():
    RED = "\33[91m"
    BLUE = "\33[94m"
    GREEN = "\033[32m"
    YELLOW = "\033[93m"
    PURPLE = '\033[0;35m' 
    CYAN = "\033[36m"
    END = "\033[0m"
    font = f"""
    {GREEN}
    █████╗ ██╗   ██╗████████╗██╗  ██╗███████╗██████╗ 
    ██╔══██╗██║   ██║╚══██╔══╝██║  ██║██╔════╝██╔══██╗
    ███████║██║   ██║   ██║   ███████║█████╗  ██████╔╝
    ██╔══██║██║   ██║   ██║   ██╔══██║██╔══╝  ██╔══██╗
    ██║  ██║╚██████╔╝   ██║   ██║  ██║███████╗██║  ██║
    ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
                                         {END} - by Manomay """
    print(font)

def activestatus() -> bool:
    print("Checking if server's health")
    
    try:
        x = requests.get(f"{SERVER}/health", timeout=5) 
        if x.status_code == 200 and x.json().get("status") == "ok":
            print("Server is healthy")
            return True
        else:
            print("Server failure")
            return False

    except requests.exceptions.RequestException as e:
        print("Server Failure: ", e)
        return False 


def accountAccess():
    
    username = input("Username: ")
    password = getpass.getpass("Password: ")    

    r = safe_post("/login", {"username": username, "password": password})

    if not r:
        return

    if r.status_code != 200:
        print("Login Failed:", r.json().get("message", "Unknown error"))
        return

    return r.json()["session_token"]
    
    
def get_history(token):
    r = safe_post("/history", {"session_token": token})

    if not r:
        return
        
    if r.status_code == 401:
        print("Session expired. Please login again.")
        return
    elif r.status_code != 200:
        print("Failed to fetch history:", r.json().get("message", "Unknown error"))
        return

    print("History:")
    for entry in r.json().get("history", []):
        print("-", entry)

def accountCreation():
    print("Create your account in Server")

    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    retype_password = getpass.getpass("Retype Password: ")
    
    if not username:
        print("Username cannot be empty")
        return
            
    if password != retype_password:
        print("passwords didn't match. Retry...")
        return
    
    r = safe_post("/signup", {"username": username, "password": password})

    if not r:
        return
    
    if r.status_code != 200:
        print("Signup failed:", r.json().get("message", "Unknown error"))
        return
    
    print("Successfully created your account")
      
def safe_post(endpoint, payload):
    try:
        return requests.post(
            f"{SERVER}{endpoint}",
            json=payload,
            timeout=5
        )
    except requests.exceptions.RequestException as e:
        print("Server Failure:", e)
        return None

if __name__ == "__main__":
    banner()
    if not activestatus():
        sys.exit("Exiting due to server failure")
    print("Server is up! Continuing with main program...")
    print("1. Register")
    print("2. Login")
    choice = input("Select: ").strip()
    if choice == "1":
        accountCreation()
    elif choice == "2":
        token = accountAccess()
        if token:
            get_history(token)
        else:
            print("Error during Login token fetch")
    else:
        print("Invalid Option")