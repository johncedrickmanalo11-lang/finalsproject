import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import pymysql
from pymysql import Error

# ================= COLORS & THEME =================
COLOR_SIDEBAR = "#1E293B"       
COLOR_SIDEBAR_HOVER = "#334155" 
COLOR_BG = "#F1F5F9"            
COLOR_CARD = "#FFFFFF"          
COLOR_PRIMARY = "#3B82F6"       
COLOR_SUCCESS = "#10B981"       
COLOR_DANGER = "#EF4444"        
COLOR_WARNING = "#F59E0B"       
COLOR_TEXT_MAIN = "#0F172A"     
COLOR_TEXT_MUTED = "#64748B"    
COLOR_BORDER = "#E2E8F0"        
COLOR_PURPLE = "#8B5CF6"        

# ================= CONFIGURATION (Strict Blocks) =================
BLOCK_CONFIG = {
    "1st Year": ["1101", "1102", "1201", "1202"],
    "2nd Year": ["2101", "2102", "2201", "2202"],
    "3rd Year": ["3101 SM", "3201 SM", "3101 BA", "3201 BA"],
    "4th Year": ["4101 BA", "4201 BA"]
}

# ================= DATABASE =================
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASS = ''      
DB_NAME = 'studentmanagement'

class DatabaseConnection:
    def __init__(self):
        self.init_db()

    def get_connection(self):
        try:
            return pymysql.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASS,
                database=DB_NAME, charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        except Error as e:
            messagebox.showerror("Database Error", f"Cannot connect to MySQL: {e}")
            return None

    def init_db(self):
        try:
            conn_root = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS)
            with conn_root.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            conn_root.close()

            conn = self.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("""CREATE TABLE IF NOT EXISTS students (
                            id INT AUTO_INCREMENT PRIMARY KEY, srcode VARCHAR(50) UNIQUE,
                            name VARCHAR(255), year_level VARCHAR(50), block VARCHAR(50),
                            course VARCHAR(100), username VARCHAR(100), password VARCHAR(100))""")
                    
                    # Teacher subject is managed by Admin (Comma separated string for simplicity)
                    cur.execute("""CREATE TABLE IF NOT EXISTS teachers (
                            id INT AUTO_INCREMENT PRIMARY KEY, srcode VARCHAR(50) UNIQUE,
                            name VARCHAR(255), subject TEXT, username VARCHAR(100), password VARCHAR(100))""")

                    cur.execute("""CREATE TABLE IF NOT EXISTS admins (
                            id INT AUTO_INCREMENT PRIMARY KEY, srcode VARCHAR(50) UNIQUE,
                            name VARCHAR(255) DEFAULT 'Administrator', username VARCHAR(100) UNIQUE, 
                            password VARCHAR(100))""")
                    cur.execute("INSERT IGNORE INTO admins (srcode, username, password) VALUES ('ADM-001', 'admin', 'admin')")

                    # edit_count tracks how many times a teacher edited a grade
                    cur.execute("""CREATE TABLE IF NOT EXISTS enrollments (
                            id INT AUTO_INCREMENT PRIMARY KEY, student_id INT, teacher_id INT,
                            subject_name VARCHAR(255), grade VARCHAR(10) DEFAULT 'N/A',
                            edit_count INT DEFAULT 0)""")
                    
                    # Notifications for drop status
                    cur.execute("""CREATE TABLE IF NOT EXISTS notifications (
                            id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, message TEXT,
                            is_read BOOLEAN DEFAULT FALSE, date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

                    cur.execute("""CREATE TABLE IF NOT EXISTS announcements (
                            id INT AUTO_INCREMENT PRIMARY KEY, author_name VARCHAR(255),
                            title VARCHAR(255), message TEXT, target VARCHAR(50),
                            target_value VARCHAR(50), date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

                    cur.execute("""CREATE TABLE IF NOT EXISTS drop_requests (
                            id INT AUTO_INCREMENT PRIMARY KEY, student_id INT, student_name VARCHAR(255),
                            subject VARCHAR(255), reason TEXT, status VARCHAR(50) DEFAULT 'Pending')""")
                conn.commit()
                conn.close()
        except Error as e:
            pass

# ================= UI HELPERS =================
def setup_styles():
    style = ttk.Style()
    style.theme_use("clam")
    # Clean, modern Treeview
    style.configure("Treeview", background="white", foreground=COLOR_TEXT_MAIN, 
                    rowheight=30, fieldbackground="white", borderwidth=0, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", background="#F1F5F9", foreground=COLOR_TEXT_MAIN, 
                    font=("Segoe UI", 10, "bold"), relief="flat")
    style.map("Treeview", background=[('selected', "#DBEAFE")], foreground=[('selected', COLOR_TEXT_MAIN)])
    
    # Tabs
    style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
    style.configure("TNotebook.Tab", background="#E2E8F0", padding=[20, 10], font=("Segoe UI", 10, "bold"))
    style.map("TNotebook.Tab", background=[("selected", "white")], foreground=[("selected", COLOR_PRIMARY)])

def create_card(parent, title=None):
    card_frame = tk.Frame(parent, bg=COLOR_CARD, bd=1, relief="solid")
    card_frame.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
    if title:
        header = tk.Frame(card_frame, bg="white", padx=20, pady=15)
        header.pack(fill='x')
        tk.Label(header, text=title, font=("Segoe UI", 14, "bold"), bg="white", fg=COLOR_TEXT_MAIN).pack(anchor='w')
        tk.Frame(card_frame, bg=COLOR_BORDER, height=1).pack(fill='x') 
    content = tk.Frame(card_frame, bg="white", padx=25, pady=25)
    content.pack(fill='both', expand=True)
    return card_frame, content

def create_sidebar_btn(parent, text, icon, cmd):
    btn = tk.Button(parent, text=f"  {icon}   {text}", command=cmd, 
                    font=("Segoe UI", 11), bg=COLOR_SIDEBAR, fg="white", 
                    bd=0, activebackground=COLOR_SIDEBAR_HOVER, activeforeground="white", 
                    anchor="w", padx=25, pady=15, cursor="hand2")
    btn.pack(fill='x', pady=2)
    btn.bind("<Enter>", lambda e: btn.config(bg=COLOR_SIDEBAR_HOVER))
    btn.bind("<Leave>", lambda e: btn.config(bg=COLOR_SIDEBAR))
    return btn

def autosize_tree(tree):
    font = tkfont.Font(family="Segoe UI", size=10) 
    for col in tree['columns']:
        header_text = tree.heading(col, 'text')
        max_w = font.measure(header_text) + 20 
        for item in tree.get_children():
            val = str(tree.set(item, col))
            w = font.measure(val) + 20
            if w > max_w: max_w = w
        tree.column(col, width=min(max_w, 500), stretch=False)
