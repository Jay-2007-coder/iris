import tkinter as tk
import database
from ui import IrisApp

def main():
    # Initialize the SQLite database (creates tables if they don't exist)
    print("Initializing database...")
    database.init_db()
    
    # Create the main Tkinter window
    print("Starting UI...")
    root = tk.Tk()
    
    # Set window icon if available, handle gracefully if not
    # try:
    #     root.iconbitmap('icon.ico')
    # except:
    #     pass
    
    # Create the Iris Application
    app = IrisApp(root, "AI-Based Iris Recognition Authentication System")
    
    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()
