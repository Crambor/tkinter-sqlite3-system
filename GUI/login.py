# base imports
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# module imports
import validation


# A master frame [contained by the root Application].
# responsible for handling the initial login when the program first starts, or after the user logs out.
class Login(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(expand=True)

        # Creating the widgets
        ttk.Label(self, text='Username').grid(row=0, column=0, sticky='W')
        self.username = ttk.Entry(self)
        self.username.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self, text='Password').grid(row=1, column=0, sticky='W')
        self.password = ttk.Entry(self, show="\u2022")
        self.password.bind('<Return>', self.verify_login)
        self.password.grid(row=1, column=1, padx=10)

        self.login = ttk.Button(self, width=20, text="Login",
                                command=self.verify_login)
        self.login.bind('<Return>', self.verify_login)
        self.login.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        self.response = ttk.Label(self, foreground='red')
        self.response.grid(row=3, column=0, columnspan=2)

    def set_focus(self):
        self.username.focus_set()

    # Method responsible for checking the login details and switching pages if the login credentials are authenticated.
    def verify_login(self, _event=None):
        username = self.username.get()
        password = self.password.get()

        if not validation.verify_login(username, password):
            self.response['text'] = "Incorrect username or password."
            return

        self.master.login(username)
        if username == 'admin' and password == 'password':
            messagebox.showinfo(
                title="Register",
                message="It is recommended for you to register an account to prevent potential security breaches.\n\n"
                        "This can be done within the 'Manage Users' menu option.")
