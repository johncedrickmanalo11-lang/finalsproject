import tkinter as tk
from tkinter import ttk, messagebox
from common import *

class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Portal")
        self.root.geometry("1280x800")
        self.root.configure(bg=COLOR_BG)
        self.db = DatabaseConnection()
        self.current_user = None
        setup_styles()
        self.show_login()

    def clear_screen(self):
        for widget in self.root.winfo_children(): widget.destroy()

    # ================= LOGIN =================
    def show_login(self):
        self.clear_screen()
        bg = tk.Frame(self.root, bg=COLOR_BG); bg.pack(fill='both', expand=True)
        card = tk.Frame(bg, bg="white", padx=50, pady=50, relief="solid", bd=1)
        card.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(card, text="STUDENT PORTAL", font=("Segoe UI", 20, "bold"), fg=COLOR_PRIMARY, bg="white").pack(pady=(0,20))
        tk.Label(card, text="Username", bg="white").pack(anchor='w')
        u = tk.Entry(card, width=30, relief="solid", bd=1); u.pack(pady=5)
        tk.Label(card, text="Password", bg="white").pack(anchor='w')
        p = tk.Entry(card, width=30, show="•", relief="solid", bd=1); p.pack(pady=5)
        
        def login():
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM students WHERE username=%s AND password=%s", (u.get(), p.get()))
                    user = cur.fetchone()
                    if user: self.setup_dashboard(user)
                    else: messagebox.showerror("Error", "Invalid Credentials")
                conn.close()

        tk.Button(card, text="LOGIN", command=login, bg=COLOR_PRIMARY, fg="white", font=("Segoe UI", 10, "bold"), width=28).pack(pady=15)
        tk.Button(card, text="Register", command=self.show_register, bg="white", bd=0, fg=COLOR_TEXT_MUTED).pack()

    def show_register(self):
        self.clear_screen()
        bg = tk.Frame(self.root, bg=COLOR_BG); bg.pack(fill='both', expand=True)
        card = tk.Frame(bg, bg="white", padx=50, pady=30); card.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(card, text="Student Registration", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=10)
        
        ents = {}
        for f in ["SR Code", "Name", "Course", "Username", "Password"]:
            tk.Label(card, text=f, bg="white").pack(anchor='w')
            e = tk.Entry(card, width=30, relief="solid", bd=1); e.pack()
            ents[f] = e
        
        tk.Label(card, text="Year Level", bg="white").pack(anchor='w')
        yb = ttk.Combobox(card, values=list(BLOCK_CONFIG.keys()), state='readonly', width=27); yb.pack()
        tk.Label(card, text="Block", bg="white").pack(anchor='w')
        bb = ttk.Combobox(card, state='readonly', width=27); bb.pack()
        yb.bind('<<ComboboxSelected>>', lambda e: bb.config(values=BLOCK_CONFIG.get(yb.get(), [])))

        def reg():
            conn = self.db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO students (srcode, name, course, year_level, block, username, password) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                                (ents['SR Code'].get(), ents['Name'].get(), ents['Course'].get(), yb.get(), bb.get(), ents['Username'].get(), ents['Password'].get()))
                    conn.commit(); messagebox.showinfo("Success", "Registered!"); self.show_login()
            except Error as e: messagebox.showerror("Error", str(e))
            finally: conn.close()
            
        tk.Button(card, text="REGISTER", command=reg, bg=COLOR_SUCCESS, fg="white", width=25).pack(pady=15)
        tk.Button(card, text="Back", command=self.show_login, bg="white", bd=0).pack()

    # ================= SIDEBAR DASHBOARD SETUP =================
    def setup_dashboard(self, user):
        self.current_user = user
        self.clear_screen()
        
        # --- LEFT SIDEBAR ---
        self.sidebar = tk.Frame(self.root, bg=COLOR_SIDEBAR, width=250)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)
        
        # User Info in Sidebar
        tk.Label(self.sidebar, text="STUDENT PORTAL", font=("Segoe UI", 16, "bold"), fg="white", bg=COLOR_SIDEBAR).pack(pady=(40, 20))
        tk.Label(self.sidebar, text=f"{user['name']}", font=("Segoe UI", 10, "bold"), fg="white", bg=COLOR_SIDEBAR, wraplength=230).pack(padx=10)
        tk.Label(self.sidebar, text=f"{user['year_level']} | {user['block']}", font=("Segoe UI", 9), fg="#94A3B8", bg=COLOR_SIDEBAR).pack(pady=(0, 30))

        # Navigation Buttons
        create_sidebar_btn(self.sidebar, "My Profile", "👤", self.view_profile)
        create_sidebar_btn(self.sidebar, "Enrollment", "📝", self.view_enrollment)
        create_sidebar_btn(self.sidebar, "My Subjects", "📚", self.view_subjects)
        create_sidebar_btn(self.sidebar, "Drop Request", "🗑️", self.view_drop_request)
        create_sidebar_btn(self.sidebar, "Notifications", "🔔", self.view_notifications)
        
        create_sidebar_btn(self.sidebar, "Logout", "🚪", self.show_login).pack(side='bottom', fill='x', pady=20)

        # --- MAIN CONTENT AREA ---
        self.main_content = tk.Frame(self.root, bg=COLOR_BG)
        self.main_content.pack(side='right', fill='both', expand=True)
        
        # Placeholder for dynamic content
        self.content_frame = tk.Frame(self.main_content, bg=COLOR_BG)
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Announcements Footer (Always Visible)
        self.setup_announcements()

        # Load default view
        self.view_profile()

    def setup_announcements(self):
        f = tk.Frame(self.main_content, bg="white", height=120, bd=1, relief="solid")
        f.pack(side='bottom', fill='x', padx=20, pady=20)
        f.pack_propagate(False)
        tk.Label(f, text="📢 Recent Announcements", font=("Segoe UI", 10, "bold"), bg=COLOR_PRIMARY, fg="white").pack(fill='x')
        
        txt = tk.Text(f, bg="white", relief="flat", height=4)
        txt.pack(fill='both', expand=True, padx=10, pady=5)
        
        conn = self.db.get_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT * FROM announcements WHERE 
                            target='Student' 
                            OR (target='Year' AND target_value=%s) 
                            OR (target='Block' AND target_value=%s) 
                            ORDER BY date_posted DESC LIMIT 3""", 
                            (self.current_user['year_level'], self.current_user['block']))
                for r in cur.fetchall():
                    txt.insert("end", f"• {r['title']}: {r['message']}\n")
            conn.close()
        txt.config(state='disabled')

    def switch_view(self, title):
        for widget in self.content_frame.winfo_children(): widget.destroy()
        tk.Label(self.content_frame, text=title, font=("Segoe UI", 18, "bold"), bg=COLOR_BG, fg=COLOR_TEXT_MAIN).pack(anchor='w', pady=(0, 20))
        return self.content_frame

    # ================= VIEW: PROFILE =================
    def view_profile(self):
        parent = self.switch_view("My Profile")
        card, content = create_card(parent, "Student Information")
        card.pack(fill='both', expand=True, padx=50)
        
        u = self.current_user
        info = [("SR Code", u['srcode']), ("Name", u['name']), ("Course", u['course']),
                ("Year Level", u['year_level']), ("Block", u['block'])]
        
        for k, v in info:
            row = tk.Frame(content, bg="white", pady=10)
            row.pack(fill='x')
            tk.Label(row, text=k, width=20, font=("Segoe UI", 11, "bold"), fg="gray", bg="white", anchor='w').pack(side='left')
            tk.Label(row, text=v, font=("Segoe UI", 12), bg="white").pack(side='left')

    # ================= VIEW: ENROLLMENT (FILTERED) =================
    def view_enrollment(self):
        parent = self.switch_view("Enrollment")
        
        card, content = create_card(parent, "Available Subjects for Enrollment")
        card.pack(fill='both', expand=True)

        tk.Label(content, text="Select a subject below to enroll.", bg="white", fg="gray").pack(anchor='w', pady=(0,10))

        cols = ("Subject", "Teacher")
        tree = ttk.Treeview(content, columns=cols, show="headings")
        tree.heading("Subject", text="Subject Name")
        tree.heading("Teacher", text="Instructor")
        tree.column("Subject", width=400)
        tree.column("Teacher", width=300)
        tree.pack(fill='both', expand=True)

        avail_map = {}
        
        def load():
            for i in tree.get_children(): tree.delete(i)
            avail_map.clear()
            
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    # 1. KUNIN MUNA LAHAT NG SUBJECT NA ENROLLED NA
                    cur.execute("SELECT subject_name FROM enrollments WHERE student_id=%s", (self.current_user['id'],))
                    enrolled_subs = {row['subject_name'] for row in cur.fetchall()} # Set of enrolled subjects

                    # 2. KUNIN ANG AVAILABLE TEACHERS/SUBJECTS
                    cur.execute("SELECT id, name, subject FROM teachers")
                    for t in cur.fetchall():
                        if t['subject']:
                            for sub in t['subject'].split(','):
                                clean = sub.strip()
                                # 3. I-CHECK KUNG 'NONE' AT KUNG NASA ENROLLED NA
                                if clean and clean.lower() != 'none' and clean not in enrolled_subs:
                                    iid = tree.insert("", "end", values=(clean, t['name']))
                                    avail_map[iid] = (t['id'], clean)
                conn.close()
        load()

        def enroll():
            sel = tree.selection()
            if not sel: return messagebox.showwarning("Select", "Please select a subject first.")
            
            tid, sname = avail_map[sel[0]]
            conn = self.db.get_connection()
            try:
                with conn.cursor() as cur:
                    # Double check just in case
                    cur.execute("SELECT id FROM enrollments WHERE student_id=%s AND subject_name=%s", (self.current_user['id'], sname))
                    if cur.fetchone():
                        messagebox.showerror("Error", f"Already enrolled in {sname}")
                        load() # Refresh
                        return
                        
                    cur.execute("INSERT INTO enrollments (student_id, teacher_id, subject_name) VALUES (%s,%s,%s)", 
                                (self.current_user['id'], tid, sname))
                    conn.commit()
                    messagebox.showinfo("Success", f"Enrolled in {sname}")
                    load() # REFRESH LIST TO HIDE THE SUBJECT
            except Exception as e: messagebox.showerror("Error", str(e))
            finally: conn.close()

        # ENROLL BUTTON
        tk.Button(content, text="✅ ENROLL SELECTED SUBJECT", command=enroll, bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 11, "bold"), pady=12).pack(fill='x', pady=20)

    # ================= VIEW: MY SUBJECTS (ENROLLED) =================
    def view_subjects(self):
        parent = self.switch_view("My Subjects")
        
        card, content = create_card(parent, "Enrolled Subjects & Grades")
        card.pack(fill='both', expand=True)

        cols = ("Subject", "Teacher", "Grade")
        tree = ttk.Treeview(content, columns=cols, show="headings")
        tree.heading("Subject", text="Subject"); tree.column("Subject", width=350)
        tree.heading("Teacher", text="Instructor"); tree.column("Teacher", width=300)
        tree.heading("Grade", text="Grade"); tree.column("Grade", width=100, anchor='center')
        tree.pack(fill='both', expand=True)

        conn = self.db.get_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT e.subject_name, t.name, e.grade 
                            FROM enrollments e JOIN teachers t ON e.teacher_id=t.id 
                            WHERE e.student_id=%s""", (self.current_user['id'],))
                for r in cur.fetchall():
                    tree.insert("", "end", values=(r['subject_name'], r['name'], r['grade']))
            conn.close()

    # ================= VIEW: DROP REQUEST =================
    def view_drop_request(self):
        parent = self.switch_view("Drop Subject Request")
        
        card, content = create_card(parent, "Submit Drop Request")
        card.pack(fill='x', pady=(0, 20))

        # Form
        tk.Label(content, text="Select Subject to Drop:", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor='w')
        
        # Get enrolled subjects
        subs = []
        conn = self.db.get_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT subject_name FROM enrollments WHERE student_id=%s", (self.current_user['id'],))
                subs = [r['subject_name'] for r in cur.fetchall()]
            conn.close()
        
        cb = ttk.Combobox(content, values=subs, state='readonly', width=50)
        cb.pack(anchor='w', pady=5)

        tk.Label(content, text="Reason for Dropping:", bg="white", font=("Segoe UI", 10, "bold")).pack(anchor='w', pady=(10,0))
        reason = tk.Entry(content, width=50, relief="solid", bd=1)
        reason.pack(anchor='w', pady=5)

        def submit():
            if not cb.get() or not reason.get(): return messagebox.showwarning("Incomplete", "Please select a subject and provide a reason.")
            
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM drop_requests WHERE student_id=%s AND subject=%s AND status='Pending'", (self.current_user['id'], cb.get()))
                if cur.fetchone():
                    messagebox.showinfo("Pending", "You already have a pending request for this subject.")
                    return
                
                cur.execute("INSERT INTO drop_requests (student_id, student_name, subject, reason) VALUES (%s,%s,%s,%s)",
                            (self.current_user['id'], self.current_user['name'], cb.get(), reason.get()))
                conn.commit()
            conn.close(); messagebox.showinfo("Success", "Drop request submitted to Admin."); reason.delete(0, 'end'); cb.set('')

        tk.Button(content, text="SUBMIT REQUEST", command=submit, bg=COLOR_DANGER, fg="white", font=("Segoe UI", 10, "bold"), pady=8).pack(anchor='w', pady=20)

        # Pending Requests List
        card2, content2 = create_card(parent, "My Pending Requests")
        card2.pack(fill='both', expand=True)
        
        tree = ttk.Treeview(content2, columns=("Subject", "Reason", "Status"), show="headings", height=5)
        tree.heading("Subject", text="Subject")
        tree.heading("Reason", text="Reason")
        tree.heading("Status", text="Status")
        tree.pack(fill='both', expand=True)
        
        conn = self.db.get_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT subject, reason, status FROM drop_requests WHERE student_id=%s", (self.current_user['id'],))
                for r in cur.fetchall():
                    tree.insert("", "end", values=(r['subject'], r['reason'], r['status']))
            conn.close()

    # ================= VIEW: NOTIFICATIONS =================
    def view_notifications(self):
        parent = self.switch_view("Notifications")
        card, content = create_card(parent, "Inbox")
        card.pack(fill='both', expand=True)

        conn = self.db.get_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM notifications WHERE user_id=%s ORDER BY date_created DESC", (self.current_user['id'],))
                rows = cur.fetchall()
                if not rows:
                    tk.Label(content, text="No new notifications.", bg="white", fg="gray").pack(pady=20)
                else:
                    for r in rows:
                        f = tk.Frame(content, bg="white", bd=0, pady=5)
                        f.pack(fill='x')
                        tk.Label(f, text="•", font=("Arial", 14), fg=COLOR_PRIMARY, bg="white").pack(side='left', padx=10)
                        tk.Label(f, text=r['message'], font=("Segoe UI", 11), bg="white").pack(side='left')
                        tk.Label(f, text=str(r['date_created']), font=("Segoe UI", 9), fg="gray", bg="white").pack(side='right', padx=10)
                        ttk.Separator(content, orient='horizontal').pack(fill='x')
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()
