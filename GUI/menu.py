# base imports
import tkinter as tk
from tkinter import ttk

# relative module imports for all the frames
from .manageusers import ManageUsers
from .employees import Employees
from .payments import Payments
from .tenants import Tenants
from .apartments import Apartments


# A master frame [contained by the root Application]
# responsible for containing the buttons that switch between different pages of the application.
class Menu(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill='both')

        # Creating the widgets
        logout = ttk.Button(self, width=10, text="Logout",
                            command=self.master.logout)
        logout.bind('<Return>', self.master.logout)
        logout.pack(side='left', fill='both', expand=True, padx=(0, 14))

        manage_users = ttk.Button(self, width=16, text="Manage Users",
                                  command=lambda: self.next_frame(ManageUsers))
        manage_users.bind('<Return>', lambda: self.next_frame(ManageUsers))
        manage_users.pack(side='left', fill='both', expand=True)

        view_employees = ttk.Button(self, width=16, text="Employees",
                                    command=lambda: self.next_frame(Employees))
        view_employees.bind('<Return>', lambda: self.next_frame(Employees))
        view_employees.pack(side='left', fill='both', expand=True)

        view_payments = ttk.Button(self, width=16, text="Payments",
                                   command=lambda: self.next_frame(Payments))
        view_payments.bind('<Return>', lambda: self.next_frame(Payments))
        view_payments.pack(side='left', fill='both', expand=True)

        view_tenants = ttk.Button(self, width=16, text="Tenants",
                                  command=lambda: self.next_frame(Tenants))
        view_tenants.bind('<Return>', lambda: self.next_frame(Tenants))
        view_tenants.pack(side='left', fill='both', expand=True)

        view_apartments = ttk.Button(self, width=16, text="Apartments",
                                     command=lambda: self.next_frame(Apartments))
        view_apartments.bind('<Return>', lambda: self.next_frame(Apartments))
        view_apartments.pack(side='left', fill='both', expand=True)

        # Buttons for usage in enabling and disabling on press
        self.current_button = manage_users
        self.current_button.configure(state='disabled')
        self.buttons = {"ManageUsers": manage_users,
                        "Employees": view_employees,
                        "Payments": view_payments,
                        "Tenants": view_tenants,
                        "Apartments": view_apartments}

    def next_frame(self, frame, _event=None):
        self.current_button.configure(state='normal')
        self.current_button = self.buttons[frame.__name__]
        self.current_button.configure(state='disabled')

        self.master.next_frame(frame)
