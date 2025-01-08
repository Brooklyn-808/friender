import json
from nicegui import ui
from uuid import uuid4
from typing import Dict

# Load data from a JSON file to persist data across sessions
DATA_FILE = "users.json"

# Initialize data storage
try:
    with open(DATA_FILE, "r") as f:
        users = json.load(f)  # {user_id: {name, password, likes, skipped, liked_by, matches, messages}}
except FileNotFoundError:
    users = {}

current_user_id = None  # Tracks the logged-in user


def save_data():
    """Save user data to a JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)


def login_page():
    """Login or registration page."""
    def login():
        global current_user_id
        username = username_input.value.strip()
        password = password_input.value.strip()

        # Check for valid credentials
        for user_id, user_data in users.items():
            if user_data["name"] == username and user_data["password"] == password:
                current_user_id = user_id
                ui.notify(f"Welcome back, {username}!")
                ui.open("/")
                return
        ui.notify("Invalid username or password. Please try again.", type="negative")

    def register():
        global current_user_id
        username = username_input.value.strip()
        password = password_input.value.strip()

        if not username or not password:
            ui.notify("Username and password cannot be empty.", type="negative")
            return

        # Check if username already exists
        if any(user["name"] == username for user in users.values()):
            ui.notify("Username already exists. Please choose another.", type="negative")
            return

        # Create a new user
        user_id = str(uuid4())
        users[user_id] = {
            "name": username,
            "password": password,
            "likes": [],
            "skipped": [],  # Track skipped profiles
            "liked_by": [],
            "matches": [],
            "messages": {},
        }
        save_data()
        current_user_id = user_id
        ui.notify(f"Welcome, {username}! Your account has been created.")
        ui.open("/")

    with ui.column().classes("items-center justify-center h-screen"):
        ui.label("Welcome to NiceGUI Tinder").classes("text-2xl font-bold mb-4")
        username_input = ui.input("Username").classes("w-1/2")
        password_input = ui.input("Password", type="password").classes("w-1/2 mt-2")
        with ui.row().classes("mt-4"):
            ui.button("Login", on_click=login).classes("mr-2")
            ui.button("Register", on_click=register)


def swipe_page():
    """Page for swiping profiles."""
    if not current_user_id:
        ui.open("/login")
        return

    def load_next_profile():
        # Filter out profiles that the user has liked or skipped
        for user_id, user_data in users.items():
            if (
                user_id != current_user_id
                and user_id not in users[current_user_id]["likes"]
                and user_id not in users[current_user_id]["skipped"]
            ):
                profile_name.text = user_data["name"]
                profile.data = user_id
                like_button.enable()
                pass_button.enable()
                return
        profile_name.text = "No more profiles to swipe!"
        like_button.disable()
        pass_button.disable()

    def like():
        liked_user_id = profile.data
        users[current_user_id]["likes"].append(liked_user_id)
        users[liked_user_id]["liked_by"].append(current_user_id)

        # Check for match
        if current_user_id in users[liked_user_id]["likes"]:
            users[current_user_id]["matches"].append(liked_user_id)
            users[liked_user_id]["matches"].append(current_user_id)
            ui.notify(f"You matched with {users[liked_user_id]['name']}!")

        save_data()
        load_next_profile()

    def skip():
        skipped_user_id = profile.data
        users[current_user_id]["skipped"].append(skipped_user_id)
        save_data()
        load_next_profile()

    with ui.column().classes("items-center"):
        ui.label("Swipe Profiles").classes("text-2xl font-bold")
        profile = ui.card().classes("w-1/2 p-4")
        profile_name = ui.label("").classes("text-xl font-bold")
        with ui.row().classes("justify-center mt-4"):
            like_button = ui.button("Like", on_click=like).classes("mr-2")
            pass_button = ui.button("Pass", on_click=skip)
        load_next_profile()


def notifications_page():
    """Page to view who liked the user."""
    if not current_user_id:
        ui.open("/login")
        return

    with ui.column().classes("items-center"):
        ui.label("Notifications").classes("text-2xl font-bold")
        liked_by = users[current_user_id]["liked_by"]
        if liked_by:
            for user_id in liked_by:
                ui.label(f"{users[user_id]['name']} liked your profile.")
        else:
            ui.label("No one has liked your profile yet.")


def liked_profiles_page():
    """Page to see the profiles the user has liked."""
    if not current_user_id:
        ui.open("/login")
        return

    with ui.column().classes("items-center"):
        ui.label("Liked Profiles").classes("text-2xl font-bold")
        liked_profiles = users[current_user_id]["likes"]
        if liked_profiles:
            for user_id in liked_profiles:
                ui.label(f"You liked {users[user_id]['name']}.")
        else:
            ui.label("You haven't liked any profiles yet.")


def chat_page():
    """Page to chat with mutual matches."""
    if not current_user_id:
        ui.open("/login")
        return

    with ui.column().classes("items-center"):
        ui.label("Chats").classes("text-2xl font-bold")
        matches = users[current_user_id]["matches"]
        if not matches:
            ui.label("You have no matches yet.")
            return

        def open_chat(match_id):
            def send_message():
                message = message_input.value.strip()
                if message:
                    users[current_user_id]["messages"].setdefault(match_id, []).append(("You", message))
                    users[match_id]["messages"].setdefault(current_user_id, []).append((users[current_user_id]["name"], message))
                    chat_box.append(ui.label(f"You: {message}"))
                    message_input.value = ""
                    save_data()

            chat_box = ui.column().classes("mt-4")
            for sender, msg in users[current_user_id]["messages"].get(match_id, []):
                chat_box.append(ui.label(f"{sender}: {msg}"))

            message_input = ui.input("Enter your message").classes("w-full mt-2")
            ui.button("Send", on_click=send_message).classes("mt-2")

        for match_id in matches:
            ui.button(f"Chat with {users[match_id]['name']}", on_click=lambda match_id=match_id: open_chat(match_id))


# Routes
@ui.page("/login")
def login_route():
    login_page()


@ui.page("/")
def main_route():
    swipe_page()


@ui.page("/notifications")
def notifications_route():
    notifications_page()


@ui.page("/liked_profiles")
def liked_profiles_route():
    liked_profiles_page()


@ui.page("/chats")
def chat_route():
    chat_page()


# Run the app
ui.run()
