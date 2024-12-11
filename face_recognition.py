import cv2
import os
import numpy as np
import sqlite3
import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Button, Label
from PIL import Image, ImageTk

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create users table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    surname TEXT,
    email TEXT UNIQUE,
    age INTEGER,
    gender TEXT,
    password TEXT,
    registration_number TEXT,
    program TEXT
)
''')

# Create feedback table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY,
    email TEXT,
    rating INTEGER,
    comments TEXT
)
''')

conn.commit()

def open_camera():
    global video_capture
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        messagebox.showerror("Error", "Failed to access the camera.")
        return False
    return True

def close_camera():
    global video_capture
    if video_capture is not None:
        video_capture.release()
        cv2.destroyAllWindows()

def register_user(name, surname, email, age, gender, password, reg_number, program, capture_face=False):
    try:
        cursor.execute('''
        INSERT INTO users (name, surname, email, age, gender, password, registration_number, program)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, surname, email, age, gender, password, reg_number, program))
        conn.commit()
        messagebox.showinfo("Success", "User registered successfully!")
        
        if capture_face:
            capture_face_images(name, surname)

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Email already registered. Please use a different email.")

def capture_face_images(name, surname):
    user_dir = f"training_images/{name}_{surname}"
    os.makedirs(user_dir, exist_ok=True)

    if not open_camera():
        return

    count = 0
    while count < 30:  # Capture 30 images
        ret, frame = video_capture.read()
        if ret:
            cv2.imshow("Face Capture", frame)
            cv2.imwrite(f"{user_dir}/face_{count}.jpg", frame)  # Save captured image
            count += 1
            cv2.waitKey(100)  # Wait for 100 ms before capturing the next image
        else:
            break

    close_camera()
    cv2.destroyAllWindows()
    messagebox.showinfo("Success", "Face images captured successfully!")

def login_password(email, password):
    cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    user_info = cursor.fetchone()

    if user_info:
        user_details = (
            f"Name: {user_info[1]}\n"
            f"Surname: {user_info[2]}\n"
            f"Email: {user_info[3]}\n"
            f"Age: {user_info[4]}\n"
            f"Gender: {user_info[5]}\n"
            f"Registration Number: {user_info[6]}\n"
            f"Program: {user_info[7]}"
        )
        messagebox.showinfo("Welcome", user_details)
        open_feedback_window(user_info[3])  # Pass email to feedback window
    else:
        messagebox.showerror("Error", "Invalid credentials.")

def submit_feedback(email, rating, comments):
    try:
        cursor.execute('''
        INSERT INTO feedback (email, rating, comments)
        VALUES (?, ?, ?)
        ''', (email, rating, comments))
        conn.commit()
        messagebox.showinfo("Success", "Feedback submitted successfully!")
    except Exception as e:
        messagebox.showerror("Error", "Failed to submit feedback.")

def open_feedback_window(email):
    feedback_window = Toplevel()
    feedback_window.title("Feedback")
    feedback_window.geometry("400x300")

    Label(feedback_window, text="Rate your experience (1-5):").pack(pady=10)
    
    rating_var = tk.IntVar()
    for i in range(1, 6):
        tk.Radiobutton(feedback_window, text=str(i), variable=rating_var, value=i).pack(anchor='w')

    Label(feedback_window, text="Comments:").pack(pady=10)
    comments_entry = Entry(feedback_window, width=50)
    comments_entry.pack(pady=10)

    def submit_feedback_action():
        rating = rating_var.get()
        comments = comments_entry.get()
        submit_feedback(email, rating, comments)
        feedback_window.destroy()

    Button(feedback_window, text="Submit Feedback", command=submit_feedback_action).pack(pady=20)

def open_registration_window():
    registration_window = Toplevel()
    registration_window.title("Register")
    registration_window.geometry("400x500")

    Label(registration_window, text="Name").pack(pady=5)
    name_entry = Entry(registration_window)
    name_entry.pack(pady=5)

    Label(registration_window, text="Surname").pack(pady=5)
    surname_entry = Entry(registration_window)
    surname_entry.pack(pady=5)

    Label(registration_window, text="Email").pack(pady=5)
    email_entry = Entry(registration_window)
    email_entry.pack(pady=5)

    Label(registration_window, text="Age").pack(pady=5)
    age_entry = Entry(registration_window)
    age_entry.pack(pady=5)

    Label(registration_window, text="Gender").pack(pady=5)
    gender_entry = Entry(registration_window)
    gender_entry.pack(pady=5)

    Label(registration_window, text="Password").pack(pady=5)
    password_entry = Entry(registration_window, show='*')
    password_entry.pack(pady=5)

    Label(registration_window, text="Registration Number").pack(pady=5)
    reg_number_entry = Entry(registration_window)
    reg_number_entry.pack(pady=5)

    Label(registration_window, text="Program").pack(pady=5)
    program_entry = Entry(registration_window)
    program_entry.pack(pady=5)

    # Checkbox for face recognition registration
    face_recognition_var = tk.BooleanVar()
    face_recognition_checkbox = tk.Checkbutton(registration_window, text="Register with Face Recognition", variable=face_recognition_var)
    face_recognition_checkbox.pack(pady=10)

    def register_user_action():
        register_user(
            name_entry.get(),
            surname_entry.get(),
            email_entry.get(),
            age_entry.get(),
            gender_entry.get(),
            password_entry.get(),
            reg_number_entry.get(),
            program_entry.get(),
            capture_face=face_recognition_var.get()
        )
        registration_window.destroy()

    Button(registration_window, text="Register", command=register_user_action).pack(pady=10)

def open_login_window():
    login_window = Toplevel()
    login_window.title("Login")
    login_window.geometry("400x300")

    Label(login_window, text="Email").pack(pady=5)
    email_entry = Entry(login_window)
    email_entry.pack(pady=5)

    Label(login_window, text="Password").pack(pady=5)
    password_entry = Entry(login_window, show='*')
    password_entry.pack(pady=5)

    def login_user_action():
        email = email_entry.get()
        password = password_entry.get()
        if email and password:
            login_password(email, password)
            login_window.destroy()
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    Button(login_window, text="Login", command=login_user_action).pack(pady=20)

def setup_gui():
    root = tk.Tk()
    root.title("Face Recognition App")
    root.geometry("600x400")

    # Load the background image
    image_path = "msu_background.jpg"
    if not os.path.isfile(image_path):
        print(f"Image not found: {image_path}")
        messagebox.showerror("Error", "Background image not found.")
        root.destroy()
        return  # Exit if the image cannot be loaded

    try:
        background_image = Image.open(image_path)
        background_image = background_image.resize((600, 400), Image.LANCZOS)
        bg_image = ImageTk.PhotoImage(background_image)
    except Exception as e:
        print(f"Error loading image: {e}")
        messagebox.showerror("Error", "Failed to load background image.")
        root.destroy()
        return  # Exit if the image cannot be loaded

    # Create a Canvas to hold the background image
    canvas = tk.Canvas(root, width=600, height=400)
    canvas.pack(fill="both", expand=True)

    # Add the background image to the canvas
    canvas.create_image(0, 0, image=bg_image, anchor="nw")

    # Add buttons
    btn_register = Button(root, text="Register", command=open_registration_window)
    btn_login = Button(root, text="Login", command=open_login_window)
    btn_exit = Button(root, text="Exit", command=root.quit)

    # Place buttons on the canvas
    canvas.create_window(100, 150, window=btn_register)
    canvas.create_window(100, 200, window=btn_login)
    canvas.create_window(100, 250, window=btn_exit)

    root.mainloop()

# Start the GUI
setup_gui()

# Close the database connection when the application is closed
conn.close()