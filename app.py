from nicegui import ui
from uuid import uuid4
from datetime import datetime

# Mock user database with passwords (replace with a real database in production)
users_db = {
    'user1': {'username': 'Alice', 'password': 'password1', 'avatar': 'https://robohash.org/alice'},
    'user2': {'username': 'Bob', 'password': 'password2', 'avatar': 'https://robohash.org/bob'}
}

liked_profiles = {}
chats = {}

# Define user session data
session = {}

# Login page
def login_page():
    ui.label('Login Page').style('font-size: 24px')
    username_input = ui.textbox('Username')
    password_input = ui.textbox('Password', type='password')
    ui.button('Login', on_click=lambda: login(username_input.value, password_input.value))
    ui.button('Sign Up', on_click=lambda: ui.redirect('/signup'))

def login(username, password):
    if username in users_db:
        if users_db[username]['password'] == password:
            session['user'] = username
            ui.redirect('/swipe')  # Redirect to swipe page
        else:
            ui.label('Incorrect password. Please try again.').style('color: red')
    else:
        ui.label('User not found, please try again.').style('color: red')

# Signup page
def signup_page():
    ui.label('Sign Up Page').style('font-size: 24px')
    username_input = ui.textbox('Username')
    password_input = ui.textbox('Password', type='password')
    confirm_password_input = ui.textbox('Confirm Password', type='password')
    
    ui.button('Sign Up', on_click=lambda: signup(username_input.value, password_input.value, confirm_password_input.value))

def signup(username, password, confirm_password):
    if username in users_db:
        ui.label('Username already exists. Please choose a different username.').style('color: red')
    elif password != confirm_password:
        ui.label('Passwords do not match. Please try again.').style('color: red')
    elif username and password:  # Make sure fields are not empty
        users_db[username] = {'username': username, 'password': password, 'avatar': f'https://robohash.org/{username}'}
        ui.label('Account created successfully! Please log in.').style('color: green')
        ui.redirect('/login')
    else:
        ui.label('Please fill in all fields.').style('color: red')

# Swipe page
def swipe_page():
    user = session.get('user')
    if user is None:
        ui.redirect('/login')  # Redirect to login page if not logged in
        return

    ui.label(f'Welcome {users_db[user]["username"]}').style('font-size: 24px')
    ui.image(users_db[user]['avatar']).style('width: 200px')
    ui.label('Swipe profiles').style('font-size: 18px')

    # Display profiles to swipe
    for user_id, user_info in users_db.items():
        if user_id == user:
            continue  # Skip self-profile
        
        with ui.row():
            ui.image(user_info['avatar']).style('width: 100px')
            ui.label(user_info['username']).style('font-size: 18px')
            like_button = ui.button('Like', on_click=lambda user_id=user_id: like_profile(user_id))
            like_button.style('background-color: green')

def like_profile(profile_id):
    user = session.get('user')
    if user is not None:
        if profile_id not in liked_profiles:
            liked_profiles[profile_id] = []
        liked_profiles[profile_id].append(user)
        ui.label(f'You liked {users_db[profile_id]["username"]}')
    else:
        ui.label('Please login first').style('color: red')

# Liked profiles page
def liked_profiles_page():
    user = session.get('user')
    if user is None:
        ui.redirect('/login')  # Redirect to login page if not logged in
        return

    ui.label(f'Profiles liked by {users_db[user]["username"]}').style('font-size: 24px')

    liked = liked_profiles.get(user, [])
    if not liked:
        ui.label('No liked profiles yet.')
    else:
        for liked_user_id in liked:
            ui.label(f'{users_db[liked_user_id]["username"]}')
            ui.image(users_db[liked_user_id]['avatar']).style('width: 100px')

# Chat page
def chat_page():
    user = session.get('user')
    if user is None:
        ui.redirect('/login')  # Redirect to login page if not logged in
        return

    ui.label(f'Chat with liked profiles of {users_db[user]["username"]}').style('font-size: 24px')

    chats_list = chats.get(user, [])
    if chats_list:
        for chat in chats_list:
            ui.label(chat)
    else:
        ui.label('No chat messages yet.')

    message_input = ui.textbox('Message')
    ui.button('Send', on_click=lambda: send_message(user, message_input.value, chats))

def send_message(user, message, chats):
    if message:
        if user not in chats:
            chats[user] = []
        chats[user].append(message)
        ui.label(f'Sent: {message}')

# Notifications page
def notifications_page():
    user = session.get('user')
    if user is None:
        ui.redirect('/login')  # Redirect to login page if not logged in
        return

    ui.label(f'Notifications for {users_db[user]["username"]}').style('font-size: 24px')

    if user in liked_profiles:
        ui.label(f'Profiles that liked you: {", ".join(liked_profiles[user])}')
    else:
        ui.label('No one has liked you yet.')

# Routes for pages using ui.router()
ui.router('/login', login_page)
ui.router('/signup', signup_page)
ui.router('/swipe', swipe_page)
ui.router('/liked', liked_profiles_page)
ui.router('/chat', chat_page)
ui.router('/notifications', notifications_page)

# Run the app
ui.run()
