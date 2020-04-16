# base imports
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

# module imports
import SQL
import validation

# relative imports from neighbouring modules
from . import flats


# A master frame [contained by the root Application]
# responsible for managing the user accounts on the system.
class Apartments(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(expand=True, fill='both')

        # Creating the widgets
        self.register_frame = RegisterApartment(self, self.master)
        self.edit_frame = EditApartmentAndFlats(self, self.master)

        self.details_frame = ApartmentDetails(self, self.master)
        self.details_frame.pack(fill='both', expand=True)

    def set_focus(self):
        self.details_frame.search_bar.focus_set()

    def show_register_frame(self, _event=None):
        self.details_frame.pack_forget()

        # Update apartment ID in case of external action
        self.register_frame.apartment_id.delete(0, 'end')
        self.register_frame.apartment_id.insert(0, SQL.apartments.get_free_apartment_id())

        # Show the actual frame to the user
        self.register_frame.pack(fill='both', expand=True)
        self.register_frame.address.focus_set()

    def show_edit_frame(self, _event=None):
        tree = self.details_frame.tree
        item_id = tree.selection()
        # If the user double clicks or presses enter whilst not on an item, it ignores it
        if not item_id:
            return
        self.details_frame.pack_forget()  # Hide the details frame from the user

        apartment_id = tree.item(item_id, 'values')[0]
        self.edit_frame.apartment.populate_fields(apartment_id, item_id)  # Inserting record into the fields
        self.edit_frame.show_details_frame()
        self.edit_frame.pack(fill='both', expand=True)
        self.edit_frame.set_focus()

    def show_details_frame(self, _event=None):
        self.register_frame.pack_forget()
        self.edit_frame.pack_forget()

        self.details_frame.pack(fill='both', expand=True)
        self.details_frame.tree.focus_set()

    def delete_apartment(self, _event=None):
        tree = self.details_frame.tree
        item_id = tree.selection()
        # If the user presses delete whilst not on an item, it ignores it
        if not item_id:
            return

        record = tree.item(item_id, 'values')

        msg = (
            "Are you sure you want to delete this apartment?"
            "\nWarning: This will delete all flats tied to this address.\n\n"
            f"{'Apartment ID:':20}\t{record[0]}\n"
            f"{'Num. Flats:':20}\t{record[1]}\n"
            f"{'Num. Tenants:':20}\t{record[2]}\n"
            f"{'Upkeep:':20}\t{record[3]}\n"
            f"{'Address:':20}\t{record[4]}\n"
            f"{'Postcode:':20}\t{record[5]}")

        if messagebox.askyesno(title='Confirm Deletion', message=msg):
            tree.delete(item_id)
            SQL.apartments.delete_apartment(record[0])
            self.show_details_frame()

            messagebox.showinfo(title="Successful Deletion",
                                message="Successfully deleted apartment from database.")


# Child frame [Main page of Apartments frame]
# responsible for containing the apartment and flat details
class ApartmentDetails(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller

        # a dictionary used to get the real field names using the header names in the display
        # key is header name from GUI, value is field name from database
        self.field_names = {"ApartmentID": "ApartmentID",
                            "Num Flats": "NumFlats",
                            "Num Tenants": "NumTenants",
                            "Upkeep": "Upkeep"}

        self.search_field = "ApartmentID"
        self.previous_sort_fields = ['', '']
        self.search_term = ''  # This is used to prevent constant queries to the database when spam clicking 'search'
        header_names = ("ApartmentID", "Num Flats", "Num Tenants", "Upkeep", "Address", "Postcode")

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

        add_apartment = ttk.Button(self, text="Add Apartment",
                                   command=self.master.show_register_frame)
        add_apartment.bind('<Return>', self.master.show_register_frame)
        add_apartment.grid(row=0, column=4, padx=(5, 0), pady=(10, 0))

        self.tree = ttk.Treeview(self, columns=header_names, show='headings', selectmode='browse')

        self.item_menu = tk.Menu(self.tree, tearoff=0)
        self.item_menu.add_command(label='Edit Apartment', command=self.master.show_edit_frame)
        self.item_menu.add_command(label='Delete Apartment', command=self.master.delete_apartment)

        self.off_item_menu = tk.Menu(self.tree, tearoff=0)
        self.off_item_menu.add_command(label='Register Apartment', command=self.master.show_register_frame)

        self.tree.bind('<Double-1>', self.master.show_edit_frame)
        self.tree.bind('<Return>', self.master.show_edit_frame)
        self.tree.bind('<Delete>', self.master.delete_apartment)
        self.tree.bind('<Button-3>', self.menu_popup)

        col_widths = (100, 100, 120, 100, 180, 80)  # This is used to set the widths of each header column

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

        # Adding the records into the tree and sorting them by apartment ID
        self.sort_records()

    def set_search_column(self, search_field):
        self.search_term = None
        self.search_field = self.field_names.get(search_field, f"Apartment{search_field}")
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
        self.search_field = "ApartmentID"
        self.search_options_var.set("ApartmentID")
        self.search_bar.delete(0, 'end')

        previous_sort_field = self.previous_sort_fields[1]
        if previous_sort_field:
            self.tree.heading(previous_sort_field, text=previous_sort_field)

        self.previous_sort_fields = ['', '']
        self.tree.delete(*self.tree.get_children())
        self.sort_records()

        messagebox.showinfo(title='Refreshed', message="Successfully refreshed records!")

    def sort_records(self, sort_field="ApartmentID"):
        records = SQL.apartments.get_apartments(self.field_names.get(sort_field, f"Apartment{sort_field}"),
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
        for apartment in records:
            apartment = [f"{val}" if type(val) != float else f"£{val:.2f}" for val in apartment]
            self.tree.insert("", index=insert_index, values=apartment)

    def menu_popup(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)
            self.item_menu.post(event.x_root, event.y_root)
        else:
            self.off_item_menu.post(event.x_root, event.y_root)


# Child frame [Secondary page of Apartment frame]
# responsible for adding new apartments into the system
class RegisterApartment(tk.Frame):
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

        add_apartment_button = ttk.Button(right_entry, width=20, text="Add Apartment",
                                          command=self.register_apartment)
        add_apartment_button.bind('<Return>', self.register_apartment)
        add_apartment_button.pack(side='left')
        right_entry.pack(side='bottom', fill='x', expand=True)

        right_widgets.pack(side='left', fill='x', expand=True, padx=10)

        # back button to return to apartment details frame
        back_button = ttk.Button(self, width=10, text="Go Back",
                                 command=self.master.show_details_frame)
        back_button.pack(side='left', padx=(5, 0), pady=(0, 5))

    def clear_fields(self):
        self.apartment_id.delete(0, 'end')
        self.address.delete(0, 'end')
        self.postcode.delete(0, 'end')
        self.description.delete('1.0', tk.END)

    def register_apartment(self, _event=None):
        self.response['foreground'] = 'red'

        apartment_id = self.apartment_id.get().upper()
        if not apartment_id:
            self.response['text'] = "Apartment ID is empty."
            return

        if validation.apartment_exists(apartment_id):
            self.response['text'] = "Apartment ID already taken."
            return

        if not validation.check_apartment_id(apartment_id):
            self.response['text'] = "Apartment ID must be in format 'A0000'"
            return

        address = self.address.get().title()
        if not address:
            self.response['text'] = "Address is empty."
            return

        postcode = self.postcode.get().upper()
        if not postcode:
            self.response['text'] = "Postcode is empty."
            return

        if not validation.check_postcode(postcode):
            self.response['text'] = "Postcode is in an incorrect format."
            return

        description = self.description.get('1.0', tk.END)

        record = (apartment_id, address, postcode, description)
        SQL.apartments.add_apartment(record)

        record = (apartment_id, 0, 0, '0.00', address, postcode)
        self.master.details_frame.tree.insert('', index=0, values=record)

        # Clear entry fields after account creation
        self.clear_fields()

        self.response['text'] = ""
        self.master.show_details_frame()
        messagebox.showinfo(title="Successfully registered apartment!",
                            message="Apartment has been successfully added to the database.")


# Child frame [Top half of Edit Apartment and Flats frame]
# responsible for editing existing apartments in the system
class EditApartment(tk.Frame):
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

        # left side of frame
        left_widgets = tk.Frame(self)

        left_fields = tk.Frame(left_widgets)
        self.apartment_id = make_labelled_entry(left_fields, "Apartment ID")
        self.num_flats = make_labelled_entry(left_fields, "Num Flats")
        self.num_tenants = make_labelled_entry(left_fields, "Num Tenants")
        self.upkeep = make_labelled_entry(left_fields, "Upkeep")
        self.address = make_labelled_entry(left_fields, "Address")
        self.postcode = make_labelled_entry(left_fields, "Postcode")
        left_fields.pack(side='top', pady=20)

        self.response = ttk.Label(left_widgets)
        self.response.pack(side='bottom')
        left_widgets.pack(side='left')

        # right side of frame
        right_widgets = tk.Frame(self)
        right_widgets.pack(side='left', fill='x', expand=True, padx=10)

        right_label = tk.Frame(right_widgets)
        ttk.Label(right_label, text='Description').pack(side='left', pady=(0, 10))
        right_label.pack(side='top', anchor='w')

        right_entry = tk.Frame(right_widgets)
        right_entry.pack(side='bottom', fill='x', expand=True)

        self.description = ScrolledText(right_entry, width=40, height=11)
        self.description.pack(fill='x', expand=True, pady=(0, 15))

        edit_apartment_button = ttk.Button(right_entry, width=20, text="Update Apartment",
                                           command=self.edit_apartment)
        edit_apartment_button.bind('<Return>', self.edit_apartment)
        edit_apartment_button.pack(side='left')

        delete_apartment_button = ttk.Button(right_entry, width=20, text="Delete Apartment",
                                             command=self.controller.delete_apartment)
        delete_apartment_button.bind('<Return>', self.controller.delete_apartment)
        delete_apartment_button.pack(side='left', padx=(10, 0))

        # back button to return to display view
        back_button = ttk.Button(right_entry, width=10, text="Go Back",
                                 command=self.controller.show_details_frame)
        back_button.pack(side='right', padx=(0, 15))

    def clear_fields(self):
        self.apartment_id.config(state='normal')
        self.apartment_id.delete(0, 'end')

        self.num_flats.config(state='normal')
        self.num_flats.delete(0, 'end')

        self.num_tenants.config(state='normal')
        self.num_tenants.delete(0, 'end')

        self.upkeep.config(state='normal')
        self.upkeep.delete(0, 'end')

        self.address.delete(0, 'end')
        self.postcode.delete(0, 'end')
        self.description.delete('1.0', tk.END)

    def populate_fields(self, apartment_id, item_id):
        self.item_id = item_id
        self.update_fields(apartment_id)

    def update_fields(self, apartment_id):
        self.clear_fields()
        self.apartment_id.insert(0, apartment_id)
        self.apartment_id.config(state='readonly')

        record = list(SQL.apartments.get_apartment(apartment_id)[0])
        record[2] = f"£{record[2]:.2f}"
        self.controller.details_frame.tree.item(self.item_id, values=(apartment_id, *record[:-1]))

        self.num_flats.insert(0, record[0])
        self.num_flats.config(state='readonly')

        self.num_tenants.insert(0, record[1])
        self.num_tenants.config(state='readonly')

        self.upkeep.insert(0, record[2])
        self.upkeep.config(state='readonly')

        self.address.insert(0, record[3])
        self.postcode.insert(0, record[4])
        self.description.insert('1.0', record[5])

    def edit_apartment(self, _event=None):
        self.response['foreground'] = 'red'

        apartment_id = self.apartment_id.get()
        address = self.address.get().title()
        if not address:
            self.response['text'] = "Address is empty."
            return

        postcode = self.postcode.get().upper()
        if not postcode:
            self.response['text'] = "Postcode is empty."
            return

        if not validation.check_postcode(postcode):
            self.response['text'] = "Postcode is in an incorrect format."
            return

        description = self.description.get('1.0', tk.END)

        record = (address, postcode, description)
        SQL.apartments.edit_apartment(apartment_id, record)

        record = (apartment_id, self.num_flats.get(), self.num_tenants.get(),
                  self.upkeep.get(), address, postcode)
        self.controller.details_frame.tree.item(self.item_id, values=record)

        # Clear entry fields after account creation
        self.clear_fields()

        self.response['text'] = ""
        self.controller.show_details_frame()
        messagebox.showinfo(title="Successfully updated apartment!",
                            message="Apartment has been successfully updated in the database.")


# A master frame [Secondary page of Apartment frame]
# responsible for adding new flats into the system and editing already existing apartments.
class EditApartmentAndFlats(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller

        self.apartment = EditApartment(self, self.master)
        self.apartment.pack(side='top', fill='both', expand=True)

        self.details_frame = flats.FlatDetails(self, self.master)
        self.details_frame.pack(side='top', fill='both', expand=True)

        self.register_frame = flats.RegisterFlat(self, self.master)
        self.edit_frame = flats.EditFlat(self, self.master)

    def set_focus(self):
        self.details_frame.search_bar.focus_set()

    def show_register_frame(self, _event=None):
        self.details_frame.pack_forget()
        self.apartment.pack_forget()

        self.register_frame.populate_fields()
        # Show the actual frame to the user
        self.register_frame.pack(fill='both', expand=True)
        self.register_frame.flat_number.focus_set()

    def show_edit_frame(self, _event=None):
        tree = self.details_frame.tree
        item_id = tree.selection()
        # If the user double clicks or presses enter whilst not on an item, it ignores it
        if not item_id:
            return
        self.details_frame.pack_forget()  # Hide the details frame from the user
        self.apartment.pack_forget()

        record = tree.item(item_id, 'values')

        flat_id = SQL.flats.get_flat_id(self.apartment.apartment_id.get(), record[0])[0][0]
        self.edit_frame.populate_fields(flat_id, record[0], record[3][1:])  # Inserting record into the fields
        self.edit_frame.pack(fill='both', expand=True)
        self.edit_frame.flat_number.focus_set()

    def show_details_frame(self, _event=None):
        self.register_frame.pack_forget()
        self.edit_frame.pack_forget()

        self.apartment.update_fields(self.apartment.apartment_id.get())
        self.apartment.pack(side='top', fill='both', expand=True)

        self.details_frame.update_records()
        self.details_frame.pack(side='top', fill='both', expand=True)
        self.details_frame.tree.focus_set()

    def delete_flat(self, _event=None):
        tree = self.details_frame.tree
        item_id = tree.selection()
        # if the user presses delete whilst not on an item, it deletes it
        if not item_id:
            return

        record = tree.item(item_id, 'values')

        msg = (
            "Are you sure you want to delete this flat?"
            "\nWarning: This will unbind any tenants from this flat.\n\n"
            f"{'Flat Number:':20}\t{record[0]}\n"
            f"{'Num. Tenants:':20}\t{record[1]}\n"
            f"{'Tenants:':20}\t{record[2]}\n"
            f"{'Weekly Rent:':20}\t{record[3]}")

        if messagebox.askyesno(title='Confirm Deletion', message=msg):
            flat_id = SQL.flats.get_flat_id(self.apartment.apartment_id.get(), record[0])[0][0]
            tree.delete(item_id)
            SQL.flats.delete_flat(flat_id)
            self.show_details_frame()

            messagebox.showinfo(title="Successful Deletion",
                                message="Successfully deleted flat from database.")
