import tkinter as tk
from tkinter import messagebox
import pymysql
import hashlib
from database import get_db_connection
import os
from PIL import Image, ImageTk

         
"""take a readable password (like "Admin123") and turn it into a long, 
  scrambled string of characters that cannot be reversed.
  hashlib.sha256(...) -> Secure Hash Algorithm 256.
  .hexdigest() -> returns the hash as a hexadecimal string.
"""
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Login")
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.width}x{self.height}+0+0")
        self.load_background()
        self.login_frame()
        self.create_admin_table()

    

    def login_frame(self):
        
        self.loginFrame = tk.Frame(self.root, bg="#3AADCD")
        self.loginFrame.place(x=130, y=25, width=350, height=350)

        admLbl = tk.Label(self.loginFrame, text="Admin Login", font=("Arial", 20,"bold"), bg="#76C4F5")
        admLbl.pack(pady=20)

        tk.Label(self.loginFrame, text="Username", bg="#96CFDE").pack()
        self.user_entry = tk.Entry(self.loginFrame)
        self.user_entry.pack(pady=7)

        tk.Label(self.loginFrame, text="Password", bg="#96B9DE").pack()
        self.pass_entry = tk.Entry(self.loginFrame, show="*")
        self.pass_entry.pack(pady=5)

        tk.Button(self.loginFrame, text="Login", command=self.login_logic, 
                bg="blue", fg="white", width=15).pack(pady=20)
        
        tk.Button(self.loginFrame, text="Go to Register", 
                command=self.register_frame, width=15).pack()
        
    def register_frame(self):
        # self.clear_screen()
        self.loginFrame = tk.Frame(self.root, bg="#96C9DE")
        self.loginFrame.place(x=130, y=25, width=350, height=350)

        admLbl = tk.Label(self.loginFrame, text="Admin Rigister", font=("Arial", 20,"bold"))
        admLbl.pack(pady=20)
        
        tk.Label(self.loginFrame, text="Username", bg="#8DC6DF").pack()
        self.new_user = tk.Entry(self.loginFrame)
        self.new_user.pack(pady=5)
        
        tk.Label(self.loginFrame, text="Password", bg="#96C3DE").pack()
        self.new_pass = tk.Entry(self.loginFrame, show="*")
        self.new_pass.pack(pady=5)

        tk.Label(self.loginFrame, text="Confirm Password", bg="#96CDDE").pack()
        self.confirm_pass = tk.Entry(self.loginFrame, show="*")
        self.confirm_pass.pack(pady=5)  
        
        tk.Button(self.loginFrame, text="Register", command=self.register_logic, bg="green", fg="white").pack(pady=20)
        tk.Button(self.loginFrame, text="Back to Login", command=self.login_frame).pack()

    def login_logic(self):
        db = get_db_connection()
        cursor = db.cursor()
        hashed = hash_password(self.pass_entry.get())
        
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password_hash=%s", (self.user_entry.get(), hashed))
        result = cursor.fetchone()
        if result:
            messagebox.showinfo("Success", f"Welcome, {self.user_entry.get()}!")
            self.launch_student_app()

        else:
            messagebox.showerror("Error", "Invalid Credentials")
            
        db.close()


   
    def register_logic(self):
        db = get_db_connection()
        cursor = db.cursor()
        hashed = hash_password(self.new_pass.get())

        if self.new_pass.get() != self.confirm_pass.get():
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        try:
            cursor.execute("INSERT INTO admin(username, password_hash) VALUES (%s, %s)", (self.new_user.get(), hashed))
            db.commit()
            messagebox.showinfo("Success", "Admin Registered!")
            messagebox.showinfo("Success", "Kindly login with your new credentials")
            self.login_frame()
        except pymysql.Error:
            messagebox.showerror("Error", "Insertion error")
        db.close()

    def create_admin_table(self):
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL
            )
        """)
        db.commit()
        db.close()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def launch_student_app(self):
        logged_in_user = self.user_entry.get()   
        self.root.destroy()
        from student import Student
        new_root = tk.Tk()
        quiz = Student(new_root, username=logged_in_user)  
        new_root.mainloop()
    
    def load_background(self):
        try:
            self.base_path = os.path.dirname( __file__ )
            # print("Base Path ",self.base_path)
            img_path = os.path.join(self.base_path, "assets", "bg7.jpg")
            # print("Image Path ",img_path)
            
            # img_path = "assets/forest.jpg"    
             
            image = Image.open(img_path)
            image = image.resize((self.width,self.height))
            self.bg_image = ImageTk.PhotoImage(image)

            bg_label = tk.Label(self.root, image=self.bg_image)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        except Exception as e:
            self.root.configure(bg="#9cd7e6")
            print(f"Error : {e}")

# program entry point
if __name__ == "__main__":
    print("programe started")
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()