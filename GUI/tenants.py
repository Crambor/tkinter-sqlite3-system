# base imports
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

# module imports
import SQL
import validation


# A master frame [contained by the root Application]
# responsible for switching between the Edit, Register and Display Details frames for the tenants
class Tenants(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill='both', expand=True)

        # Creating the widgets
        self.register_frame = RegisterTenant(self, self.master)
        self.edit_frame = EditTenant(self, self.master)

        self.details_frame = TenantDetails(self, self.master)
        self.details_frame.pack(fill='both', expand=True)

    def set_focus(self):
        self.details_frame.search_bar.focus_set()

    def show_register_frame(self, _event=None):
        if not validation.apartments_exist():
            messagebox.showerror(title="Add Apartment",
                                 message="No apartments have been registered to this system.\n"
                                         "Please register an apartment before adding a tenant.")
            return

        self.details_frame.pack_forget()

        # Update tenant ID in case of external action
        self.register_frame.tenant_id.delete(0, 'end')
        self.register_frame.tenant_id.insert(0, SQL.tenants.get_free_tenant_id())

        # Show the actual frame to the user
        self.register_frame.pack(fill='both', expand=True)
        self.register_frame.forename.focus_set()

    def show_edit_frame(self, _event=None):
        tree = self.details_frame.tree
        item_id = tree.selection()
        # If the user double clicks or presses enter whilst not on an item, it ignores it
        if not item_id:
            return
        self.details_frame.pack_forget()  # Hide the details frame from the user

        tenant_id = tree.item(item_id, 'values')[0]
        self.edit_frame.populate_fields(tenant_id, item_id)  # Inserting record into the fields
        self.edit_frame.pack(fill='both', expand=True)
        self.edit_frame.forename.focus_set()

    def show_details_frame(self, _event=None):
        self.register_frame.pack_forget()
        self.edit_frame.pack_forget()

        self.details_frame.pack(fill='both', expand=True)
        self.details_frame.tree.focus_set()

    def delete_tenant(self, _event=None):
        tree = self.details_frame.tree
        item_id = tree.selection()
        # If the user presses delete whilst not on an item, it ignores it
        if not item_id:
            return

        record = tree.item(item_id, 'values')

        msg = (
            "Are you sure you want to delete this tenant?\n\n"
            f"{'Tenant ID:':20}\t{record[0]}\n"
            f"{'Forename:':20}\t{record[1]}\n"
            f"{'Surname:':20}\t{record[2]}\n"
            f"{'Contact:':20}\t{record[3]}\n"
            f"{'Address:':20}\t{record[4]}\n"
            f"{'Postcode:':20}\t{record[5]}")

        if messagebox.askyesno(title='Confirm Deletion', message=msg):
            tree.delete(item_id)
            SQL.tenants.delete_tenant(record[0])
            self.show_details_frame()

            messagebox.showinfo(title="Successful Deletion",
                                message="Successfully deleted tenant from database.")


# Child frame [Main page of Tenants frame]
# responsible for containing the tenant details
class TenantDetails(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller

        # a dictionary used to get the real field names using the header names in the display
        # key is header name from GUI, value is field name from database
        self.field_names = {"TenantID": "TenantID",
                            "Address": "ApartmentAddress",
                            "FlatNo": "FlatNumber",
                            "Postcode": "ApartmentPostcode"}

        self.search_field = "TenantID"
        self.previous_sort_fields = ['', '']
        self.search_term = ''  # This is used to prevent constant queries to the database when spam clicking 'search'
        header_names = ("TenantID", "Forename", "Surname", "Contact", "Address", "FlatNo", "Postcode")

        # Creating the widgets
        self.search_options_var = tk.StringVar()
        search_options = ttk.OptionMenu(self, self.search_options_var, header_names[0], *header_names,
                                        command=self.set_search_column)
        search_options.configure(width=9)  # This will prevent resizing the menu every time a choice is chosen
        search_options.grid(row=0, column=0, sticky='NW', padx=(10, 0), pady=(10, 0))

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

        add_tenant = ttk.Button(self, text="Add Tenant",
                                command=self.master.show_register_frame)
        add_tenant.bind('<Return>', self.master.show_register_frame)
        add_tenant.grid(row=0, column=4, padx=(5, 0), pady=(10, 0))

        self.tree = ttk.Treeview(self, columns=header_names, show='headings', selectmode='browse')

        self.item_menu = tk.Menu(self.tree, tearoff=0)
        self.item_menu.add_command(label='Edit Tenant', command=self.master.show_edit_frame)
        self.item_menu.add_command(label='Delete Tenant', command=self.master.delete_tenant)

        self.off_item_menu = tk.Menu(self.tree, tearoff=0)
        self.off_item_menu.add_command(label='Register Tenant', command=self.master.show_register_frame)

        self.tree.bind('<Double-1>', self.master.show_edit_frame)
        self.tree.bind('<Return>', self.master.show_edit_frame)
        self.tree.bind('<Delete>', self.master.delete_tenant)
        self.tree.bind('<Button-3>', self.menu_popup)

        col_widths = (70, 80, 100, 100, 180, 70, 80)
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

        # Adding the records into the tree and sorting them by tenant ID
        self.sort_records()

    def set_search_column(self, search_field):
        self.search_term = None
        self.search_field = self.field_names.get(search_field, f"Tenant{search_field}")
        self.search()

    def search(self, _event=None):
        search_term = ' '.join(self.search_bar.get().split())
        if self.search_term == search_term:
            return

        self.search_term = search_term

        sort_field = self.previous_sort_fields[1]
        if self.previous_sort_fields[0] == sort_field:
            self.previous_sort_fields[0] = ''
        else:
            self.previous_sort_fields[0] = sort_field

        self.sort_records(sort_field)

    def refresh(self, _event=None):
        self.search_term = ''
        self.search_field = "TenantID"
        self.search_options_var.set("TenantID")
        self.search_bar.delete(0, 'end')

        previous_sort_field = self.previous_sort_fields[1]
        if previous_sort_field:
            self.tree.heading(previous_sort_field, text=previous_sort_field)

        self.previous_sort_fields = ['', '']
        self.tree.delete(*self.tree.get_children())
        self.sort_records()

        messagebox.showinfo(title='Refreshed', message="Successfully refreshed records!")

    def sort_records(self, sort_field="TenantID"):
        records = SQL.tenants.get_tenants(self.field_names.get(sort_field, f"Tenant{sort_field}"),
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
        for tenant in records:
            self.tree.insert("", index=insert_index, values=tenant)

    def menu_popup(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)
            self.item_menu.post(event.x_root, event.y_root)
        else:
            self.off_item_menu.post(event.x_root, event.y_root)


# Child frame [Secondary page of Tenants frame]
# responsible for registering new tenants into the system
class RegisterTenant(tk.Frame):
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

        # This function allows you to pack the label and option menu side by side.
        # It returns the option menu variable for later usage.
        def make_labelled_option_menu(parent, label_text, options):
            options = (f"Select {label_text}", *options)
            frame = tk.Frame(parent)
            frame.pack(side='top', fill='x', padx=(10, 0), pady=(10, 0))

            ttk.Label(frame, width=15, text=label_text).pack(side='left', anchor='w')
            option_menu_var = tk.StringVar()
            option_menu = ttk.OptionMenu(frame, option_menu_var, options[0], *options)
            option_menu.pack(side='right', fill='x', expand=True, padx=10)
            return option_menu_var

        # Creating the widgets
        details_frame = tk.Frame(self)
        details_frame.pack(side='top', fill='both', expand=True)

        # left side of details frame
        left_widgets = tk.Frame(details_frame)

        left_fields = tk.Frame(left_widgets)
        self.tenant_id = make_labelled_entry(left_fields, "Tenant ID")
        self.forename = make_labelled_entry(left_fields, "Forename")
        self.surname = make_labelled_entry(left_fields, "Surname")
        self.contact = make_labelled_entry(left_fields, "Contact Number")
        self.address = make_labelled_option_menu(left_fields, "Address", SQL.apartments.get_addresses())
        self.flat_number = make_labelled_entry(left_fields, "Flat Number")
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

        add_tenant_button = ttk.Button(right_entry, width=20, text="Add Tenant",
                                       command=self.register_tenant)
        add_tenant_button.bind('<Return>', self.register_tenant)
        add_tenant_button.pack(side='left')
        right_entry.pack(side='bottom', fill='x', expand=True)

        right_widgets.pack(side='left', fill='x', expand=True, padx=10)

        # back button
        self.back = ttk.Button(self, width=10, text="Go Back",
                               command=self.master.show_details_frame)
        self.back.pack(side='left', padx=(5, 0), pady=(0, 5))

    def clear_fields(self):
        self.tenant_id.delete(0, 'end')
        self.tenant_id.insert(0, SQL.tenants.get_free_tenant_id())
        self.forename.delete(0, 'end')
        self.surname.delete(0, 'end')
        self.contact.delete(0, 'end')
        self.address.set("Select Address")
        self.flat_number.delete(0, 'end')
        self.description.delete('1.0', tk.END)

    def register_tenant(self, _event=None):
        self.response['foreground'] = 'red'

        tenant_id = self.tenant_id.get().upper()
        if not tenant_id:
            self.response['text'] = "Tenant ID is empty."
            return

        if validation.tenant_exists(tenant_id):
            self.response['text'] = "Tenant ID already taken."
            return

        if not validation.check_tenant_id(tenant_id):
            self.response['text'] = "Tenant ID must be in format 'T0000'"
            return

        forename = self.forename.get().title()
        if not forename:
            self.response['text'] = "Forename is empty."
            return

        surname = self.surname.get().title()
        if not surname:
            self.response['text'] = "Surname is empty."
            return

        contact = self.contact.get()
        if not contact:
            self.response['text'] = "Contact is empty."
            return

        if not validation.check_contact(contact):
            self.response['text'] = "Contact number is in an incorrect format."
            return

        flat_id = None
        address = self.address.get()
        flat_number = self.flat_number.get()
        if address != "Select Address" and flat_number:
            flat_id = SQL.tenants.get_flat_id(address, flat_number)
            if not flat_id:
                self.response['text'] = "This flat number is not registered to this address."
                return

        description = self.description.get('1.0', tk.END)
        record = (tenant_id, flat_id, forename, surname, contact, description)
        SQL.tenants.add_tenant(record)

        postcode = SQL.tenants.get_postcode(address)[0][0]
        record = (tenant_id, forename, surname, contact, address, flat_number, postcode)
        self.master.details_frame.tree.insert('', index=0, values=record)

        # Clear entry fields after account creation
        self.clear_fields()

        self.response['text'] = ""
        self.master.show_details_frame()
        messagebox.showinfo(title="Successfully registered tenant!",
                            message="Tenant has been successfully added to the database.")


# Child frame [Secondary page of Tenants frame]
# responsible for editing existing tenant details in the system
class EditTenant(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller

        self.item_id = ''

        # This function allows you to pack the label and entry side by side.
        # It returns the entry object for later usage.
        def make_labelled_entry(parent, label_text):
            frame = tk.Frame(parent)
            frame.pack(side='top', fill='x', padx=(10, 0), pady=(10, 0))

            ttk.Label(frame, width=15, text=label_text).pack(side='left', anchor='w')
            entry = ttk.Entry(frame, width=30)
            entry.pack(side='right', padx=10)
            return entry

        # This function allows you to pack the label and option menu side by side.
        # It returns the option menu variable for later usage.
        def make_labelled_option_menu(parent, label_text, options):
            options = (f"Select {label_text}", *options)
            frame = tk.Frame(parent)
            frame.pack(side='top', fill='x', padx=(10, 0), pady=(10, 0))

            ttk.Label(frame, width=15, text=label_text).pack(side='left', anchor='w')
            option_menu_var = tk.StringVar()
            option_menu = ttk.OptionMenu(frame, option_menu_var, options[0], *options)
            option_menu.pack(side='right', fill='x', expand=True, padx=10)
            return option_menu_var

        # Creating the widgets
        details_frame = tk.Frame(self)
        details_frame.pack(side='top', fill='both', expand=True)

        # left side of details frame
        left_widgets = tk.Frame(details_frame)
        left_widgets.pack(side='left')

        left_fields = tk.Frame(left_widgets)
        left_fields.pack(side='top', pady=20)
        self.tenant_id = make_labelled_entry(left_fields, "Tenant ID")
        self.forename = make_labelled_entry(left_fields, "Forename")
        self.surname = make_labelled_entry(left_fields, "Surname")
        self.contact = make_labelled_entry(left_fields, "Contact Number")
        self.address = make_labelled_option_menu(left_fields, "Address", SQL.apartments.get_addresses())
        self.flat_number = make_labelled_entry(left_fields, "Flat Number")
        left_fields.pack(side='top', pady=20)

        self.response = ttk.Label(left_widgets)
        self.response.pack(side='bottom')

        # right side of details frame
        right_widgets = tk.Frame(details_frame)
        right_widgets.pack(side='left', fill='x', expand=True, padx=10)

        right_label = tk.Frame(right_widgets)
        right_label.pack(side='top', anchor='w')
        ttk.Label(right_label, text='Description').pack(side='left', pady=(0, 10))

        right_entry = tk.Frame(right_widgets)
        right_entry.pack(side='bottom', fill='x', expand=True)
        self.description = ScrolledText(right_entry, width=40, height=11)
        self.description.pack(fill='x', expand=True, pady=(0, 15))

        edit_tenant_button = ttk.Button(right_entry, width=20, text="Update Tenant",
                                        command=self.edit_tenant)
        edit_tenant_button.bind('<Return>', self.edit_tenant)
        edit_tenant_button.pack(side='left')

        delete_tenant_button = ttk.Button(right_entry, width=20, text="Delete Tenant",
                                          command=self.master.delete_tenant)
        delete_tenant_button.bind('<Return>', self.master.delete_tenant)
        delete_tenant_button.pack(side='left', padx=(10, 0))

        # back button to return to details frame
        self.back = ttk.Button(self, width=10, text="Go Back",
                               command=self.master.show_details_frame)
        self.back.pack(side='left', padx=(5, 0), pady=(0, 5))

    def clear_fields(self):
        self.tenant_id.config(state='normal')
        self.tenant_id.delete(0, 'end')

        self.forename.delete(0, 'end')
        self.surname.delete(0, 'end')
        self.contact.delete(0, 'end')
        self.address.set("Select Address")
        self.flat_number.delete(0, 'end')
        self.description.delete('1.0', tk.END)

    def populate_fields(self, tenant_id, item_id):
        self.item_id = item_id

        self.clear_fields()
        self.tenant_id.insert(0, tenant_id)
        self.tenant_id.config(state='readonly')

        record = SQL.tenants.get_tenant(tenant_id)[0]
        self.forename.insert(0, record[0])
        self.surname.insert(0, record[1])
        self.contact.insert(0, record[2])
        self.address.set(record[3] if record[3] is not None else "Select Address")
        self.flat_number.insert(0, record[4] if record[4] is not None else '')
        self.description.insert('1.0', record[5])

    def edit_tenant(self, _event=None):
        self.response['foreground'] = 'red'

        tenant_id = self.tenant_id.get()
        forename = self.forename.get().title()
        if not forename:
            self.response['text'] = "Forename is empty."
            return

        surname = self.surname.get().title()
        if not surname:
            self.response['text'] = "Surname is empty."
            return

        contact = self.contact.get()
        if not contact:
            self.response['text'] = "Contact is empty."
            return

        if not validation.check_contact(contact):
            self.response['text'] = "Contact number is in an incorrect format."
            return

        flat_id = None
        address = self.address.get()
        flat_number = self.flat_number.get()
        if address != "Select Address" and flat_number:
            flat_id = SQL.tenants.get_flat_id(address, flat_number)
            if not flat_id:
                self.response['text'] = "This flat number is not registered to this address."
                return

        description = self.description.get('1.0', tk.END)
        record = (flat_id, forename, surname, contact, description)
        SQL.tenants.edit_tenant(tenant_id, record)

        postcode = SQL.tenants.get_postcode(address)[0][0]
        record = (tenant_id, forename, surname, contact, address, flat_number, postcode)
        self.master.details_frame.tree.item(self.item_id, values=record)

        self.response['text'] = ""
        self.master.show_details_frame()
        messagebox.showinfo(title="Successfully updated tenant!",
                            message="Tenant record has been successfully updated!")
