import os
import sys
import subprocess

def run_command(command):
    print(f"Running: {command}")
    try:
        # Using shell=True for compatibility with various environments
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Error running command: {e}")
        if "migrate" in command:
            print("\n[TIP] If you're seeing 'table already exists' errors, try deleting the 'db.sqlite3' file and run this script again.")
        sys.exit(1)

def main():
    # Set environment variable for secret key if not set
    if not os.environ.get("DJANGO_SECRET_KEY"):
        os.environ["DJANGO_SECRET_KEY"] = "django-insecure-bootstrap-key-for-local-run"

    print("========================================")
    print("      Starting Roshd (رشد) Bootstrap    ")
    print("========================================\n")

    # 1. Run migrations
    print("[1/2] Setting up database...")
    # We ensure migrations are current but normally the provided 0001_initial is enough
    run_command("python manage.py makemigrations roshd")
    run_command("python manage.py migrate")

    # 2. Start the server
    print("\n[2/2] Starting development server...")
    print("      >>> http://127.0.0.1:8000/ <<<\n")

    try:
        run_command("python manage.py runserver")
    except KeyboardInterrupt:
        print("\nStopping server...")

if __name__ == "__main__":
    main()
