import tkinter as tk
from tkinter import messagebox
import requests
import hashlib
from PIL import Image, ImageTk
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import re

# Function to check password strength
def check_password_strength(password):
    suggestions = []
    score = 0

    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
    else:
        suggestions.append("Use at least 12 characters.")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        suggestions.append("Add uppercase letters.")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        suggestions.append("Add lowercase letters.")

    if re.search(r"\d", password):
        score += 1
    else:
        suggestions.append("Include numbers.")

    if re.search(r"[@$!%*?&]", password):
        score += 1
    else:
        suggestions.append("Include special characters (@$!%*?&).")

    return score, suggestions

# Function to check HaveIBeenPwned API
def check_pwned_api(password):
    sha1password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    first5, tail = sha1password[:5], sha1password[5:]
    response = requests.get(f"https://api.pwnedpasswords.com/range/{first5}")
    hashes = (line.split(':') for line in response.text.splitlines())
    for h, count in hashes:
        if h == tail:
            return int(count)
    return 0

# Function to generate PDF
def generate_pdf_report(password, score, suggestions, breach_count):
    filename = "password_report.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Password Security Report")
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"Password: {password}")
    c.drawString(100, 700, f"Strength Score: {score}/6")

    if breach_count > 0:
        c.setFillColorRGB(1, 0, 0)
        c.drawString(100, 680, f"⚠ Found in {breach_count} data breaches!")
        c.setFillColorRGB(0, 0, 0)
    else:
        c.setFillColorRGB(0, 0.5, 0)
        c.drawString(100, 680, "✅ Not found in known breaches.")
        c.setFillColorRGB(0, 0, 0)

    c.drawString(100, 650, "Suggestions to Improve:")
    y = 630
    for s in suggestions:
        c.drawString(120, y, f"- {s}")
        y -= 20

    c.save()
    messagebox.showinfo("PDF Generated", f"Report saved as {filename}")

# Function for main password check
def check_password():
    password = entry.get()
    if not password:
        messagebox.showwarning("Input Error", "Please enter a password")
        return

    score, suggestions = check_password_strength(password)
    breach_count = check_pwned_api(password)

    result_text = f"Strength Score: {score}/6\n"
    if breach_count > 0:
        result_text += f"⚠ Found in {breach_count} data breaches!\n"
    else:
        result_text += "✅ Not found in known breaches.\n"

    if suggestions:
        result_text += "\nSuggestions:\n" + "\n".join(f"- {s}" for s in suggestions)

    result_label.config(text=result_text)

    # Enable PDF button after check
    pdf_button.config(command=lambda: generate_pdf_report(password, score, suggestions, breach_count))
    pdf_button.pack(pady=10)

# GUI Setup
root = tk.Tk()
root.title("Password Security Checker")
root.geometry("500x500")
root.configure(bg="black")

# Lock Icon
lock_icon_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Lock_icon_green.svg/1024px-Lock_icon_green.svg.png"
try:
    lock_img_data = requests.get(lock_icon_url, timeout=10).content
    lock_img = Image.open(io.BytesIO(lock_img_data)).convert("RGBA").resize((80, 80))
    lock_photo = ImageTk.PhotoImage(lock_img)
    lock_label = tk.Label(root, image=lock_photo, bg="black")
    lock_label.pack(pady=10)
except Exception:
    lock_label = tk.Label(root, text="🔒", font=("Arial", 40), bg="black", fg="green")
    lock_label.pack(pady=10)

# Title Label
title_label = tk.Label(root, text="Password Security Checker", font=("Arial", 16, "bold"), fg="green", bg="black")
title_label.pack(pady=10)

# Entry Field
entry = tk.Entry(root, show="*", font=("Arial", 14), width=30)
entry.pack(pady=10)

# Check Button
check_button = tk.Button(root, text="Check Password", font=("Arial", 14), bg="green", fg="black", command=check_password)
check_button.pack(pady=10)

# Result Label
result_label = tk.Label(root, text="", font=("Arial", 12), fg="white", bg="black", justify="left")
result_label.pack(pady=10)

# PDF Button (hidden until check is run)
pdf_button = tk.Button(root, text="Generate PDF Report", font=("Arial", 12), bg="gray", fg="white")

root.mainloop()
