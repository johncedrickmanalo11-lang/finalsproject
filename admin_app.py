import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from common import *

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Dashboard - Enterprise Edition")
        self.root.geometry("1400x850")
        self.root.configure(bg=COLOR_BG)
        self.db = DatabaseConnection()
        setup_styles()
        self.show_login()

    def clear_screen(self):
        for widget in self.root.winfo_children(): widget.destroy()

    # ================= LOGIN & FORGOT PASSWORD =================
    def show_login(self):
        self.clear_screen()
        bg = tk.Frame(self.root, bg=COLOR_BG); bg.pack(fill='both', expand=True)
        card = tk.Frame(bg, bg="white", padx=60, pady=60, relief="solid", bd=1)
        card.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(card, text="ADMINISTRATOR", font=("Segoe UI", 24, "bold"), bg="white", fg=COLOR_TEXT_MAIN).pack(pady=(0, 30))
        
        tk.Label(card, text="Username", bg="white", fg="gray").pack(anchor='w')
        u_ent = tk.Entry(card, width=35, font=("Segoe UI", 11), relief="solid", bd=1, bg="#F8FAFC"); u_ent.pack(pady=(5,15), ipady=5)
        
        tk.Label(card, text="Password", bg="white", fg="gray").pack(anchor='w')
        p_ent = tk.Entry(card, width=35, show='•', font=("Segoe UI", 11), relief="solid", bd=1, bg="#F8FAFC"); p_ent.pack(pady=(5,10), ipady=5)
        
        def login():
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM admins WHERE username=%s AND password=%s", (u_ent.get(), p_ent.get()))
                    user = cur.fetchone()
                    if user: self.dashboard(user)
                    else: messagebox.showerror("Error", "Invalid Admin Credentials")
                conn.close()

        tk.Button(card, text="LOGIN DASHBOARD", command=login, bg=COLOR_PRIMARY, fg="white", font=("Segoe UI", 10, "bold"), width=34, pady=12, relief='flat').pack(pady=(10, 5))
        tk.Button(card, text="Forgot Password?", command=self.show_forgot_password, bg="white", fg=COLOR_DANGER, bd=0, cursor="hand2").pack()

    def show_forgot_password(self):
        win = tk.Toplevel(self.root); win.title("Reset Admin Password"); win.geometry("400x350"); win.configure(bg="white")
        tk.Label(win, text="Reset Password", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=20)
        tk.Label(win, text="Username:", bg="white").pack(anchor='w', padx=40)
        u_ent = tk.Entry(win, width=30, relief="solid", bd=1); u_ent.pack(pady=5)
        tk.Label(win, text="Admin SR Code (Security Key):", bg="white").pack(anchor='w', padx=40)
        s_ent = tk.Entry(win, width=30, relief="solid", bd=1); s_ent.pack(pady=5)
        tk.Label(win, text="New Password:", bg="white").pack(anchor='w', padx=40)
        new_p = tk.Entry(win, width=30, show="•", relief="solid", bd=1); new_p.pack(pady=5)
        
        def reset():
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM admins WHERE username=%s AND srcode=%s", (u_ent.get(), s_ent.get()))
                    if cur.fetchone():
                        cur.execute("UPDATE admins SET password=%s WHERE username=%s", (new_p.get(), u_ent.get()))
                        conn.commit(); messagebox.showinfo("Success", "Password has been reset.", parent=win); win.destroy()
                    else: messagebox.showerror("Error", "Invalid Username or SR Code.", parent=win)
                conn.close()
        tk.Button(win, text="RESET PASSWORD", command=reset, bg=COLOR_WARNING, fg="white", pady=5, width=20).pack(pady=20)

    # ================= DASHBOARD =================
    def dashboard(self, user):
        self.clear_screen()
        sidebar = tk.Frame(self.root, bg=COLOR_SIDEBAR, width=260)
        sidebar.pack(side='left', fill='y'); sidebar.pack_propagate(False)
        
        tk.Label(sidebar, text="ADMIN DASHBOARD", font=("Segoe UI", 18, "bold"), fg="white", bg=COLOR_SIDEBAR).pack(pady=(40, 10))
        tk.Label(sidebar, text=f"Welcome, {user['name']}", font=("Segoe UI", 10), fg="#94A3B8", bg=COLOR_SIDEBAR).pack(pady=(0, 40))
        
        create_sidebar_btn(sidebar, "Overview & Analytics", "📊", lambda: self.switch_tab(0))
        create_sidebar_btn(sidebar, "Master Student List", "👥", lambda: self.switch_tab(1))
        create_sidebar_btn(sidebar, "Teachers & Subjects", "👨‍🏫", lambda: self.switch_tab(2))
        create_sidebar_btn(sidebar, "Grades Summary", "🎓", lambda: self.switch_tab(3))
        create_sidebar_btn(sidebar, "Drop Requests", "📩", lambda: self.switch_tab(4))
        create_sidebar_btn(sidebar, "Announcements", "📢", lambda: self.switch_tab(5))
        create_sidebar_btn(sidebar, "Logout", "🚪", self.show_login).pack(side='bottom', fill='x', pady=20)

        self.main_area = tk.Frame(self.root, bg=COLOR_BG)
        self.main_area.pack(side='right', fill='both', expand=True)
        self.nb = ttk.Notebook(self.main_area)
        self.nb.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.tab_analytics(self.nb)
        self.tab_students(self.nb)
        self.tab_teachers(self.nb)
        self.tab_all_grades(self.nb)
        self.tab_drops(self.nb)
        self.tab_announce(self.nb)
        ttk.Style().layout('TNotebook.Tab', []) 

    def switch_tab(self, idx): self.nb.select(idx)

    def create_stat_tile(self, parent, title, value, icon, color):
        tile = tk.Frame(parent, bg="white", height=90)
        tile.pack_propagate(False)
        strip = tk.Frame(tile, bg=color, width=5); strip.pack(side='left', fill='y')
        content = tk.Frame(tile, bg="white", padx=15, pady=10)
        content.pack(side='left', fill='both', expand=True)
        tk.Label(content, text=title, font=("Segoe UI", 9, "bold"), fg="#64748B", bg="white").pack(anchor='nw')
        tk.Label(content, text=str(value), font=("Segoe UI", 24, "bold"), fg=COLOR_TEXT_MAIN, bg="white").pack(anchor='nw', pady=(0,0))
        tk.Label(tile, text=icon, font=("Segoe UI", 24), fg=color, bg="white").pack(side='right', padx=20)
        return tile

    # --- TAB 1: ANALYTICS ---
    def tab_analytics(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab)
        stats_frame = tk.Frame(tab, bg=COLOR_BG); stats_frame.pack(fill='x', pady=(0, 20))
        
        conn = self.db.get_connection()
        c_stud, c_teach, c_enroll, c_req = 0, 0, 0, 0
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) as c FROM students"); c_stud = cur.fetchone()['c']
                cur.execute("SELECT COUNT(*) as c FROM teachers"); c_teach = cur.fetchone()['c']
                cur.execute("SELECT COUNT(DISTINCT student_id) as c FROM enrollments"); c_enroll = cur.fetchone()['c']
                cur.execute("SELECT COUNT(*) as c FROM drop_requests WHERE status='Pending'"); c_req = cur.fetchone()['c']
            conn.close()

        stats_frame.grid_columnconfigure(0, weight=1); stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1); stats_frame.grid_columnconfigure(3, weight=1)
        self.create_stat_tile(stats_frame, "Total Students", c_stud, "👥", COLOR_PRIMARY).grid(row=0, column=0, padx=5, sticky='ew')
        self.create_stat_tile(stats_frame, "Total Teachers", c_teach, "👨‍🏫", COLOR_SUCCESS).grid(row=0, column=1, padx=5, sticky='ew')
        self.create_stat_tile(stats_frame, "Enrolled Students", c_enroll, "🎓", COLOR_PURPLE).grid(row=0, column=2, padx=5, sticky='ew')
        self.create_stat_tile(stats_frame, "Pending Requests", c_req, "📩", COLOR_WARNING).grid(row=0, column=3, padx=5, sticky='ew')

        graphs_container = tk.Frame(tab, bg=COLOR_BG); graphs_container.pack(fill='both', expand=True)
        left_panel = tk.Frame(graphs_container, bg=COLOR_BG); left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        card1, c1 = create_card(left_panel, "Student Population (By Block/Year)")
        card1.pack(fill='both', expand=True)
        self.plot_bar_students(c1)

        right_panel = tk.Frame(graphs_container, bg=COLOR_BG); right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        card2, c2 = create_card(right_panel, "Pass vs Fail Rates Analysis")
        card2.pack(fill='both', expand=True)
        
        ctrl = tk.Frame(c2, bg="white"); ctrl.pack(fill='x', pady=(0,10))
        tk.Label(ctrl, text="Subject:", bg="white", font=("Segoe UI", 8)).grid(row=0, column=0, sticky='w')
        sub_cb = ttk.Combobox(ctrl, state='readonly', width=30); sub_cb.grid(row=1, column=0, sticky='ew', padx=2)
        tk.Label(ctrl, text="Year:", bg="white", font=("Segoe UI", 8)).grid(row=0, column=1, sticky='w')
        yr_cb = ttk.Combobox(ctrl, values=["All Years"] + list(BLOCK_CONFIG.keys()), state='readonly', width=15); yr_cb.grid(row=1, column=1, sticky='ew', padx=2); yr_cb.current(0)
        tk.Label(ctrl, text="Block:", bg="white", font=("Segoe UI", 8)).grid(row=0, column=2, sticky='w')
        blk_cb = ttk.Combobox(ctrl, values=["All Blocks"], state='readonly', width=15); blk_cb.grid(row=1, column=2, sticky='ew', padx=2); blk_cb.current(0)
        yr_cb.bind("<<ComboboxSelected>>", lambda e: (blk_cb.config(values=["All Blocks"] + BLOCK_CONFIG.get(yr_cb.get(), [])), blk_cb.current(0)))
        
        conn = self.db.get_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT subject_name FROM enrollments")
                subs = [r['subject_name'] for r in cur.fetchall()]
                sub_cb['values'] = ["All Subjects"] + subs
            conn.close()
        sub_cb.current(0)
        chart_frame = tk.Frame(c2, bg="white"); chart_frame.pack(fill='both', expand=True)

        def generate_pass_fail():
            for w in chart_frame.winfo_children(): w.destroy()
            s, y, b = sub_cb.get(), yr_cb.get(), blk_cb.get()
            query = """SELECT e.grade FROM enrollments e JOIN students s ON e.student_id = s.id WHERE e.grade != 'N/A'"""
            params = []
            if s != "All Subjects": query += " AND e.subject_name=%s"; params.append(s)
            if y != "All Years": query += " AND s.year_level=%s"; params.append(y)
            if b != "All Blocks": query += " AND s.block=%s"; params.append(b)
            pass_c, fail_c = 0, 0
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute(query, tuple(params))
                    for r in cur.fetchall():
                        try:
                            if float(r['grade']) <= 3.0: pass_c += 1
                            else: fail_c += 1
                        except: pass 
                conn.close()
            if pass_c == 0 and fail_c == 0: tk.Label(chart_frame, text="No Data Available", bg="white").pack(expand=True); return
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.pie([pass_c, fail_c], labels=[f'Pass\n({pass_c})', f'Fail\n({fail_c})'], autopct='%1.1f%%', colors=[COLOR_SUCCESS, COLOR_DANGER], startangle=90)
            ax.set_title(f"Pass Rate: {s[:15]}...", fontsize=9)
            canvas = FigureCanvasTkAgg(fig, master=chart_frame); canvas.draw(); canvas.get_tk_widget().pack(fill='both', expand=True)
        tk.Button(ctrl, text="GO", command=generate_pass_fail, bg=COLOR_PRIMARY, fg="white", font=("Segoe UI", 8)).grid(row=1, column=3, padx=5)
        generate_pass_fail()

    def plot_bar_students(self, parent):
        conn = self.db.get_connection()
        data = {}
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT year_level, block, COUNT(*) as c FROM students GROUP BY year_level, block ORDER BY year_level, block")
                for r in cur.fetchall(): data[f"{r['year_level']}\n{r['block']}"] = r['c']
            conn.close()
        if not data: tk.Label(parent, text="No Student Data", bg="white").pack(expand=True); return
        fig, ax = plt.subplots(figsize=(5, 4))
        bars = ax.bar(data.keys(), data.values(), color=COLOR_PRIMARY)
        ax.set_ylabel("No. of Students"); ax.grid(axis='y', linestyle='--', alpha=0.5)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8); plt.tight_layout()
        for bar in bars: ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(), f'{int(bar.get_height())}', ha='center', va='bottom', fontsize=8)
        canvas = FigureCanvasTkAgg(fig, master=parent); canvas.draw(); canvas.get_tk_widget().pack(fill='both', expand=True)

    # --- TAB 2: MASTER STUDENT LIST ---
    def tab_students(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab)
        card, content = create_card(tab, "Master Student List")
        card.pack(fill='both', expand=True)
        f_filt = tk.Frame(content, bg="white"); f_filt.pack(fill='x', pady=(0,10))
        tk.Label(f_filt, text="Filter By Year:", bg="white").pack(side='left')
        y_cb = ttk.Combobox(f_filt, values=["All"] + list(BLOCK_CONFIG.keys()), state='readonly', width=15); y_cb.pack(side='left', padx=5); y_cb.current(0)
        tk.Label(f_filt, text="Block:", bg="white").pack(side='left', padx=(10,0))
        b_cb = ttk.Combobox(f_filt, values=["All"], state='readonly', width=15); b_cb.pack(side='left', padx=5); b_cb.current(0)
        y_cb.bind("<<ComboboxSelected>>", lambda e: (b_cb.config(values=["All"] + BLOCK_CONFIG.get(y_cb.get(), [])), b_cb.current(0)))
        tree = ttk.Treeview(content, columns=("SR", "Name", "Year", "Block", "Course"), show="headings")
        for c in ["SR", "Name", "Year", "Block", "Course"]: tree.heading(c, text=c)
        tree.pack(fill='both', expand=True)
        def load_stud():
            for i in tree.get_children(): tree.delete(i)
            qry = "SELECT * FROM students WHERE 1=1"
            prms = []
            if y_cb.get() != "All": qry += " AND year_level=%s"; prms.append(y_cb.get())
            if b_cb.get() != "All": qry += " AND block=%s"; prms.append(b_cb.get())
            qry += " ORDER BY year_level, block, name"
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute(qry, tuple(prms))
                    for r in cur.fetchall(): tree.insert("", "end", values=(r['srcode'], r['name'], r['year_level'], r['block'], r['course']))
                conn.close()
            autosize_tree(tree)
        tk.Button(f_filt, text="Apply Filter", command=load_stud, bg=COLOR_PRIMARY, fg="white").pack(side='left', padx=15)
        load_stud()

    # --- TAB 3: TEACHERS & SUBJECTS (UPDATED: FORM-BASED ADD) ---
    def tab_teachers(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab)
        card, content = create_card(tab, "Teachers & Subject Loads")
        card.pack(fill='both', expand=True)

        # Updated: Form-based Input (No Commas needed)
        f1 = tk.Frame(content, bg="white", bd=1, relief="solid", padx=10, pady=10)
        f1.pack(fill='x', pady=(0, 10))
        tk.Label(f1, text="SUBJECT ASSIGNMENT FORM", font=("Segoe UI", 10, "bold"), bg="white", fg=COLOR_PRIMARY).pack(anchor='w')
        
        f_form = tk.Frame(f1, bg="white"); f_form.pack(fill='x', pady=5)
        tk.Label(f_form, text="1. Select Teacher from list below", bg="white", fg="gray").pack(side='left', padx=(0,20))
        tk.Label(f_form, text="2. Enter One Subject Name:", bg="white", font=("Segoe UI", 9, "bold")).pack(side='left')
        sub_ent = tk.Entry(f_form, width=25, relief="solid", bd=1); sub_ent.pack(side='left', padx=5)

        tree = ttk.Treeview(content, columns=("SR", "Name", "Subjects"), show="headings")
        tree.heading("SR", text="Teacher ID"); tree.heading("Name", text="Name"); tree.heading("Subjects", text="Handled Subjects")
        tree.pack(fill='both', expand=True)

        def load_t():
            for i in tree.get_children(): tree.delete(i)
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT srcode, name, subject FROM teachers ORDER BY name")
                    for r in cur.fetchall(): tree.insert("", "end", values=(r['srcode'], r['name'], r['subject']))
                conn.close()
            autosize_tree(tree)

        def add_single_subject():
            sel = tree.selection()
            if not sel: return messagebox.showwarning("Selection Missing", "Please click on a teacher in the list first.")
            new_subject = sub_ent.get().strip()
            if not new_subject: return messagebox.showwarning("Input Missing", "Please enter a subject name.")

            tid = tree.item(sel)['values'][0]
            current_str = str(tree.item(sel)['values'][2]) # Get current subjects string
            
            # Logic: Parse list, check duplicate, append
            if current_str == 'None' or not current_str:
                current_list = []
            else:
                current_list = [s.strip() for s in current_str.split(',')]

            # Check for duplicate
            if new_subject in current_list:
                messagebox.showerror("Duplicate", f"Teacher is already assigned to '{new_subject}'")
                return

            # Append and Join
            current_list.append(new_subject)
            updated_str = ", ".join(current_list)

            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE teachers SET subject=%s WHERE srcode=%s", (updated_str, tid))
                    conn.commit()
                conn.close()
                load_t()
                sub_ent.delete(0, 'end')
                messagebox.showinfo("Success", f"Added '{new_subject}' successfully!")

        tk.Button(f_form, text="➕ ADD SUBJECT", command=add_single_subject, bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 9, "bold")).pack(side='left', padx=10)
        
        # Clear Button (Optional but helpful)
        def clear_subjects():
            sel = tree.selection()
            if not sel: return
            if not messagebox.askyesno("Confirm", "Remove ALL subjects for this teacher?"): return
            tid = tree.item(sel)['values'][0]
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute("UPDATE teachers SET subject='' WHERE srcode=%s", (tid,))
                conn.commit()
            conn.close(); load_t()

        tk.Button(f_form, text="🗑️ CLEAR ALL", command=clear_subjects, bg=COLOR_DANGER, fg="white", font=("Segoe UI", 8)).pack(side='right')
        load_t()

    # --- TAB 4: GRADES SUMMARY (Filtered) ---
    def tab_all_grades(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab)
        card, content = create_card(tab, "Academic Records Summary")
        card.pack(fill='both', expand=True)
        
        f_filt = tk.Frame(content, bg="white"); f_filt.pack(fill='x', pady=(0,10))
        tk.Label(f_filt, text="Filter By Year:", bg="white").pack(side='left')
        y_cb = ttk.Combobox(f_filt, values=["All"] + list(BLOCK_CONFIG.keys()), state='readonly', width=15); y_cb.pack(side='left', padx=5); y_cb.current(0)
        tk.Label(f_filt, text="Block:", bg="white").pack(side='left', padx=(10,0))
        b_cb = ttk.Combobox(f_filt, values=["All"], state='readonly', width=15); b_cb.pack(side='left', padx=5); b_cb.current(0)
        y_cb.bind("<<ComboboxSelected>>", lambda e: (b_cb.config(values=["All"] + BLOCK_CONFIG.get(y_cb.get(), [])), b_cb.current(0)))

        tree = ttk.Treeview(content, columns=("Student", "Year", "Block", "Subject", "Teacher", "Grade"), show="headings")
        tree.heading("Student", text="Student Name"); tree.heading("Year", text="Year")
        tree.heading("Block", text="Block"); tree.heading("Subject", text="Subject")
        tree.heading("Teacher", text="Teacher"); tree.heading("Grade", text="Grade")
        tree.column("Grade", width=80, anchor='center')
        tree.pack(fill='both', expand=True)
        
        avg_lbl = tk.Label(content, text="Average Grade: --", font=("Segoe UI", 12, "bold"), bg=COLOR_BG, fg=COLOR_PRIMARY)
        avg_lbl.pack(fill='x', pady=10)

        def load_grades():
            for i in tree.get_children(): tree.delete(i)
            query = """SELECT s.name, s.year_level, s.block, e.subject_name, t.name as tname, e.grade 
                        FROM enrollments e JOIN students s ON e.student_id = s.id 
                        JOIN teachers t ON e.teacher_id = t.id WHERE e.grade != 'N/A'"""
            params = []
            if y_cb.get() != "All": query += " AND s.year_level = %s"; params.append(y_cb.get())
            if b_cb.get() != "All": query += " AND s.block = %s"; params.append(b_cb.get())
            query += " ORDER BY s.year_level, s.block, s.name"

            total, count = 0, 0
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute(query, tuple(params))
                    for r in cur.fetchall():
                        tree.insert("", "end", values=(r['name'], r['year_level'], r['block'], r['subject_name'], r['tname'], r['grade']))
                        try: total += float(r['grade']); count += 1
                        except: pass
                conn.close()
            avg = round(total / count, 2) if count > 0 else 0
            avg_lbl.config(text=f"Average Grade (Filtered): {avg}")
            autosize_tree(tree)
        tk.Button(f_filt, text="Apply Filter", command=load_grades, bg=COLOR_PRIMARY, fg="white").pack(side='left', padx=15)
        load_grades()

    # --- TAB 5: DROP REQUESTS ---
    def tab_drops(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab)
        card, content = create_card(tab, "Drop Requests Management")
        card.pack(fill='both', expand=True)
        tree = ttk.Treeview(content, columns=("ID", "Student", "Subject", "Reason", "Status"), show="headings")
        for c in ["ID", "Student", "Subject", "Reason", "Status"]: tree.heading(c, text=c)
        tree.pack(fill='both', expand=True)

        def load_d():
            for i in tree.get_children(): tree.delete(i)
            conn = self.db.get_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM drop_requests WHERE status='Pending'")
                    for r in cur.fetchall(): tree.insert("", "end", values=(r['id'], r['student_name'], r['subject'], r['reason'], r['status']))
                conn.close()
            autosize_tree(tree)

        def process(action_type):
            sel = tree.selection()
            if not sel: return messagebox.showwarning("Select", "Select a request first.")
            vals = tree.item(sel)['values']; rid, sub = vals[0], vals[2]
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute("UPDATE drop_requests SET status=%s WHERE id=%s", (action_type, rid))
                cur.execute("SELECT student_id FROM drop_requests WHERE id=%s", (rid,))
                sid = cur.fetchone()['student_id']
                cur.execute("INSERT INTO notifications (user_id, message) VALUES (%s,%s)", (sid, f"Your drop request for {sub} was {action_type}."))
                if action_type == "Approved": cur.execute("DELETE FROM enrollments WHERE student_id=%s AND subject_name=%s", (sid, sub))
                conn.commit()
            conn.close(); load_d(); messagebox.showinfo("Done", f"Request {action_type}")
        f_btn = tk.Frame(content, bg="white", pady=10); f_btn.pack(fill='x')
        tk.Button(f_btn, text="✅ APPROVE SELECTED", command=lambda: process("Approved"), bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 10, "bold")).pack(side='left', padx=5)
        tk.Button(f_btn, text="❌ REJECT SELECTED", command=lambda: process("Rejected"), bg=COLOR_DANGER, fg="white", font=("Segoe UI", 10, "bold")).pack(side='left', padx=5)
        load_d()

    # --- TAB 6: ANNOUNCEMENTS ---
    def tab_announce(self, nb):
        tab = tk.Frame(nb, bg=COLOR_BG); nb.add(tab)
        card, content = create_card(tab, "Broadcast Announcement")
        card.pack(fill='both', expand=True, padx=100, pady=40)
        tk.Label(content, text="Target:", bg="white").pack(anchor='w')
        tgt = ttk.Combobox(content, values=["All Students", "All Teachers"], state='readonly'); tgt.pack(fill='x', pady=5); tgt.current(0)
        tk.Label(content, text="Title:", bg="white").pack(anchor='w'); tit = tk.Entry(content, relief="solid", bd=1); tit.pack(fill='x', pady=5)
        tk.Label(content, text="Message:", bg="white").pack(anchor='w'); msg = tk.Text(content, height=5, relief="solid", bd=1); msg.pack(fill='x', pady=5)
        def send():
            t_map = {"All Students": "Student", "All Teachers": "Teacher"}
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute("INSERT INTO announcements (author_name, title, message, target, target_value) VALUES (%s,%s,%s,%s,%s)", ("Admin", tit.get(), msg.get("1.0","end"), t_map[tgt.get()], ""))
                conn.commit()
            conn.close(); messagebox.showinfo("Sent", "Announcement Posted"); tit.delete(0,'end'); msg.delete("1.0",'end')
        tk.Button(content, text="POST ANNOUNCEMENT", command=send, bg=COLOR_PRIMARY, fg="white", pady=10).pack(fill='x', pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()
