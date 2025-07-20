from app import app  # noqa: F401

print("Running main.py...")

from app import app  # noqa: F401

print("App imported successfully.")

if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(host="0.0.0.0", port=5000, debug=True)
