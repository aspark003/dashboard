import json
from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Load data from JSON files
def load_data():
    try:
        with open('users.json', 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}

    try:
        with open('profiles.json', 'r') as f:
            profiles = json.load(f)
    except FileNotFoundError:
        profiles = {}

    return users, profiles

# Save data to JSON files
def save_data(users, profiles):
    try:
        with open('users.json', 'w') as f:
            json.dump(users, f)

        with open('profiles.json', 'w') as f:
            json.dump(profiles, f)

        # Reload data to reflect the latest changes
        global users_data, profiles_data
        users_data, profiles_data = load_data()
    except Exception as e:
        print(f"Error saving data: {e}")

# Load the users and profiles from the saved JSON data
users_data, profiles_data = load_data()

@app.route('/', methods=['GET', 'POST'])
def home():
    message = ""

    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        password = request.form.get('password')

        if action == 'login':
            if username in users_data and users_data[username] == password:
                # Find phone number for this username
                phone = next((p for p, profile in profiles_data.items() if profile['username'] == username), None)
                if phone:
                    return redirect(url_for('dashboard', phone=phone))  # Redirect to dashboard instead of profile
                else:
                    message = "Profile not found."
            else:
                message = "Invalid login credentials."

    return render_template('webhtml.html', message=message)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = ""

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        address = request.form.get('address')
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        age = request.form.get('age')

        if username in users_data:
            message = "Username already exists."
        elif phone in profiles_data:
            message = "Phone number already used."
        else:
            users_data[username] = password

            profiles_data[phone] = {
                'username': username,
                'password': password,
                'fullname': fullname,
                'address': address,
                'gender': gender,
                'age': age
            }

            save_data(users_data, profiles_data)  # Save data to file
            message = "Signup successful! Please log in."
            return redirect(url_for('home'))

    return render_template('signup.html', message=message)

@app.route('/dashboard/<phone>')
def dashboard(phone):
    user = profiles_data.get(phone)

    if not user:
        return "User not found", 404  # If no user is found

    return render_template('dashboard.html', user=user)

@app.route('/users')
def list_users():
    return render_template('users_list.html', profiles=profiles_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
