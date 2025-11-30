import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import pymysql
from pymysql import Error
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

# ================= DATABASE CONNECTION SETTINGS =================
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASS = ''      
DB_NAME = 'student_management'

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

# Fonts
FONT_BRAND = ("Segoe UI", 24, "bold")
FONT_H1 = ("Segoe UI", 18, "bold")
FONT_H2 = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 9)

# Configuration
BLOCK_CONFIG = {
    "1st Year": ["1101", "1102", "1201", "1202"],
    "2nd Year": ["2101", "2102", "2201", "2202"],
    "3rd Year": ["3101 SM", "3201 SM", "3101 BA", "3201 BA"],
    "4th Year": ["4101 BA", "4201 BA"]
}

# Unicode Icons
ICON_DASHBOARD = "📊"
ICON_USERS = "👥"
ICON_TEACHERS = "👨‍🏫"
ICON_REQ = "📩"
ICON_GRADES = "🎓"
ICON_LOGOUT = "🚪"
ICON_USER = "👤"
ICON_BELL = "🔔"
ICON_MEGAPHONE = "📢"

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
                    
                    cur.execute("""CREATE TABLE IF NOT EXISTS teachers (
                            id INT AUTO_INCREMENT PRIMARY KEY, srcode VARCHAR(50) UNIQUE,
                            name VARCHAR(255), subject TEXT, username VARCHAR(100), password VARCHAR(100))""")

                    cur.execute("""CREATE TABLE IF NOT EXISTS admins (
                            id INT AUTO_INCREMENT PRIMARY KEY, srcode VARCHAR(50) UNIQUE,
                            name VARCHAR(255) DEFAULT 'Administrator', username VARCHAR(100) UNIQUE, 
                            password VARCHAR(100))""")
                    cur.execute("INSERT IGNORE INTO admins (srcode, username, password) VALUES ('ADM-001', 'admin', 'admin')")

                    cur.execute("""CREATE TABLE IF NOT EXISTS enrollments (
                            id INT AUTO_INCREMENT PRIMARY KEY, student_id INT, teacher_id INT,
                            subject_name VARCHAR(255), grade VARCHAR(10) DEFAULT 'N/A',
                            edit_count INT DEFAULT 0)""")
                    
                    try:
                        cur.execute("SELECT edit_count FROM enrollments LIMIT 1")
                    except:
                        cur.execute("ALTER TABLE enrollments ADD COLUMN edit_count INT DEFAULT 0")

                    cur.execute("""CREATE TABLE IF NOT EXISTS announcements (
                            id INT AUTO_INCREMENT PRIMARY KEY, author_name VARCHAR(255),
                            title VARCHAR(255), message TEXT, target VARCHAR(50),
                            target_value VARCHAR(50), date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

                    cur.execute("""CREATE TABLE IF NOT EXISTS drop_requests (
                            id INT AUTO_INCREMENT PRIMARY KEY, student_id INT, student_name VARCHAR(255),
                            subject VARCHAR(255), reason TEXT, status VARCHAR(50) DEFAULT 'Pending')""")
                    
                    cur.execute("""CREATE TABLE IF NOT EXISTS notifications (
                            id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, message TEXT,
                            is_read BOOLEAN DEFAULT FALSE, date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
                conn.commit()
                conn.close()
        except Error as e:
            messagebox.showerror("Init Error", f"Error initializing database: {e}")

class StudentManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("SMS - Enterprise Edition")
        self.root.geometry("1366x768")
        self.root.configure(bg=COLOR_BG)
        self.db = DatabaseConnection()
        self.current_user = None
        self.setup_styles()
        self.show_welcome_screen()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=COLOR_TEXT_MAIN, 
                        rowheight=35, fieldbackground="white", font=FONT_BODY, borderwidth=0)
        style.configure("Treeview.Heading", background="#F8FAFC", foreground=COLOR_TEXT_MAIN, 
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Treeview", background=[('selected', "#E0F2FE")], foreground=[('selected', COLOR_PRIMARY)])
        style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background="#E2E8F0", padding=[20, 10], font=FONT_BOLD)
        style.map("TNotebook.Tab", background=[("selected", "white")], foreground=[("selected", COLOR_PRIMARY)])

    def clear_screen(self):
        for widget in self.root.winfo_children(): widget.destroy()

    # ================= MODERN UI HELPERS =================
    def create_card(self, parent, title=None):
        card_frame = tk.Frame(parent, bg=COLOR_CARD, bd=1, relief="solid")
        card_frame.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        if title:
            header = tk.Frame(card_frame, bg="white", padx=20, pady=15)
            header.pack(fill='x')
            tk.Label(header, text=title, font=FONT_H2, bg="white", fg=COLOR_TEXT_MAIN).pack(anchor='w')
            tk.Frame(card_frame, bg=COLOR_BORDER, height=1).pack(fill='x') 
        content = tk.Frame(card_frame, bg="white", padx=25, pady=25)
        content.pack(fill='both', expand=True)
        return card_frame, content

    def create_stat_tile(self, parent, title, value, icon, color):
        tile = tk.Frame(parent, bg="white", width=220, height=100)
        tile.pack_propagate(False)
        tk.Frame(tile, bg=color, width=5).pack(side='left', fill='y') 
        content = tk.Frame(tile, bg="white", padx=15)
        content.pack(side='left', fill='both', expand=True)
        tk.Label(content, text=title, font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT_MUTED, bg="white").pack(anchor='nw', pady=(15, 0))
        tk.Label(content, text=str(value), font=("Segoe UI", 24, "bold"), fg=COLOR_TEXT_MAIN, bg="white").pack(anchor='nw')
        tk.Label(tile, text=icon, font=("Segoe UI", 24), bg="white", fg=color).pack(side='right', padx=15)
        return tile

    def create_sidebar_btn(self, parent, text, icon, cmd):
        btn = tk.Button(parent, text=f"  {icon}   {text}", command=cmd, 
                        font=("Segoe UI", 11), bg=COLOR_SIDEBAR, fg="white", 
                        bd=0, activebackground=COLOR_SIDEBAR_HOVER, activeforeground="white", 
                        anchor="w", padx=25, pady=15, cursor="hand2")
        btn.pack(fill='x', pady=1)
        btn.bind("<Enter>", lambda e: btn.config(bg=COLOR_SIDEBAR_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=COLOR_SIDEBAR))
        return btn

    def autosize_tree(self, tree):
        font = tkfont.Font(family="Segoe UI", size=10) 
        for col in tree['columns']:
            header_text = tree.heading(col, 'text')
            max_w = font.measure(header_text) + 30 
            for item in tree.get_children():
                val = str(tree.set(item, col))
                w = font.measure(val) + 30
                if w > max_w: max_w = w
            tree.column(col, width=min(max_w, 800), stretch=False)

    # ================= AUTHENTICATION =================
    def show_welcome_screen(self):
        self.clear_screen()
        left_panel = tk.Frame(self.root, bg=COLOR_SIDEBAR)
        left_panel.place(relx=0, rely=0, relwidth=0.4, relheight=1)
        right_panel = tk.Frame(self.root, bg="white")
        right_panel.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)

        tk.Label(left_panel, text="SMS", font=("Segoe UI", 80, "bold"), fg="white", bg=COLOR_SIDEBAR).place(relx=0.5, rely=0.4, anchor='center')
        tk.Label(left_panel, text="STUDENT MANAGEMENT\nSYSTEM", font=("Segoe UI", 16, "bold"), fg="#94A3B8", bg=COLOR_SIDEBAR, justify='center').place(relx=0.5, rely=0.55, anchor='center')

        container = tk.Frame(right_panel, bg="white")
        container.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(container, text="Welcome Back", font=FONT_BRAND, fg=COLOR_TEXT_MAIN, bg="white").pack(pady=(0, 10))
        
        for role, color in [("Student", COLOR_PRIMARY), ("Teacher", COLOR_SUCCESS), ("Admin", COLOR_TEXT_MAIN)]:
            tk.Button(container, text=f"Login as {role}", command=lambda r=role: self.show_login(r),
                      font=FONT_BOLD, bg="white", fg=color, width=30, pady=12, relief="flat",
                      bd=1, highlightbackground=color, highlightthickness=1, cursor="hand2").pack(pady=8)

    def show_login(self, role):
        self.clear_screen()
        bg_frame = tk.Frame(self.root, bg=COLOR_BG)
        bg_frame.pack(fill='both', expand=True)
        
        card = tk.Frame(bg_frame, bg="white", padx=50, pady=50, relief="solid", bd=1)
        card.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(card, text=f"{role} Sign In", font=FONT_H1, bg="white", fg=COLOR_TEXT_MAIN).pack(pady=(0, 30))
        
        tk.Label(card, text="Username", bg="white", fg=COLOR_TEXT_MUTED, font=FONT_SMALL).pack(anchor='w')
        u_ent = tk.Entry(card, width=35, font=("Segoe UI", 11), relief="solid", bd=1, bg="#F8FAFC")
        u_ent.pack(pady=(5, 15), ipady=5)
        
        tk.Label(card, text="Password", bg="white", fg=COLOR_TEXT_MUTED, font=FONT_SMALL).pack(anchor='w')
        p_ent = tk.Entry(card, width=35, font=("Segoe UI", 11), show='•', relief="solid", bd=1, bg="#F8FAFC")
        p_ent.pack(pady=(5, 10), ipady=5)
        
        tk.Button(card, text="LOGIN", command=lambda: self.login_action(role, u_ent.get(), p_ent.get()), 
                  bg=COLOR_PRIMARY, fg="white", font=FONT_BOLD, width=34, pady=10, relief='flat', cursor="hand2").pack()
        
        tk.Button(card, text="Forgot Password?", command=lambda: self.show_forgot_password(role), 
                  bg="white", fg=COLOR_DANGER, bd=0, font=FONT_SMALL, cursor="hand2").pack(pady=(10, 5))

        if role != "Admin":
            tk.Button(card, text="Create an Account", command=lambda: self.show_register(role), 
                      bg="white", fg=COLOR_PRIMARY, bd=0, font=FONT_SMALL, cursor="hand2").pack(pady=(5, 0))
        
        tk.Button(card, text="← Back to Home", command=self.show_welcome_screen, 
                  bg="white", fg=COLOR_TEXT_MUTED, bd=0, cursor="hand2").pack(pady=(10,0))

    def show_forgot_password(self, role):
        self.clear_screen()
        bg_frame = tk.Frame(self.root, bg=COLOR_BG)
        bg_frame.pack(fill='both', expand=True)
        
        card = tk.Frame(bg_frame, bg="white", padx=50, pady=50, relief="solid", bd=1)
        card.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(card, text=f"Reset Password ({role})", font=FONT_H2, bg="white", fg=COLOR_TEXT_MAIN).pack(pady=(0, 20))
        
        v_frame = tk.Frame(card, bg="white")
        v_frame.pack(fill='x')
        
        tk.Label(v_frame, text="Username", bg="white", fg=COLOR_TEXT_MUTED, font=FONT_SMALL).pack(anchor='w')
        u_ent = tk.Entry(v_frame, width=35, font=FONT_BODY, relief="solid", bd=1, bg="#F8FAFC"); u_ent.pack(pady=5, ipady=5)
        
        tk.Label(v_frame, text="SR Code (ID Number)", bg="white", fg=COLOR_TEXT_MUTED, font=FONT_SMALL).pack(anchor='w')
        s_ent = tk.Entry(v_frame, width=35, font=FONT_BODY, relief="solid", bd=1, bg="#F8FAFC"); s_ent.pack(pady=5, ipady=5)

        r_frame = tk.Frame(card, bg="white")
        
        tk.Label(r_frame, text="New Password", bg="white", fg=COLOR_TEXT_MUTED, font=FONT_SMALL).pack(anchor='w')
        new_p = tk.Entry(r_frame, width=35, font=FONT_BODY, show="•", relief="solid", bd=1, bg="#F8FAFC"); new_p.pack(pady=5, ipady=5)
        
        tk.Label(r_frame, text="Confirm Password", bg="white", fg=COLOR_TEXT_MUTED, font=FONT_SMALL).pack(anchor='w')
        con_p = tk.Entry(r_frame, width=35, font=FONT_BODY, show="•", relief="solid", bd=1, bg="#F8FAFC"); con_p.pack(pady=5, ipady=5)

        def verify_user():
            u, s = u_ent.get(), s_ent.get()
            table = "admins" if role == "Admin" else ("teachers" if role == "Teacher" else "students")
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute(f"SELECT id FROM {table} WHERE username=%s AND srcode=%s", (u, s))
                    res = cur.fetchone()
                    if res:
                        self.reset_user_id = res['id']
                        v_frame.pack_forget(); verify_btn.pack_forget()
                        r_frame.pack(fill='x'); update_btn.pack(pady=10)
                    else:
                        messagebox.showerror("Error", "Account not found or SR Code incorrect.")
                conn.close()

        def update_password():
            np, cp = new_p.get(), con_p.get()
            if np != cp: return messagebox.showerror("Error", "Passwords do not match")
            table = "admins" if role == "Admin" else ("teachers" if role == "Teacher" else "students")
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute(f"UPDATE {table} SET password=%s WHERE id=%s", (np, self.reset_user_id))
                    conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Password updated successfully!")
                self.show_login(role)

        verify_btn = tk.Button(card, text="VERIFY ACCOUNT", command=verify_user, bg=COLOR_PRIMARY, fg="white", font=FONT_BOLD, width=34, pady=10, relief='flat')
        verify_btn.pack(pady=10)
        update_btn = tk.Button(card, text="UPDATE PASSWORD", command=update_password, bg=COLOR_SUCCESS, fg="white", font=FONT_BOLD, width=34, pady=10, relief='flat')
        tk.Button(card, text="Cancel", command=lambda: self.show_login(role), bg="white", fg="gray", bd=0).pack(pady=5)

    def show_register(self, role):
        self.clear_screen()
        bg = tk.Frame(self.root, bg=COLOR_BG)
        bg.pack(fill='both', expand=True)
        card, content = self.create_card(bg, f"Create {role} Account")
        card.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.4)
        
        self.reg_data = {}
        fields = [("SR Code / ID", "srcode"), ("Full Name", "name"), ("Username", "username"), ("Password", "password")]
        if role == "Student": fields.insert(2, ("Course", "course"))

        for i, (lbl, key) in enumerate(fields):
            tk.Label(content, text=lbl, bg="white", fg=COLOR_TEXT_MUTED, font=FONT_SMALL).pack(anchor='w', pady=(10,0))
            ent = tk.Entry(content, relief="solid", bd=1, bg="#F8FAFC", font=FONT_BODY)
            ent.pack(fill='x', ipady=4)
            self.reg_data[key] = ent
        
        if role == "Student":
            tk.Label(content, text="Year Level", bg="white", fg=COLOR_TEXT_MUTED).pack(anchor='w', pady=(10,0))
            yc = ttk.Combobox(content, values=list(BLOCK_CONFIG.keys()), state='readonly')
            yc.pack(fill='x', ipady=4); self.reg_data['year'] = yc
            tk.Label(content, text="Block", bg="white", fg=COLOR_TEXT_MUTED).pack(anchor='w', pady=(10,0))
            bc = ttk.Combobox(content, state='readonly')
            bc.pack(fill='x', ipady=4); self.reg_data['block'] = bc
            yc.bind('<<ComboboxSelected>>', lambda e: (bc.config(values=BLOCK_CONFIG.get(yc.get(), [])), bc.current(0) if BLOCK_CONFIG.get(yc.get()) else None))
            
        tk.Button(content, text="REGISTER", command=lambda: self.register_action(role), bg=COLOR_SUCCESS, fg="white", font=FONT_BOLD, pady=10, relief='flat').pack(fill='x', pady=20)
        tk.Button(content, text="Cancel", command=lambda: self.show_login(role), bg="white", fg="gray", bd=0).pack()

    def register_action(self, role):
        data = {k: v.get() for k, v in self.reg_data.items()}
        if not all(data.values()): return messagebox.showerror("Error", "All fields are required")
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                table = "students" if role == "Student" else "teachers"
                cur.execute(f"SELECT id FROM {table} WHERE srcode=%s", (data['srcode'],))
                if cur.fetchone(): return messagebox.showerror("Error", "SR Code already exists!")
                if role == "Student":
                    cur.execute("INSERT INTO students (srcode, name, year_level, block, course, username, password) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                             (data['srcode'], data['name'], data['year'], data['block'], data['course'], data['username'], data['password']))
                else:
                    cur.execute("INSERT INTO teachers (srcode, name, subject, username, password) VALUES (%s,%s,%s,%s,%s)",
                             (data['srcode'], data['name'], "", data['username'], data['password']))
                conn.commit()
                messagebox.showinfo("Success", "Account created successfully")
                self.show_login(role)
        except Error as e: messagebox.showerror("Database Error", str(e))
        finally: conn.close()

    def login_action(self, role, u, p):
        conn = self.db.get_connection()
        if not conn: return
        if role == "Admin": tbl = "admins"
        elif role == "Teacher": tbl = "teachers"
        else: tbl = "students"
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {tbl} WHERE username=%s AND password=%s", (u, p))
                res = cur.fetchone()
                if res:
                    self.current_user = res
                    self.current_user['role'] = role
                    if role == "Admin": self.admin_dashboard()
                    elif role == "Teacher": self.teacher_dashboard()
                    else: self.student_dashboard()
                else:
                    messagebox.showerror("Error", "Invalid Credentials")
        finally: conn.close()

    # ================= DASHBOARD =================
    def setup_dashboard_layout(self):
        self.clear_screen()
        header = tk.Frame(self.root, bg="white", height=70, bd=1, relief="solid")
        header.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        logo_area = tk.Frame(header, bg=COLOR_SIDEBAR, width=250, height=70)
        logo_area.pack(side='left', fill='y')
        logo_area.pack_propagate(False)
        tk.Label(logo_area, text="SMS Portal", font=("Segoe UI", 16, "bold"), fg="white", bg=COLOR_SIDEBAR).pack(expand=True)
        
        user_info = tk.Frame(header, bg="white")
        user_info.pack(side='right', padx=30)
        tk.Label(user_info, text=f"{self.current_user['name']}", font=FONT_BOLD, fg=COLOR_TEXT_MAIN, bg="white").pack(anchor='e')
        tk.Label(user_info, text=f"{self.current_user['role']} | {self.current_user.get('srcode', '')}", font=FONT_SMALL, fg=COLOR_TEXT_MUTED, bg="white").pack(anchor='e')
        
        self.sidebar = tk.Frame(self.root, bg=COLOR_SIDEBAR, width=250)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)
        
        self.main_container = tk.Frame(self.root, bg=COLOR_BG)
        self.main_container.pack(side='right', fill='both', expand=True)
        self.main = tk.Frame(self.main_container, bg=COLOR_BG, padx=30, pady=30)
        self.main.pack(fill='both', expand=True)
        
        self.create_sidebar_btn(self.sidebar, "Logout", ICON_LOGOUT, self.show_welcome_screen).pack(side='bottom', fill='x', pady=20)

    # ================= ADMIN DASHBOARD =================
    def admin_dashboard(self):
        self.setup_dashboard_layout()
        self.create_sidebar_btn(self.sidebar, "Overview", ICON_DASHBOARD, lambda: self.switch_admin_tab(0))
        self.create_sidebar_btn(self.sidebar, "Students", ICON_USERS, lambda: self.switch_admin_tab(2))
        self.create_sidebar_btn(self.sidebar, "Teachers", ICON_TEACHERS, lambda: self.switch_admin_tab(3))
        self.create_sidebar_btn(self.sidebar, "Requests", ICON_REQ, lambda: self.switch_admin_tab(1))
        self.create_sidebar_btn(self.sidebar, "Post Update", ICON_MEGAPHONE, lambda: self.switch_admin_tab(4))
        
        self.admin_nb = ttk.Notebook(self.main)
        self.admin_nb.pack(fill='both', expand=True)
        
        self.admin_analytics_tab(self.admin_nb) 
        self.admin_drop_requests_tab(self.admin_nb) 
        self.admin_students_tab(self.admin_nb) 
        self.admin_teachers_tab(self.admin_nb) 
        self.admin_announce_tab(self.admin_nb) 
        
        style = ttk.Style()
        style.layout('TNotebook.Tab', []) 

    def switch_admin_tab(self, index):
        self.admin_nb.select(index)

    # ------------------ UPDATED ANALYTICS TAB ------------------
    def admin_analytics_tab(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG)
        nb.add(tab, text="Overview")
        
        # --- Top Statistics Tiles ---
        stats_frame = tk.Frame(tab, bg=COLOR_BG)
        stats_frame.pack(fill='x', pady=(0, 20))
        
        conn = self.db.get_connection()
        c_stud, c_teach, c_req, c_enroll = 0, 0, 0, 0
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) as c FROM students"); c_stud = cur.fetchone()['c']
                cur.execute("SELECT COUNT(*) as c FROM teachers"); c_teach = cur.fetchone()['c']
                cur.execute("SELECT COUNT(*) as c FROM drop_requests WHERE status='Pending'"); c_req = cur.fetchone()['c']
                cur.execute("SELECT COUNT(DISTINCT student_id) as c FROM enrollments"); c_enroll = cur.fetchone()['c']
            conn.close()
            
        self.create_stat_tile(stats_frame, "Total Students", c_stud, ICON_USERS, COLOR_PRIMARY).pack(side='left', padx=(0, 15))
        self.create_stat_tile(stats_frame, "Total Teachers", c_teach, ICON_TEACHERS, COLOR_SUCCESS).pack(side='left', padx=15)
        self.create_stat_tile(stats_frame, "Enrolled Students", c_enroll, ICON_GRADES, COLOR_PURPLE).pack(side='left', padx=15)
        self.create_stat_tile(stats_frame, "Pending Requests", c_req, ICON_REQ, COLOR_WARNING).pack(side='left', padx=15)

        # --- Graphs Section ---
        graphs_frame = tk.Frame(tab, bg=COLOR_BG)
        graphs_frame.pack(fill='both', expand=True)

        card1, content1 = self.create_card(graphs_frame, "Total Enrolled (By Year Level)")
        card1.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        card2, content2 = self.create_card(graphs_frame, "Number of Students per Block")
        card2.pack(side='left', fill='both', expand=True, padx=(10, 0))

        # --- Data Fetching ---
        year_data = {"1st Year": 0, "2nd Year": 0, "3rd Year": 0, "4th Year": 0}
        block_data = {}
        
        conn = self.db.get_connection()
        if conn:
            with conn.cursor() as cur:
                # Query 1: Enrolled students count grouped by Year Level (For Line Chart)
                cur.execute("""
                    SELECT s.year_level, COUNT(DISTINCT e.student_id) as c 
                    FROM enrollments e 
                    JOIN students s ON e.student_id = s.id 
                    GROUP BY s.year_level
                """)
                for r in cur.fetchall():
                    if r['year_level'] in year_data:
                        year_data[r['year_level']] = r['c']

                # Query 2: Student count grouped by Block (For Bar Graph)
                cur.execute("SELECT block, COUNT(*) as c FROM students GROUP BY block ORDER BY block")
                for r in cur.fetchall():
                    if r['block']: # Ensure block is not empty
                        block_data[r['block']] = r['c']
            conn.close()

        # --- Chart 1: Line Chart (Enrolled per Year) ---
        fig1, ax1 = plt.subplots(figsize=(5, 4))
        
        x_years = list(year_data.keys())
        y_counts = list(year_data.values())

        ax1.plot(x_years, y_counts, marker='o', linestyle='-', color=COLOR_PRIMARY, linewidth=2, markersize=8)
        
        ax1.set_ylabel("No. of Students")
        ax1.grid(True, linestyle='--', alpha=0.6)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        for i, v in enumerate(y_counts):
            ax1.text(i, v + 0.1, str(v), ha='center', fontweight='bold', color=COLOR_TEXT_MAIN)

        canvas1 = FigureCanvasTkAgg(fig1, master=content1)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill='both', expand=True)

        # --- Chart 2: Bar Graph (Students per Block) ---
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        
        if block_data:
            x_blocks = list(block_data.keys())
            y_students = list(block_data.values())
            
            bars = ax2.bar(x_blocks, y_students, color=COLOR_PURPLE, width=0.6)
            
            ax2.set_ylabel("Student Count")
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            
            plt.setp(ax2.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', fontsize=9)
            
            plt.subplots_adjust(bottom=0.2)
        else:
            ax2.text(0.5, 0.5, "No Student Data", ha='center', va='center')
        
        canvas2 = FigureCanvasTkAgg(fig2, master=content2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill='both', expand=True)
    # -----------------------------------------------------------

    def admin_students_tab(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab, text="Students")
        card, content = self.create_card(tab, "Student Directory")
        card.pack(fill='both', expand=True)
        
        controls = tk.Frame(content, bg="white")
        controls.pack(fill='x', pady=(0, 10))
        
        tk.Label(controls, text="Filter by Year:", bg="white", font=FONT_BOLD).pack(side='left')
        yr_filter = ttk.Combobox(controls, values=["All"] + list(BLOCK_CONFIG.keys()), state='readonly', width=15)
        yr_filter.current(0)
        yr_filter.pack(side='left', padx=10)
        
        tk.Label(controls, text="Filter by Block:", bg="white", font=FONT_BOLD).pack(side='left')
        blk_filter = ttk.Combobox(controls, values=["All"], state='readonly', width=15)
        blk_filter.current(0)
        blk_filter.pack(side='left', padx=10)
        
        def update_block_options(e):
            sel_yr = yr_filter.get()
            if sel_yr == "All": blk_filter.config(values=["All"])
            else: blk_filter.config(values=["All"] + BLOCK_CONFIG.get(sel_yr, []))
            blk_filter.current(0); load_students()
            
        yr_filter.bind('<<ComboboxSelected>>', update_block_options)
        blk_filter.bind('<<ComboboxSelected>>', lambda e: load_students())

        t_frame = tk.Frame(content, bg="white")
        t_frame.pack(fill='both', expand=True)
        
        yscroll = ttk.Scrollbar(t_frame, orient="vertical")
        xscroll = ttk.Scrollbar(t_frame, orient="horizontal")
        
        tree = ttk.Treeview(t_frame, columns=("SR", "Name", "Year", "Block", "Course"), show="headings", 
                            yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        
        yscroll.config(command=tree.yview)
        xscroll.config(command=tree.xview)
        
        yscroll.pack(side="right", fill="y")
        xscroll.pack(side="bottom", fill="x")
        tree.pack(fill='both', expand=True)

        for c in ["SR", "Name", "Year", "Block", "Course"]: tree.heading(c, text=c)
        
        def load_students():
            for i in tree.get_children(): tree.delete(i)
            sel_yr = yr_filter.get(); sel_blk = blk_filter.get()
            query = "SELECT srcode, name, year_level, block, course FROM students WHERE 1=1"
            params = []
            if sel_yr != "All": query += " AND year_level = %s"; params.append(sel_yr)
            if sel_blk != "All": query += " AND block = %s"; params.append(sel_blk)
            query += " ORDER BY year_level, block, name ASC"
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute(query, tuple(params))
                    for r in cur.fetchall(): tree.insert("", "end", values=list(r.values()))
                conn.close()
            
            self.autosize_tree(tree)

        load_students()

    def admin_teachers_tab(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab, text="Teachers")
        card, content = self.create_card(tab, "Teacher Subject Assignment")
        card.pack(fill='both', expand=True)
        
        input_frame = tk.Frame(content, bg="#F8FAFC", bd=1, relief="solid", padx=15, pady=15)
        input_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(input_frame, text="Step 1: Enter Subject Name", font=FONT_BOLD, bg="#F8FAFC").pack(anchor='w')
        sub_entry = tk.Entry(input_frame, width=50, font=FONT_BODY)
        sub_entry.pack(anchor='w', pady=5)
        tk.Label(input_frame, text="e.g. Mathematics, Science, History 101", bg="#F8FAFC", fg="gray", font=FONT_SMALL).pack(anchor='w')

        tree_frame = tk.Frame(content, bg="white")
        tree_frame.pack(fill='both', expand=True)
        tk.Label(tree_frame, text="Step 2: Select a Teacher from the list", font=FONT_BOLD, bg="white").pack(anchor='w', pady=(0, 5))
        
        t_frame = tk.Frame(tree_frame, bg="white")
        t_frame.pack(fill='both', expand=True)
        
        yscroll = ttk.Scrollbar(t_frame, orient="vertical")
        xscroll = ttk.Scrollbar(t_frame, orient="horizontal")
        
        tree = ttk.Treeview(t_frame, columns=("ID", "Name", "Subject"), show="headings",
                            yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        
        yscroll.config(command=tree.yview)
        xscroll.config(command=tree.xview)
        
        yscroll.pack(side="right", fill="y")
        xscroll.pack(side="bottom", fill="x")
        tree.pack(fill='both', expand=True)

        tree.heading("ID", text="ID"); tree.column("ID", width=100)
        tree.heading("Name", text="Name"); tree.column("Name", width=250)
        tree.heading("Subject", text="Current Subject(s)"); tree.column("Subject", width=400)

        selected_teacher_id = tk.StringVar()
        selected_teacher_name = tk.StringVar()
        current_subjects = tk.StringVar()

        def load_teachers():
            for i in tree.get_children(): tree.delete(i)
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT srcode, name, subject FROM teachers ORDER BY name ASC")
                    for r in cur.fetchall(): tree.insert("", "end", values=(r['srcode'], r['name'], r['subject']))
                conn.close()
            self.autosize_tree(tree)

        def on_select(event):
            sel = tree.selection()
            if not sel: return
            vals = tree.item(sel)['values']
            selected_teacher_id.set(vals[0]) 
            selected_teacher_name.set(vals[1])
            current_subjects.set(vals[2])

        tree.bind("<<TreeviewSelect>>", on_select)

        action_frame = tk.Frame(content, bg="white", pady=15)
        action_frame.pack(fill='x')

        def assign_subject():
            if not sub_entry.get(): return messagebox.showwarning("Warning", "Please enter a subject name first.")
            if not selected_teacher_id.get(): return messagebox.showwarning("Warning", "Please select a teacher from the list.")
            
            new_sub = sub_entry.get().strip()
            old_subs = current_subjects.get()
            
            if old_subs and old_subs != "None":
                updated_subs = f"{old_subs}, {new_sub}"
            else:
                updated_subs = new_sub
            
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE teachers SET subject=%s WHERE srcode=%s", (updated_subs, selected_teacher_id.get()))
                    conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"Assigned '{new_sub}' to {selected_teacher_name.get()}")
                load_teachers()
                sub_entry.delete(0, 'end') 

        tk.Button(action_frame, text="ADD SUBJECT TO SELECTED TEACHER", command=assign_subject, bg=COLOR_PRIMARY, fg="white", font=FONT_BOLD, relief="flat", padx=20, pady=10).pack()
        load_teachers()

    def admin_drop_requests_tab(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab, text="Requests")
        card, content = self.create_card(tab, "Subject Drop Requests")
        card.pack(fill='both', expand=True)
        
        t_frame = tk.Frame(content, bg="white")
        t_frame.pack(fill='both', expand=True, pady=(0,20))
        
        yscroll = ttk.Scrollbar(t_frame, orient="vertical")
        xscroll = ttk.Scrollbar(t_frame, orient="horizontal")
        
        tree = ttk.Treeview(t_frame, columns=("ID", "Student", "Subject", "Reason", "Status"), show="headings",
                            yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        
        yscroll.config(command=tree.yview)
        xscroll.config(command=tree.xview)
        
        yscroll.pack(side="right", fill="y")
        xscroll.pack(side="bottom", fill="x")
        tree.pack(fill='both', expand=True)

        tree.heading("ID", text="ID")
        tree.heading("Student", text="Student")
        tree.heading("Subject", text="Subject")
        tree.heading("Reason", text="Reason")
        tree.heading("Status", text="Status")
        
        btn_box = tk.Frame(content, bg="white"); btn_box.pack(fill='x')
        
        def load():
            for i in tree.get_children(): tree.delete(i)
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM drop_requests WHERE status='Pending'")
                    for r in cur.fetchall(): tree.insert("", "end", values=(r['id'], r['student_name'], r['subject'], r['reason'], r['status']))
                conn.close()
            self.autosize_tree(tree)
        
        def action(act):
            sel = tree.selection()
            if not sel: return
            item = tree.item(sel)['values']
            st = "Approved" if act == "Approve" else "Rejected"
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE drop_requests SET status=%s WHERE id=%s", (st, item[0]))
                    cur.execute("SELECT student_id FROM drop_requests WHERE id=%s", (item[0],))
                    sid = cur.fetchone()['student_id']
                    msg = f"Your request to drop {item[2]} has been {st} by the Administrator."
                    cur.execute("INSERT INTO notifications (user_id, message) VALUES (%s, %s)", (sid, msg))
                    if act == "Approve": cur.execute("DELETE FROM enrollments WHERE student_id=%s AND subject_name=%s", (sid, item[2]))
                    conn.commit()
                conn.close()
            load()

        tk.Button(btn_box, text="Approve Selected", command=lambda: action("Approve"), bg=COLOR_SUCCESS, fg="white", font=FONT_BOLD, relief="flat", padx=15, pady=5).pack(side='left', padx=5)
        tk.Button(btn_box, text="Reject Selected", command=lambda: action("Reject"), bg=COLOR_DANGER, fg="white", font=FONT_BOLD, relief="flat", padx=15, pady=5).pack(side='left', padx=5)
        load()

    def admin_announce_tab(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab)
        card, content = self.create_card(tab, "Post Admin Announcement")
        card.pack(fill='both', expand=True, padx=100, pady=50)

        f1 = tk.Frame(content, bg="white"); f1.pack(fill='x', pady=10)
        tk.Label(f1, text="Target Audience:", bg="white", font=FONT_BOLD).pack(side='left')
        
        tgt_t = ttk.Combobox(f1, values=["All Users", "Teachers Only", "Students Only", "Specific Year Level"], state='readonly')
        tgt_t.pack(side='left', padx=15)
        tgt_v = ttk.Combobox(f1, state='disabled', width=20); tgt_v.pack(side='left')
        
        def chg(e):
            s = tgt_t.get()
            tgt_v.set('')
            if s == "Specific Year Level": 
                tgt_v.config(state='readonly', values=list(BLOCK_CONFIG.keys()))
            else: 
                tgt_v.config(state='disabled')
        tgt_t.bind("<<ComboboxSelected>>", chg)

        tk.Label(content, text="Title", bg="white", font=FONT_SMALL, fg=COLOR_TEXT_MUTED).pack(anchor='w')
        tit = tk.Entry(content, relief="solid", bd=1, font=FONT_BODY, bg="#F8FAFC"); tit.pack(fill='x', pady=(5, 15), ipady=5)
        tk.Label(content, text="Message", bg="white", font=FONT_SMALL, fg=COLOR_TEXT_MUTED).pack(anchor='w')
        msg = tk.Text(content, height=8, relief="solid", bd=1, font=FONT_BODY, bg="#F8FAFC"); msg.pack(fill='x', pady=(5, 15))
        
        def post():
            sel = tgt_t.get()
            if not sel or not tit.get() or not msg.get("1.0", "end-1c").strip():
                return messagebox.showwarning("Warning", "Please fill all fields")

            db_t, db_v = "All", ""
            if sel == "Teachers Only": db_t = "Teacher"
            elif sel == "Students Only": db_t = "Student"
            elif sel == "Specific Year Level": 
                db_t = "Year"
                db_v = tgt_v.get()
            
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO announcements (author_name, title, message, target, target_value) VALUES (%s,%s,%s,%s,%s)",
                                ("Admin", tit.get(), msg.get("1.0", "end-1c"), db_t, db_v))
                    conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Announcement Posted!"); tit.delete(0,'end'); msg.delete("1.0",'end')

        tk.Button(content, text="BROADCAST UPDATE", command=post, bg=COLOR_PRIMARY, fg="white", font=FONT_BOLD, relief="flat", pady=10).pack(fill='x')


    # ================= TEACHER DASHBOARD =================
    def teacher_dashboard(self):
        self.setup_dashboard_layout()
        self.create_sidebar_btn(self.sidebar, "Profile", ICON_USER, lambda: self.switch_teacher_tab(0))
        self.create_sidebar_btn(self.sidebar, "Grading", ICON_GRADES, lambda: self.switch_teacher_tab(1))
        self.create_sidebar_btn(self.sidebar, "Announcements", ICON_MEGAPHONE, lambda: self.switch_teacher_tab(2))
        
        self.teacher_nb = ttk.Notebook(self.main)
        self.teacher_nb.pack(fill='both', expand=True)
        style = ttk.Style(); style.layout('TNotebook.Tab', []) 
        
        self.teacher_profile_tab(self.teacher_nb)
        self.teacher_grading_ui(self.teacher_nb)
        self.teacher_announce_ui(self.teacher_nb)

    def switch_teacher_tab(self, index):
        self.teacher_nb.select(index)

    def teacher_profile_tab(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab)
        card, content = self.create_card(tab, "My Profile")
        card.pack(fill='both', expand=True, padx=100, pady=50)
        
        data = self.current_user
        subjects = data.get('subject', '').replace(',', '\n') if data.get('subject') else "None Assigned"
        
        fields = [("SR Code", data.get('srcode')), ("Full Name", data['name']), ("Username", data['username'])]
        
        r = 0
        for k, v in fields:
            tk.Label(content, text=k, font=("Segoe UI", 11, "bold"), fg=COLOR_TEXT_MUTED, bg="white").grid(row=r, column=0, sticky='w', pady=15)
            tk.Label(content, text=v, font=("Segoe UI", 14), fg=COLOR_TEXT_MAIN, bg="white").grid(row=r, column=1, sticky='w', padx=40, pady=15)
            r+=1
            
        tk.Label(content, text="Assigned Subjects:", font=("Segoe UI", 11, "bold"), fg=COLOR_TEXT_MUTED, bg="white").grid(row=r, column=0, sticky='nw', pady=15)
        tk.Message(content, text=subjects, font=("Segoe UI", 12), fg=COLOR_PRIMARY, bg="white", width=400).grid(row=r, column=1, sticky='w', padx=40, pady=15)

    def teacher_grading_ui(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab)
        
        banner = tk.Frame(tab, bg="white", pady=15, padx=20, bd=1, relief="solid")
        banner.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
        banner.pack(fill='x', pady=(0, 25))
        
        tk.Label(banner, text="Active Subject:", font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT_MUTED, bg="white").pack(side='left')
        subs = [s.strip() for s in self.current_user.get('subject', '').split(',') if s.strip()]
        self.sub_var = tk.StringVar()
        scb = ttk.Combobox(banner, textvariable=self.sub_var, values=subs, state='readonly', width=30, font=FONT_BOLD)
        scb.pack(side='left', padx=15)
        if subs: scb.current(0)

        controls = tk.Frame(tab, bg=COLOR_BG, pady=15)
        controls.pack(fill='x')
        tk.Label(controls, text="Select Class:", font=FONT_BOLD, bg=COLOR_BG).pack(side='left')
        yr_var = ttk.Combobox(controls, values=list(BLOCK_CONFIG.keys()), state='readonly', width=15)
        yr_var.pack(side='left', padx=10)
        blk_var = ttk.Combobox(controls, state='disabled', width=15)
        blk_var.pack(side='left', padx=10)
        yr_var.bind('<<ComboboxSelected>>', lambda e: (blk_var.config(state='readonly', values=BLOCK_CONFIG[yr_var.get()]), blk_var.current(0)))
        
        card, content = self.create_card(tab)
        card.pack(fill='both', expand=True)
        
        # Scrollable Tree
        t_frame = tk.Frame(content, bg="white")
        t_frame.pack(fill='both', expand=True, pady=(0,20))
        
        yscroll = ttk.Scrollbar(t_frame, orient="vertical")
        xscroll = ttk.Scrollbar(t_frame, orient="horizontal")
        
        tree = ttk.Treeview(t_frame, columns=("SR", "Name", "Grade", "Edits"), show="headings",
                            yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        
        yscroll.config(command=tree.yview)
        xscroll.config(command=tree.xview)
        
        yscroll.pack(side="right", fill="y")
        xscroll.pack(side="bottom", fill="x")
        tree.pack(fill='both', expand=True)

        tree.heading("SR", text="SR Code")
        tree.heading("Name", text="Student Name")
        tree.heading("Grade", text="Grade")
        tree.heading("Edits", text="Edits Left")
        
        action_bar = tk.Frame(content, bg="white"); action_bar.pack(fill='x')
        
        def load():
            if not self.sub_var.get() or not blk_var.get(): return messagebox.showwarning("Info", "Select Subject, Year and Block")
            for i in tree.get_children(): tree.delete(i)
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("""SELECT s.srcode, s.name, e.grade, e.edit_count FROM enrollments e 
                                JOIN students s ON e.student_id=s.id 
                                WHERE e.teacher_id=%s AND e.subject_name=%s AND s.year_level=%s AND s.block=%s ORDER BY s.name ASC""",
                                (self.current_user['id'], self.sub_var.get(), yr_var.get(), blk_var.get()))
                    for r in cur.fetchall(): 
                        edits_left = 2 - r['edit_count']
                        tree.insert("", "end", values=(r['srcode'], r['name'], r['grade'], max(0, edits_left)))
                conn.close()
            self.autosize_tree(tree)

        tk.Button(controls, text="Load Students", command=load, bg=COLOR_PRIMARY, fg="white", font=FONT_BOLD, relief="flat", padx=15).pack(side='left')
        tk.Label(action_bar, text="Assign Grade:", bg="white", font=FONT_BOLD).pack(side='left')
        grd = ttk.Combobox(action_bar, values=['1.0','1.25','1.5','1.75','2.0','2.25','2.5','2.75','3.0','5.0'], width=10)
        grd.pack(side='left', padx=10)
        
        def save():
            sel = tree.selection()
            if not sel: return
            item = tree.item(sel)['values']
            src = item[0]
            edits_left = int(item[3])
            
            if edits_left <= 0:
                messagebox.showerror("Limit Reached", "You have reached the maximum number of edits (2) for this grade.")
                return

            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("""UPDATE enrollments e JOIN students s ON e.student_id=s.id 
                                SET e.grade=%s, e.edit_count = e.edit_count + 1 
                                WHERE s.srcode=%s AND e.teacher_id=%s AND e.subject_name=%s""",
                                (grd.get(), src, self.current_user['id'], self.sub_var.get()))
                    conn.commit()
                conn.close()
                load()
                messagebox.showinfo("Saved", "Grade updated successfully.")

        tk.Button(action_bar, text="Save Grade", command=save, bg=COLOR_SUCCESS, fg="white", font=FONT_BOLD, relief="flat", padx=15).pack(side='left')

    def teacher_announce_ui(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab)
        
        inner_nb = ttk.Notebook(tab)
        inner_nb.pack(fill='both', expand=True)

        tab_create = tk.Frame(inner_nb, bg=COLOR_BG)
        inner_nb.add(tab_create, text="  Create Post  ")

        card, content = self.create_card(tab_create, "Post Announcement to Class")
        card.pack(fill='both', expand=True, padx=50, pady=20)
        
        f1 = tk.Frame(content, bg="white"); f1.pack(fill='x', pady=10)
        tk.Label(f1, text="Target Audience:", bg="white", font=FONT_BOLD).pack(side='left')
        
        tgt_t = ttk.Combobox(f1, values=["All My Classes", "Specific Year", "Specific Block"], state='readonly', width=20)
        tgt_t.pack(side='left', padx=15)
        tgt_v = ttk.Combobox(f1, state='disabled', width=20); tgt_v.pack(side='left')
        
        def chg(e):
            s = tgt_t.get()
            tgt_v.set('')
            if s == "Specific Year": 
                tgt_v.config(state='readonly', values=list(BLOCK_CONFIG.keys()))
            elif s == "Specific Block": 
                all_blocks = [b for l in BLOCK_CONFIG.values() for b in l]
                tgt_v.config(state='readonly', values=all_blocks)
            else: 
                tgt_v.config(state='disabled')
        tgt_t.bind("<<ComboboxSelected>>", chg)
        
        tk.Label(content, text="Title", bg="white", font=FONT_SMALL, fg=COLOR_TEXT_MUTED).pack(anchor='w')
        tit = tk.Entry(content, relief="solid", bd=1, font=FONT_BODY, bg="#F8FAFC"); tit.pack(fill='x', pady=(5, 15), ipady=5)
        tk.Label(content, text="Message", bg="white", font=FONT_SMALL, fg=COLOR_TEXT_MUTED).pack(anchor='w')
        msg = tk.Text(content, height=8, relief="solid", bd=1, font=FONT_BODY, bg="#F8FAFC"); msg.pack(fill='x', pady=(5, 15))
        
        def post():
            db_t, db_v = "Class", "" 
            if tgt_t.get() == "Specific Year": 
                db_t = "Year"
                db_v = tgt_v.get()
            elif tgt_t.get() == "Specific Block": 
                db_t = "Block"
                db_v = tgt_v.get()
            
            if not tit.get() or not msg.get("1.0", "end-1c").strip():
                 return messagebox.showwarning("Error", "Please fill in all fields")

            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO announcements (author_name, title, message, target, target_value) VALUES (%s,%s,%s,%s,%s)",
                                (self.current_user['name'], tit.get(), msg.get("1.0", "end-1c"), db_t, db_v))
                    conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Announcement Posted!"); tit.delete(0,'end'); msg.delete("1.0",'end')

        tk.Button(content, text="POST ANNOUNCEMENT", command=post, bg=COLOR_PRIMARY, fg="white", font=FONT_BOLD, relief="flat", pady=10).pack(fill='x')

        tab_inbox = tk.Frame(inner_nb, bg=COLOR_BG)
        inner_nb.add(tab_inbox, text="  Inbox (From Admin)  ")
        
        canvas = tk.Canvas(tab_inbox, bg=COLOR_BG, highlightthickness=0)
        scr = ttk.Scrollbar(tab_inbox, command=canvas.yview)
        scr.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        canvas.configure(yscrollcommand=scr.set)
        frame = tk.Frame(canvas, bg=COLOR_BG)
        canvas.create_window((0,0), window=frame, anchor='nw', width=1000)

        conn = self.db.get_connection()
        rows = []
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM announcements WHERE target IN ('All', 'Teacher') ORDER BY date_posted DESC")
                rows = cur.fetchall()
            conn.close()

        if not rows: 
            tk.Label(frame, text="No announcements from Admin", bg=COLOR_BG, fg="gray", font=FONT_H2).pack(pady=50)

        for r in rows:
            p = tk.Frame(frame, bg="white", bd=1, relief="solid", padx=20, pady=20)
            p.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
            p.pack(fill='x', expand=True, padx=50, pady=10)
            
            badge_text = " ADMIN BROADCAST " if r['target'] == 'All' else " TEACHER MEMO "
            badge_color = COLOR_DANGER if r['target'] == 'All' else COLOR_WARNING
            tk.Label(p, text=badge_text, bg=badge_color, fg="white", font=("Segoe UI", 8, "bold")).pack(anchor='ne')
            
            tk.Label(p, text=r['title'], font=FONT_H2, bg="white", fg=COLOR_TEXT_MAIN).pack(anchor='w')
            tk.Label(p, text=f"From {r['author_name']} • {r['date_posted']}", font=FONT_SMALL, fg=COLOR_TEXT_MUTED, bg="white").pack(anchor='w', pady=(0, 10))
            tk.Message(p, text=r['message'], width=800, bg="white", font=FONT_BODY, fg=COLOR_TEXT_MAIN).pack(anchor='w')
            
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))


    # ================= STUDENT DASHBOARD =================
    def student_dashboard(self):
        self.setup_dashboard_layout()
        self.create_sidebar_btn(self.sidebar, "Profile", ICON_USER, lambda: self.switch_stud_tab(0))
        self.create_sidebar_btn(self.sidebar, "Grades", ICON_GRADES, lambda: self.switch_stud_tab(1))
        self.create_sidebar_btn(self.sidebar, "Enrollment", ICON_TEACHERS, lambda: self.switch_stud_tab(2))
        self.create_sidebar_btn(self.sidebar, "Drop Subject", ICON_REQ, lambda: self.switch_stud_tab(3))
        self.create_sidebar_btn(self.sidebar, "Announcements", ICON_REQ, lambda: self.switch_stud_tab(4))
        self.create_sidebar_btn(self.sidebar, "Notifications", ICON_BELL, lambda: self.switch_stud_tab(5))
        
        self.stud_nb = ttk.Notebook(self.main)
        self.stud_nb.pack(fill='both', expand=True)
        style = ttk.Style(); style.layout('TNotebook.Tab', []) 
        
        self.stud_profile(self.stud_nb)
        self.stud_grades(self.stud_nb)
        self.stud_enroll(self.stud_nb)
        self.stud_drop(self.stud_nb)
        self.stud_announce(self.stud_nb)
        self.stud_notifications(self.stud_nb)
        
    def switch_stud_tab(self, i): self.stud_nb.select(i)

    def stud_profile(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab)
        card, content = self.create_card(tab, "My Profile")
        card.pack(fill='both', expand=True, padx=100, pady=50)
        data = self.current_user
        fields = [("SR Code", data.get('srcode')), ("Full Name", data['name']), 
                  ("Course", data.get('course', 'N/A')), ("Year Level", data.get('year_level', 'N/A')), ("Block", data.get('block', 'N/A'))]
        for i, (k, v) in enumerate(fields):
            tk.Label(content, text=k, font=("Segoe UI", 11, "bold"), fg=COLOR_TEXT_MUTED, bg="white").grid(row=i, column=0, sticky='w', pady=15)
            tk.Label(content, text=v, font=("Segoe UI", 14), fg=COLOR_TEXT_MAIN, bg="white").grid(row=i, column=1, sticky='w', padx=40, pady=15)

    def stud_grades(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab)
        card, content = self.create_card(tab, "Academic Record")
        card.pack(fill='both', expand=True)
        
        t_frame = tk.Frame(content, bg="white")
        t_frame.pack(fill='both', expand=True)
        yscroll = ttk.Scrollbar(t_frame, orient="vertical")
        xscroll = ttk.Scrollbar(t_frame, orient="horizontal")
        
        tree = ttk.Treeview(t_frame, columns=("Sub", "Prof", "Grd"), show="headings",
                            yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        yscroll.config(command=tree.yview)
        xscroll.config(command=tree.xview)
        yscroll.pack(side="right", fill="y")
        xscroll.pack(side="bottom", fill="x")
        tree.pack(fill='both', expand=True)

        tree.heading("Sub", text="Subject")
        tree.heading("Prof", text="Instructor")
        tree.heading("Grd", text="Grade")
        
        conn = self.db.get_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT e.subject_name, t.name, e.grade FROM enrollments e JOIN teachers t ON e.teacher_id=t.id WHERE e.student_id=%s", (self.current_user['id'],))
                for r in cur.fetchall(): tree.insert("", "end", values=(r['subject_name'], r['name'], r['grade']))
            conn.close()
        self.autosize_tree(tree)

    def stud_enroll(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab)
        card, content = self.create_card(tab, "Enroll Subjects")
        card.pack(fill='x', pady=20)
        tk.Label(content, text="Select Subject to Enroll:", bg="white", font=FONT_BOLD).pack(anchor='w')
        subs = []
        sub_map = {}
        conn = self.db.get_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, subject FROM teachers")
                for t in cur.fetchall():
                    if t['subject']:
                        for s in t['subject'].split(','):
                            l = f"{s.strip()} ({t['name']})"
                            subs.append(l)
                            sub_map[l] = (t['id'], s.strip())
            conn.close()
        sv = ttk.Combobox(content, values=subs, state='readonly', width=50); sv.pack(pady=10)
        
        def enroll():
            if not sv.get(): return
            tid, sname = sub_map[sv.get()]
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM enrollments WHERE student_id=%s AND subject_name=%s", (self.current_user['id'], sname))
                    if cur.fetchone(): messagebox.showerror("Error", "Already enrolled"); return
                    cur.execute("INSERT INTO enrollments (student_id, teacher_id, subject_name) VALUES (%s,%s,%s)", (self.current_user['id'], tid, sname))
                    conn.commit()
                conn.close(); messagebox.showinfo("Success", "Enrolled!")

        tk.Button(content, text="Confirm Enrollment", command=enroll, bg=COLOR_SUCCESS, fg="white", font=FONT_BOLD, relief="flat", pady=8).pack()

    def stud_drop(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab)
        card, content = self.create_card(tab, "Request to Drop")
        card.pack(fill='x', pady=20)
        subs = []
        conn = self.db.get_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT subject_name FROM enrollments WHERE student_id=%s", (self.current_user['id'],))
                subs = [r['subject_name'] for r in cur.fetchall()]
            conn.close()
        cb = ttk.Combobox(content, values=subs, state='readonly', width=40); cb.pack(pady=5)
        reas = tk.Entry(content, width=40, relief="solid", bd=1); reas.pack(pady=5)
        
        def req():
            if not cb.get(): return
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO drop_requests (student_id, student_name, subject, reason) VALUES (%s,%s,%s,%s)",
                                (self.current_user['id'], self.current_user['name'], cb.get(), reas.get()))
                    conn.commit()
                conn.close(); messagebox.showinfo("Sent", "Request sent.")

        tk.Button(content, text="Submit Request", command=req, bg=COLOR_WARNING, fg="white", font=FONT_BOLD, relief="flat", pady=8).pack(pady=10)

    def stud_announce(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab)
        canvas = tk.Canvas(tab, bg=COLOR_BG, highlightthickness=0)
        scr = ttk.Scrollbar(tab, command=canvas.yview)
        scr.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        canvas.configure(yscrollcommand=scr.set)
        frame = tk.Frame(canvas, bg=COLOR_BG)
        canvas.create_window((0,0), window=frame, anchor='nw', width=1000) 
        
        conn = self.db.get_connection()
        rows = []
        if conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT * FROM announcements WHERE 
                            target IN ('All', 'Student') 
                            OR (target='Class' AND author_name IN (SELECT t.name FROM enrollments e JOIN teachers t ON e.teacher_id=t.id WHERE e.student_id=%s))
                            OR (target='Year' AND target_value=%s) 
                            OR (target='Block' AND target_value=%s) 
                            ORDER BY date_posted DESC""",
                            (self.current_user['id'], self.current_user['year_level'], self.current_user['block']))
                rows = cur.fetchall()
            conn.close()

        if not rows: tk.Label(frame, text="No new announcements", bg=COLOR_BG, fg="gray", font=FONT_H2).pack(pady=50)

        for r in rows:
            p = tk.Frame(frame, bg="white", bd=1, relief="solid", padx=20, pady=20)
            p.configure(highlightbackground=COLOR_BORDER, highlightthickness=1)
            p.pack(fill='x', expand=True, padx=50, pady=10)
            badge_c = COLOR_PRIMARY 
            if r['target'] == 'Year': badge_c = COLOR_PURPLE
            elif r['target'] == 'Block': badge_c = COLOR_WARNING
            elif r['target'] == 'All' or r['target'] == 'Student': badge_c = COLOR_DANGER 
            
            tk.Label(p, text=f" {r['target']} ", bg=badge_c, fg="white", font=("Segoe UI", 8, "bold")).pack(anchor='ne')
            tk.Label(p, text=r['title'], font=FONT_H2, bg="white", fg=COLOR_TEXT_MAIN).pack(anchor='w')
            tk.Label(p, text=f"From {r['author_name']} • {r['date_posted']}", font=FONT_SMALL, fg=COLOR_TEXT_MUTED, bg="white").pack(anchor='w', pady=(0, 10))
            tk.Message(p, text=r['message'], width=800, bg="white", font=FONT_BODY, fg=COLOR_TEXT_MAIN).pack(anchor='w')
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def stud_notifications(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab)
        card, content = self.create_card(tab, "Notifications")
        card.pack(fill='both', expand=True, padx=50, pady=20)
        list_frame = tk.Frame(content, bg="white")
        list_frame.pack(fill='both', expand=True)

        conn = self.db.get_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM notifications WHERE user_id=%s ORDER BY date_created DESC", (self.current_user['id'],))
                notifs = cur.fetchall()
                if not notifs:
                    tk.Label(list_frame, text="No notifications yet.", bg="white", fg="gray", font=FONT_H2).pack(pady=50)
                else:
                    for n in notifs:
                        row = tk.Frame(list_frame, bg="white", bd=0, pady=10)
                        row.pack(fill='x', pady=5)
                        tk.Label(row, text="•", font=("Arial", 16), fg=COLOR_PRIMARY, bg="white").pack(side='left', padx=(10,5))
                        tk.Label(row, text=n['message'], font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg="white").pack(side='left')
                        tk.Label(row, text=str(n['date_created']), font=FONT_SMALL, fg=COLOR_TEXT_MUTED, bg="white").pack(side='right', padx=10)
                        tk.Frame(list_frame, bg=COLOR_BORDER, height=1).pack(fill='x') 
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementSystem(root)
    root.mainloop()
