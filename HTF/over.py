import threading
import tkinter as tk


# Define a class to represent a user session
class UserSession(threading.Thread):
    def __init__(self, username, password, gui):
        super().__init__()
        self.username = username
        self.password = password
        self.is_logged_in = False
        self.gui = gui

    def run(self):
        # Simulate logging in (replace this with actual login logic)
        if self.username == "example" and self.password == "password":
            self.is_logged_in = True
            self.gui.update_user_button(self.username, "Login Successful")
        else:
            self.gui.update_user_button(self.username, "Login Failed")


# Create a dictionary to manage user sessions
sessions = {}


class UserSessionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("User Sessions")

        self.session_frame = tk.Frame(self.root)
        self.session_frame.pack()

    def create_session(self, username, password):
        session = UserSession(username, password, self)
        sessions[username] = session
        session.start()

    def stop_session(self, username):
        if username in sessions:
            session = sessions[username]
            session.join()  # Wait for the session to finish
            del sessions[username]
            print(f"Session for user {username} stopped.")
            self.update_user_button(username, "Session Closed")

    def update_user_button(self, username, message):
        user_button = tk.Button(self.session_frame, text=f"{username}: {message}")
        user_button.pack()

        close_button = tk.Button(self.session_frame, text=f"Close {username} Session",
                                 command=lambda: self.stop_session(username))
        close_button.pack()


# Create the main application window
if __name__ == "__main__":
    root = tk.Tk()
    gui = UserSessionGUI(root)

    # Example usage:
    gui.create_session("example", "password")
    gui.create_session("user2", "wrongpassword")

    root.mainloop()
