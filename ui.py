import tkinter as tk
from tkinter import messagebox, ttk
import cv2
from PIL import Image, ImageTk
import database
import iris_processing
import matcher

MATCH_THRESHOLD = 30  # Minimum number of good matches required for authentication

class IrisApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("800x650")
        
        # Open video source (0 for default webcam)
        self.vid = cv2.VideoCapture(0)
        
        # Create a canvas that can fit the video source size
        self.canvas = tk.Canvas(window, width=640, height=480, bg="black")
        self.canvas.pack(pady=10)
        
        # Current extracted features
        self.current_left_desc = None
        self.current_right_desc = None
        
        # Frame for controls
        self.control_frame = tk.Frame(window)
        self.control_frame.pack(fill=tk.X, padx=20)
        
        # Registration Frame
        self.reg_frame = tk.LabelFrame(self.control_frame, text="Registration")
        self.reg_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(self.reg_frame, text="Username:").pack(side=tk.LEFT, padx=5)
        self.username_entry = tk.Entry(self.reg_frame)
        self.username_entry.pack(side=tk.LEFT, padx=5)
        
        self.btn_register = tk.Button(self.reg_frame, text="Register", command=self.register)
        self.btn_register.pack(side=tk.LEFT, padx=5)
        
        # Authentication Frame
        self.auth_frame = tk.LabelFrame(self.control_frame, text="Authentication")
        self.auth_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.btn_login = tk.Button(self.auth_frame, text="Login", command=self.login, width=15, height=2, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"))
        self.btn_login.pack(padx=5, pady=5)
        
        # Management Frame
        self.manage_frame = tk.LabelFrame(self.control_frame, text="Management")
        self.manage_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.btn_logs = tk.Button(self.manage_frame, text="View Logs", command=self.view_logs)
        self.btn_logs.pack(fill=tk.X, padx=5, pady=2)
        
        self.btn_delete = tk.Button(self.manage_frame, text="Delete User", command=self.delete_user)
        self.btn_delete.pack(fill=tk.X, padx=5, pady=2)
        
        # Status Label
        self.status_label = tk.Label(window, text="Status: Ready", font=("Helvetica", 12))
        self.status_label.pack(pady=5)
        
        # Update loop
        self.delay = 15
        self.update()
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.read()
        if ret:
            # Process the frame for iris features
            annotated_frame, left_desc, right_desc = iris_processing.process_frame(frame)
            
            # Store latest features
            self.current_left_desc = left_desc
            self.current_right_desc = right_desc
            
            # Convert frame to PhotoImage
            annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(annotated_frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            
        self.window.after(self.delay, self.update)
        
    def register(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Warning", "Please enter a username.")
            return
            
        if self.current_left_desc is None and self.current_right_desc is None:
            messagebox.showwarning("Warning", "No eyes detected. Please look at the camera.")
            return
            
        # Store features as a tuple
        features = (self.current_left_desc, self.current_right_desc)
        
        success, msg = database.register_user(username, features)
        if success:
            self.status_label.config(text=f"Status: {msg}", fg="green")
            self.username_entry.delete(0, tk.END)
            messagebox.showinfo("Success", f"User '{username}' registered successfully!")
        else:
            self.status_label.config(text=f"Status: {msg}", fg="red")
            
    def login(self):
        if self.current_left_desc is None and self.current_right_desc is None:
            self.status_label.config(text="Status: Authentication Failed (No eyes detected)", fg="red")
            database.log_attempt("Unknown", "Failed (No eyes)")
            return
            
        live_features = (self.current_left_desc, self.current_right_desc)
        users = database.get_users()
        
        if not users:
            messagebox.showwarning("Warning", "No users registered in the database.")
            return
            
        best_match_username = None
        highest_score = 0
        
        for username, stored_features in users.items():
            score = matcher.calculate_match_score(stored_features, live_features)
            if score > highest_score:
                highest_score = score
                best_match_username = username
                
        if best_match_username and highest_score >= MATCH_THRESHOLD:
            msg = f"User Verified: {best_match_username} (Score: {highest_score})"
            self.status_label.config(text=f"Status: {msg}", fg="green")
            database.log_attempt(best_match_username, "Success")
            messagebox.showinfo("Access Granted", f"Welcome, {best_match_username}!\nMatch Score: {highest_score}")
        else:
            msg = f"Access Denied. Max score: {highest_score}"
            self.status_label.config(text=f"Status: {msg}", fg="red")
            database.log_attempt("Unknown", "Failed")
            messagebox.showerror("Access Denied", f"Authentication failed.\nHighest Score: {highest_score}")
            
    def view_logs(self):
        logs_window = tk.Toplevel(self.window)
        logs_window.title("Authentication Logs")
        logs_window.geometry("500x300")
        
        tree = ttk.Treeview(logs_window, columns=("Username", "Time", "Status"), show="headings")
        tree.heading("Username", text="Username")
        tree.heading("Time", text="Time")
        tree.heading("Status", text="Status")
        
        tree.column("Username", width=150)
        tree.column("Time", width=200)
        tree.column("Status", width=100)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        logs = database.get_logs()
        for log in logs:
            # log: username, timestamp, status
            tree.insert("", tk.END, values=(log[0], log[1], log[2]))
            
    def delete_user(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Warning", "Please enter a username to delete in the Registration section.")
            return
            
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{username}'?"):
            if database.delete_user(username):
                messagebox.showinfo("Success", f"User '{username}' deleted successfully.")
                self.username_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Warning", f"User '{username}' not found.")
                
    def on_closing(self):
        if self.vid.isOpened():
            self.vid.release()
        self.window.destroy()
