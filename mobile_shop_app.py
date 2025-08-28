"""
mobile_shop_app.py
Starter PC Mobile Shop Management (Tkinter + SQLite)

Features:
- Products: add / edit / delete
- Inward (purchases) -> increases stock
- Outward (sales) -> decreases stock, checks stock qty
- Dashboard: today's sales total, total stock value
- Reports: Today's sales table, Stock report (with export to CSV)
- SQLite DB: mobileshop.db (created automatically)
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime, date
import csv
import os

DB_FILE = "mobileshop.db"

# ------------------------
# Database functions
# ------------------------
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # products table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT,
        model TEXT,
        imei TEXT,
        purchase_price REAL,
        selling_price REAL,
        stock_qty INTEGER DEFAULT 0
    )
    """)
    # purchases (inward)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        qty INTEGER,
        date TEXT,
        vendor TEXT,
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)
    # sales (outward)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        qty INTEGER,
        date TEXT,
        customer TEXT,
        payment_mode TEXT,
        total_amount REAL,
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)
    conn.commit()
    conn.close()

# ------------------------
# Data CRUD helpers
# ------------------------
def add_product(brand, model, imei, purchase_price, selling_price, stock_qty):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO products (brand, model, imei, purchase_price, selling_price, stock_qty)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (brand, model, imei, purchase_price, selling_price, stock_qty))
    conn.commit()
    conn.close()

def update_product(pid, brand, model, imei, purchase_price, selling_price, stock_qty):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE products SET brand=?, model=?, imei=?, purchase_price=?, selling_price=?, stock_qty=?
        WHERE id=?
    """, (brand, model, imei, purchase_price, selling_price, stock_qty, pid))
    conn.commit()
    conn.close()

def delete_product(pid):
    conn = get_connection()
    cur = conn.cursor()
    # optionally prevent deletion if sales/purchases exist; for starter allow cascade but keep referential integrity
    cur.execute("DELETE FROM products WHERE id=?", (pid,))
    conn.commit()
    conn.close()

def list_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products ORDER BY brand, model")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_product(pid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE id=?", (pid,))
    row = cur.fetchone()
    conn.close()
    return row

def record_purchase(product_id, qty, vendor, entry_date=None):
    if entry_date is None:
        entry_date = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cur = conn.cursor()
    # insert into purchases
    cur.execute("INSERT INTO purchases (product_id, qty, date, vendor) VALUES (?, ?, ?, ?)",
                (product_id, qty, entry_date, vendor))
    # update product stock
    cur.execute("UPDATE products SET stock_qty = stock_qty + ? WHERE id=?", (qty, product_id))
    conn.commit()
    conn.close()

def record_sale(product_id, qty, customer, payment_mode, entry_date=None):
    if entry_date is None:
        entry_date = datetime.now().strftime("%Y-%m-%d")
    # get selling price
    prod = get_product(product_id)
    if not prod:
        raise ValueError("Product not found")
    selling_price = prod["selling_price"] or 0.0
    total_amount = selling_price * qty

    conn = get_connection()
    cur = conn.cursor()
    # check stock
    cur.execute("SELECT stock_qty FROM products WHERE id=?", (product_id,))
    stock = cur.fetchone()["stock_qty"]
    if stock < qty:
        conn.close()
        return False, stock  # insufficient
    # insert sale
    cur.execute("""INSERT INTO sales (product_id, qty, date, customer, payment_mode, total_amount)
                   VALUES (?, ?, ?, ?, ?, ?)""", (product_id, qty, entry_date, customer, payment_mode, total_amount))
    # update product stock
    cur.execute("UPDATE products SET stock_qty = stock_qty - ? WHERE id=?", (qty, product_id))
    conn.commit()
    conn.close()
    return True, total_amount

def todays_sales():
    today = date.today().strftime("%Y-%m-%d")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.id, s.product_id, p.brand, p.model, s.qty, s.total_amount, s.customer, s.payment_mode, s.date
        FROM sales s JOIN products p ON s.product_id = p.id
        WHERE s.date = ?
        ORDER BY s.id DESC
    """, (today,))
    rows = cur.fetchall()
    conn.close()
    return rows

def stock_report():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, brand, model, imei, purchase_price, selling_price, stock_qty FROM products ORDER BY brand, model")
    rows = cur.fetchall()
    conn.close()
    return rows

def total_stock_value():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(purchase_price * stock_qty) as value FROM products")
    val = cur.fetchone()["value"]
    conn.close()
    return val or 0.0

def todays_sales_total_amount():
    rows = todays_sales()
    total = sum(row["total_amount"] for row in rows)
    return total

# ------------------------
# GUI
# ------------------------
class MobileShopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mobile Shop Management - Starter")
        self.geometry("1000x600")
        self.style = ttk.Style(self)
        # choose default theme if available
        try:
            self.style.theme_use('clam')
        except:
            pass

        self.create_widgets()
        self.refresh_dashboard()

    def create_widgets(self):
        # Top Frame - Dashboard
        top = ttk.Frame(self, padding=10)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="Mobile Shop - Starter", font=("Helvetica", 16, "bold")).pack(side=tk.LEFT)
        btn_frame = ttk.Frame(top)
        btn_frame.pack(side=tk.RIGHT)

        ttk.Button(btn_frame, text="Products", command=self.open_products_win).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Inward (Purchase)", command=self.open_inward_win).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Outward (Sales)", command=self.open_sales_win).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Reports", command=self.open_reports_win).pack(side=tk.LEFT, padx=5)

        # Dashboard area
        dash = ttk.Frame(self, padding=10)
        dash.pack(side=tk.TOP, fill=tk.X)

        self.today_sales_var = tk.StringVar(value="₹0.00")
        self.stock_value_var = tk.StringVar(value="₹0.00")
        self.total_products_var = tk.StringVar(value="0")

        ttk.Label(dash, text="Today's Sales:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, padx=(0,8))
        ttk.Label(dash, textvariable=self.today_sales_var, font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W)

        ttk.Label(dash, text="Total Stock Value:", font=("Arial", 12)).grid(row=0, column=2, sticky=tk.W, padx=(20,8))
        ttk.Label(dash, textvariable=self.stock_value_var, font=("Arial", 12, "bold")).grid(row=0, column=3, sticky=tk.W)

        ttk.Label(dash, text="Total Products:", font=("Arial", 12)).grid(row=0, column=4, sticky=tk.W, padx=(20,8))
        ttk.Label(dash, textvariable=self.total_products_var, font=("Arial", 12, "bold")).grid(row=0, column=5, sticky=tk.W)

        # Middle - Quick tables of today's sales
        mid = ttk.Frame(self, padding=10)
        mid.pack(fill=tk.BOTH, expand=True)

        ttk.Label(mid, text="Today's Sales (Quick view)", font=("Arial", 12, "underline")).pack(anchor=tk.W)

        self.sales_tree = ttk.Treeview(mid, columns=("id","brand","model","qty","amount","customer","pmode"), show="headings", height=8)
        for c,h in [("id","ID"),("brand","Brand"),("model","Model"),("qty","Qty"),("amount","Amount"),("customer","Customer"),("pmode","Payment")]:
            self.sales_tree.heading(c, text=h)
            self.sales_tree.column(c, width=100, anchor=tk.CENTER)
        self.sales_tree.pack(fill=tk.BOTH, expand=True, pady=8)

        # Bottom - Status
        bottom = ttk.Frame(self, padding=10)
        bottom.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Button(bottom, text="Refresh Dashboard", command=self.refresh_dashboard).pack(side=tk.LEFT)
        ttk.Button(bottom, text="Export Today's Sales CSV", command=self.export_todays_sales_csv).pack(side=tk.RIGHT)

    def refresh_dashboard(self):
        total = todays_sales_total_amount()
        self.today_sales_var.set(f"₹{total:.2f}")
        stock_val = total_stock_value()
        self.stock_value_var.set(f"₹{stock_val:.2f}")
        prods = list_products()
        self.total_products_var.set(str(len(prods)))

        # refresh today's sales tree
        for i in self.sales_tree.get_children():
            self.sales_tree.delete(i)
        for row in todays_sales():
            self.sales_tree.insert("", tk.END, values=(row["id"], row["brand"], row["model"], row["qty"], f"₹{row['total_amount']:.2f}", row["customer"], row["payment_mode"]))

    # ====== Product window ======
    def open_products_win(self):
        win = tk.Toplevel(self)
        win.title("Products")
        win.geometry("900x500")

        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id","brand","model","imei","purchase","selling","stock")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        headings = {"id":"ID","brand":"Brand","model":"Model","imei":"IMEI","purchase":"Purchase Price","selling":"Selling Price","stock":"Stock"}
        for c in cols:
            tree.heading(c, text=headings[c])
            tree.column(c, anchor=tk.CENTER, width=110)
        tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # populate
        def refresh_tree():
            for i in tree.get_children():
                tree.delete(i)
            for p in list_products():
                tree.insert("", tk.END, values=(p["id"], p["brand"], p["model"], p["imei"], f"{p['purchase_price']:.2f}", f"{p['selling_price']:.2f}", p["stock_qty"]))
        refresh_tree()

        # right control panel
        ctrl = ttk.Frame(frame, padding=10)
        ctrl.pack(side=tk.RIGHT, fill=tk.Y)

        def on_add():
            dialog = ProductDialog(self, title="Add Product")
            if dialog.result:
                b,m,imei,pp,sp,st = dialog.result
                try:
                    add_product(b,m,imei,float(pp),float(sp),int(st))
                    refresh_tree()
                    self.refresh_dashboard()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add product: {e}")

        def on_edit():
            selected = tree.focus()
            if not selected:
                messagebox.showinfo("Select", "Select a product to edit")
                return
            vals = tree.item(selected, "values")
            pid = int(vals[0])
            p = get_product(pid)
            dialog = ProductDialog(self, title="Edit Product", product=p)
            if dialog.result:
                b,m,imei,pp,sp,st = dialog.result
                try:
                    update_product(pid,b,m,imei,float(pp),float(sp),int(st))
                    refresh_tree()
                    self.refresh_dashboard()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update product: {e}")

        def on_delete():
            selected = tree.focus()
            if not selected:
                messagebox.showinfo("Select", "Select a product to delete")
                return
            vals = tree.item(selected, "values")
            pid = int(vals[0])
            if messagebox.askyesno("Confirm", f"Delete product ID {pid}?"):
                delete_product(pid)
                refresh_tree()
                self.refresh_dashboard()

        ttk.Button(ctrl, text="Add Product", command=on_add).pack(fill=tk.X, pady=5)
        ttk.Button(ctrl, text="Edit Selected", command=on_edit).pack(fill=tk.X, pady=5)
        ttk.Button(ctrl, text="Delete Selected", command=on_delete).pack(fill=tk.X, pady=5)
        ttk.Button(ctrl, text="Refresh", command=refresh_tree).pack(fill=tk.X, pady=5)
        ttk.Button(ctrl, text="Export Stock CSV", command=self.export_stock_csv).pack(fill=tk.X, pady=5)

    # ====== Inward (Purchase) window ======
    def open_inward_win(self):
        win = tk.Toplevel(self)
        win.title("Inward (Purchase Entry)")
        win.geometry("500x350")
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Product:").grid(row=0, column=0, sticky=tk.W, pady=5)
        prods = list_products()
        prod_map = { f"{p['id']} - {p['brand']} {p['model']} (Stock: {p['stock_qty']})": p['id'] for p in prods }
        prod_names = list(prod_map.keys())
        prod_cb = ttk.Combobox(frame, values=prod_names, state="readonly")
        prod_cb.grid(row=0, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Qty:").grid(row=1, column=0, sticky=tk.W, pady=5)
        qty_ent = ttk.Entry(frame)
        qty_ent.grid(row=1, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Vendor:").grid(row=2, column=0, sticky=tk.W, pady=5)
        vendor_ent = ttk.Entry(frame)
        vendor_ent.grid(row=2, column=1, sticky=tk.W, pady=5)

        def save_purchase():
            sel = prod_cb.get()
            if not sel:
                messagebox.showinfo("Select", "Select a product")
                return
            pid = prod_map[sel]
            try:
                q = int(qty_ent.get())
                if q <= 0:
                    raise ValueError("Qty must be positive")
            except:
                messagebox.showerror("Invalid", "Enter valid qty")
                return
            v = vendor_ent.get().strip()
            try:
                record_purchase(pid, q, v or "Unknown")
                messagebox.showinfo("Saved", f"Purchase recorded. {q} units added.")
                win.destroy()
                self.refresh_dashboard()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(frame, text="Save Purchase", command=save_purchase).grid(row=4, column=0, columnspan=2, pady=10)

    # ====== Sales (Outward) window ======
    def open_sales_win(self):
        win = tk.Toplevel(self)
        win.title("Outward (Sales Entry)")
        win.geometry("550x380")
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Product:").grid(row=0, column=0, sticky=tk.W, pady=5)
        prods = list_products()
        prod_map = { f"{p['id']} - {p['brand']} {p['model']} (Stock: {p['stock_qty']})": p['id'] for p in prods }
        prod_names = list(prod_map.keys())
        prod_cb = ttk.Combobox(frame, values=prod_names, state="readonly")
        prod_cb.grid(row=0, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Qty:").grid(row=1, column=0, sticky=tk.W, pady=5)
        qty_ent = ttk.Entry(frame)
        qty_ent.grid(row=1, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Customer:").grid(row=2, column=0, sticky=tk.W, pady=5)
        cust_ent = ttk.Entry(frame)
        cust_ent.grid(row=2, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Payment Mode:").grid(row=3, column=0, sticky=tk.W, pady=5)
        pmode_cb = ttk.Combobox(frame, values=["Cash","Card","UPI","Other"], state="readonly")
        pmode_cb.grid(row=3, column=1, sticky=tk.W, pady=5)
        pmode_cb.set("Cash")

        def save_sale():
            sel = prod_cb.get()
            if not sel:
                messagebox.showinfo("Select", "Select a product")
                return
            pid = prod_map[sel]
            try:
                q = int(qty_ent.get())
                if q <= 0:
                    raise ValueError()
            except:
                messagebox.showerror("Invalid", "Enter valid qty")
                return
            cust = cust_ent.get().strip() or "Walk-in"
            pmode = pmode_cb.get() or "Cash"
            ok, info = record_sale(pid, q, cust, pmode)
            if not ok:
                messagebox.showerror("Insufficient Stock", f"Available stock: {info}. Cannot sell {q}.")
                return
            else:
                messagebox.showinfo("Sale Saved", f"Sale recorded. Total: ₹{info:.2f}")
                win.destroy()
                self.refresh_dashboard()

        ttk.Button(frame, text="Save Sale", command=save_sale).grid(row=5, column=0, columnspan=2, pady=10)

    # ====== Reports window ======
    def open_reports_win(self):
        win = tk.Toplevel(self)
        win.title("Reports")
        win.geometry("900x600")
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Tabs
        nb = ttk.Notebook(frame)
        nb.pack(fill=tk.BOTH, expand=True)

        # Today's Sales Tab
        tab1 = ttk.Frame(nb)
        nb.add(tab1, text="Today's Sales")

        tree1 = ttk.Treeview(tab1, columns=("id","brand","model","qty","amount","customer","payment","date"), show="headings")
        for c,h in [("id","ID"),("brand","Brand"),("model","Model"),("qty","Qty"),("amount","Amount"),("customer","Customer"),("payment","Payment"),("date","Date")]:
            tree1.heading(c, text=h)
            tree1.column(c, width=110, anchor=tk.CENTER)
        tree1.pack(fill=tk.BOTH, expand=True, pady=5)

        def refresh_sales():
            for i in tree1.get_children():
                tree1.delete(i)
            for row in todays_sales():
                tree1.insert("", tk.END, values=(row["id"],row["brand"],row["model"],row["qty"],f"₹{row['total_amount']:.2f}",row["customer"],row["payment_mode"],row["date"]))
            total = todays_sales_total_amount()
            lbl_total.config(text=f"Today's Total: ₹{total:.2f}")

        lbl_total = ttk.Label(tab1, text="Today's Total: ₹0.00", font=("Arial", 12, "bold"))
        lbl_total.pack(anchor=tk.W, pady=4)
        ttk.Button(tab1, text="Refresh", command=refresh_sales).pack(anchor=tk.NE)
        refresh_sales()

        # Stock Tab
        tab2 = ttk.Frame(nb)
        nb.add(tab2, text="Stock Report")

        tree2 = ttk.Treeview(tab2, columns=("id","brand","model","imei","purchase","selling","stock","value"), show="headings")
        for c,h,w in [("id","ID",50),("brand","Brand",120),("model","Model",120),("imei","IMEI",120),("purchase","Purchase",80),("selling","Selling",80),("stock","Stock",60),("value","Stock Value",100)]:
            tree2.heading(c, text=h)
            tree2.column(c, width=w, anchor=tk.CENTER)
        tree2.pack(fill=tk.BOTH, expand=True, pady=5)
        lbl_stockval = ttk.Label(tab2, text="Total Stock Value: ₹0.00", font=("Arial", 12, "bold"))
        lbl_stockval.pack(anchor=tk.W, pady=4)

        def refresh_stock():
            for i in tree2.get_children():
                tree2.delete(i)
            total = 0.0
            for row in stock_report():
                val = (row["purchase_price"] or 0.0) * (row["stock_qty"] or 0)
                total += val
                tree2.insert("", tk.END, values=(row["id"],row["brand"],row["model"],row["imei"],f"₹{row['purchase_price']:.2f}",f"₹{row['selling_price']:.2f}",row["stock_qty"],f"₹{val:.2f}"))
            lbl_stockval.config(text=f"Total Stock Value: ₹{total:.2f}")

        ttk.Button(tab2, text="Refresh Stock Report", command=refresh_stock).pack(anchor=tk.NE)
        refresh_stock()

        # Export Buttons
        bottom = ttk.Frame(win, padding=8)
        bottom.pack(fill=tk.X)
        ttk.Button(bottom, text="Export Today's Sales CSV", command=self.export_todays_sales_csv).pack(side=tk.LEFT)
        ttk.Button(bottom, text="Export Stock CSV", command=self.export_stock_csv).pack(side=tk.LEFT, padx=8)

    # ===== CSV export helpers =====
    def export_todays_sales_csv(self):
        rows = todays_sales()
        if not rows:
            messagebox.showinfo("No Data", "No sales for today.")
            return
        fpath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="Save Today's Sales CSV", initialfile=f"todays_sales_{date.today().isoformat()}.csv")
        if not fpath:
            return
        with open(fpath, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ID","Brand","Model","Qty","TotalAmount","Customer","PaymentMode","Date"])
            for r in rows:
                w.writerow([r["id"], r["brand"], r["model"], r["qty"], f"{r['total_amount']:.2f}", r["customer"], r["payment_mode"], r["date"]])
        messagebox.showinfo("Saved", f"Today's sales exported to {os.path.basename(fpath)}")

    def export_stock_csv(self):
        rows = stock_report()
        if not rows:
            messagebox.showinfo("No Data", "No products available.")
            return
        fpath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="Save Stock CSV", initialfile=f"stock_report_{date.today().isoformat()}.csv")
        if not fpath:
            return
        with open(fpath, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ID","Brand","Model","IMEI","PurchasePrice","SellingPrice","StockQty","StockValue"])
            for r in rows:
                val = (r["purchase_price"] or 0.0) * (r["stock_qty"] or 0)
                w.writerow([r["id"], r["brand"], r["model"], r["imei"], f"{r['purchase_price']:.2f}", f"{r['selling_price']:.2f}", r["stock_qty"], f"{val:.2f}"])
        messagebox.showinfo("Saved", f"Stock exported to {os.path.basename(fpath)}")

# Product add/edit dialog
class ProductDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, product=None):
        self.product = product
        super().__init__(parent, title=title)

    def body(self, master):
        ttk.Label(master, text="Brand:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.brand = ttk.Entry(master); self.brand.grid(row=0,column=1, pady=4)
        ttk.Label(master, text="Model:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.model = ttk.Entry(master); self.model.grid(row=1,column=1, pady=4)
        ttk.Label(master, text="IMEI:").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.imei = ttk.Entry(master); self.imei.grid(row=2,column=1, pady=4)
        ttk.Label(master, text="Purchase Price:").grid(row=3, column=0, sticky=tk.W, pady=4)
        self.pp = ttk.Entry(master); self.pp.grid(row=3,column=1, pady=4)
        ttk.Label(master, text="Selling Price:").grid(row=4, column=0, sticky=tk.W, pady=4)
        self.sp = ttk.Entry(master); self.sp.grid(row=4,column=1, pady=4)
        ttk.Label(master, text="Stock Qty:").grid(row=5, column=0, sticky=tk.W, pady=4)
        self.st = ttk.Entry(master); self.st.grid(row=5,column=1, pady=4)

        if self.product:
            p = self.product
            self.brand.insert(0, p["brand"] or "")
            self.model.insert(0, p["model"] or "")
            self.imei.insert(0, p["imei"] or "")
            self.pp.insert(0, str(p["purchase_price"] or 0.0))
            self.sp.insert(0, str(p["selling_price"] or 0.0))
            self.st.insert(0, str(p["stock_qty"] or 0))

        return self.brand

    def validate(self):
        try:
            if not self.brand.get().strip():
                raise ValueError("Brand required")
            if not self.model.get().strip():
                raise ValueError("Model required")
            float(self.pp.get())
            float(self.sp.get())
            int(self.st.get())
        except Exception as e:
            messagebox.showerror("Invalid", str(e))
            return False
        return True

    def apply(self):
        self.result = (self.brand.get().strip(), self.model.get().strip(), self.imei.get().strip(),
                        self.pp.get().strip(), self.sp.get().strip(), self.st.get().strip())

# ------------------------
# Main
# ------------------------
if __name__ == "__main__":
    init_db()
    app = MobileShopApp()
    app.mainloop()
