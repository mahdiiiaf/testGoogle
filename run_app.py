import os
import sys
import subprocess

def run_command(command):
    print(f"Running: {command}")
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)

def main():
    # Set environment variable for secret key if not set
    if not os.environ.get("DJANGO_SECRET_KEY"):
        os.environ["DJANGO_SECRET_KEY"] = "django-insecure-bootstrap-key-for-local-run"

    print("--- Starting Roshd Bootstrap ---")

    # 1. Install dependencies (optional, but good to ensure)
    # run_command("pip install django djangorestframework django-cors-headers")

    # 2. Run migrations
    run_command("python manage.py makemigrations roshd")
    run_command("python manage.py migrate")

    # 3. Start the server
    print("--- Starting Server at http://127.0.0.1:8000/ ---")
    run_command("python manage.py runserver")

if __name__ == "__main__":
    main()
