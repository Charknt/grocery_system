#!/usr/bin/env python3
"""
Local Grocery Inventory Management System
Tkinter + SQLite  |  Palette: #F4EEFF · #DCD6F7 · #A6B1E1 · #424874
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import uuid
from datetime import datetime

# ══════════════════════════════════════════════════════════════════
#  PALETTE
# ══════════════════════════════════════════════════════════════════
BG      = "#F4EEFF"   # app background  (lightest)
PANEL   = "#DCD6F7"   # sidebar, cards
ACCENT  = "#A6B1E1"   # borders, scrollbars
DARK    = "#424874"   # buttons, headings
WHITE   = "#FFFFFF"
TEXT    = "#2D2D3A"
MUTED   = "#7A7A9A"
RED     = "#B85C68"
GREEN   = "#5A9C7A"

# ══════════════════════════════════════════════════════════════════
#  DATABASE
# ══════════════════════════════════════════════════════════════════
DB_FILE = "grocery.db"


def db_conn():
    return sqlite3.connect(DB_FILE)


def init_db():
    with db_conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS supplier(
            supplier_id       TEXT PRIMARY KEY,
            supplier_name     TEXT NOT NULL,
            contact_number    TEXT,
            email_address     TEXT,
            delivery_schedule TEXT
        );
        CREATE TABLE IF NOT EXISTS staff(
            staff_id       TEXT PRIMARY KEY,
            first_name     TEXT NOT NULL,
            middle_initial TEXT,
            last_name      TEXT NOT NULL,
            role           TEXT,
            shift          TEXT,
            contact_number TEXT
        );
        CREATE TABLE IF NOT EXISTS product(
            product_id     TEXT PRIMARY KEY,
            product_name   TEXT NOT NULL,
            category       TEXT,
            brand          TEXT,
            unit_price     REAL DEFAULT 0,
            stock_quantity INTEGER DEFAULT 0,
            expiry_date    TEXT
        );
        CREATE TABLE IF NOT EXISTS sales(
            sale_id       TEXT PRIMARY KEY,
            sale_date     TEXT,
            quantity_sold INTEGER,
            total_amount  REAL,
            staff_id      TEXT,
            product_id    TEXT
        );
        CREATE TABLE IF NOT EXISTS delivery(
            delivery_id       TEXT PRIMARY KEY,
            delivery_date     TEXT,
            quantity_received INTEGER,
            total_cost        REAL,
            supplier_id       TEXT,
            product_id        TEXT,
            staff_id          TEXT
        );
        """)


def gen_id(prefix=""):
    return prefix + uuid.uuid4().hex[:8].upper()


# ══════════════════════════════════════════════════════════════════
#  REUSABLE WIDGET HELPERS
# ══════════════════════════════════════════════════════════════════

def _apply_tree_style():
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("G.Treeview",
                background=WHITE, foreground=TEXT,
                rowheight=28, fieldbackground=WHITE,
                font=("Segoe UI", 9), borderwidth=0)
    s.configure("G.Treeview.Heading",
                background=DARK, foreground=WHITE,
                font=("Segoe UI", 9, "bold"), relief="flat")
    s.map("G.Treeview",
          background=[("selected", ACCENT)],
          foreground=[("selected", WHITE)])
    s.configure("Vertical.TScrollbar",
                background=PANEL, troughcolor=BG,
                arrowcolor=DARK, bordercolor=PANEL)


def make_tree(parent, cols, height=14):
    _apply_tree_style()
    wrap = tk.Frame(parent, bg=ACCENT, bd=1, relief="flat")
    tree = ttk.Treeview(wrap, columns=cols, show="headings",
                        style="G.Treeview", selectmode="browse",
                        height=height)
    sb = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center", minwidth=60, width=120)
    return wrap, tree


def make_btn(parent, text, cmd=None, primary=True, danger=False, **kw):
    if danger:
        bg, fg = RED, WHITE
    elif primary:
        bg, fg = DARK, WHITE
    else:
        bg, fg = PANEL, TEXT
    return tk.Button(
        parent, text=text, command=cmd,
        bg=bg, fg=fg, relief="flat", bd=0,
        font=("Segoe UI", 9, "bold"),
        cursor="hand2", padx=14, pady=7,
        activebackground=ACCENT, activeforeground=WHITE,
        **kw
    )


def make_search(parent, var, label="Search"):
    f = tk.Frame(parent, bg=BG)
    tk.Label(f, text=label, bg=BG, fg=MUTED,
             font=("Segoe UI", 9)).pack(side="left", padx=(0, 6))
    entry = tk.Entry(f, textvariable=var,
                     bg=WHITE, fg=TEXT, relief="flat",
                     font=("Segoe UI", 9), width=28,
                     highlightthickness=1,
                     highlightbackground=ACCENT,
                     highlightcolor=DARK,
                     insertbackground=DARK)
    entry.pack(side="left", ipady=5, padx=2)
    return f


def field_entry(parent, row, label, key, var, kind="entry", opts=None):
    """Render a labeled input field in a grid parent."""
    tk.Label(parent, text=label, bg=BG, fg=MUTED,
             font=("Segoe UI", 8)).grid(row=row * 2, column=0,
                                        sticky="w", pady=(8, 0))
    if kind == "combo":
        w = ttk.Combobox(parent, textvariable=var,
                         values=opts or [], state="readonly",
                         font=("Segoe UI", 9), width=36)
        if opts:
            w.current(0)
    else:
        w = tk.Entry(parent, textvariable=var,
                     bg=WHITE, fg=TEXT, relief="flat", width=38,
                     font=("Segoe UI", 9),
                     highlightthickness=1,
                     highlightbackground=PANEL,
                     highlightcolor=ACCENT,
                     insertbackground=DARK)
    w.grid(row=row * 2 + 1, column=0, sticky="ew", ipady=6)
    return w


# ══════════════════════════════════════════════════════════════════
#  FORM DIALOG
# ══════════════════════════════════════════════════════════════════

class FormDialog(tk.Toplevel):
    """
    Generic modal form.
    fields : list of (label, key, 'entry'|'combo', options_list)
    on_save: callable(dict)  – raises Exception on validation error
    prefill: dict of key→value (optional)
    """

    def __init__(self, master, title, fields, on_save, prefill=None):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()
        self.transient(master)

        n = len(fields)
        w, h = 430, 64 + n * 56 + 66
        self.update_idletasks()
        px = master.winfo_rootx() + max(0, (master.winfo_width()  - w) // 2)
        py = master.winfo_rooty() + max(0, (master.winfo_height() - h) // 2)
        self.geometry(f"{w}x{h}+{px}+{py}")

        # ── Header bar ──
        hdr = tk.Frame(self, bg=DARK, height=46)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=title, bg=DARK, fg=WHITE,
                 font=("Segoe UI", 11, "bold")).pack(
            side="left", padx=20, pady=0)

        # ── Body ──
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=22, pady=10)

        self.vars = {}
        for i, (lbl, key, kind, opts) in enumerate(fields):
            val = (prefill or {}).get(key, "")
            var = tk.StringVar(value=str(val) if val is not None else "")
            field_entry(body, i, lbl, key, var, kind, opts)
            self.vars[key] = var

        # ── Footer ──
        foot = tk.Frame(self, bg=BG)
        foot.pack(fill="x", padx=22, pady=10)
        make_btn(foot, "Cancel", self.destroy, primary=False).pack(
            side="right", padx=(4, 0))
        make_btn(foot, "  Save  ", lambda: self._save(on_save)).pack(
            side="right")

    def _save(self, on_save):
        data = {k: v.get().strip() for k, v in self.vars.items()}
        try:
            on_save(data)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)


# ══════════════════════════════════════════════════════════════════
#  PICKER DIALOG
# ══════════════════════════════════════════════════════════════════

def picker_dialog(master, title, options):
    """Simple combo-based picker; returns selected value or None."""
    if not options:
        return None
    dlg = tk.Toplevel(master)
    dlg.title(title)
    dlg.resizable(False, False)
    dlg.configure(bg=BG)
    dlg.grab_set()
    dlg.transient(master)
    dlg.geometry("320x160")
    dlg.update_idletasks()
    px = master.winfo_rootx() + (master.winfo_width()  - 320) // 2
    py = master.winfo_rooty() + (master.winfo_height() - 160) // 2
    dlg.geometry(f"+{px}+{py}")

    tk.Label(dlg, text=title, bg=BG, fg=DARK,
             font=("Segoe UI", 10, "bold")).pack(pady=(16, 6))
    var = tk.StringVar(value=options[0])
    cb = ttk.Combobox(dlg, textvariable=var, values=options,
                      state="readonly", width=36, font=("Segoe UI", 9))
    cb.pack(padx=18, pady=4)

    result = [None]

    def ok():
        result[0] = var.get()
        dlg.destroy()

    make_btn(dlg, "  OK  ", ok).pack(pady=12)
    dlg.wait_window()
    return result[0]


# ══════════════════════════════════════════════════════════════════
#  BASE PAGE
# ══════════════════════════════════════════════════════════════════

class Page(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)

    def page_header(self, title, subtitle=""):
        """Returns the header frame (for placing action buttons on right)."""
        f = tk.Frame(self, bg=BG)
        f.pack(fill="x", padx=28, pady=(22, 8))
        tk.Label(f, text=title, bg=BG, fg=DARK,
                 font=("Segoe UI", 17, "bold")).pack(side="left")
        if subtitle:
            tk.Label(f, text=f"  {subtitle}", bg=BG, fg=MUTED,
                     font=("Segoe UI", 9)).pack(side="left", pady=6)
        return f

    def divider(self):
        tk.Frame(self, bg=ACCENT, height=1).pack(fill="x", padx=28, pady=6)


# ══════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════

class DashboardPage(Page):
    def __init__(self, master):
        super().__init__(master)
        self.page_header("Dashboard", "Store overview at a glance")
        self._build()

    def _stats(self):
        today = datetime.now().strftime("%Y-%m-%d")
        with db_conn() as c:
            prods    = c.execute("SELECT COUNT(*) FROM product").fetchone()[0]
            low      = c.execute(
                "SELECT COUNT(*) FROM product WHERE stock_quantity < 5").fetchone()[0]
            sales_n  = c.execute(
                "SELECT COUNT(*) FROM sales WHERE sale_date=?", (today,)).fetchone()[0]
            del_n    = c.execute(
                "SELECT COUNT(*) FROM delivery WHERE delivery_date=?", (today,)).fetchone()[0]
        return prods, low, sales_n, del_n

    def _build(self):
        prods, low, sales_n, del_n = self._stats()

        # ── Stat cards ──
        card_row = tk.Frame(self, bg=BG)
        card_row.pack(fill="x", padx=28, pady=(0, 12))

        card_data = [
            ("📦", "Total Products",   str(prods),   DARK),
            ("⚠",  "Low Stock Items",  str(low),     RED),
            ("🛒",  "Sales Today",     str(sales_n), GREEN),
            ("🚚",  "Deliveries Today",str(del_n),   ACCENT),
        ]
        for icon, label, val, color in card_data:
            self._stat_card(card_row, icon, label, val, color)

        self.divider()

        # ── Low stock table ──
        tk.Label(self, text="⚠  Low Stock Products  (quantity < 5)",
                 bg=BG, fg=DARK,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=28)
        tk.Label(self, text="Items that need restocking soon.",
                 bg=BG, fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=28, pady=(0, 6))

        wrap, tree = make_tree(self,
                               ["Product Name", "Category", "Brand", "Stock Qty"],
                               height=10)
        wrap.pack(fill="both", expand=True, padx=28, pady=(0, 16))

        with db_conn() as c:
            rows = c.execute("""
                SELECT product_name, category, brand, stock_quantity
                FROM product
                WHERE stock_quantity < 5
                ORDER BY stock_quantity ASC
            """).fetchall()
        for r in rows:
            tree.insert("", "end", values=r)

        if not rows:
            tree.insert("", "end",
                        values=("All products are well-stocked!", "", "", ""))

    def _stat_card(self, parent, icon, label, val, color):
        card = tk.Frame(parent, bg=PANEL,
                        highlightthickness=1, highlightbackground=ACCENT)
        card.pack(side="left", expand=True, fill="both", padx=5, ipady=6)
        tk.Label(card, text=icon, bg=PANEL, fg=color,
                 font=("Segoe UI", 18)).pack(pady=(12, 0))
        tk.Label(card, text=val, bg=PANEL, fg=color,
                 font=("Segoe UI", 28, "bold")).pack()
        tk.Label(card, text=label, bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(pady=(0, 12))


# ══════════════════════════════════════════════════════════════════
#  PRODUCTS
# ══════════════════════════════════════════════════════════════════

class ProductsPage(Page):
    CATS = ["Canned Goods", "Snacks", "Drinks", "Instant Noodles",
            "Toiletries", "Cleaning Supplies", "Household", "Others"]

    def __init__(self, master):
        super().__init__(master)
        hdr = self.page_header("Products", "Manage your product catalog")
        make_btn(hdr, "+ Add Product", self._add).pack(side="right")
        self._build()

    def _form_fields(self):
        return [
            ("Product Name",              "product_name",   "entry", []),
            ("Category",                  "category",       "combo", self.CATS),
            ("Brand",                     "brand",          "entry", []),
            ("Unit Price (₱)",            "unit_price",     "entry", []),
            ("Stock Quantity",            "stock_quantity", "entry", []),
            ("Expiry Date  (YYYY-MM-DD)", "expiry_date",    "entry", []),
        ]

    def _build(self):
        # Search bar
        sf = tk.Frame(self, bg=BG)
        sf.pack(fill="x", padx=28, pady=(0, 6))
        self.q = tk.StringVar()
        self.q.trace("w", lambda *_: self._refresh())
        make_search(sf, self.q).pack(side="left")

        # Treeview
        wrap, self.tree = make_tree(
            self, ["ID", "Name", "Category", "Brand", "Price (₱)", "Stock", "Expiry"])
        wrap.pack(fill="both", expand=True, padx=28)

        # Action buttons
        bf = tk.Frame(self, bg=BG)
        bf.pack(fill="x", padx=28, pady=10)
        make_btn(bf, "✏  Edit",    self._edit,   primary=False).pack(side="left", padx=(0, 4))
        make_btn(bf, "🗑  Delete",  self._delete, danger=True).pack(side="left")

        self._refresh()

    def _refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        q = self.q.get().strip().lower()
        with db_conn() as c:
            rows = c.execute(
                "SELECT * FROM product ORDER BY product_name").fetchall()
        for r in rows:
            if q and q not in r[1].lower() \
                    and q not in (r[2] or "").lower() \
                    and q not in (r[3] or "").lower():
                continue
            disp = list(r)
            disp[4] = f"₱{float(r[4]):.2f}"
            self.tree.insert("", "end", values=disp)

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Nothing Selected",
                                   "Please select a product first.")
            return None
        return self.tree.item(sel[0])["values"][0]

    def _add(self):
        def save(d):
            if not d["product_name"]:
                raise ValueError("Product Name is required.")
            pid = gen_id("PRD")
            with db_conn() as c:
                c.execute(
                    "INSERT INTO product VALUES(?,?,?,?,?,?,?)",
                    (pid, d["product_name"], d["category"], d["brand"],
                     float(d["unit_price"] or 0),
                     int(d["stock_quantity"] or 0),
                     d["expiry_date"] or None))
            self._refresh()

        FormDialog(self.winfo_toplevel(), "Add Product",
                   self._form_fields(), save)

    def _edit(self):
        pid = self._selected_id()
        if pid is None:
            return
        with db_conn() as c:
            row = c.execute(
                "SELECT * FROM product WHERE product_id=?", (pid,)).fetchone()
        keys = ["product_id", "product_name", "category", "brand",
                "unit_price", "stock_quantity", "expiry_date"]
        prefill = dict(zip(keys, row))

        def save(d):
            with db_conn() as c:
                c.execute("""
                    UPDATE product
                    SET product_name=?, category=?, brand=?,
                        unit_price=?, stock_quantity=?, expiry_date=?
                    WHERE product_id=?""",
                          (d["product_name"], d["category"], d["brand"],
                           float(d["unit_price"] or 0),
                           int(d["stock_quantity"] or 0),
                           d["expiry_date"] or None, pid))
            self._refresh()

        FormDialog(self.winfo_toplevel(), "Edit Product",
                   self._form_fields(), save, prefill)

    def _delete(self):
        pid = self._selected_id()
        if pid is None:
            return
        if not messagebox.askyesno("Delete Product",
                                   "Are you sure you want to delete this product?"):
            return
        with db_conn() as c:
            c.execute("DELETE FROM product WHERE product_id=?", (pid,))
        self._refresh()


# ══════════════════════════════════════════════════════════════════
#  SUPPLIERS
# ══════════════════════════════════════════════════════════════════

class SuppliersPage(Page):
    SCHEDULES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                 "Saturday", "Sunday", "Weekly", "Bi-weekly", "Monthly",
                 "As Needed"]

    def __init__(self, master):
        super().__init__(master)
        hdr = self.page_header("Suppliers", "Manage your product suppliers")
        make_btn(hdr, "+ Add Supplier", self._add).pack(side="right")
        self._build()

    def _form_fields(self):
        return [
            ("Supplier Name",     "supplier_name",    "entry", []),
            ("Contact Number",    "contact_number",   "entry", []),
            ("Email Address",     "email_address",    "entry", []),
            ("Delivery Schedule", "delivery_schedule","combo", self.SCHEDULES),
        ]

    def _build(self):
        sf = tk.Frame(self, bg=BG)
        sf.pack(fill="x", padx=28, pady=(0, 6))
        self.q = tk.StringVar()
        self.q.trace("w", lambda *_: self._refresh())
        make_search(sf, self.q).pack(side="left")

        wrap, self.tree = make_tree(
            self, ["ID", "Supplier Name", "Contact", "Email", "Schedule"])
        wrap.pack(fill="both", expand=True, padx=28)

        bf = tk.Frame(self, bg=BG)
        bf.pack(fill="x", padx=28, pady=10)
        make_btn(bf, "✏  Edit",   self._edit,   primary=False).pack(side="left", padx=(0, 4))
        make_btn(bf, "🗑  Delete", self._delete, danger=True).pack(side="left")

        self._refresh()

    def _refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        q = self.q.get().strip().lower()
        with db_conn() as c:
            rows = c.execute(
                "SELECT * FROM supplier ORDER BY supplier_name").fetchall()
        for r in rows:
            if q and q not in r[1].lower() \
                    and q not in (r[3] or "").lower():
                continue
            self.tree.insert("", "end", values=r)

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Nothing Selected",
                                   "Please select a supplier first.")
            return None
        return self.tree.item(sel[0])["values"][0]

    def _add(self):
        def save(d):
            if not d["supplier_name"]:
                raise ValueError("Supplier Name is required.")
            sid = gen_id("SUP")
            with db_conn() as c:
                c.execute("INSERT INTO supplier VALUES(?,?,?,?,?)",
                          (sid, d["supplier_name"], d["contact_number"],
                           d["email_address"], d["delivery_schedule"]))
            self._refresh()

        FormDialog(self.winfo_toplevel(), "Add Supplier",
                   self._form_fields(), save)

    def _edit(self):
        sid = self._selected_id()
        if sid is None:
            return
        with db_conn() as c:
            row = c.execute(
                "SELECT * FROM supplier WHERE supplier_id=?", (sid,)).fetchone()
        keys = ["supplier_id", "supplier_name", "contact_number",
                "email_address", "delivery_schedule"]
        prefill = dict(zip(keys, row))

        def save(d):
            with db_conn() as c:
                c.execute("""
                    UPDATE supplier
                    SET supplier_name=?, contact_number=?,
                        email_address=?, delivery_schedule=?
                    WHERE supplier_id=?""",
                          (d["supplier_name"], d["contact_number"],
                           d["email_address"], d["delivery_schedule"], sid))
            self._refresh()

        FormDialog(self.winfo_toplevel(), "Edit Supplier",
                   self._form_fields(), save, prefill)

    def _delete(self):
        sid = self._selected_id()
        if sid is None:
            return
        if not messagebox.askyesno("Delete Supplier",
                                   "Delete this supplier?"):
            return
        with db_conn() as c:
            c.execute("DELETE FROM supplier WHERE supplier_id=?", (sid,))
        self._refresh()


# ══════════════════════════════════════════════════════════════════
#  STAFF
# ══════════════════════════════════════════════════════════════════

class StaffPage(Page):
    ROLES  = ["Cashier", "Stocker", "Manager", "Supervisor",
              "Delivery Staff", "Janitor"]
    SHIFTS = ["Morning  (6AM – 2PM)", "Afternoon  (2PM – 10PM)",
              "Night  (10PM – 6AM)", "Full Day  (8AM – 5PM)"]

    def __init__(self, master):
        super().__init__(master)
        hdr = self.page_header("Staff", "Manage store employees")
        make_btn(hdr, "+ Add Staff", self._add).pack(side="right")
        self._build()

    def _form_fields(self):
        return [
            ("First Name",     "first_name",     "entry", []),
            ("Middle Initial", "middle_initial",  "entry", []),
            ("Last Name",      "last_name",       "entry", []),
            ("Role",           "role",            "combo", self.ROLES),
            ("Shift",          "shift",           "combo", self.SHIFTS),
            ("Contact Number", "contact_number",  "entry", []),
        ]

    def _build(self):
        sf = tk.Frame(self, bg=BG)
        sf.pack(fill="x", padx=28, pady=(0, 6))
        self.q = tk.StringVar()
        self.q.trace("w", lambda *_: self._refresh())
        make_search(sf, self.q).pack(side="left")

        wrap, self.tree = make_tree(
            self, ["ID", "First Name", "M.I.", "Last Name",
                   "Role", "Shift", "Contact"])
        wrap.pack(fill="both", expand=True, padx=28)

        bf = tk.Frame(self, bg=BG)
        bf.pack(fill="x", padx=28, pady=10)
        make_btn(bf, "✏  Edit",   self._edit,   primary=False).pack(side="left", padx=(0, 4))
        make_btn(bf, "🗑  Delete", self._delete, danger=True).pack(side="left")

        self._refresh()

    def _refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        q = self.q.get().strip().lower()
        with db_conn() as c:
            rows = c.execute(
                "SELECT * FROM staff ORDER BY last_name").fetchall()
        for r in rows:
            fullname = (r[1] + " " + r[3]).lower()
            if q and q not in fullname and q not in (r[4] or "").lower():
                continue
            self.tree.insert("", "end", values=r)

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Nothing Selected",
                                   "Please select a staff member first.")
            return None
        return self.tree.item(sel[0])["values"][0]

    def _add(self):
        def save(d):
            if not d["first_name"] or not d["last_name"]:
                raise ValueError("First Name and Last Name are required.")
            sid = gen_id("STF")
            with db_conn() as c:
                c.execute("INSERT INTO staff VALUES(?,?,?,?,?,?,?)",
                          (sid, d["first_name"], d["middle_initial"],
                           d["last_name"], d["role"], d["shift"],
                           d["contact_number"]))
            self._refresh()

        FormDialog(self.winfo_toplevel(), "Add Staff Member",
                   self._form_fields(), save)

    def _edit(self):
        stf_id = self._selected_id()
        if stf_id is None:
            return
        with db_conn() as c:
            row = c.execute(
                "SELECT * FROM staff WHERE staff_id=?", (stf_id,)).fetchone()
        keys = ["staff_id", "first_name", "middle_initial", "last_name",
                "role", "shift", "contact_number"]
        prefill = dict(zip(keys, row))

        def save(d):
            with db_conn() as c:
                c.execute("""
                    UPDATE staff
                    SET first_name=?, middle_initial=?, last_name=?,
                        role=?, shift=?, contact_number=?
                    WHERE staff_id=?""",
                          (d["first_name"], d["middle_initial"],
                           d["last_name"], d["role"], d["shift"],
                           d["contact_number"], stf_id))
            self._refresh()

        FormDialog(self.winfo_toplevel(), "Edit Staff Member",
                   self._form_fields(), save, prefill)

    def _delete(self):
        stf_id = self._selected_id()
        if stf_id is None:
            return
        if not messagebox.askyesno("Delete Staff",
                                   "Delete this staff member?"):
            return
        with db_conn() as c:
            c.execute("DELETE FROM staff WHERE staff_id=?", (stf_id,))
        self._refresh()


# ══════════════════════════════════════════════════════════════════
#  SALES
# ══════════════════════════════════════════════════════════════════

class SalesPage(Page):
    def __init__(self, master):
        super().__init__(master)
        hdr = self.page_header("Sales", "Record and view sales transactions")
        make_btn(hdr, "+ New Sale", self._add).pack(side="right")
        self._build()

    def _build(self):
        sf = tk.Frame(self, bg=BG)
        sf.pack(fill="x", padx=28, pady=(0, 6))
        self.q = tk.StringVar()
        self.q.trace("w", lambda *_: self._refresh())
        make_search(sf, self.q, "Filter by product / date").pack(side="left")

        wrap, self.tree = make_tree(
            self, ["Sale ID", "Date", "Product", "Staff",
                   "Qty Sold", "Total (₱)"])
        wrap.pack(fill="both", expand=True, padx=28)

        bf = tk.Frame(self, bg=BG)
        bf.pack(fill="x", padx=28, pady=10)
        make_btn(bf, "🗑  Delete", self._delete, danger=True).pack(side="left")
        tk.Label(bf, text="Note: deleting a sale does not restore stock.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(side="left", padx=10)

        self._refresh()

    def _refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        q = self.q.get().strip().lower()
        with db_conn() as c:
            rows = c.execute("""
                SELECT s.sale_id, s.sale_date,
                       COALESCE(p.product_name, '—'),
                       COALESCE(st.first_name||' '||st.last_name, '—'),
                       s.quantity_sold,
                       s.total_amount
                FROM sales s
                LEFT JOIN product p  ON s.product_id = p.product_id
                LEFT JOIN staff   st ON s.staff_id   = st.staff_id
                ORDER BY s.sale_date DESC
            """).fetchall()
        for r in rows:
            if q and q not in (r[1] or "").lower() \
                    and q not in (r[2] or "").lower():
                continue
            disp = list(r)
            disp[5] = f"₱{float(r[5] or 0):.2f}"
            self.tree.insert("", "end", values=disp)

    def _add(self):
        with db_conn() as c:
            products = c.execute(
                "SELECT product_id, product_name, unit_price, stock_quantity "
                "FROM product ORDER BY product_name").fetchall()
            staff = c.execute(
                "SELECT staff_id, first_name||' '||last_name "
                "FROM staff ORDER BY last_name").fetchall()

        if not products:
            messagebox.showwarning("No Products",
                                   "Please add products before recording a sale.")
            return

        prod_opts = [f"{p[0]}  –  {p[1]}  (₱{p[2]:.2f}, stock: {p[3]})"
                     for p in products]
        stf_opts  = ([f"{s[0]}  –  {s[1]}" for s in staff]
                     if staff else ["(No staff added)"])

        fields = [
            ("Product",               "product", "combo", prod_opts),
            ("Staff Member",          "staff",   "combo", stf_opts),
            ("Quantity Sold",         "qty",     "entry", []),
            ("Sale Date (YYYY-MM-DD)","date",    "entry", []),
        ]

        def save(d):
            if not d["product"]:
                raise ValueError("Please select a product.")
            if not d["qty"]:
                raise ValueError("Quantity is required.")
            pid_raw = d["product"].split("–")[0].strip().split()[0]
            qty     = int(d["qty"])
            date_v  = d["date"] or datetime.now().strftime("%Y-%m-%d")

            # Validate qty
            with db_conn() as c:
                prod_row = c.execute(
                    "SELECT unit_price, stock_quantity, product_name "
                    "FROM product WHERE product_id=?", (pid_raw,)).fetchone()
            if not prod_row:
                raise ValueError("Product not found.")
            price, stock, pname = prod_row
            if qty <= 0:
                raise ValueError("Quantity must be greater than 0.")
            if qty > stock:
                raise ValueError(
                    f"Insufficient stock!\n"
                    f"'{pname}' only has {stock} unit(s) available.")

            total = price * qty
            sale_id = gen_id("SAL")

            # Get staff ID
            stf_id = None
            if "–" in d["staff"]:
                stf_id = d["staff"].split("–")[0].strip().split()[0]

            with db_conn() as c:
                c.execute("INSERT INTO sales VALUES(?,?,?,?,?,?)",
                          (sale_id, date_v, qty, total, stf_id, pid_raw))
                c.execute(
                    "UPDATE product SET stock_quantity = stock_quantity - ? "
                    "WHERE product_id=?", (qty, pid_raw))
            self._refresh()

        FormDialog(self.winfo_toplevel(), "Record New Sale", fields, save,
                   {"date": datetime.now().strftime("%Y-%m-%d")})

    def _delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Nothing Selected",
                                   "Select a sale to delete.")
            return
        sale_id = self.tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Delete Sale",
                                   "Delete this sale record?\n"
                                   "Stock quantity will NOT be restored."):
            return
        with db_conn() as c:
            c.execute("DELETE FROM sales WHERE sale_id=?", (sale_id,))
        self._refresh()


# ══════════════════════════════════════════════════════════════════
#  DELIVERIES
# ══════════════════════════════════════════════════════════════════

class DeliveryPage(Page):
    def __init__(self, master):
        super().__init__(master)
        hdr = self.page_header("Deliveries", "Track incoming stock deliveries")
        make_btn(hdr, "+ New Delivery", self._add).pack(side="right")
        self._build()

    def _build(self):
        sf = tk.Frame(self, bg=BG)
        sf.pack(fill="x", padx=28, pady=(0, 6))
        self.q = tk.StringVar()
        self.q.trace("w", lambda *_: self._refresh())
        make_search(sf, self.q, "Filter by product / supplier").pack(side="left")

        wrap, self.tree = make_tree(
            self, ["Delivery ID", "Date", "Product", "Supplier",
                   "Received By", "Qty Received", "Total Cost (₱)"])
        wrap.pack(fill="both", expand=True, padx=28)

        bf = tk.Frame(self, bg=BG)
        bf.pack(fill="x", padx=28, pady=10)
        make_btn(bf, "🗑  Delete", self._delete, danger=True).pack(side="left")
        tk.Label(bf, text="Note: deleting a delivery does not adjust stock.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(side="left", padx=10)

        self._refresh()

    def _refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        q = self.q.get().strip().lower()
        with db_conn() as c:
            rows = c.execute("""
                SELECT d.delivery_id, d.delivery_date,
                       COALESCE(p.product_name, '—'),
                       COALESCE(s.supplier_name, '—'),
                       COALESCE(st.first_name||' '||st.last_name, '—'),
                       d.quantity_received, d.total_cost
                FROM delivery d
                LEFT JOIN product  p  ON d.product_id  = p.product_id
                LEFT JOIN supplier s  ON d.supplier_id = s.supplier_id
                LEFT JOIN staff    st ON d.staff_id    = st.staff_id
                ORDER BY d.delivery_date DESC
            """).fetchall()
        for r in rows:
            if q and q not in (r[2] or "").lower() \
                    and q not in (r[3] or "").lower():
                continue
            disp = list(r)
            disp[6] = f"₱{float(r[6] or 0):.2f}"
            self.tree.insert("", "end", values=disp)

    def _add(self):
        with db_conn() as c:
            products  = c.execute(
                "SELECT product_id, product_name FROM product "
                "ORDER BY product_name").fetchall()
            suppliers = c.execute(
                "SELECT supplier_id, supplier_name FROM supplier "
                "ORDER BY supplier_name").fetchall()
            staff     = c.execute(
                "SELECT staff_id, first_name||' '||last_name "
                "FROM staff ORDER BY last_name").fetchall()

        if not products:
            messagebox.showwarning("No Products",
                                   "Add products before recording a delivery.")
            return
        if not suppliers:
            messagebox.showwarning("No Suppliers",
                                   "Add suppliers before recording a delivery.")
            return

        prod_opts = [f"{p[0]}  –  {p[1]}" for p in products]
        sup_opts  = [f"{s[0]}  –  {s[1]}" for s in suppliers]
        stf_opts  = ([f"{s[0]}  –  {s[1]}" for s in staff]
                     if staff else ["(No staff added)"])

        fields = [
            ("Product",                 "product",  "combo", prod_opts),
            ("Supplier",                "supplier", "combo", sup_opts),
            ("Received By (Staff)",     "staff",    "combo", stf_opts),
            ("Quantity Received",       "qty",      "entry", []),
            ("Cost per Unit (₱)",       "cost_per", "entry", []),
            ("Delivery Date (YYYY-MM-DD)", "date",  "entry", []),
        ]

        def save(d):
            if not d["product"]:
                raise ValueError("Please select a product.")
            if not d["supplier"]:
                raise ValueError("Please select a supplier.")
            if not d["qty"]:
                raise ValueError("Quantity is required.")

            pid = d["product"].split("–")[0].strip().split()[0]
            sid = d["supplier"].split("–")[0].strip().split()[0]
            qty = int(d["qty"])
            if qty <= 0:
                raise ValueError("Quantity must be greater than 0.")
            cost_per = float(d["cost_per"] or 0)
            total    = qty * cost_per
            date_v   = d["date"] or datetime.now().strftime("%Y-%m-%d")
            did      = gen_id("DEL")

            stf_id = None
            if "–" in d["staff"]:
                stf_id = d["staff"].split("–")[0].strip().split()[0]

            with db_conn() as c:
                c.execute("INSERT INTO delivery VALUES(?,?,?,?,?,?,?)",
                          (did, date_v, qty, total, sid, pid, stf_id))
                c.execute(
                    "UPDATE product SET stock_quantity = stock_quantity + ? "
                    "WHERE product_id=?", (qty, pid))
            self._refresh()

        FormDialog(self.winfo_toplevel(), "Record New Delivery", fields, save,
                   {"date": datetime.now().strftime("%Y-%m-%d")})

    def _delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Nothing Selected",
                                   "Select a delivery to delete.")
            return
        did = self.tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Delete Delivery",
                                   "Delete this delivery record?\n"
                                   "Stock quantity will NOT be adjusted."):
            return
        with db_conn() as c:
            c.execute("DELETE FROM delivery WHERE delivery_id=?", (did,))
        self._refresh()


# ══════════════════════════════════════════════════════════════════
#  REPORTS
# ══════════════════════════════════════════════════════════════════

class ReportsPage(Page):
    def __init__(self, master):
        super().__init__(master)
        self.page_header("Reports", "Sample Queries & Analytics")
        self._build()

    def _build(self):
        # ── Query buttons ──
        btn_frame = tk.Frame(self, bg=PANEL)
        btn_frame.pack(fill="x", padx=28)

        queries = [
            ("①  Products In Stock",       self._q1),
            ("②  Deliveries by Supplier",  self._q2),
            ("③  Sales by Product",        self._q3),
            ("④  Low Stock Items",         self._q4),
            ("⑤  Total Sold per Product",  self._q5),
        ]
        for lbl, cmd in queries:
            b = tk.Button(btn_frame, text=lbl, command=cmd,
                          bg=PANEL, fg=DARK, relief="flat", bd=0,
                          font=("Segoe UI", 9, "bold"),
                          cursor="hand2", padx=12, pady=10,
                          activebackground=ACCENT,
                          activeforeground=DARK, anchor="w")
            b.pack(side="left", padx=1)
            b.bind("<Enter>", lambda e, b=b: b.configure(bg=ACCENT))
            b.bind("<Leave>", lambda e, b=b: b.configure(bg=PANEL))

        # ── Status label ──
        self.status_lbl = tk.Label(
            self, text="← Select a report above to view results.",
            bg=BG, fg=MUTED, font=("Segoe UI", 10))
        self.status_lbl.pack(anchor="w", padx=28, pady=(10, 4))

        # ── Tree container ──
        self.tree_host = tk.Frame(self, bg=BG)
        self.tree_host.pack(fill="both", expand=True, padx=28, pady=(0, 16))

    def _show(self, cols, rows, title):
        for w in self.tree_host.winfo_children():
            w.destroy()
        self.status_lbl.configure(
            text=f"{title}   ·   {len(rows)} result(s) found", fg=DARK)
        wrap, tree = make_tree(self.tree_host, cols)
        wrap.pack(fill="both", expand=True)
        for r in rows:
            disp = []
            for v in r:
                if isinstance(v, float):
                    disp.append(f"₱{v:.2f}")
                else:
                    disp.append(v if v is not None else "—")
            tree.insert("", "end", values=disp)

    # ── 1. Products in stock ──────────────────────────────────────
    def _q1(self):
        with db_conn() as c:
            rows = c.execute("""
                SELECT product_name, category, stock_quantity
                FROM product
                WHERE stock_quantity > 0
                ORDER BY product_name
            """).fetchall()
        self._show(["Product Name", "Category", "Stock Qty"], rows,
                   "① All Products Currently In Stock")

    # ── 2. Deliveries by supplier ─────────────────────────────────
    def _q2(self):
        with db_conn() as c:
            names = [r[0] for r in c.execute(
                "SELECT supplier_name FROM supplier ORDER BY supplier_name"
            ).fetchall()]
        if not names:
            messagebox.showinfo("No Suppliers", "No suppliers found.")
            return
        name = picker_dialog(self.winfo_toplevel(), "Select Supplier", names)
        if not name:
            return
        with db_conn() as c:
            rows = c.execute("""
                SELECT d.delivery_date, p.product_name, d.quantity_received
                FROM delivery d
                JOIN supplier s ON d.supplier_id = s.supplier_id
                JOIN product  p ON d.product_id  = p.product_id
                WHERE s.supplier_name = ?
                ORDER BY d.delivery_date DESC
            """, (name,)).fetchall()
        self._show(["Delivery Date", "Product Name", "Qty Received"], rows,
                   f"② Deliveries from  {name}")

    # ── 3. Sales by product ───────────────────────────────────────
    def _q3(self):
        with db_conn() as c:
            prods = c.execute(
                "SELECT product_id, product_name FROM product "
                "ORDER BY product_name").fetchall()
        if not prods:
            messagebox.showinfo("No Products", "No products found.")
            return
        opts = [f"{p[0]}  –  {p[1]}" for p in prods]
        sel  = picker_dialog(self.winfo_toplevel(), "Select Product", opts)
        if not sel:
            return
        pid   = sel.split("–")[0].strip().split()[0]
        pname = sel.split("–")[1].strip()
        with db_conn() as c:
            rows = c.execute("""
                SELECT sale_date, quantity_sold, total_amount
                FROM sales
                WHERE product_id = ?
                ORDER BY sale_date DESC
            """, (pid,)).fetchall()
        self._show(["Sale Date", "Qty Sold", "Total Amount (₱)"], rows,
                   f"③ Sales for  {pname}")

    # ── 4. Low stock items ────────────────────────────────────────
    def _q4(self):
        with db_conn() as c:
            rows = c.execute("""
                SELECT product_name, category, brand, stock_quantity
                FROM product
                WHERE stock_quantity < 5
                ORDER BY stock_quantity ASC
            """).fetchall()
        self._show(["Product Name", "Category", "Brand", "Stock Qty"], rows,
                   "④ Low Stock Items  (quantity < 5)")

    # ── 5. Total sold per product ─────────────────────────────────
    def _q5(self):
        with db_conn() as c:
            rows = c.execute("""
                SELECT p.product_name,
                       SUM(s.quantity_sold)  AS total_sold,
                       SUM(s.total_amount)   AS total_revenue
                FROM sales   s
                JOIN product p ON s.product_id = p.product_id
                GROUP BY s.product_id, p.product_name
                ORDER BY total_sold DESC
            """).fetchall()
        self._show(["Product Name", "Total Qty Sold", "Total Revenue (₱)"], rows,
                   "⑤ Total Sold per Product  (highest → lowest)")


# ══════════════════════════════════════════════════════════════════
#  MAIN APPLICATION WINDOW
# ══════════════════════════════════════════════════════════════════

class App(tk.Tk):
    NAV_ITEMS = [
        ("🏠", "Dashboard",  DashboardPage),
        ("📦", "Products",   ProductsPage),
        ("🚚", "Suppliers",  SuppliersPage),
        ("👤", "Staff",      StaffPage),
        ("🛒", "Sales",      SalesPage),
        ("📬", "Deliveries", DeliveryPage),
        ("📊", "Reports",    ReportsPage),
    ]

    def __init__(self):
        super().__init__()
        self.title("GroceryMS  –  Inventory Management System")
        self.geometry("1140x700")
        self.minsize(920, 620)
        self.configure(bg=PANEL)

        # Global ttk style
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TCombobox", fieldbackground=WHITE,
                    background=WHITE, foreground=TEXT,
                    arrowcolor=DARK, selectbackground=ACCENT)
        s.map("TCombobox", fieldbackground=[("readonly", WHITE)])

        self._build_ui()
        self._show_page(0)

    # ── Layout ────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Sidebar ──
        self.sidebar = tk.Frame(self, bg=DARK, width=188)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo = tk.Frame(self.sidebar, bg=DARK, height=88)
        logo.pack(fill="x")
        logo.pack_propagate(False)

        inner = tk.Frame(logo, bg=DARK)
        inner.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(inner, text="🛒", bg=DARK, fg=WHITE,
                 font=("Segoe UI", 22)).pack(side="left", padx=(0, 8))
        txt_col = tk.Frame(inner, bg=DARK)
        txt_col.pack(side="left")
        tk.Label(txt_col, text="GroceryMS", bg=DARK, fg=WHITE,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(txt_col, text="Inventory System", bg=DARK, fg=ACCENT,
                 font=("Segoe UI", 7)).pack(anchor="w")

        # Divider
        tk.Frame(self.sidebar, bg=ACCENT, height=1).pack(fill="x", padx=16, pady=2)

        # Nav buttons
        self.nav_buttons = []
        for i, (icon, name, _) in enumerate(self.NAV_ITEMS):
            btn = tk.Button(
                self.sidebar,
                text=f"  {icon}   {name}",
                anchor="w", relief="flat", bd=0,
                bg=DARK, fg=WHITE,
                font=("Segoe UI", 10),
                cursor="hand2",
                padx=18, pady=11,
                activebackground=ACCENT,
                activeforeground=DARK,
                command=lambda i=i: self._show_page(i)
            )
            btn.pack(fill="x", pady=1)
            self.nav_buttons.append(btn)

        # Footer
        tk.Frame(self.sidebar, bg=ACCENT, height=1).pack(
            fill="x", padx=16, side="bottom", pady=4)
        tk.Label(self.sidebar, text="v1.0  ·  SQLite",
                 bg=DARK, fg=ACCENT,
                 font=("Segoe UI", 7)).pack(side="bottom", pady=2)

        # ── Main content area ──
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        self._active_page = None

    # ── Page switching ────────────────────────────────────────────
    def _show_page(self, idx):
        # Update nav highlights
        for i, btn in enumerate(self.nav_buttons):
            if i == idx:
                btn.configure(bg=ACCENT, fg=DARK,
                               font=("Segoe UI", 10, "bold"))
            else:
                btn.configure(bg=DARK, fg=WHITE,
                               font=("Segoe UI", 10))

        # Swap page
        if self._active_page:
            self._active_page.destroy()

        PageClass = self.NAV_ITEMS[idx][2]
        self._active_page = PageClass(self.content)
        self._active_page.pack(fill="both", expand=True)


# ══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    init_db()
    app = App()
    app.mainloop()
