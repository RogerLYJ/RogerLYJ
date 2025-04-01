import math

try:
    import tkinter as tk
    from tkinter import messagebox
    print("tkinter module loaded successfully.")  # 调试信息
except ModuleNotFoundError as e:
    print(f"Error: {e}")
    print("The 'tkinter' module is not installed or available in your environment.")
    print("Please install it to use the GUI mode. For example, on Linux, run 'sudo apt-get install python3-tk'.")
    tk = None

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error: Division by zero"
    return a / b

def power(a, b):
    return math.pow(a, b)

def square_root(a):
    if a < 0:
        return "Error: Negative number"
    return math.sqrt(a)

def logarithm(a, base=10):
    if a <= 0:
        return "Error: Non-positive number"
    return math.log(a, base)

def display_menu():
    print("Scientific Calculator")
    print("1. Addition")2
    
    print("2. Subtraction")
    print("3. Multiplication")
    print("4. Division")
    print("5. Power")
    print("6. Square Root")
    print("7. Logarithm")
    print("8. Exit")

def main():
    while True:
        display_menu()
        choice = input("Choose an operation (1-8): ").strip()  # Ensure input is stripped of whitespace
        
        if choice == '8':
            print("Exiting the calculator. Goodbye!")
            break
        
        if choice in ['1', '2', '3', '4', '5']:
            try:
                a = float(input("Enter the first number: "))
                b = float(input("Enter the second number: "))
            except ValueError:
                print("Error: Invalid input. Please enter numeric values.")
                continue
        
        if choice == '1':
            print("Result:", add(a, b))
        elif choice == '2':
            print("Result:", subtract(a, b))
        elif choice == '3':
            print("Result:", multiply(a, b))
        elif choice == '4':
            print("Result:", divide(a, b))
        elif choice == '5':
            print("Result:", power(a, b))
        elif choice == '6':
            try:
                a = float(input("Enter the number: "))
                print("Result:", square_root(a))
            except ValueError:
                print("Error: Invalid input. Please enter a numeric value.")
        elif choice == '7':
            try:
                a = float(input("Enter the number: "))
                base = input("Enter the base (default is 10): ").strip()
                base = float(base) if base else 10
                print("Result:", logarithm(a, base))
            except ValueError:
                print("Error: Invalid input. Please enter numeric values.")
        else:
            print("Invalid choice. Please try again.")

def create_gui():
    def calculate():
        operation = operation_var.get()
        try:
            num1 = float(entry1.get())
            num2 = float(entry2.get()) if entry2.get() else None
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values.")
            return

        try:
            if operation == "Addition":
                result = add(num1, num2)
            elif operation == "Subtraction":
                result = subtract(num1, num2)
            elif operation == "Multiplication":
                result = multiply(num1, num2)
            elif operation == "Division":
                result = divide(num1, num2)
            elif operation == "Power":
                result = power(num1, num2)
            elif operation == "Square Root":
                result = square_root(num1)
            elif operation == "Logarithm":
                base = float(entry2.get()) if entry2.get() else 10
                result = logarithm(num1, base)
            else:
                result = "Invalid Operation"
            result_label.config(text=f"Result: {result}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def toggle_second_input(*args):
        operation = operation_var.get()
        if operation in ["Square Root"]:
            entry2.config(state="disabled")
        else:
            entry2.config(state="normal")

    # Create main window
    root = tk.Tk()
    root.title("Scientific Calculator")

    # Input fields
    tk.Label(root, text="First Number:").grid(row=0, column=0, padx=10, pady=5)
    entry1 = tk.Entry(root)
    entry1.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Second Number/Base:").grid(row=1, column=0, padx=10, pady=5)
    entry2 = tk.Entry(root)
    entry2.grid(row=1, column=1, padx=10, pady=5)

    # Operation selection
    tk.Label(root, text="Operation:").grid(row=2, column=0, padx=10, pady=5)
    operation_var = tk.StringVar(value="Addition")
    operations = ["Addition", "Subtraction", "Multiplication", "Division", "Power", "Square Root", "Logarithm"]
    operation_menu = tk.OptionMenu(root, operation_var, *operations, command=toggle_second_input)
    operation_menu.grid(row=2, column=1, padx=10, pady=5)

    # Calculate button
    calculate_button = tk.Button(root, text="Calculate", command=calculate)
    calculate_button.grid(row=3, column=0, columnspan=2, pady=10)

    # Result display
    result_label = tk.Label(root, text="Result: ")
    result_label.grid(row=4, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    mode = input("Choose mode: 1 for CLI, 2 for GUI: ").strip()
    if mode == "1":
        main()
    elif mode == "2":
        if tk is None:
            print("GUI mode is unavailable because 'tkinter' is not installed.")
        else:
            create_gui()
    else:
        print("Invalid mode. Exiting.")
