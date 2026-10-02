import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pymysql
from database import get_db_connection
import database as db


class Student():
    def __init__(self,root, username="Admin"):
        self.root = root
        self.username=username
        self.root.title("Student Record")
        self.root.config(bg="#0F172A")

        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.width}x{self.height-80}+0+0")
        
        title_bar = tk.Frame(self.root, bg="#1E293B")
        title_bar.pack(side="top", fill="x")

        title_bar = tk.Frame(self.root, bg="#1E293B", height=60)
        title_bar.pack(side="top", fill="x")
        title_bar.pack_propagate(False)  # keep fixed height

        # RIGHT side items must be packed BEFORE the left title
        # ── Logout button (top-right) ────────────────────────────────────────
        logout_btn = tk.Button(title_bar,
                               text="⏻  Logout",
                               command=self.logout,
                               bd=0, relief="flat",
                               bg="#EF4444", fg="white",
                               activebackground="#B91C1C", activeforeground="white",
                               font=("Segoe UI", 11, "bold"),
                               padx=12, pady=6,
                               cursor="hand2")
        logout_btn.pack(side="right", padx=15, pady=10)

        # ── Username label (right of logout) ─────────────────────────────────
        user_lbl = tk.Label(title_bar,
                            text=f"👤  {self.username}",
                            font=("Segoe UI", 12, "bold"),
                            bg="#1E293B", fg="#F1F5F9",
                            padx=10, pady=6)
        user_lbl.pack(side="right", padx=5, pady=10)

        # ── App title (left) ─────────────────────────────────────────────────
        title = tk.Label(title_bar,
                         text="Prakruthi Student Record Management System",
                         bd=0, relief="flat",
                         bg="#1E293B", fg="#38BDF8",
                         font=("Georgia", 28, "bold"))
        title.pack(side="left", padx=50)
        

        # database connection and table creation
        self.conn = get_db_connection()
        self.create_student_table()

        self.optionFrameFun()
        self.detailFrameFun()
        self.tableFun()

        # Treeview styling is fully handled inside tableFun() via Dark.Treeview

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            from admin_login import AdminApp
            new_root = tk.Tk()
            AdminApp(new_root)
            new_root.mainloop()


    def tableFun(self):
        tabFrame = tk.Frame(self.detFrame, bd=0, bg="#0F172A")
        tabFrame.place(width=(self.width/2)+600, height=self.height-244, x=0, y=40)

        # ── Scrollbars ────────────────────────────────────────────────────
        x_scrol = tk.Scrollbar(tabFrame, orient="horizontal",
                               bg="#334155", troughcolor="#1E293B",
                               activebackground="#475569")
        x_scrol.pack(side="bottom", fill="x")

        y_scrol = tk.Scrollbar(tabFrame, orient="vertical",
                               bg="#334155", troughcolor="#1E293B",
                               activebackground="#475569")
        y_scrol.pack(side="right", fill="y")

        # ── Style matching the app colour palette ─────────────────────────
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Treeview",
                        background="#1E293B",
                        foreground="#F1F5F9",
                        fieldbackground="#0F172A",
                        bordercolor="#334155",
                        borderwidth=1,
                        relief="solid",
                        rowheight=36,
                        font=("Segoe UI", 11))
        style.configure("Dark.Treeview.Heading",
                        background="#0F172A",
                        foreground="#38BDF8",
                        bordercolor="#334155",
                        borderwidth=1,
                        relief="flat",
                        font=("Segoe UI", 12, "bold"))
        style.map("Dark.Treeview",
                  background=[("selected", "#818CF8")],
                  foreground=[("selected", "#0F172A")])

        # ── Treeview widget ───────────────────────────────────────────────
        cols = ("roll", "name", "address", "gender", "grade")
        self.table = ttk.Treeview(tabFrame,
                                  style="Dark.Treeview",
                                  xscrollcommand=x_scrol.set,
                                  yscrollcommand=y_scrol.set,
                                  columns=cols,
                                  show="headings")

        x_scrol.config(command=self.table.xview)
        y_scrol.config(command=self.table.yview)

        # ── Column headings and widths ────────────────────────────────────
        headers    = {"roll":"Roll No","name":"Name","address":"Address",
                      "gender":"Gender","grade":"Grade"}
        col_widths = {"roll":110,"name":200,"address":280,"gender":120,"grade":100}

        for col in cols:
            self.table.heading(col, text=headers[col])
            self.table.column(col, anchor="center",
                              width=col_widths[col], minwidth=60)

        # ── Alternating row colours ────────────────────────────────────────
        self.table.tag_configure("evenrow",
                                 background="#0F172A", foreground="#F1F5F9")
        self.table.tag_configure("oddrow",
                                 background="#1E293B", foreground="#F1F5F9")

        self.table.pack(fill="both", expand=1)
        self.load_table_data()

    def _format_student_row(self, row):
        row = list(row)
        row[0] = f"P{int(row[0]):03}"
        return row

    def _show_records(self, records):
        self.table.delete(*self.table.get_children())

        if not records:
            return

        for idx, row in enumerate(records):
            if row is None:
                continue
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.table.insert('', tk.END,
                              values=self._format_student_row(row),
                              tags=(tag,))

    def load_table_data(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("select * from student")
            data = cursor.fetchall()
            self._show_records(data)
            cursor.close()
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error: {e}")


    def optionFrameFun(self):
        self.optionFrameFun = tk.Frame(self.root, bd=0, relief="flat", bg="#1E293B")
        self.optionFrameFun.place(x=0, y=52, width=1500, height=60)

        btn_cfg = dict(bd=0, relief="flat", bg="#334155", fg="#F1F5F9",
                       width=15, font=("Segoe UI", 13, "bold"),
                       activebackground="#38BDF8", activeforeground="#0F172A",
                       cursor="hand2")

        buttons = [
            ("Summary",        self.summaryFrameFun),
            ("Add Student",    self.addFrameFun),
            ("Search Student", self.searchFrameFun),
            ("Update Record",  self.updFrameFun),
            ("Show All",       self.showAll),
            ("Remove Student", self.delFrameFun),
            ("Clear Screen",   self.delete_frame),
        ]

        for col, (text, cmd) in enumerate(buttons):
            tk.Button(self.optionFrameFun, text=text, command=cmd, **btn_cfg)\
              .grid(row=0, column=col, padx=5, pady=10)


    def detailFrameFun(self):
        self.detFrame = tk.Frame(self.root, bd=0, bg="#1E293B")
        self.detFrame.place(width=self.width/1, height=self.height-60,
                            x=self.width/500, y=115)

        lbl = tk.Label(self.detFrame, text="Record Details",
                       width=13, font=("Georgia", 20, "bold"),
                       bg="#1E293B", fg="#38BDF8")
        lbl.pack(side="top", fill="x")

    #summary frame and the logic 
    
    def summaryFrameFun(self):
        self.delete_frame()

        CARD_COLORS  = ["#164E63", "#312E81", "#14532D"]  # teal / indigo / green

        self.addFrame = tk.Frame(self.root, bg="#0F172A")
        self.addFrame.place(width=(self.width/2)+600, height=self.height-240, x=2, y=155)

        grades = [("8th Grade","8"), ("9th Grade","9"), ("10th Grade","10")]
        x_positions = [30, 450, 850]

        for (label, grade), x, color in zip(grades, x_positions,CARD_COLORS):
            total, male, female, others = db.get_totalstudents(grade)

            frame = tk.LabelFrame(self.addFrame, text=label, bg=color,
                                  fg="#38BDF8", font=("Segoe UI", 13, "bold"),
                                  bd=2, relief="ridge")
            frame.place(x=x, y=5, width=370, height=300)

            for row_i, (ltext, val) in enumerate([
                    (f"Total Students", total),
                    (f"Male",           male),
                    (f"Female",         female),
                    (f"Others",         others)]):
                tk.Label(frame, text=f"{ltext}: {val}",
                         bg=color, fg="#F1F5F9",
                         font=("Segoe UI", 15, "bold"))\
                  .grid(row=row_i, column=0, padx=15, pady=12, sticky="w")

    #this all are the easy metthod to give the size,color,place 
    # ── helpers ───────────────────────────────────────────────────────────────
    def _make_form_frame(self, height):
        f = tk.Frame(self.root, bd=2, relief="ridge", bg="#334155")
        f.place(width=self.width/3, height=height,
                x=(self.width/2)-300, y=160)
        return f

    def _lbl(self, parent, text):
        return tk.Label(parent, text=text, bg="#334155", fg="#BAE6FD",
                        font=("Segoe UI", 15, "bold"))

    def _entry(self, parent):
        return tk.Entry(parent, width=18, font=("Segoe UI", 15, "bold"),
                        bd=2, bg="#1E293B", fg="#F1F5F9",
                        insertbackground="#F1F5F9")

    def _combo(self, parent, values):
        c = ttk.Combobox(parent, width=17, values=values,
                         font=("Segoe UI", 15, "bold"))
        style = ttk.Style()
        style.configure("TCombobox", fieldbackground="#1E293B",
                         background="#1E293B", foreground="#F1F5F9")
        return c

    def _ok_btn(self, parent, cmd):
        return tk.Button(parent, command=cmd, text="Enter",
                         bd=0, relief="flat",
                         bg="#38BDF8", fg="#0F172A",
                         activebackground="#818CF8", activeforeground="#0F172A",
                         font=("Segoe UI", 20, "bold"), width=20, cursor="hand2")

    #add student frame

    def addFrameFun(self):
        self.delete_frame()
        self.addFrame = self._make_form_frame(self.height-300)

        self._lbl(self.addFrame, "Roll No:").grid(row=0, column=0, padx=5, pady=10)
        self.rollNo = self._entry(self.addFrame)
        self.rollNo.grid(row=0, column=1, padx=5, pady=10)

        self._lbl(self.addFrame, "Name:").grid(row=1, column=0, padx=5, pady=10)
        self.name = self._entry(self.addFrame)
        self.name.grid(row=1, column=1, padx=5, pady=10)

        self._lbl(self.addFrame, "Address:").grid(row=2, column=0, padx=5, pady=10)
        self.address = self._entry(self.addFrame)
        self.address.grid(row=2, column=1, padx=5, pady=10)

        self._lbl(self.addFrame, "Gender:").grid(row=3, column=0, padx=5, pady=10)
        self.gender = self._combo(self.addFrame, ("Male","Female","Others"))
        self.gender.set("Select Option")
        self.gender.grid(row=3, column=1, padx=5, pady=10)

        self._lbl(self.addFrame, "Grade:").grid(row=4, column=0, padx=5, pady=10)
        self.grade = self._combo(self.addFrame, ("8","9","10"))
        self.grade.set("Select Option")
        self.grade.grid(row=4, column=1, padx=5, pady=10)

        self._ok_btn(self.addFrame, self.addFun)\
            .grid(row=5, column=0, padx=30, pady=25, columnspan=2)

    #search student frame

    def searchFrameFun(self):
        self.delete_frame()
        self.addFrame = self._make_form_frame(self.height-400)

        self._lbl(self.addFrame, "Select:").grid(row=0, column=0, padx=20, pady=20)
        self.option = self._combo(self.addFrame, ("rollNo","Name"))
        self.option.set("Select Option")
        self.option.grid(row=0, column=1, padx=10, pady=20)

        self._lbl(self.addFrame, "Value:").grid(row=1, column=0, padx=20, pady=20)
        self.value = self._entry(self.addFrame)
        self.value.grid(row=1, column=1, padx=10, pady=20)

        self._ok_btn(self.addFrame, self.searchFun)\
            .grid(row=2, column=0, padx=30, pady=20, columnspan=2)

    #update student frame

    def updFrameFun(self):
        self.delete_frame()
        self.addFrame = self._make_form_frame(self.height-350)

        self._lbl(self.addFrame, "Select:").grid(row=0, column=0, padx=20, pady=20)
        self.option = self._combo(self.addFrame, ("Name","gender","grade"))
        self.option.set("Select Option")
        self.option.grid(row=0, column=1, padx=10, pady=20)

        self._lbl(self.addFrame, "New Value:").grid(row=1, column=0, padx=20, pady=20)
        self.value = self._entry(self.addFrame)
        self.value.grid(row=1, column=1, padx=10, pady=20)

        self._lbl(self.addFrame, "Roll No:").grid(row=2, column=0, padx=20, pady=20)
        self.roll = self._entry(self.addFrame)
        self.roll.grid(row=2, column=1, padx=10, pady=20)

        self._ok_btn(self.addFrame, self.updFun)\
            .grid(row=3, column=0, padx=30, pady=25, columnspan=2)

    #delete student frame

    def delFrameFun(self):
        self.delete_frame()
        self.addFrame = self._make_form_frame(self.height-500)

        self._lbl(self.addFrame, "Roll No:").grid(row=0, column=0, padx=20, pady=25)
        self.rollNo = self._entry(self.addFrame)
        self.rollNo.grid(row=0, column=1, padx=10, pady=25)

        self._ok_btn(self.addFrame, self.delFun)\
            .grid(row=1, column=0, padx=30, pady=25, columnspan=2)


    def delete_frame(self):
        if hasattr(self, 'addFrame'):
            self.addFrame.place_forget()


    # ── DB logic (unchanged) ──────────────────────────────────────────────────

    #add student logic

    def addFun(self):

        rn = self.rollNo.get()
        name = self.name.get()
        address = self.address.get()
        gender = self.gender.get()
        grade = self.grade.get()

        if rn and name and address and gender and grade:
            rNo = int(rn)
            grade = int(grade)
            try:
                cursor = self.conn.cursor()
                cursor.execute("insert into student(rollNo,name,address,gender,grade) values(%s,%s,%s,%s,%s)",
                               (rNo, name, address, gender, grade))
                self.conn.commit()
                tk.messagebox.showinfo("Success", f"Student {name} with Roll_No.{rNo} is Registered!")
                self.delete_frame()
                cursor.execute("select * from student where rollNo=%s", (rNo,))
                row = cursor.fetchone()
                self._show_records([row])
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error: {e}")
                self.delete_frame()
            finally:
                cursor.close()
        else:
            tk.messagebox.showerror("Error", "Please Fill All Input Fields!")

    #search student logic

    def searchFun(self):
        opt = self.option.get()
        val = self.value.get()

        if opt == "rollNo ":
            rn = int(val)
            try:
                cursor = self.conn.cursor()
                cursor.execute("select * from student where rollNo=%s", (rn,))
                row = cursor.fetchone()
                self._show_records([row])
                self.delete_frame()
                cursor.close
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error: {e}")
        else:
            query = "select * from student where rollNo=%s" if opt == "rollNo" \
                    else "select * from student where name=%s"
            try:
                cursor = self.conn.cursor()
                cursor.execute(query, (val,))
                data = cursor.fetchall()
                self._show_records(data)
                self.delete_frame()
                cursor.close()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error: {e}")

    #update student logic            

    def updFun(self):
        opt = self.option.get()
        val = self.value.get()
        rNo = int(self.roll.get())
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"update student set {opt}=%s where rollNo=%s", (val, rNo))
            self.conn.commit()
            tk.messagebox.showinfo("Success", f"Record Updated for Roll_No.{rNo}")
            self.delete_frame()
            cursor.execute("select * from student where rollNo=%s", (rNo,))
            row = cursor.fetchone()
            self._show_records([row])
            cursor.close()
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error: {e}")

    #show all student logic       

    def showAll(self):
        self.delete_frame()
        self.load_table_data()

    #delete student logic

    def delFun(self):
        self.delete_frame()
        rNo = int(self.rollNo.get())
        cursor = self.conn.cursor()
        try:
            cursor.execute("delete from student where rollNo=%s", (rNo,))
            self.conn.commit()
            tk.messagebox.showinfo("Success", f"Student with Roll_No.{rNo} is Removed")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error: {e}")
        finally:
            self.con.close()
            self.destroyFrame()

    def create_student_table(self):
        query = """create table if not exists student(
                     rollNo int primary key,
                     name varchar(50) not null,
                     address varchar(200),
                     gender varchar(100),
                     grade int)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()
            print("Student table created successfully!")
            cursor.close()
        except Exception as e:
            print(f"Error: {e}")

#root = tk.Tk()
#obj = Student(root)
#root.mainloop()