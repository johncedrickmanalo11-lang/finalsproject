import tkinter as tk
from tkinter import ttk, messagebox
from common import *

class TeacherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Teacher Portal")
        self.root.geometry("1300x800")
        self.root.configure(bg=COLOR_BG)
        self.db = DatabaseConnection()
        self.current_user = None
        setup_styles()
        self.show_login()

    def clear_screen(self):
        for widget in self.root.winfo_children(): widget.destroy()

    # ================= LOGIN & REGISTER =================
    def show_login(self):
        self.clear_screen()
        bg = tk.Frame(self.root, bg=COLOR_BG); bg.pack(fill='both', expand=True)
        card = tk.Frame(bg, bg="white", padx=50, pady=50, relief="solid", bd=1)
        card.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(card, text="TEACHER PORTAL", font=("Segoe UI", 20, "bold"), fg=COLOR_SUCCESS, bg="white").pack(pady=(0,20))
        tk.Label(card, text="Username", bg="white").pack(anchor='w')
        u = tk.Entry(card, width=30, relief="solid", bd=1); u.pack(pady=5, ipady=3)
        tk.Label(card, text="Password", bg="white").pack(anchor='w')
        p = tk.Entry(card, width=30, show="•", relief="solid", bd=1); p.pack(pady=5, ipady=3)
        
        def login():
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM teachers WHERE username=%s AND password=%s", (u.get(), p.get()))
                    user = cur.fetchone()
                    if user: self.dashboard(user)
                    else: messagebox.showerror("Error", "Invalid Credentials")
                conn.close()

        tk.Button(card, text="LOGIN", command=login, bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 10, "bold"), width=28).pack(pady=15)
        tk.Button(card, text="Register New Account", command=self.show_register, bg="white", fg=COLOR_PRIMARY, bd=0).pack()

    def show_register(self):
        self.clear_screen()
        bg = tk.Frame(self.root, bg=COLOR_BG); bg.pack(fill='both', expand=True)
        card = tk.Frame(bg, bg="white", padx=50, pady=30, relief="solid", bd=1)
        card.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(card, text="Teacher Registration", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=10)
        
        # Removed Subject field as requested
        ents = {}
        for f in ["SR Code", "Full Name", "Username", "Password"]:
            tk.Label(card, text=f, bg="white").pack(anchor='w')
            e = tk.Entry(card, width=35, relief="solid", bd=1); e.pack(pady=3)
            ents[f] = e

        def reg():
            conn = self.db.get_connection()
            try:
                with conn.cursor() as cur:
                    # Subjects set to empty string initially
                    cur.execute("INSERT INTO teachers (srcode, name, username, password, subject) VALUES (%s,%s,%s,%s,%s)",
                                (ents["SR Code"].get(), ents["Full Name"].get(), ents["Username"].get(), ents["Password"].get(), ""))
                    conn.commit(); messagebox.showinfo("Success", "Account Created! Ask Admin to assign subjects."); self.show_login()
            except Error as e: messagebox.showerror("Error", str(e))
            finally: conn.close()
            
        tk.Button(card, text="REGISTER", command=reg, bg=COLOR_PRIMARY, fg="white", width=25, pady=8).pack(pady=20)
        tk.Button(card, text="Back to Login", command=self.show_login, bg="white", bd=0).pack()

    # ================= DASHBOARD =================
    def dashboard(self, user):
        self.current_user = user
        self.clear_screen()
        
        # Header with BLUE Subject Selector
        header = tk.Frame(self.root, bg="white", height=70, bd=1, relief="solid")
        header.pack(fill='x')
        
        tk.Label(header, text=f"Welcome, {user['name']}", font=("Segoe UI", 12), bg="white").pack(side='left', padx=20)
        tk.Button(header, text="Logout", command=self.show_login, bg=COLOR_DANGER, fg="white", bd=0).pack(side='right', padx=20)

        # Blue Subject Area
        sub_frame = tk.Frame(header, bg=COLOR_PRIMARY, padx=20, pady=10)
        sub_frame.pack(side='right', padx=20)
        tk.Label(sub_frame, text="Active Subject:", fg="white", bg=COLOR_PRIMARY, font=("Segoe UI", 10, "bold")).pack(side='left')
        
        subs = user['subject'].split(',') if user['subject'] else []
        subs = [s.strip() for s in subs if s.strip()]
        self.active_subject = tk.StringVar()
        
        sub_cb = ttk.Combobox(sub_frame, textvariable=self.active_subject, values=subs, state='readonly', width=25)
        sub_cb.pack(side='left', padx=10)
        if subs: sub_cb.current(0)
        else: sub_cb.set("No Assigned Subjects")

        # Main Layout
        main = tk.Frame(self.root, bg=COLOR_BG, padx=20, pady=20)
        main.pack(fill='both', expand=True)
        
        nb = ttk.Notebook(main)
        nb.pack(fill='both', expand=True)
        
        self.tab_profile(nb)
        self.tab_grading(nb)
        self.tab_announce(nb)

    def tab_profile(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab, text="  My Profile  ")
        card, content = create_card(tab, "Teacher Information")
        card.pack(fill='both', expand=True, padx=50, pady=50)
        
        d = self.current_user
        info = [("SR Code", d['srcode']), ("Name", d['name']), ("Username", d['username']), ("Subjects", d['subject'])]
        
        for k, v in info:
            r = tk.Frame(content, bg="white", pady=5)
            r.pack(fill='x')
            tk.Label(r, text=k, width=20, anchor='w', font=("Segoe UI", 11, "bold"), bg="white", fg="gray").pack(side='left')
            tk.Label(r, text=v, font=("Segoe UI", 12), bg="white").pack(side='left')

    def tab_grading(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab, text="  Grading Sheet  ")
        
        # Navigation for "Nakahiwalay ang 1st-4th Year"
        # We use a Tabset inside the grading view for Years
        year_nb = ttk.Notebook(tab)
        year_nb.pack(fill='both', expand=True, padx=10, pady=10)
        
        for year in BLOCK_CONFIG.keys():
            y_frame = tk.Frame(year_nb, bg=COLOR_BG)
            year_nb.add(y_frame, text=f"  {year}  ")
            self.build_year_view(y_frame, year)

    def build_year_view(self, parent, year):
        # Block Selector for this Year
        ctrl = tk.Frame(parent, bg=COLOR_BG, pady=10)
        ctrl.pack(fill='x')
        tk.Label(ctrl, text=f"Select Block for {year}:", bg=COLOR_BG, font=("Segoe UI", 10, "bold")).pack(side='left')
        
        block_cb = ttk.Combobox(ctrl, values=BLOCK_CONFIG[year], state='readonly', width=15)
        block_cb.pack(side='left', padx=10)
        block_cb.current(0)

        card, content = create_card(parent)
        card.pack(fill='both', expand=True)
        
        tree = ttk.Treeview(content, columns=("SR", "Name", "Grade", "Edits"), show="headings")
        tree.heading("SR", text="SR Code"); tree.heading("Name", text="Student Name (Alphabetical)"); 
        tree.heading("Grade", text="Grade"); tree.heading("Edits", text="Edits Left (Max 2)")
        tree.pack(fill='both', expand=True)
        
        def load():
            for i in tree.get_children(): tree.delete(i)
            sub = self.active_subject.get()
            if not sub or sub == "No Assigned Subjects": return
            
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("""SELECT s.srcode, s.name, e.grade, e.edit_count 
                                FROM enrollments e JOIN students s ON e.student_id=s.id 
                                WHERE e.teacher_id=%s AND e.subject_name=%s AND s.year_level=%s AND s.block=%s 
                                ORDER BY s.name ASC""",
                                (self.current_user['id'], sub, year, block_cb.get()))
                    for r in cur.fetchall():
                        left = 2 - r['edit_count']
                        tree.insert("", "end", values=(r['srcode'], r['name'], r['grade'], max(0, left)))
                conn.close()
        
        tk.Button(ctrl, text="LOAD STUDENTS", command=load, bg=COLOR_PRIMARY, fg="white").pack(side='left', padx=20)

        # Grade Input
        bot = tk.Frame(content, bg="white", pady=10); bot.pack(fill='x')
        tk.Label(bot, text="Assign Grade:", bg="white").pack(side='left')
        g_cb = ttk.Combobox(bot, values=['1.0','1.25','1.5','1.75','2.0','2.25','2.5','2.75','3.0','5.0'], width=10)
        g_cb.pack(side='left', padx=5)
        
        def save():
            sel = tree.selection()
            if not sel: return
            item = tree.item(sel)['values']
            src = item[0]
            edits = int(item[3])
            
            if edits <= 0: return messagebox.showerror("Limit Reached", "You have edited this grade 2 times already.")
            
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute("""UPDATE enrollments e JOIN students s ON e.student_id=s.id 
                            SET e.grade=%s, e.edit_count=e.edit_count+1 
                            WHERE s.srcode=%s AND e.teacher_id=%s AND e.subject_name=%s""",
                            (g_cb.get(), src, self.current_user['id'], self.active_subject.get()))
                conn.commit()
            conn.close(); load(); messagebox.showinfo("Saved", "Grade Updated")
            
        tk.Button(bot, text="SAVE GRADE", command=save, bg=COLOR_SUCCESS, fg="white").pack(side='left', padx=10)

    def tab_announce(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab, text="  Announcements  ")
        card, content = create_card(tab, "Post to Students")
        card.pack(fill='both', expand=True, padx=50, pady=30)
        
        tk.Label(content, text="Target Year:", bg="white").pack(anchor='w')
        y_cb = ttk.Combobox(content, values=list(BLOCK_CONFIG.keys()), state='readonly'); y_cb.pack(fill='x', pady=5)
        
        tk.Label(content, text="Target Block (Optional):", bg="white").pack(anchor='w')
        b_cb = ttk.Combobox(content, state='readonly'); b_cb.pack(fill='x', pady=5)
        y_cb.bind("<<ComboboxSelected>>", lambda e: b_cb.config(values=["All Blocks"] + BLOCK_CONFIG[y_cb.get()]))
        
        tk.Label(content, text="Message:", bg="white").pack(anchor='w')
        msg = tk.Text(content, height=5, relief="solid", bd=1); msg.pack(fill='x', pady=5)
        
        def post():
            target = "Block" if b_cb.get() and b_cb.get() != "All Blocks" else "Year"
            val = b_cb.get() if target == "Block" else y_cb.get()
            
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute("INSERT INTO announcements (author_name, title, message, target, target_value) VALUES (%s,%s,%s,%s,%s)",
                            (self.current_user['name'], "Class Update", msg.get("1.0","end"), target, val))
                conn.commit()
            conn.close(); messagebox.showinfo("Posted", "Announcement Sent"); msg.delete("1.0","end")

        tk.Button(content, text="POST", command=post, bg=COLOR_PRIMARY, fg="white", pady=10).pack(fill='x', pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = TeacherApp(root)
    root.mainloop()
