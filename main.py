import tkinter as tk
from tkinter import ttk, messagebox
from connection import cnx, cur
from datetime import datetime

def get_employees():
    cur.execute("SELECT e.id, e.name, e.email, d.name, r.name, e.salary, e.hire_date FROM employees e LEFT JOIN departments d ON e.department_id = d.id LEFT JOIN roles r ON e.role_id = r.id")
    return cur.fetchall()

def add_employee(name, email, dept_id, role_id, salary, hire_date):
    cur.execute("INSERT INTO employees (name, email, department_id, role_id, salary, hire_date) VALUES (%s, %s, %s, %s, %s, %s)", (name, email, dept_id, role_id, salary, hire_date))
    cnx.commit()

def update_employee(emp_id, name, email, dept_id, role_id, salary, hire_date):
    cur.execute("UPDATE employees SET name=%s, email=%s, department_id=%s, role_id=%s, salary=%s, hire_date=%s WHERE id=%s", (name, email, dept_id, role_id, salary, hire_date, emp_id))
    cnx.commit()

def delete_employee(emp_id):
    cur.execute("DELETE FROM employees WHERE id=%s", (emp_id,))
    cnx.commit()

def promote_employee(emp_id):
    # Get current role level
    cur.execute("SELECT r.level FROM employees e JOIN roles r ON e.role_id = r.id WHERE e.id=%s", (emp_id,))
    current_level = cur.fetchone()[0]
    # Get next level role
    cur.execute("SELECT id FROM roles WHERE level = %s", (current_level + 1,))
    next_role = cur.fetchone()
    if next_role:
        cur.execute("UPDATE employees SET role_id=%s WHERE id=%s", (next_role[0], emp_id))
        cnx.commit()
        return True
    return False

def demote_employee(emp_id):
    # Get current role level
    cur.execute("SELECT r.level FROM employees e JOIN roles r ON e.role_id = r.id WHERE e.id=%s", (emp_id,))
    current_level = cur.fetchone()[0]
    # Get previous level role
    cur.execute("SELECT id FROM roles WHERE level = %s", (current_level - 1,))
    prev_role = cur.fetchone()
    if prev_role:
        cur.execute("UPDATE employees SET role_id=%s WHERE id=%s", (prev_role[0], emp_id))
        cnx.commit()
        return True
    return False

def get_departments():
    cur.execute("SELECT id, name FROM departments")
    return cur.fetchall()

def get_roles():
    cur.execute("SELECT id, name, level FROM roles ORDER BY level")
    return cur.fetchall()

def search_employee_by_id(emp_id):
    cur.execute("SELECT e.id, e.name, e.email, d.name, r.name, e.salary, e.hire_date FROM employees e LEFT JOIN departments d ON e.department_id = d.id LEFT JOIN roles r ON e.role_id = r.id WHERE e.id = %s", (emp_id,))
    return cur.fetchone()

class EmployeeERP:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee ERP System")
        self.root.geometry("1200x600")

        # Create paned window
        paned = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left panel - Add Employee
        left_frame = tk.Frame(paned, width=400)
        paned.add(left_frame)

        # Right panel - Employee Management
        right_frame = tk.Frame(paned)
        paned.add(right_frame)

        # Left panel content
        self.create_add_employee_panel(left_frame)

        # Right panel content
        self.create_management_panel(right_frame)

        self.view_employees()

    def create_add_employee_panel(self, parent):
        # Title
        tk.Label(parent, text="Add New Employee", font=("Arial", 14, "bold")).pack(pady=10)

        # Form frame
        form_frame = tk.Frame(parent)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.add_name_entry = tk.Entry(form_frame, width=25)
        self.add_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.add_email_entry = tk.Entry(form_frame, width=25)
        self.add_email_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Department:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.add_dept_combo = ttk.Combobox(form_frame, values=[d[1] for d in get_departments()], width=22)
        self.add_dept_combo.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Role:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.add_role_combo = ttk.Combobox(form_frame, values=[r[1] for r in get_roles()], width=22)
        self.add_role_combo.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Salary:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.add_salary_entry = tk.Entry(form_frame, width=25)
        self.add_salary_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Hire Date (YYYY-MM-DD):").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.add_hire_entry = tk.Entry(form_frame, width=25)
        self.add_hire_entry.grid(row=5, column=1, padx=5, pady=5)

        # Add button
        tk.Button(parent, text="Add Employee", command=self.add_employee_from_panel, bg="green", fg="white").pack(pady=10)

    def create_management_panel(self, parent):
        # Title
        tk.Label(parent, text="Employee Management", font=("Arial", 14, "bold")).pack(pady=10)

        # Search frame
        search_frame = tk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(search_frame, text="Search by ID:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=10)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Search", command=self.search_employee).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=5)

        # Treeview for employees
        self.tree = ttk.Treeview(parent, columns=('ID', 'Name', 'Email', 'Department', 'Role', 'Salary', 'Hire Date'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Email', text='Email')
        self.tree.heading('Department', text='Department')
        self.tree.heading('Role', text='Role')
        self.tree.heading('Salary', text='Salary')
        self.tree.heading('Hire Date', text='Hire Date')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(button_frame, text="Update Employee", command=self.update_employee_window).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="Delete Employee", command=self.delete_employee).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="Promote Employee", command=self.promote_employee).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="Demote Employee", command=self.demote_employee).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="Refresh", command=self.view_employees).pack(side=tk.LEFT, padx=5, pady=5)

    def add_employee_from_panel(self):
        name = self.add_name_entry.get()
        email = self.add_email_entry.get()
        dept_name = self.add_dept_combo.get()
        dept_id = next((d[0] for d in get_departments() if d[1] == dept_name), None)
        role_name = self.add_role_combo.get()
        role_id = next((r[0] for r in get_roles() if r[1] == role_name), None)
        salary = self.add_salary_entry.get()
        hire_date = self.add_hire_entry.get()
        if name and email and dept_id and role_id and salary and hire_date:
            try:
                add_employee(name, email, dept_id, role_id, salary, hire_date)
                self.view_employees()
                # Clear fields
                self.add_name_entry.delete(0, tk.END)
                self.add_email_entry.delete(0, tk.END)
                self.add_dept_combo.set('')
                self.add_role_combo.set('')
                self.add_salary_entry.delete(0, tk.END)
                self.add_hire_entry.delete(0, tk.END)
                messagebox.showinfo("Success", "Employee added successfully")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showerror("Error", "All fields are required")

    def view_employees(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        employees = get_employees()
        for emp in employees:
            self.tree.insert('', tk.END, values=emp)


    def update_employee_window(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select an employee to update")
            return
        item = self.tree.item(selected[0])
        values = item['values']
        emp_id = values[0]

        update_win = tk.Toplevel(self.root)
        update_win.title("Update Employee")

        tk.Label(update_win, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = tk.Entry(update_win)
        name_entry.insert(0, values[1])
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(update_win, text="Email:").grid(row=1, column=0, padx=5, pady=5)
        email_entry = tk.Entry(update_win)
        email_entry.insert(0, values[2])
        email_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(update_win, text="Department:").grid(row=2, column=0, padx=5, pady=5)
        dept_combo = ttk.Combobox(update_win, values=[d[1] for d in get_departments()])
        dept_combo.set(values[3])
        dept_combo.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(update_win, text="Role:").grid(row=3, column=0, padx=5, pady=5)
        role_combo = ttk.Combobox(update_win, values=[r[1] for r in get_roles()])
        role_combo.set(values[4])
        role_combo.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(update_win, text="Salary:").grid(row=4, column=0, padx=5, pady=5)
        salary_entry = tk.Entry(update_win)
        salary_entry.insert(0, values[5])
        salary_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(update_win, text="Hire Date (YYYY-MM-DD):").grid(row=5, column=0, padx=5, pady=5)
        hire_entry = tk.Entry(update_win)
        hire_entry.insert(0, values[6])
        hire_entry.grid(row=5, column=1, padx=5, pady=5)

        def save():
            name = name_entry.get()
            email = email_entry.get()
            dept_name = dept_combo.get()
            dept_id = next((d[0] for d in get_departments() if d[1] == dept_name), None)
            role_name = role_combo.get()
            role_id = next((r[0] for r in get_roles() if r[1] == role_name), None)
            salary = salary_entry.get()
            hire_date = hire_entry.get()
            if name and email and dept_id and role_id and salary and hire_date:
                try:
                    update_employee(emp_id, name, email, dept_id, role_id, salary, hire_date)
                    self.view_employees()
                    update_win.destroy()
                    messagebox.showinfo("Success", "Employee updated successfully")
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            else:
                messagebox.showerror("Error", "All fields are required")

        tk.Button(update_win, text="Save", command=save).grid(row=6, column=0, columnspan=2, pady=10)

    def delete_employee(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select an employee to delete")
            return
        item = self.tree.item(selected[0])
        emp_id = item['values'][0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this employee?"):
            try:
                delete_employee(emp_id)
                self.view_employees()
                messagebox.showinfo("Success", "Employee deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def promote_employee(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select an employee to promote")
            return
        item = self.tree.item(selected[0])
        emp_id = item['values'][0]
        if promote_employee(emp_id):
            self.view_employees()
            messagebox.showinfo("Success", "Employee promoted successfully")
        else:
            messagebox.showerror("Error", "Cannot promote further")

    def search_employee(self):
        emp_id = self.search_entry.get()
        if not emp_id:
            messagebox.showerror("Error", "Please enter an ID to search")
            return
        try:
            emp_id = int(emp_id)
            employee = search_employee_by_id(emp_id)
            if employee:
                for row in self.tree.get_children():
                    self.tree.delete(row)
                self.tree.insert('', tk.END, values=employee)
            else:
                messagebox.showerror("Error", "Employee not found")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric ID")

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.view_employees()

    def demote_employee(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select an employee to demote")
            return
        item = self.tree.item(selected[0])
        emp_id = item['values'][0]
        if demote_employee(emp_id):
            self.view_employees()
            messagebox.showinfo("Success", "Employee demoted successfully")
        else:
            messagebox.showerror("Error", "Cannot demote further")

if __name__ == "__main__":
    root = tk.Tk()
    app = EmployeeERP(root)
    root.mainloop()
