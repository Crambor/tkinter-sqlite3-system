# base imports
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

# module imports
import SQL
import validation


# Child frame [Bottom half of Edit Apartment And Flats frame]
# responsible for containing the flat details
class FlatDetails(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller

        # a dictionary used to get the real field names using the header names in the display
        # key is header name from GUI, value is field name from database
        self.field_names = {"Flat Number": "FlatNumber",
                            "Num Tenants": "NumTenants",
                            "Tenants": "Tenants",
                            "Weekly Rent": "WeeklyRent"}

        self.search_field = "FlatNumber"
        self.previous_sort_fields = ['Flat Number', 'Flat Number']
        self.search_term = ''  # This is used to prevent constant queries to the database when spam clicking 'search'
        header_names = ("Flat Number", "Num Tenants", "Tenants", "Weekly Rent")

        # Creating the widgets
        self.search_options_var = tk.StringVar()
        self.search_options = ttk.OptionMenu(self, self.search_options_var, header_names[0], *header_names,
                                             command=self.set_search_column)
        self.search_options.configure(width=12)  # This will prevent resizing the menu every time a choice is chosen
        self.search_options.grid(row=0, column=0, sticky='NW', padx=(10, 0), pady=(10, 0))

        self.search_bar = ttk.Entry(self)
        self.search_bar.bind('<Return>', self.search)
        self.search_bar.grid(row=0, column=1, sticky='EW', padx=(10, 0), pady=(10, 0))

        search_button = ttk.Button(self, width=8, text="Search",
                                   command=self.search)
        search_button.bind('<Return>', self.search)
        search_button.grid(row=0, column=2, padx=(5, 0), pady=(10, 0))

        refresh = ttk.Button(self, width=5, text='\u21ba',
                             command=self.refresh)
        refresh.bind('<Return>', self.refresh)
        refresh.grid(row=0, column=3, padx=(20, 0), pady=(10, 0))

        add_flat = ttk.Button(self, text="Add Flat",
                              command=self.master.show_register_frame)
        add_flat.bind('<Return>', self.master.show_register_frame)
        add_flat.grid(row=0, column=4, padx=(5, 0), pady=(10, 0))

        self.tree = ttk.Treeview(self, columns=header_names, show='headings', selectmode='browse')

        self.item_menu = tk.Menu(self.tree, tearoff=0)
        self.item_menu.add_command(label='Edit Flat', command=self.master.show_edit_frame)
        self.item_menu.add_command(label='Delete Flat', command=self.master.delete_flat)

        self.off_item_menu = tk.Menu(self.tree, tearoff=0)
        self.off_item_menu.add_command(label='Register Flat', command=self.master.show_register_frame)

        self.tree.bind('<Double-1>', self.master.show_edit_frame)
        self.tree.bind('<Return>', self.master.show_edit_frame)
        self.tree.bind('<Delete>', self.master.delete_flat)
        self.tree.bind('<Button-3>', self.menu_popup)

        col_widths = (100, 100, 380, 100)

        for i, col in enumerate(header_names):
            self.tree.column(col, width=col_widths[i], minwidth=col_widths[i])
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_records(c))

        self.tree.grid(row=1, column=0, sticky='NSEW', rowspan=3, columnspan=5, padx=(10, 0), pady=(10, 0))

        x_scrollbar = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        x_scrollbar.grid(row=4, column=0, sticky='EW', columnspan=5, padx=(10, 0), pady=(0, 10))

        y_scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        y_scrollbar.grid(row=1, column=5, sticky='NS', rowspan=3, padx=(0, 10), pady=(10, 0))

        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

        self.tree.config(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

    def set_search_column(self, search_field):
        self.search_term = None
        self.search_field = self.field_names.get(search_field, f"Flat{search_field}")
        self.search()

    def search(self, _event=None):
        search_term = ' '.join(self.search_bar.get().split())
        if self.search_term == search_term:
            return

        self.search_term = search_term
        self.update_records()

    def refresh(self, _event=None):
        self.search_term = ''
        self.search_field = "FlatNumber"
        self.search_options_var.set("Flat Number")
        self.search_bar.delete(0, 'end')

        previous_sort_field = self.previous_sort_fields[1]
        if previous_sort_field:
            self.tree.heading(previous_sort_field, text=previous_sort_field)

        self.previous_sort_fields = ['', '']
        self.tree.delete(*self.tree.get_children())
        self.sort_records()

        messagebox.showinfo(title='Refreshed', message="Successfully refreshed records!")

    def update_records(self):
        sort_field = self.previous_sort_fields[1]
        if self.previous_sort_fields[0] == sort_field:
            self.previous_sort_fields[0] = ''
        else:
            self.previous_sort_fields[0] = sort_field

        self.sort_records(sort_field)

    def sort_records(self, sort_field="Flat Number"):
        if sort_field == "Tenants":
            return

        records = SQL.flats.get_flats(self.master.apartment.apartment_id.get(),
                                      self.field_names.get(sort_field, f"Flat{sort_field}"),
                                      self.search_field, self.search_term)

        previous_sort_field = self.previous_sort_fields[1]
        if previous_sort_field:
            self.tree.heading(previous_sort_field, text=previous_sort_field)

        self.previous_sort_fields[1] = sort_field
        if self.previous_sort_fields[0] == self.previous_sort_fields[1]:
            insert_index = 0
            self.previous_sort_fields[0] = ''
            self.tree.heading(sort_field, text=sort_field + " ▼")
        else:
            insert_index = 'end'
            self.previous_sort_fields[0] = sort_field
            self.tree.heading(sort_field, text=sort_field + " ▲")

        self.tree.delete(*self.tree.get_children())
        for flat in records:
            flat = [f"{val}" if type(val) != float else f"£{val:.2f}" for val in flat]
            self.tree.insert("", index=insert_index, values=flat)

    def menu_popup(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)
            self.item_menu.post(event.x_root, event.y_root)
        else:
            self.off_item_menu.post(event.x_root, event.y_root)


# Child frame [Secondary page of Edit Apartments And Flats frame]
# responsible for registering new flats into the system
class RegisterFlat(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller

        # This function allows you to pack the label and entry side by side.
        # It returns the entry object for later usage.
        def make_labelled_entry(parent, label_text):
            frame = tk.Frame(parent)
            frame.pack(side='top', fill='x', padx=(10, 0), pady=(10, 0))

            ttk.Label(frame, width=15, text=label_text).pack(side='left', anchor='w')
            entry = ttk.Entry(frame, width=30)
            entry.pack(side='right', padx=10)
            return entry

        # Creating the widgets
        details_frame = tk.Frame(self)
        details_frame.pack(side='top', fill='both', expand=True)

        # left side of details frame
        left_widgets = tk.Frame(details_frame)

        left_fields = tk.Frame(left_widgets)
        self.apartment_id = make_labelled_entry(left_fields, "Apartment ID")
        self.address = make_labelled_entry(left_fields, "Address")
        self.postcode = make_labelled_entry(left_fields, "Postcode")
        self.flat_number = make_labelled_entry(left_fields, "Flat Number")
        self.weekly_rent = make_labelled_entry(left_fields, "Weekly Rent")
        left_fields.pack(side='top', pady=20)

        self.response = ttk.Label(left_widgets)
        self.response.pack(side='bottom')
        left_widgets.pack(side='left')

        # right side of details frame
        right_widgets = tk.Frame(details_frame)
        right_label = tk.Frame(right_widgets)
        ttk.Label(right_label, text='Description').pack(side='left', pady=(0, 10))
        right_label.pack(side='top', anchor='w')

        right_entry = tk.Frame(right_widgets)
        self.description = ScrolledText(right_entry, width=40, height=11)
        self.description.pack(fill='x', expand=True, pady=(0, 15))

        add_flat_button = ttk.Button(right_entry, width=20, text="Add Flat",
                                     command=self.register_flat)
        add_flat_button.bind('<Return>', self.register_flat)
        add_flat_button.pack(side='left')
        right_entry.pack(side='bottom', fill='x', expand=True)

        right_widgets.pack(side='left', fill='x', expand=True, padx=10)

        # back button
        back_button = ttk.Button(self, width=10, text="Go Back",
                                 command=self.master.show_details_frame)
        back_button.pack(side='left', padx=(5, 0), pady=(0, 5))

    def clear_fields(self):
        self.apartment_id.configure(state='normal')
        self.apartment_id.delete(0, 'end')

        self.address.configure(state='normal')
        self.address.delete(0, 'end')

        self.postcode.configure(state='normal')
        self.postcode.delete(0, 'end')

        self.flat_number.delete(0, 'end')
        self.weekly_rent.delete(0, 'end')
        self.description.delete('1.0', tk.END)

    def populate_fields(self):
        self.clear_fields()
        self.apartment_id.insert(0, self.master.apartment.apartment_id.get())
        self.apartment_id.configure(state='readonly')

        self.address.insert(0, self.master.apartment.address.get())
        self.address.configure(state='readonly')

        self.postcode.insert(0, self.master.apartment.postcode.get())
        self.postcode.configure(state='readonly')

    def register_flat(self, _event=None):
        self.response['foreground'] = 'red'

        apartment_id = self.apartment_id.get()
        flat_number = self.flat_number.get()
        if not flat_number:
            self.response['text'] = "Flat number is empty."
            return

        if not flat_number.isdigit():
            self.response['text'] = "Flat number must be an integer."
            return

        if validation.apartment_flat_exists(apartment_id, flat_number):
            self.response['text'] = "This flat number is already taken."
            return

        weekly_rent = self.weekly_rent.get()
        if not weekly_rent:
            self.response['text'] = "Weekly rent is empty."
            return

        if not validation.is_float(weekly_rent):
            self.response['text'] = "Weekly rent must be a monetary amount."
            return
        weekly_rent = f"{float(weekly_rent):.2f}"

        description = self.description.get('1.0', tk.END)

        record = (SQL.flats.get_free_flat_id(), apartment_id, flat_number, weekly_rent, description)
        SQL.flats.add_flat(record)

        # Clear entry fields after flat creation
        self.clear_fields()

        self.response['text'] = ""
        self.master.show_details_frame()
        messagebox.showinfo(title="Successfully registered flat!",
                            message="Flat has been successfully added to the database.")


# Child frame [Secondary page of Edit Apartments And Flats frame]
# responsible for editing existing flats in the system
class EditFlat(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller

        self.flat_id = ''
        self.previous_flat_number = -1

        # This function allows you to pack the label and entry side by side.
        # It returns the entry object for later usage.
        def make_labelled_entry(parent, label_text):
            frame = tk.Frame(parent)
            frame.pack(side='top', fill='x', padx=(10, 0), pady=(10, 0))

            ttk.Label(frame, width=15, text=label_text).pack(side='left', anchor='w')
            entry = ttk.Entry(frame, width=30)
            entry.pack(side='right', padx=10)
            return entry

        # Creating the widgets
        details_frame = tk.Frame(self)
        details_frame.pack(side='top', fill='both', expand=True)

        # left side of details frame
        left_widgets = tk.Frame(details_frame)

        left_fields = tk.Frame(left_widgets)
        self.apartment_id = make_labelled_entry(left_fields, "Apartment ID")
        self.address = make_labelled_entry(left_fields, "Address")
        self.postcode = make_labelled_entry(left_fields, "Postcode")
        self.flat_number = make_labelled_entry(left_fields, "Flat Number")
        self.weekly_rent = make_labelled_entry(left_fields, "Weekly Rent")
        left_fields.pack(side='top', pady=20)

        self.response = ttk.Label(left_widgets)
        self.response.pack(side='bottom')
        left_widgets.pack(side='left')

        # right side of details frame
        right_widgets = tk.Frame(details_frame)
        right_label = tk.Frame(right_widgets)
        ttk.Label(right_label, text='Description').pack(side='left', pady=(0, 10))
        right_label.pack(side='top', anchor='w')

        right_entry = tk.Frame(right_widgets)
        self.description = ScrolledText(right_entry, width=40, height=11)
        self.description.pack(fill='x', expand=True, pady=(0, 15))

        edit_flat_button = ttk.Button(right_entry, width=20, text="Update Flat",
                                      command=self.edit_flat)
        edit_flat_button.bind('<Return>', self.edit_flat)
        edit_flat_button.pack(side='left')

        delete_flat_button = ttk.Button(right_entry, width=20, text="Delete Flat",
                                        command=self.master.delete_flat)
        delete_flat_button.bind('<Return>', self.master.delete_flat)
        delete_flat_button.pack(side='left', padx=(5, 0))
        right_entry.pack(side='bottom', fill='x', expand=True)

        right_widgets.pack(side='left', fill='x', expand=True, padx=10)

        # back button
        back_button = ttk.Button(self, width=10, text="Go Back",
                                 command=self.master.show_details_frame)
        back_button.pack(side='left', padx=(5, 0), pady=(0, 5))

    def clear_fields(self):
        self.apartment_id.configure(state='normal')
        self.apartment_id.delete(0, 'end')

        self.address.configure(state='normal')
        self.address.delete(0, 'end')

        self.postcode.configure(state='normal')
        self.postcode.delete(0, 'end')

        self.flat_number.delete(0, 'end')
        self.weekly_rent.delete(0, 'end')
        self.description.delete('1.0', tk.END)

    def populate_fields(self, flat_id, flat_number, weekly_rent):
        self.flat_id = flat_id
        self.previous_flat_number = flat_number

        self.clear_fields()
        self.apartment_id.insert(0, self.master.apartment.apartment_id.get())
        self.apartment_id.configure(state='readonly')

        self.address.insert(0, self.master.apartment.address.get())
        self.address.configure(state='readonly')

        self.postcode.insert(0, self.master.apartment.postcode.get())
        self.postcode.configure(state='readonly')

        self.flat_number.insert(0, flat_number)
        self.weekly_rent.insert(0, weekly_rent)

    def edit_flat(self, _event=None):
        self.response['foreground'] = 'red'

        apartment_id = self.apartment_id.get()
        flat_number = self.flat_number.get()
        if not flat_number:
            self.response['text'] = "Flat number is empty."
            return

        if not flat_number.isdigit():
            self.response['text'] = "Flat number must be an integer."
            return

        if flat_number != self.previous_flat_number and validation.apartment_flat_exists(apartment_id, flat_number):
            self.response['text'] = "This flat number is already taken."
            return

        weekly_rent = self.weekly_rent.get()
        if not weekly_rent:
            self.response['text'] = "Weekly rent is empty."
            return

        if not validation.is_float(weekly_rent):
            self.response['text'] = "Weekly rent must be a monetary amount."
            return
        weekly_rent = f"{float(weekly_rent):.2f}"

        description = self.description.get('1.0', tk.END)

        record = (flat_number, weekly_rent, description)
        SQL.flats.edit_flat(self.flat_id, record)

        # Clear entry fields after flat update
        self.clear_fields()

        self.response['text'] = ""
        self.master.show_details_frame()
        messagebox.showinfo(title="Successfully updated flat!",
                            message="Flat has been successfully updated in the database.")
