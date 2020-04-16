# base imports
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

# module imports
import SQL
import validation


# A master frame [contained by the root Application]
# responsible for managing the user accounts on the system.
class Payments(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(expand=True, fill='both')

        # Creating the widgets
        self.register_frame = RegisterPayment(self, self.master)
        self.edit_frame = EditPayment(self, self.master)

        self.details_frame = PaymentDetails(self, self.master)
        self.details_frame.pack(fill='both', expand=True)

    def set_focus(self):
        self.details_frame.search_bar.focus_set()

    def show_register_frame(self, _event=None):
        self.details_frame.pack_forget()
        self.register_frame.pack(fill='both', expand=True)
        self.register_frame.method.focus_set()

    def show_edit_frame(self, _event=None):
        tree = self.details_frame.tree
        item_id = tree.selection()
        # If the user double clicks or presses enter whilst not on an item, it ignores it
        if not item_id:
            return
        self.details_frame.pack_forget()  # Hide the details frame from the user

        payment_id = self.details_frame.payment_ids[item_id[0]]
        payment_type = tree.item(item_id, 'values')[0]
        self.edit_frame.populate_fields(payment_id, payment_type)  # Inserting record into the fields
        self.edit_frame.pack(fill='both', expand=True)
        self.edit_frame.method.focus_set()

    def show_details_frame(self, _event=None):
        self.register_frame.pack_forget()
        self.edit_frame.pack_forget()

        self.details_frame.sort_records()
        self.details_frame.pack(fill='both', expand=True)
        self.details_frame.tree.focus_set()

    def delete_payment(self, _event=None):
        tree = self.details_frame.tree
        item_id = tree.selection()
        # If the user presses delete whilst not on an item, it ignores it
        if not item_id:
            return

        payment_id = self.details_frame.payment_ids[item_id[0]]
        record = tree.item(item_id, 'values')

        msg = (
            "Are you sure you want to delete this payment?\n\n"
            f"{'Payment Type:':20}\t{record[0]}\n"
            f"{'Payee:':20}\t{record[1]}\n"
            f"{'Method:':20}\t{record[2]}\n"
            f"{'Amount Paid:':20}\t{record[3]}\n"
            f"{'Payment Date:':20}\t{record[4]}\n"
            f"{'Payment Time:':20}\t{record[5]}")

        if messagebox.askyesno(title='Confirm Deletion', message=msg):
            tree.delete(item_id)
            SQL.payments.delete_payment(payment_id, record[0])
            self.show_details_frame()

            messagebox.showinfo(title="Successful Deletion",
                                message="Successfully deleted payment from database.")


# Child frame [Main page of Payments frame]
# responsible for containing the payment details
class PaymentDetails(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller

        # a dictionary used to get the real field names using the header names in the display
        # key is header name from GUI, value is field name from database
        self.field_names = {"Payee": "Payee",
                            "Amount": "TotalPaid"}

        self.payment_ids = {}
        self.search_field = "Payee"
        self.type_search = ['*', 'Inbound', 'Outbound']
        self.search_term = ''  # This is used to prevent constant queries to the database when spam clicking 'search'
        self.datetime_sorts = {'Date': 'DESC',
                               'Time': 'DESC'}
        self.header_names = ("Type", "Payee", "Method", "Amount", "Date", "Time")

        # Creating the widgets
        self.search_options_var = tk.StringVar()
        self.search_options = ttk.OptionMenu(self, self.search_options_var, self.header_names[0], *self.header_names,
                                             command=self.set_search_column)
        self.search_options_var.set("Payee")
        self.search_options.configure(width=8)  # This will prevent resizing the menu every time a choice is chosen
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

        generate_report = ttk.Button(self, text="Generate Report", state='disabled')
        generate_report.grid(row=0, column=4, padx=(5, 0), pady=(10, 0))

        add_payment = ttk.Button(self, text="Add Payment",
                                 command=self.master.show_register_frame)
        add_payment.bind('<Return>', self.master.show_register_frame)
        add_payment.grid(row=0, column=5, padx=(5, 0), pady=(10, 0))

        self.tree = ttk.Treeview(self, columns=self.header_names, show='headings', selectmode='browse')

        self.item_menu = tk.Menu(self.tree, tearoff=0)
        self.item_menu.add_command(label='Edit Payment', command=self.master.show_edit_frame)
        self.item_menu.add_command(label='Delete Payment', command=self.master.delete_payment)

        self.off_item_menu = tk.Menu(self.tree, tearoff=0)
        self.off_item_menu.add_command(label='Add Payment', command=self.master.show_register_frame)
        self.off_item_menu.add_command(label='Generate Report')

        self.tree.bind('<Double-1>', self.master.show_edit_frame)
        self.tree.bind('<Return>', self.master.show_edit_frame)
        self.tree.bind('<Delete>', self.master.delete_payment)
        self.tree.bind('<Button-3>', self.menu_popup)

        col_widths = (80, 200, 120, 100, 100, 80)
        for i, col in enumerate(self.header_names):
            self.tree.column(col, width=col_widths[i], minwidth=col_widths[i])
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_records(c))
        self.tree.heading('Date', text="Date ▲")
        self.tree.heading('Time', text="Time ▲")

        self.tree.grid(row=1, column=0, sticky='NSEW', rowspan=3, columnspan=6, padx=(10, 0), pady=(10, 0))

        x_scrollbar = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        x_scrollbar.grid(row=4, column=0, sticky='EW', columnspan=6, padx=(10, 0), pady=(0, 10))

        y_scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        y_scrollbar.grid(row=1, column=6, sticky='NS', rowspan=3, padx=(0, 10), pady=(10, 0))

        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

        self.tree.config(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

        # Adding the records into the tree and sorting them by payment ID
        self.sort_records()

    def set_search_column(self, search_field):
        self.search_term = None
        self.search_field = self.field_names.get(search_field, f"Payment{search_field}")
        self.search()

    def search(self, _event=None):
        search_term = ' '.join(self.search_bar.get().split())
        if self.search_term == search_term:
            return

        self.search_term = search_term
        self.sort_records()

    def refresh(self, _event=None):
        self.search_term = ''
        self.search_field = "Payee"
        self.search_options_var.set("Payee")
        self.search_bar.delete(0, 'end')
        self.type_search = ['*', 'Inbound', 'Outbound']

        self.datetime_sorts = {'Date': 'DESC',
                               'Time': 'DESC'}
        self.tree.heading('Date', text="Date ▲")
        self.tree.heading('Time', text="Time ▲")

        self.tree.delete(*self.tree.get_children())
        self.sort_records()

        messagebox.showinfo(title='Refreshed', message="Successfully refreshed records!")

    def sort_records(self, header_name=''):
        if header_name in ('Payee', 'Method', 'Amount'):
            return

        elif header_name == 'Type':
            self.type_search = self.type_search[1:] + [self.type_search.pop(0)]

        elif header_name in ('Date', 'Time'):
            current_sort = self.datetime_sorts[header_name]
            if current_sort == 'ASC':
                self.datetime_sorts[header_name] = 'DESC'
                self.tree.heading(header_name, text=header_name + " ▲")
            else:
                self.datetime_sorts[header_name] = 'ASC'
                self.tree.heading(header_name, text=header_name + " ▼")

        records = SQL.payments.get_payments(self.type_search[0], self.datetime_sorts,
                                            self.search_field, self.search_term)

        self.tree.delete(*self.tree.get_children())
        self.payment_ids = {}
        for payment in records:
            payment = [f"{val}" if type(val) != float
                       else f"+£{val:.2f}" if payment[1] == "Inbound"
                       else f"- £{val:.2f}"
                       for val in payment]

            item_id = self.tree.insert("", index='end', values=payment[1:])
            self.payment_ids[item_id] = payment[0]

    def menu_popup(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)
            self.item_menu.post(event.x_root, event.y_root)
        else:
            self.off_item_menu.post(event.x_root, event.y_root)


# Child frame [Secondary page of Payments frame]
# responsible for registering new payments into the system
class RegisterPayment(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller

        # This function allows you to pack the label and entry side by side.
        # It returns the entry object for later usage.
        def make_labelled_entry(parent, label_text, entry_text=''):
            frame = tk.Frame(parent)
            frame.pack(side='top', fill='x', padx=(10, 0), pady=(10, 0))

            ttk.Label(frame, width=16, text=label_text).pack(side='left', anchor='w')
            entry = ttk.Entry(frame, width=30)
            entry.insert(0, entry_text)
            entry.pack(side='right', padx=10)
            return entry

        # This function allows you to pack the label and option menu side by side.
        # It returns the option menu variable for later usage.
        def make_labelled_option_menu(parent, label_text, options, command=None):
            frame = tk.Frame(parent)
            frame.pack(side='top', fill='x', padx=(10, 0), pady=(10, 0))

            ttk.Label(frame, width=16, text=label_text).pack(side='left', anchor='w')
            option_menu_var = tk.StringVar()
            option_menu = ttk.OptionMenu(frame, option_menu_var, f"Select {label_text}", *options,
                                         command=command)
            option_menu.pack(side='right', fill='x', expand=True, padx=10)
            return option_menu_var, option_menu

        # Creating the widgets
        details_frame = tk.Frame(self)
        details_frame.pack(side='top', fill='both', expand=True)

        # left side of details frame
        left_widgets = tk.Frame(details_frame)

        left_fields = tk.Frame(left_widgets)
        self.payment_type = "Select Payment Type"
        self.payment_type_var = make_labelled_option_menu(left_fields, "Payment Type", ("Inbound", "Outbound"),
                                                          command=self.set_payees)[0]
        self.payee = make_labelled_option_menu(left_fields, "Payee", ())
        self.method = make_labelled_entry(left_fields, "Payment Method")
        self.amount = make_labelled_entry(left_fields, "Amount Paid")
        self.date = make_labelled_entry(left_fields, "Date of Payment", str(datetime.date.today()))
        self.time = make_labelled_entry(left_fields, "Time of Payment", '00:00')
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

        add_payment_button = ttk.Button(right_entry, width=20, text="Add Payment",
                                        command=self.register_payment)
        add_payment_button.bind('<Return>', self.register_payment)
        add_payment_button.pack(side='left')
        right_entry.pack(side='bottom', fill='x', expand=True)

        right_widgets.pack(side='left', fill='x', expand=True, padx=10)

        # back button
        back_button = ttk.Button(self, width=10, text="Go Back",
                                 command=self.master.show_details_frame)
        back_button.pack(side='left', padx=(5, 0), pady=(0, 5))

    def set_payees(self, payment_type):
        if payment_type == self.payment_type:
            return
        self.payment_type = payment_type

        self.payee[0].set("Select Payee")
        menu = self.payee[1]['menu']
        menu.delete(0, 'end')
        for payee in SQL.payments.get_payees(payment_type):
            payee = ' '.join(payee)
            menu.add_command(label=payee,
                             command=lambda value=payee: self.payee[0].set(value))

    def clear_fields(self):
        self.payment_type = "Select Payment Type"
        self.payment_type_var.set("Select Payment Type")
        self.payee[0].set("Select Payee")
        self.method.delete(0, 'end')
        self.amount.delete(0, 'end')
        self.date.delete(0, 'end')
        self.date.insert(0, str(datetime.date.today()))

        self.time.delete(0, 'end')
        self.time.insert(0, '00:00')

        self.description.delete('1.0', tk.END)

    def register_payment(self, _event=None):
        self.response['foreground'] = 'red'

        payment_type = self.payment_type
        if payment_type == "Select Payment Type":
            self.response['text'] = "Payment Type must be selected."
            return

        payee = self.payee[0].get().split(' ', 1)
        if payee[0] == "Select":
            self.response['text'] = "Payee must be selected."
            return

        method = self.method.get().title()
        if not method:
            self.response['text'] = "Payment method is empty."
            return

        amount = self.amount.get()
        if not amount:
            self.response['text'] = "Amount paid is empty."
            return

        if not validation.is_float(amount):
            self.response['text'] = "Amount paid must be a monetary amount."
            return
        amount = f"{float(amount):.2f}"

        date = self.date.get()
        if not date:
            self.response['text'] = "Date is empty."
            return

        if not validation.check_date(date):
            self.response['text'] = "Date input is invalid.\nMust be of form YYYY-MM-DD"
            return
        date = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")

        time = self.time.get()
        if not time:
            self.response['text'] = "Time is empty."
            return

        if not validation.check_time(time):
            self.response['text'] = "Time input is invalid.\nMust be of form HH:MM"
            return
        time = datetime.datetime.strptime(time, "%H:%M").strftime("%H:%M")

        description = self.description.get('1.0', tk.END)
        record = (payment_type, method, amount, date, time, description)
        SQL.payments.add_payment(record, payee[0])

        # Clear entry fields after account creation
        self.clear_fields()

        self.response['text'] = ""
        self.master.show_details_frame()
        messagebox.showinfo(title="Successfully added payment!",
                            message="Payment has been successfully added to the database.")


# Child frame [Secondary page of Payments frame]
# responsible for editing existing payment details in the system
class EditPayment(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller

        self.payment_id = ''

        # This function allows you to pack the label and entry side by side.
        # It returns the entry object for later usage.
        def make_labelled_entry(parent, label_text):
            frame = tk.Frame(parent)
            frame.pack(side='top', fill='x', padx=(10, 0), pady=(10, 0))

            ttk.Label(frame, width=16, text=label_text).pack(side='left', anchor='w')
            entry = ttk.Entry(frame, width=30)
            entry.pack(side='right', padx=10)
            return entry

        # This function allows you to pack the label and option menu side by side.
        # It returns the option menu variable for later usage.
        def make_labelled_option_menu(parent, label_text, options):
            frame = tk.Frame(parent)
            frame.pack(side='top', fill='x', padx=(10, 0), pady=(10, 0))

            ttk.Label(frame, width=16, text=label_text).pack(side='left', anchor='w')
            option_menu_var = tk.StringVar()
            option_menu = ttk.OptionMenu(frame, option_menu_var, f"Select {label_text}", *options)
            option_menu.pack(side='right', fill='x', expand=True, padx=10)
            return option_menu_var, option_menu

        # Creating the widgets
        details_frame = tk.Frame(self)
        details_frame.pack(side='top', fill='both', expand=True)

        # left side of details frame
        left_widgets = tk.Frame(details_frame)
        left_widgets.pack(side='left')

        left_fields = tk.Frame(left_widgets)
        self.payment_type = make_labelled_entry(left_fields, "Payment Type")
        self.payee = make_labelled_option_menu(left_fields, "Payee", ())
        self.method = make_labelled_entry(left_fields, "Payment Method")
        self.amount = make_labelled_entry(left_fields, "Amount Paid")
        self.date = make_labelled_entry(left_fields, "Date of Payment")
        self.time = make_labelled_entry(left_fields, "Time of Payment")
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

        edit_payment_button = ttk.Button(right_entry, width=20, text="Update Payment",
                                         command=self.edit_payment)
        edit_payment_button.bind('<Return>', self.edit_payment)
        edit_payment_button.pack(side='left')

        delete_payment_button = ttk.Button(right_entry, width=20, text="Delete Payment",
                                           command=self.master.delete_payment)
        delete_payment_button.bind('<Return>', self.master.delete_payment)
        delete_payment_button.pack(side='left', padx=(10, 0))

        # back button to return to details frame
        back_button = ttk.Button(self, width=10, text="Go Back",
                                 command=self.master.show_details_frame)
        back_button.pack(side='left', padx=(5, 0), pady=(0, 5))

    def set_payees(self, payment_type, payee):
        self.payee[0].set(payee)
        menu = self.payee[1]['menu']
        menu.delete(0, 'end')
        for payee in SQL.payments.get_payees(payment_type):
            payee = ' '.join(payee)
            menu.add_command(label=payee,
                             command=lambda value=payee: self.payee[0].set(value))

    def clear_fields(self):
        self.payment_type.config(state='normal')
        self.payment_type.delete(0, 'end')
        self.method.delete(0, 'end')
        self.amount.delete(0, 'end')
        self.date.delete(0, 'end')
        self.time.delete(0, 'end')
        self.description.delete('1.0', tk.END)

    def populate_fields(self, payment_id, payment_type):
        self.payment_id = payment_id

        self.clear_fields()
        self.payment_type.insert(0, payment_type)
        self.payment_type.config(state='readonly')

        record = SQL.payments.get_payment(payment_id, payment_type)[0]
        self.set_payees(payment_type, record[0])
        self.method.insert(0, record[1])
        self.amount.insert(0, record[2])
        self.date.insert(0, record[3])
        self.time.insert(0, record[4])
        self.description.insert('1.0', record[5])

    def edit_payment(self, _event=None):
        self.response['foreground'] = 'red'

        payment_type = self.payment_type.get()
        method = self.method.get().title()
        if not method:
            self.response['text'] = "Payment method is empty."
            return

        amount = self.amount.get()
        if not amount:
            self.response['text'] = "Amount paid is empty."
            return

        if not validation.is_float(amount):
            self.response['text'] = "Amount paid must be a monetary amount."
            return
        amount = f"{float(amount):.2f}"

        date = self.date.get()
        if not date:
            self.response['text'] = "Date is empty."
            return

        if not validation.check_date(date):
            self.response['text'] = "Date input is invalid.\nMust be of form YYYY-MM-DD"
            return
        date = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")

        time = self.time.get()
        if not time:
            self.response['text'] = "Time is empty."
            return

        if not validation.check_time(time):
            self.response['text'] = "Time input is invalid.\nMust be of form HH:MM"
            return
        time = datetime.datetime.strptime(time, "%H:%M").strftime("%H:%M")

        description = self.description.get('1.0', tk.END)

        payee_id = self.payee[0].get().split(' ', 1)[0]
        record = (method, amount, date, time, description)
        SQL.payments.edit_payment(self.payment_id, payment_type, record, payee_id)

        self.response['text'] = ""
        self.master.show_details_frame()
        messagebox.showinfo(title="Successfully updated payment!",
                            message="Payment record has been successfully updated!")
