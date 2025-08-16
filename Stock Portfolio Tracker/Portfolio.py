import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import csv
from datetime import datetime

# Modern color scheme
COLORS = {
    'bg': '#2c3e50',
    'fg': '#ecf0f1',
    'button': '#3498db',
    'button_hover': '#2980b9',
    'success': '#2ecc71',
    'warning': '#e74c3c',
    'accent': '#f1c40f'
}

# Hardcoded stock prices with company names and recent performance
stock_data = {
    "AAPL": {"price": 180, "company": "Apple Inc.", "trend": "up"},
    "TSLA": {"price": 250, "company": "Tesla Inc.", "trend": "down"},
    "GOOGL": {"price": 2800, "company": "Alphabet Inc.", "trend": "up"},
    "AMZN": {"price": 3400, "company": "Amazon.com Inc.", "trend": "up"},
    "MSFT": {"price": 300, "company": "Microsoft Corp.", "trend": "down"},
    "NFLX": {"price": 600, "company": "Netflix Inc.", "trend": "down"},
    "META": {"price": 350, "company": "Meta Platforms Inc.", "trend": "up"}
}

class EnhancedStockPortfolioTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Advanced Stock Portfolio Tracker")
        self.master.configure(bg=COLORS['bg'])
        self.master.geometry("1000x700")
        
        # Custom styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background=COLORS['bg'])
        self.style.configure('TLabel', background=COLORS['bg'], foreground=COLORS['fg'], font=('Arial', 10))
        self.style.configure('TButton', 
                           background=COLORS['button'], 
                           foreground=COLORS['fg'],
                           font=('Arial', 10, 'bold'),
                           borderwidth=1)
        self.style.map('TButton',
                      background=[('active', COLORS['button_hover'])],
                      foreground=[('active', COLORS['fg'])])

        self.stocks = {}
        
        # Main container
        self.main_frame = ttk.Frame(master, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=10)
        
        # Stock selection with autocomplete
        self.selected_stock = tk.StringVar()
        self.companies = [f"{k} - {v['company']}" for k, v in stock_data.items()]
        self.stock_dropdown = ttk.Combobox(
            self.input_frame, 
            textvariable=self.selected_stock,
            values=self.companies,
            font=('Arial', 10)
        )
        self.stock_dropdown.grid(row=0, column=0, padx=5, sticky=tk.W)
        
        # Quantity input with increment/decrement buttons
        self.quantity_frame = ttk.Frame(self.input_frame)
        self.quantity_frame.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        self.quantity_var = tk.IntVar(value=1)
        self.quantity_entry = ttk.Entry(
            self.quantity_frame, 
            textvariable=self.quantity_var,
            width=5,
            font=('Arial', 10)
        )
        self.quantity_entry.grid(row=0, column=1, padx=(0, 5))
        
        ttk.Button(
            self.quantity_frame, 
            text="+", 
            width=2,
            command=lambda: self.quantity_var.set(self.quantity_var.get() + 1)
        ).grid(row=0, column=2)
        
        ttk.Button(
            self.quantity_frame, 
            text="-", 
            width=2,
            command=lambda: self.quantity_var.set(max(1, self.quantity_var.get() - 1))
        ).grid(row=0, column=0)
        
        # Add stock button
        ttk.Button(
            self.input_frame, 
            text="Add to Portfolio", 
            command=self.add_stock,
            style='TButton'
        ).grid(row=0, column=2, padx=5)
        
        # Remove stock button
        ttk.Button(
            self.input_frame, 
            text="Remove from Portfolio", 
            command=self.remove_stock,
            style='TButton'
        ).grid(row=0, column=3, padx=5)
        
        # Portfolio display
        self.portfolio_frame = ttk.LabelFrame(
            self.main_frame,
            text="Your Portfolio",
            padding="10"
        )
        self.portfolio_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview for portfolio display
        columns = ('symbol', 'company', 'quantity', 'price', 'value', 'trend')
        self.portfolio_tree = ttk.Treeview(
            self.portfolio_frame,
            columns=columns,
            show='headings',
            height=5,
            selectmode='browse'
        )
        
        # Column headings
        self.portfolio_tree.heading('symbol', text='Symbol')
        self.portfolio_tree.heading('company', text='Company')
        self.portfolio_tree.heading('quantity', text='Shares')
        self.portfolio_tree.heading('price', text='Price')
        self.portfolio_tree.heading('value', text='Value')
        self.portfolio_tree.heading('trend', text='Trend')
        
        # Column widths
        self.portfolio_tree.column('symbol', width=80)
        self.portfolio_tree.column('company', width=200)
        self.portfolio_tree.column('quantity', width=80, anchor=tk.CENTER)
        self.portfolio_tree.column('price', width=100, anchor=tk.E)
        self.portfolio_tree.column('value', width=120, anchor=tk.E)
        self.portfolio_tree.column('trend', width=80, anchor=tk.CENTER)
        
        self.portfolio_tree.pack(fill=tk.BOTH, expand=True)
        
        # Charts frame
        self.charts_frame = ttk.Frame(self.main_frame)
        self.charts_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Total value frame
        self.value_frame = ttk.Frame(self.charts_frame)
        self.value_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=5)
        
        self.total_value_var = tk.StringVar(value="Total Portfolio Value: $0.00")
        self.total_value_label = ttk.Label(
            self.value_frame,
            textvariable=self.total_value_var,
            font=('Arial', 14, 'bold'),
            foreground=COLORS['accent']
        )
        self.total_value_label.pack(pady=10)
        
        # Charts
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
        self.fig.patch.set_facecolor(COLORS['bg'])
        self.ax1.set_facecolor(COLORS['bg'])
        self.ax2.set_facecolor(COLORS['bg'])
        
        for ax in [self.ax1, self.ax2]:
            ax.tick_params(axis='x', colors=COLORS['fg'])
            ax.tick_params(axis='y', colors=COLORS['fg'])
            ax.spines['bottom'].set_color(COLORS['fg'])
            ax.spines['left'].set_color(COLORS['fg'])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.yaxis.label.set_color(COLORS['fg'])
            ax.xaxis.label.set_color(COLORS['fg'])
            ax.title.set_color(COLORS['fg'])
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.charts_frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
        
        # Action buttons
        self.button_frame = ttk.Frame(self.charts_frame)
        self.button_frame.grid(row=0, column=1, sticky=tk.E, padx=5)
        
        self.export_btn = ttk.Button(
            self.button_frame,
            text="Export Portfolio",
            command=self.save_to_file,
            style='TButton'
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ttk.Button(
            self.button_frame,
            text="Refresh",
            command=self.update_charts,
            style='TButton'
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(
            self.button_frame,
            text="Clear Portfolio",
            command=self.clear_portfolio,
            style='TButton'
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Initialize charts
        self.update_charts()
        
        # Apply the custom styling to the treeview
        self.style.configure("Treeview",
                            background="#f5f5f5",
                            foreground="black",
                            fieldbackground="#f5f5f5",
                            font=('Arial', 9))
        
        self.style.configure("Treeview.Heading",
                            background="#d9d9d9",
                            foreground="black",
                            font=('Arial', 10, 'bold'))
        
        self.style.map("Treeview",
                      background=[('selected', COLORS['button'])]
                      )
    
    def add_stock(self):
        try:
            selected = self.selected_stock.get()
            if not selected:
                messagebox.showwarning("Warning", "Please select a stock")
                return
                
            symbol = selected.split(" - ")[0]
            company = selected.split(" - ")[1]
            quantity = self.quantity_var.get()
            
            if symbol in stock_data:
                price = stock_data[symbol]['price']
                trend = "↑" if stock_data[symbol]['trend'] == "up" else "↓"
                trend_color = "#2ecc71" if trend == "↑" else "#e74c3c"
                
                # Check if stock already in portfolio
                item_exists = False
                for item in self.portfolio_tree.get_children():
                    if self.portfolio_tree.item(item)['values'][0] == symbol:
                        current_qty = self.portfolio_tree.item(item)['values'][2]
                        new_qty = current_qty + quantity
                        total_value = new_qty * price
                        
                        self.portfolio_tree.item(
                            item,
                            values=(symbol, company, new_qty, f"${price:,.2f}", 
                                    f"${total_value:,.2f}", trend),
                            tags=(trend,)
                        )
                        item_exists = True
                        break
                
                if not item_exists:
                    total_value = quantity * price
                    self.portfolio_tree.insert(
                        '', 
                        tk.END, 
                        values=(symbol, company, quantity, f"${price:,.2f}", 
                               f"${total_value:,.2f}", trend),
                        tags=(trend,)
                    )
                
                # Apply tag configuration
                self.portfolio_tree.tag_configure(
                    "↑", 
                    foreground="#2ecc71",
                    font=('Arial', 9, 'bold')
                )
                
                self.portfolio_tree.tag_configure(
                    "↓", 
                    foreground="#e74c3c",
                    font=('Arial', 9, 'bold')
                )
                
                self.update_charts()
                messagebox.showinfo("Success", f"Added {quantity} shares of {symbol}")
                
            else:
                messagebox.showerror("Error", "Stock symbol not found")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def remove_stock(self):
        selected_item = self.portfolio_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a stock to remove")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to remove the selected stock?"):
            self.portfolio_tree.delete(selected_item)
            self.update_charts()
            messagebox.showinfo("Success", "Stock removed from portfolio")
    
    def calculate_investment(self):
        total_value = 0
        for item in self.portfolio_tree.get_children():
            value_str = self.portfolio_tree.item(item)['values'][4]
            value = float(value_str.replace("$", "").replace(",", ""))
            total_value += value
        
        self.total_value_var.set(f"Total Portfolio Value: ${total_value:,.2f}")
        return total_value
    
    def update_charts(self):
        total_value = self.calculate_investment()
        
        # Get portfolio distribution data
        symbols = []
        values = []
        for item in self.portfolio_tree.get_children():
            data = self.portfolio_tree.item(item)['values']
            symbols.append(data[0])
            values.append(float(data[4].replace("$", "").replace(",", "")))
        
        # Pie chart
        self.ax1.clear()
        if symbols:
            self.ax1.pie(
                values,
                labels=symbols,
                autopct='%1.1f%%',
                startangle=90,
                colors=['#3498db', '#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6']
            )
            self.ax1.set_title('Portfolio Distribution', color=COLORS['fg'])
        else:
            self.ax1.text(
                0.5, 
                0.5, 
                'No portfolio data\nAdd stocks to see visualization', 
                horizontalalignment='center',
                verticalalignment='center',
                color=COLORS['fg']
            )
        
        # Performance chart
        self.ax2.clear()
        if symbols:
            changes = []
            for symbol in symbols:
                trend = 0.05 if stock_data[symbol]['trend'] == "up" else -0.06
                changes.append(trend)
            
            self.ax2.bar(
                symbols,
                changes,
                color=['#2ecc71' if x > 0 else '#e74c3c' for x in changes]
            )
            self.ax2.set_title('Recent Performance Trend', color=COLORS['fg'])
            self.ax2.set_ylabel('Percentage Change', color=COLORS['fg'])
            self.ax2.axhline(0, color=COLORS['fg'], linestyle='--', linewidth=0.8)
        else:
            self.ax2.text(
                0.5, 
                0.5, 
                'No performance data\nAdd stocks to see trends', 
                horizontalalignment='center',
                verticalalignment='center',
                color=COLORS['fg']
            )
        
        self.canvas.draw()
    
    def save_to_file(self):
        file_types = [
            ('CSV Files', '*.csv'),
            ('JSON Files', '*.json'),
            ('Text Files', '*.txt')
        ]
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=file_types,
            title="Save Portfolio Data"
        )
        
        if not file_path:
            return
        
        try:
            portfolio_data = []
            for item in self.portfolio_tree.get_children():
                data = self.portfolio_tree.item(item)['values']
                portfolio_data.append({
                    'symbol': data[0],
                    'company': data[1],
                    'quantity': data[2],
                    'price': data[3],
                    'value': data[4],
                    'trend': data[5]
                })
            
            total_value = self.calculate_investment()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if file_path.endswith('.csv'):
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Stock Portfolio", "Generated on", timestamp])
                    writer.writerow(["Symbol", "Company", "Shares", "Price", "Value", "Trend"])
                    for item in portfolio_data:
                        writer.writerow([
                            item['symbol'],
                            item['company'],
                            item['quantity'],
                            item['price'],
                            item['value'],
                            item['trend']
                        ])
                    writer.writerow([])
                    writer.writerow(["Total Portfolio Value:", f"${total_value:,.2f}"])
            
            elif file_path.endswith('.json'):
                data = {
                    'portfolio': portfolio_data,
                    'total_value': total_value,
                    'timestamp': timestamp
                }
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4)
            
            elif file_path.endswith('.txt'):
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(f"Stock Portfolio Snapshot\n")
                    file.write(f"Generated on: {timestamp}\n\n")
                    file.write("-" * 50 + "\n")
                    for item in portfolio_data:
                        file.write(f"Symbol: {item['symbol']}\n")
                        file.write(f"Company: {item['company']}\n")
                        file.write(f"Shares: {item['quantity']}\n")
                        file.write(f"Price: {item['price']}\n")
                        file.write(f"Value: {item['value']}\n")
                        file.write(f"Trend: {item['trend']}\n")
                        file.write("-" * 50 + "\n")
                    file.write(f"\nTotal Portfolio Value: ${total_value:,.2f}\n")
            
            messagebox.showinfo("Success", "Portfolio data saved successfully!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def clear_portfolio(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear your portfolio?"):
            self.portfolio_tree.delete(*self.portfolio_tree.get_children())
            self.update_charts()
            self.total_value_var.set("Total Portfolio Value: $0.00")

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedStockPortfolioTracker(root) 
    root.mainloop()
