import os
import requests
import json
import re
import wordninja
import pyttsx3
from tkinter import font
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import ctypes
from sys import platform

def speech(botReply):
    engine = pyttsx3.init()
    engine.say(botReply)
    engine.runAndWait()

def clean_response(text):
    """
    Cleans and formats the response from the LLM.
    - Removes extra spaces
    - Uses wordninja for tokenization
    - Fixes punctuation and contractions
    - Some errors, but mostly works, known errors coded in
    """
    
    #remove spaces
    text = text.replace(" ", "")
    
    #add notation for punctuation
    text = text.replace(".", " period ")
    text = text.replace(",", " comma ")
    text = text.replace("!", " xc")
    text = text.replace("?", " question ") 
    
    #Use wordninja to split text
    words = wordninja.split(text)
    #put words together
    text = " ".join(words)
    
    # Fix spaces around punctuation
    text = re.sub(r'\s([.,!?])', r'\1', text)
    text = re.sub(r'([.,!?])(\w)', r'\1 \2', text)
    
    
    #keep after space fixing
    #hard code known errors
    text = text.replace(" iam ", " I am ")

    #Replace notation for punctuation
    text = text.replace(" period", ".")
    text = text.replace(" comma ", ",")
    text = text.replace(" xc", "!")
    text = text.replace(" question ", "?")

    # Fix contractions like "it ' s" -> "it's"
    text = re.sub(r"(\w)\s'\s(\w)", r"\1'\2", text)

    return text



def goon(prompt):
    #system message
    data = {
        "model": "mistral",
        "messages": [
            {"role": "system", "content": (
                "Personality"
            )},
            {"role": "user", "content": prompt}
        ]
    }
    
    #API Connection
    response = requests.post("http://localhost:11434/api/chat", json=data, stream=True)

    bot_reply_parts = []

    for line in response.iter_lines():
        if line:
            try:
                decoded_line = json.loads(line.decode("utf-8"))
                if "message" in decoded_line and "content" in decoded_line["message"]:
                    bot_reply_parts.append(decoded_line["message"]["content"])
            except json.JSONDecodeError:
                continue

    # Join all collected parts into a single response
    bot_reply = " ".join(bot_reply_parts).strip()
    bot_reply = clean_response(bot_reply)

    return bot_reply

# GUI Setup
def send_message():
    #get user input
    user_input = entry.get()
    #check if close command
    if (user_input == "bye"):
        chat_window.config(state=tk.DISABLED)
        root.after(1000, root.destroy)
        return
    
    #Do nothing if user input empty
    if not user_input.strip():
        return

    chat_window.config(state=tk.NORMAL)
    chat_window.insert(tk.END, f"You: {user_input}\n", "user")
    entry.delete(0, tk.END)
    chat_window.see(tk.END)
    
    response = goon(user_input)

    chat_window.insert(tk.END, f"Bot: {response}\n\n", "bot")
    chat_window.config(state=tk.DISABLED)
    chat_window.see(tk.END)
    
    #update GUI before running audio
    root.update_idletasks() 
    speech(response)
    
    
# Create main window
root = tk.Tk()
#change to be user select
root.title("Name")
root.configure(bg="#1e1e1e")


def keep_on_top():
    root.lift()
    root.after(1000, keep_on_top)

keep_on_top()

#font setup
customFont = font.Font(family="Iceberg", size=14)

#region Colors
TEXT_BG = "#2d2d2d"  # Chat window background
TEXT_FG = "#ffffff"  # Chat text color
USER_COLOR = "#6cc4ff"  # Light blue for user messages
BOT_COLOR = "#ff6666"  # Light red for bot messages
ENTRY_BG = "#3a3a3a"  # Input box background
ENTRY_FG = "#ffffff"  # Input box text color
BUTTON_BG = "#444444"  # Button background
BUTTON_FG = "#ffffff"  # Button text color
#endregion

# --- Create Frame for Layout ---
main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack(expand=True, fill="both", padx=10, pady=10)

# --- Chat Window Frame (Left Side) ---
chat_frame = tk.Frame(main_frame, bg="#1e1e1e")
chat_frame.grid(row=0, column=0, sticky="nsew")

# --- GoonBot Sprite (Right Side) ---
sprite_frame = tk.Frame(main_frame, bg="#1e1e1e")
sprite_frame.grid(row=0, column=1, sticky="ns")  # Fixed width

# --- Chat Display (Inside Left Frame) ---
chat_window = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, font=customFont,
                                        bg=TEXT_BG, fg=TEXT_FG, insertbackground="black", borderwidth=2)
chat_window.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
chat_window.tag_config("user", foreground=USER_COLOR)
chat_window.tag_config("bot", foreground=BOT_COLOR)

# Create input field
entry = tk.Entry(root, width=50, font=customFont, bg="#444444")
entry.pack(padx=10, pady=5)


# Create Send button
send_button = tk.Button(root, text="Send", command=send_message, font=customFont, bg="#444444")
send_button.pack(pady=5)

# --- Get the Script's Directory for Image ---
script_dir = os.path.dirname(os.path.abspath(__file__))  # Get current script location
sprite_path = os.path.join(script_dir, "Example.png")  # Dynamically find "user selected png"

# --- Load and Display the Sprite (Inside Right Frame) ---
if os.path.exists(sprite_path):
    goonbot_image = Image.open(sprite_path)
    goonbot_image = goonbot_image.resize((400, 400), Image.Resampling.LANCZOS)  # Resize image
    goonbot_photo = ImageTk.PhotoImage(goonbot_image)

    sprite_label = tk.Label(sprite_frame, image=goonbot_photo, bg="#1e1e1e")
    sprite_label.pack()
#err check
else:
    print(f"⚠️ WARNING: Image not found at {sprite_path}!")

# --- Configure Grid Resizing ---
main_frame.columnconfigure(0, weight=3)  # Chat Frame takes 3 parts
main_frame.columnconfigure(1, weight=1)  # Sprite Frame takes 1 part
chat_frame.rowconfigure(0, weight=1)  # Chat window expands
chat_frame.rowconfigure(1, weight=0)  # Input row stays fixed
chat_frame.columnconfigure(0, weight=3)  # Input field expands
chat_frame.columnconfigure(1, weight=1)  # Send button stays fixed

#Run
root.mainloop()