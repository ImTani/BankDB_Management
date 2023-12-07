from decimal import Decimal
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, \
QVBoxLayout, QHBoxLayout, QDialog, QLineEdit, QPushButton, QMessageBox, QFormLayout, QFileDialog
import mysql.connector as sql
from pandas import DataFrame

class BankApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

        self.db = sql.connect(
            host="localhost",
            user="root",
            password="tani",
        )
        self.cursor = self.db.cursor()

        self.check_database()

    def check_database(self):

        self.cursor.execute("SHOW DATABASES LIKE 'TanishkBankDB'")
        result = self.cursor.fetchone()

        if not result:
            QMessageBox.critical(self, "Error", "Database not detected. Setup Database before use.")
        else:
            self.cursor.execute("use TanishkBankDB")

    def setup_database(self):

        self.cursor.execute("SHOW DATABASES LIKE 'TanishkBankDB'")
        result = self.cursor.fetchone()

        if not result:

            self.cursor.execute("CREATE DATABASE TanishkBankDB")
            self.db.commit()
            QMessageBox.information(self, "Success!", "Database has been successfully setup.")
        else:
            QMessageBox.warning(self, "Error", "Database already setup.")

        self.cursor.execute("USE TanishkBankDB")

        self.cursor.execute("SHOW TABLES LIKE 'customers'")
        result = self.cursor.fetchone()

        if not result:

            create_table_query = """
            CREATE TABLE customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                account_number VARCHAR(20) UNIQUE NOT NULL,
                balance DECIMAL(10,2) DEFAULT 0.00
            )
            """
            self.cursor.execute(create_table_query)
            self.db.commit()

    def init_ui(self):

        layout = QVBoxLayout()

        btn_add_customer = QPushButton('Add Customer', self)
        btn_add_customer.clicked.connect(self.show_add_customer_dialog)
        layout.addWidget(btn_add_customer)

        btn_view_customer = QPushButton('View Customer Details', self)
        btn_view_customer.clicked.connect(self.show_view_customer_dialog)
        layout.addWidget(btn_view_customer)

        btn_update_customer = QPushButton('Update Customer Details', self)
        btn_update_customer.clicked.connect(self.show_update_customer_dialog)
        layout.addWidget(btn_update_customer)

        btn_delete_customer = QPushButton('Delete Customer', self)
        btn_delete_customer.clicked.connect(self.show_delete_customer_dialog)
        layout.addWidget(btn_delete_customer)

        btn_deposit = QPushButton('Deposit Amount', self)
        btn_deposit.clicked.connect(self.show_deposit_dialog)
        layout.addWidget(btn_deposit)

        btn_withdraw = QPushButton('Withdraw Amount', self)
        btn_withdraw.clicked.connect(self.show_withdraw_dialog)
        layout.addWidget(btn_withdraw)

        btn_setup_database = QPushButton('Setup Database', self)
        btn_setup_database.clicked.connect(self.setup_database)
        layout.addWidget(btn_setup_database)

        btn_show_all_customers = QPushButton('Show All Customers', self)
        btn_show_all_customers.clicked.connect(self.show_all_customers)
        layout.addWidget(btn_show_all_customers)

        self.setLayout(layout)

        self.setWindowTitle('Bank Database Management System')
        self.setFixedSize(350, 400)  
        self.show()

    def show_add_customer_dialog(self):
        dialog = AddCustomerDialog(self)
        dialog.exec_()

    def show_view_customer_dialog(self):
        dialog = ViewCustomerDialog(self)
        dialog.exec_()

    def show_update_customer_dialog(self):
        dialog = UpdateCustomerDialog(self)
        dialog.exec_()

    def show_delete_customer_dialog(self):
        dialog = DeleteCustomerDialog(self)
        dialog.exec_()

    def show_deposit_dialog(self):
        dialog = DepositDialog(self)
        dialog.exec_()

    def show_withdraw_dialog(self):
        dialog = WithdrawDialog(self)
        dialog.exec_()

    def show_all_customers(self):
        dialog = ShowAllCustomersDialog(self)
        dialog.exec_()

    def closeEvent(self, event):

        self.db.close()

class AddCustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Add Customer')

        self.first_name_input = QLineEdit(self)
        self.last_name_input = QLineEdit(self)
        self.account_number_input = QLineEdit(self)
        self.balance_input = QLineEdit(self)

        layout = QFormLayout(self)
        layout.addRow('First Name:', self.first_name_input)
        layout.addRow('Last Name:', self.last_name_input)
        layout.addRow('Account Number:', self.account_number_input)
        layout.addRow('Balance:', self.balance_input)

        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton('Cancel')
        add_customer_button = QPushButton('Add Customer')
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(add_customer_button)
        layout.addRow(buttons_layout)

        cancel_button.clicked.connect(self.reject)
        add_customer_button.clicked.connect(self.acceptAndAddCustomer)

    def acceptAndAddCustomer(self):
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        account_number = self.account_number_input.text()
        balance_text = self.balance_input.text()

        if not first_name or not last_name or not account_number or not balance_text:
            QMessageBox.warning(self, 'Error', 'Please fill in all fields.')
            return

        try:
            balance = Decimal(balance_text)
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Invalid balance. Please enter a valid decimal value.')
            return

        check_query = "SELECT * FROM customers WHERE account_number = %s"
        data = (account_number,)
        parent = self.parent()
        parent.cursor.execute(check_query, data)
        result = parent.cursor.fetchone()

        if result:
            QMessageBox.warning(self, 'Error', 'Account number already exists. Please enter a different account number.')
        else:
            insert_query = "INSERT INTO customers (first_name, last_name, account_number, balance) VALUES (%s, %s, %s, %s)"
            data = (first_name, last_name, account_number, balance)
            parent.cursor.execute(insert_query, data)

            parent.db.commit()

            QMessageBox.information(self, 'Success', 'Customer added successfully!')
            self.accept()

class ViewCustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('View Customer Details')

        self.account_number_input = QLineEdit(self)
        self.account_number_input.setPlaceholderText('Enter account number')

        layout = QFormLayout(self)
        layout.addRow('Account Number:', self.account_number_input)

        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton('Cancel')
        view_details_button = QPushButton('View Details')
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(view_details_button)
        layout.addRow(buttons_layout)

        cancel_button.clicked.connect(self.reject)  
        view_details_button.clicked.connect(self.viewDetails)

    def viewDetails(self):

        account_number = self.account_number_input.text()

        select_query = "SELECT * FROM customers WHERE account_number = %s"
        data = (account_number,)
        parent = self.parent()
        parent.cursor.execute(select_query, data)

        result = parent.cursor.fetchone()

        if result:
            QMessageBox.information(self, 'Customer Details',
                                    f'First Name: {result[1]}\nLast Name: {result[2]}\nAccount Number: {result[3]}\nBalance: Rs.{result[4]:.2f}')
        else:
            QMessageBox.warning(self, 'Customer Not Found', 'Customer not found.')

        self.accept()  

class UpdateCustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Update Customer Details')

        self.account_number_input = QLineEdit(self)
        self.new_first_name_input = QLineEdit(self)
        self.new_last_name_input = QLineEdit(self)
        self.new_balance_input = QLineEdit(self)

        layout = QFormLayout(self)
        layout.addRow('Account Number:', self.account_number_input)
        layout.addRow('New First Name:', self.new_first_name_input)
        layout.addRow('New Last Name:', self.new_last_name_input)
        layout.addRow('New Balance:', self.new_balance_input)

        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton('Cancel')
        update_details_button = QPushButton('Update Details')
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(update_details_button)
        layout.addRow(buttons_layout)

        cancel_button.clicked.connect(self.reject)
        update_details_button.clicked.connect(self.acceptAndUpdate)

    def acceptAndUpdate(self):
        account_number = self.account_number_input.text()
        new_first_name = self.new_first_name_input.text()
        new_last_name = self.new_last_name_input.text()
        new_balance_input_text = self.new_balance_input.text()

        check_query = "SELECT * FROM customers WHERE account_number = %s"
        data = (account_number,)
        parent = self.parent()
        parent.cursor.execute(check_query, data)
        result = parent.cursor.fetchone()

        if not result:
            QMessageBox.warning(self, 'Error', 'Customer not found.')
        elif not any([new_first_name, new_last_name, new_balance_input_text]):
            QMessageBox.warning(self, 'Error', 'Please fill in at least one field.')
        else:
            update_fields = []

            if not new_first_name:
                update_fields.append(("first_name", result[1]))  
            else:
                update_fields.append(("first_name", new_first_name))

            if not new_last_name:
                update_fields.append(("last_name", result[2]))  
            else:
                update_fields.append(("last_name", new_last_name))

            if not new_balance_input_text:
                update_fields.append(("balance", result[4]))  
            else:
                new_balance = Decimal(new_balance_input_text)
                update_fields.append(("balance", new_balance))

            set_query = ", ".join([f"{field} = %s" for field, _ in update_fields])

            update_query = f"UPDATE customers SET {set_query} WHERE account_number = %s"

            update_values = [value for _, value in update_fields]
            update_values.append(account_number)

            parent.cursor.execute(update_query, update_values)
            parent.db.commit()

            QMessageBox.information(self, 'Success', 'Customer details updated successfully!')
            self.accept()

class DeleteCustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Delete Customer')

        self.account_number_input = QLineEdit(self)
        self.account_number_input.setPlaceholderText('Enter account number')

        layout = QFormLayout(self)
        layout.addRow('Account Number:', self.account_number_input)

        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton('Cancel')
        delete_customer_button = QPushButton('Delete Customer')
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(delete_customer_button)
        layout.addRow(buttons_layout)

        cancel_button.clicked.connect(self.reject)
        delete_customer_button.clicked.connect(self.confirmAndDelete)

    def confirmAndDelete(self):

        account_number = self.account_number_input.text()

        check_query = "SELECT * FROM customers WHERE account_number = %s"
        data = (account_number,)
        parent = self.parent()
        parent.cursor.execute(check_query, data)
        result = parent.cursor.fetchone()

        if not result:
            QMessageBox.warning(self, 'Error', 'Customer not found.')
        else:

            confirm = QMessageBox.question(self, 'Confirmation',
                                           f"Do you really want to delete the customer {result[1]} {result[2]}?",
                                           QMessageBox.Yes | QMessageBox.No)

            if confirm == QMessageBox.Yes:

                delete_query = "DELETE FROM customers WHERE account_number = %s"
                parent.cursor.execute(delete_query, data)

                parent.db.commit()

                QMessageBox.information(self, 'Success', 'Customer deleted successfully!')
                self.accept()
            else:
                QMessageBox.information(self, 'Deletion Canceled', 'Deletion canceled.')

class DepositDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Deposit Money')

        self.account_number_input = QLineEdit(self)
        self.deposit_amount_input = QLineEdit(self)

        layout = QFormLayout(self)
        layout.addRow('Account Number:', self.account_number_input)
        layout.addRow('Deposit Amount:', self.deposit_amount_input)

        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton('Cancel')
        deposit_button = QPushButton('Deposit')
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(deposit_button)
        layout.addRow(buttons_layout)

        cancel_button.clicked.connect(self.reject)
        deposit_button.clicked.connect(self.acceptAndDeposit)

    def acceptAndDeposit(self):

        account_number = self.account_number_input.text()

        check_query = "SELECT * FROM customers WHERE account_number = %s"
        data = (account_number,)
        parent = self.parent()
        parent.cursor.execute(check_query, data)
        result = parent.cursor.fetchone()

        if not result:
            QMessageBox.warning(self, 'Error', 'Customer not found.')
        else:

            deposit_amount = Decimal(self.deposit_amount_input.text()) if self.deposit_amount_input.text() else None

            if deposit_amount:
                pass
            else:
                QMessageBox.warning(self, 'Error', 'Please enter an amount.')
                return

            update_query = "UPDATE customers SET balance = balance + %s WHERE account_number = %s"
            data = (deposit_amount, account_number)
            parent.cursor.execute(update_query, data)

            parent.db.commit()

            new_balance = result[4] + deposit_amount if deposit_amount is not None else result[4]
            QMessageBox.information(self, 'Success', f"Deposit of Rs.{deposit_amount:.2f} successful. "
                                                    f"New balance: Rs.{new_balance:.2f}")
            self.accept()

class WithdrawDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Withdraw Money')

        self.account_number_input = QLineEdit(self)
        self.withdrawal_amount_input = QLineEdit(self)

        layout = QFormLayout(self)
        layout.addRow('Account Number:', self.account_number_input)
        layout.addRow('Withdrawal Amount:', self.withdrawal_amount_input)

        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton('Cancel')
        withdraw_button = QPushButton('Withdraw')
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(withdraw_button)
        layout.addRow(buttons_layout)

        cancel_button.clicked.connect(self.reject)
        withdraw_button.clicked.connect(self.acceptAndWithdraw)

    def acceptAndWithdraw(self):

        account_number = self.account_number_input.text()

        check_query = "SELECT * FROM customers WHERE account_number = %s"
        data = (account_number,)
        parent = self.parent()
        parent.cursor.execute(check_query, data)
        result = parent.cursor.fetchone()

        if not result:
            QMessageBox.warning(self, 'Error', 'Customer not found.')
        else:

            withdrawal_amount = Decimal(self.withdrawal_amount_input.text()) if self.withdrawal_amount_input.text() else None

            if withdrawal_amount:
                pass
            else:
                QMessageBox.warning(self, 'Error', 'Please enter an amount.')
                return

            if withdrawal_amount is not None and result[4] < withdrawal_amount:
                QMessageBox.warning(self, 'Error', 'Insufficient balance. Withdrawal canceled.')

            else:

                update_query = "UPDATE customers SET balance = balance - %s WHERE account_number = %s"
                data = (withdrawal_amount, account_number)
                parent.cursor.execute(update_query, data)

                parent.db.commit()

                new_balance = result[4] - withdrawal_amount if withdrawal_amount is not None else result[4]
                QMessageBox.information(self, 'Success', f"Withdrawal of Rs.{withdrawal_amount:.2f} successful. "
                                                        f"New balance: Rs.{new_balance:.2f}")
                self.accept()

class ShowAllCustomersDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Show All Customers')

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText('Search...')
        self.search_input.textChanged.connect(self.filter_table)

        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['ID', 'First Name', 'Last Name', 'Account Number', 'Balance'])
        self.table.setMinimumSize(650, 400)

        self.export_button = QPushButton('Export to Excel', self)
        self.export_button.clicked.connect(self.export_to_excel)

        layout = QVBoxLayout(self)
        layout.addWidget(self.search_input)
        layout.addWidget(self.table)
        layout.addWidget(self.export_button)

        self.populate_table()

    def filter_table(self):
        search_text = self.search_input.text().lower()

        for row in range(self.table.rowCount()):
            visible = any(search_text in self.table.item(row, col).text().lower() for col in range(self.table.columnCount()))
            self.table.setRowHidden(row, not visible)

    def populate_table(self):
        parent = self.parent()

        parent.cursor.execute("SELECT * FROM customers")
        results = parent.cursor.fetchall()

        for row_num, row_data in enumerate(results):
            self.table.insertRow(row_num)
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.table.setItem(row_num, col_num, item)

    def export_to_excel(self):
        parent = self.parent()

        parent.cursor.execute("SELECT * FROM customers")
        results = parent.cursor.fetchall()

        df = DataFrame(results, columns=['ID', 'First Name', 'Last Name', 'Account Number', 'Balance'])

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx);;All Files (*)")

        if file_path:
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, 'Export Successful', f'Data exported to {file_path}')

def main():
    app = QApplication(sys.argv)
    bank_app = BankApp()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()