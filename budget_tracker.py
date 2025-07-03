import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# === Global Variables ===
df = None
category_spent = None
canvas = None

# === GUI ===
root = tk.Tk()
root.title("🧾 Personal Budget Tracker")
root.geometry("900x700")
root.configure(bg="white")

# === Title ===
title = tk.Label(root, text="📊 Budget Tracker", font=("Arial", 18, "bold"), bg="white", fg="#333")
title.pack(pady=10)

# === Upload CSV Button ===
def load_csv():
    global df, category_spent
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return

    try:
        df = pd.read_csv(file_path)
        if 'Category' not in df.columns or 'Amount' not in df.columns:
            messagebox.showerror("Invalid File", "CSV must contain 'Category' and 'Amount' columns.")
            df = None
            return

        category_spent = df.groupby('Category')['Amount'].sum()
        messagebox.showinfo("✅ Success", "CSV loaded successfully! Now enter your budget.")
        load_btn.config(bg="#4CAF50", fg="white", text="✅ CSV Loaded")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

load_btn = tk.Button(
    root, text="📂 Load Expense CSV", command=load_csv,
    font=("Arial", 12), bg="#2196F3", fg="white", padx=10, pady=5
)
load_btn.pack(pady=5)

# === Budget Entry ===
entry_label = tk.Label(root, text="Enter your total monthly budget (₹):", font=("Arial", 12), bg="white")
entry_label.pack()

budget_entry = tk.Entry(root, font=("Arial", 12), width=30)
budget_entry.pack(pady=5)

output_label = tk.Label(root, text="", font=("Arial", 12), bg="white", fg="green")
output_label.pack(pady=10)
button_frame = tk.Frame(root, bg="white", padx=5, pady=5)
button_frame.pack(padx=5)
# === Frame for Table + Plots ===
frame_bottom = tk.Frame(root, bg="white")
frame_bottom.pack(fill="both", expand=True, padx=10, pady=10)


# === Table ===
table = ttk.Treeview(frame_bottom, columns=("Category", "Amount"), show="headings", height=5)
table.heading("Category", text="Category")
table.heading("Amount", text="Amount (₹)")
table.column("Category", width=150)
table.column("Amount", width=100)

# === Generate Report ===
def generate_report():
    global canvas, df, category_spent

    if df is None:
        messagebox.showerror("Error", "Please upload a valid CSV file first.")
        return

    try:
        budget = float(budget_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number for budget.")
        return

    total_spent = np.sum(df['Amount'])
    average_spent = np.mean(df['Amount'])
    remaining_budget = max(budget - total_spent, 0)

    if total_spent > budget:
        output_label.config(text=f"⚠️ You overspent by ₹{total_spent - budget:.2f}", fg="red")
    else:
        output_label.config(text=f"✅ You're within budget. Remaining: ₹{remaining_budget:.2f}", fg="green")

    # Clear previous table
    for row in table.get_children():
        table.delete(row)

    # Fill table
    for category, amount in category_spent.items():
        table.insert("", "end", values=(category, f"{amount:.2f}"))

    table.pack(pady=10)

    # Clear old plot
    if canvas:
        canvas.get_tk_widget().destroy()

    # === Matplotlib Charts ===
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))

    # Pie 1: Category-wise
    axs[0].pie(
        category_spent,
        labels=category_spent.index,
        autopct="%1.1f%%",
        startangle=140,
        textprops={'fontsize': 8}
    )
    axs[0].set_title("Spending by Category", fontsize=10)

    # Pie 2: Budget Overview
    budget_data = [total_spent, remaining_budget, average_spent]
    budget_labels = ["Total Spent", "Remaining Budget", "Average Spent"]

    axs[1].pie(
        budget_data,
        labels=budget_labels,
        autopct="%1.1f%%",
        colors=["#ff9999", "#99ff99", "#66b3ff"],
        startangle=90,
        textprops={'fontsize': 8}
    )
    axs[1].set_title("Budget vs Spending", fontsize=10)

    # Display plot
    canvas = FigureCanvasTkAgg(fig, master=frame_bottom)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

# === Reset Function ===
def clear():
    global canvas, df, category_spent
    budget_entry.delete(0, tk.END)
    output_label.config(text="", fg="black")

    # Clear table
    for row in table.get_children():
        table.delete(row)

    # Clear plot
    if canvas:
        canvas.get_tk_widget().destroy()
        canvas = None


# === Buttons ===
show_btn = tk.Button(button_frame, text="Show Budget Report", command=generate_report,
                     font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", padx=10, pady=5)
show_btn.pack(side="left", padx=10)

reset_btn = tk.Button(button_frame, text="Reset", command=clear,
                      font=("Arial", 12, "bold"), bg="#f44336", fg="white", padx=10, pady=5)
reset_btn.pack(side="left", padx=10)

# === Main Loop ===
root.mainloop()
