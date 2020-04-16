# base imports
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# module imports
import SQL
import validation


# A master frame [contained by the root Application]
# responsible for managing the user accounts on the system.
class ManageUsers(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(expand=True, fill='both')

        # Creating the widgets
        self.user_list = UserList(self, self.master)
        self.user_list.pack(side='left', fill='both', expand=True, padx=(20, 0), pady=40)

        self.register = RegisterUser(self, self.master)
        self.register.pack(fill='both', expand=True, padx=(20, 50), pady=(40, 0))

        self.change_password = ChangePassword(self, self.master)
        self.change_password.pack(side='bottom', padx=(20, 50), pady=(0, 40))

    def set_focus(self):
        self.register.username.focus_set()


# Child frame [left half of the ManageUsers container frame GUI]
# Responsible for containing the list of users on this system.
class UserList(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller
        self.user_blocks = {}

        # Creating the widgets
        def resize_events(_event):  # Resize user block frames to match the size of the canvas frame.
            main_canvas.itemconfig(frame_id, width=main_canvas.winfo_width() - 2)

        main_canvas = tk.Canvas(self, bg='white')
        main_canvas.bind("<Configure>", resize_events)
        main_canvas.pack(fill='both', expand=True)

        self.user_list_frame = tk.Frame(main_canvas, bg='white')
        frame_id = main_canvas.create_window((0, 0), window=self.user_list_frame, anchor='nw')

        # Adding users into the user list
        for user in SQL.users.get_users():
            self.add_user(user[0])

    def add_user(self, username):
        user_block = tk.Frame(self.user_list_frame, background='grey')
        user_block.pack(fill='x', expand=True, padx=5, pady=(5, 0))

        tk.Label(user_block, text=username, bg='grey').pack(side='left', padx=6, pady=2)

        # Prevents the user from accidentally deleting their own account.
        button_state = 'disabled' if self.controller.username == username else 'normal'
        delete_user = ttk.Button(user_block, state=button_state, text="Delete User",
                                 command=lambda: self.del_user(username))

        delete_user.pack(side='right', ipadx=3, padx=3, pady=3)
        change_password = ttk.Button(user_block, text="Change Password",
                                     command=lambda: self.change_password_user(username))
        change_password.pack(side='right', ipadx=3, padx=3, pady=3)

        self.user_blocks[username] = user_block

    def del_user(self, username):
        if messagebox.askyesno(title='Confirm Deletion',
                               message=f"Are you sure you want to delete the user account '{username}'?"):
            SQL.users.del_user(username)
            self.user_blocks[username].destroy()
            del self.user_blocks[username]

            # Changes the 'change password' user so that you aren't given a deleted user to change the password for.
            if self.master.change_password.username == username:
                self.change_password_user(self.controller.username)

    def change_password_user(self, username):
        self.master.change_password.username = username
        self.master.change_password.username_label['text'] = f"User: {username}"
        self.master.change_password.old_password.focus_set()


# Child frame [top right quadrant of the ManageUsers container frame GUI]
# responsible for creating new user accounts.
class RegisterUser(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller

        # Creating the widgets
        ttk.Label(self, text="Create User Account").grid(row=0, column=0, columnspan=2)
        ttk.Label(self, text='Username').grid(row=1, column=0, sticky='W')
        self.username = ttk.Entry(self)
        self.username.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self, text='Password').grid(row=2, column=0, sticky='W')
        self.password = ttk.Entry(self, show="\u2022")
        self.password.grid(row=2, column=1, padx=10)

        ttk.Label(self, text='Confirm Password').grid(row=3, column=0, sticky='W')
        self.confirm_password = ttk.Entry(self, show="\u2022")
        self.confirm_password.bind('<Return>', self.register_user)
        self.confirm_password.grid(row=3, column=1, padx=10, pady=10)

        self.register = ttk.Button(self, width=20, text="Register",
                                   command=self.register_user)
        self.register.bind('<Return>', self.register_user)
        self.register.grid(row=4, column=0, columnspan=2)

        self.response = ttk.Label(self)
        self.response.grid(row=5, column=0, columnspan=2)

    def register_user(self, _event=None):
        self.response['foreground'] = 'red'

        username = self.username.get()
        if not username:
            self.response['text'] = "Username is empty."
            return

        if validation.user_exists(username):
            self.response['text'] = "Username already taken."
            return

        if len(username) > 20:
            self.response['text'] = "Username is too long."
            return

        # The system will not require more than a few user accounts.
        if SQL.users.get_num_users() == 10:
            self.response['text'] = "Account capacity has been reached."
            return

        password = self.password.get()
        if len(password) < 6:
            self.response['text'] = "Password should be 6 characters or more."
            return

        confirm_password = self.confirm_password.get()
        if password != confirm_password:
            self.response['text'] = "Password does not match."
            return

        SQL.users.add_user(username, password)  # Add user details to the database
        self.master.user_list.add_user(username)      # Add user details to the user list

        self.response['foreground'] = 'green'
        self.response['text'] = "Successfully created account!"

        # Clear entry fields after account creation
        self.username.delete(0, 'end')
        self.password.delete(0, 'end')
        self.confirm_password.delete(0, 'end')


# Child frame [bottom right quadrant of the ManageUsers container frame GUI]
# responsible for changing the password of a user account.
class ChangePassword(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller
        self.username = controller.username

        # Creating the widgets
        self.username_label = ttk.Label(self, text=f"User: {self.username}")
        self.username_label.grid(row=0, column=0, columnspan=2)

        ttk.Label(self, text='Old Password').grid(row=1, column=0, sticky='W')
        self.old_password = ttk.Entry(self, show="\u2022")
        self.old_password.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self, text='New Password').grid(row=2, column=0, sticky='W')
        self.new_password = ttk.Entry(self, show="\u2022")
        self.new_password.grid(row=2, column=1, padx=10)

        ttk.Label(self, text='Confirm Password').grid(row=3, column=0, sticky='W')
        self.confirm_password = ttk.Entry(self, show="\u2022")
        self.confirm_password.bind('<Return>', self.change_password)
        self.confirm_password.grid(row=3, column=1, padx=10, pady=10)

        change_password_button = ttk.Button(self, width=20, text="Change Password",
                                            command=self.change_password)
        change_password_button.bind('<Return>', self.change_password)
        change_password_button.grid(row=4, column=0, columnspan=2)

        self.response = ttk.Label(self)
        self.response.grid(row=5, column=0, columnspan=2)

    def change_password(self, _event=None):
        self.response['foreground'] = 'red'

        old_password = self.old_password.get()
        if not validation.verify_login(self.username, old_password):
            self.response['text'] = "Incorrect password."
            return

        new_password = self.new_password.get()
        if len(new_password) < 6:
            self.response['text'] = "Password should be 6 characters or more."
            return

        confirm_password = self.confirm_password.get()
        if new_password != confirm_password:
            self.response['text'] = "Password does not match."
            return

        SQL.users.change_password(self.username, new_password)

        self.response['foreground'] = 'green'
        self.response['text'] = "Successfully changed password."

        # Clear entry fields after password change
        self.old_password.delete(0, 'end')
        self.new_password.delete(0, 'end')
        self.confirm_password.delete(0, 'end')
