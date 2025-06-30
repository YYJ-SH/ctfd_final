# Cookie CTF Challenge

This is a simple CTF challenge where participants must manipulate cookies to retrieve the flag.

## 📁 Files

- `app.py`: Flask-based web application
- `flag.txt`: Contains the hidden flag (only accessible to "admins")
- `requirements.txt`: Python dependencies

## 🚀 How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   python app.py
   ```

3. Visit `http://localhost:5000` in your browser.

## 🔒 Security Note

- Ensure `flag.txt` is **not accessible** via any direct route or web server configuration.
- This app runs in debug mode for development/CTF purposes. Do not expose it to the public internet as-is.

## 🏁 Goal

Access the `/flag` endpoint as an admin by modifying the `is_admin` cookie.

Good luck!
