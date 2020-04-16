# base imports
import tkinter as tk

# module imports
import SQL

# relative module imports
from .login import Login
from .menu import Menu
from .manageusers import ManageUsers


# The root application (window) that the rest of the GUI is built on.
# responsible for handling switching between pages and containing the username of the current user logged in.
class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Prototype")

        # Offsets are calculated and used to center the window in the middle of the screen.
        offset_x = (self.winfo_screenwidth() // 2) - 360
        offset_y = (self.winfo_screenheight() // 2) - 240
        self.geometry(f"720x480+{offset_x}+{offset_y}")
        self.minsize(720, 480)

        self.frames = []
        self.add_frames(Login)
        self.username = ''

        # Called when user tries to exit via red 'X' in top right or alt-f4
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.mainloop()

    # Closes the connection to the database and closes the application.
    def on_closing(self):
        SQL.main.close_connection()
        self.destroy()

    def destroy_current_frames(self):
        for frame in self.frames:
            frame.destroy()

        self.frames = []

    def add_frames(self, *new_frames):
        for new_frame in new_frames:
            frame = new_frame(self)
            self.frames.append(frame)

        # we only want to call focus on the final frame added
        frame.set_focus()

    def next_frame(self, frame):
        previous_frame = self.frames.pop()
        previous_frame.destroy()
        self.add_frames(frame)

    def login(self, username):
        self.username = username
        self.destroy_current_frames()
        self.add_frames(Menu, ManageUsers)

    # Method for logging out of the current session and going back to the login page
    def logout(self):
        self.destroy_current_frames()
        self.add_frames(Login)
