import tkinter as tk
from tkinter import ttk, messagebox
from deep_translator import GoogleTranslator
import pyttsx3
import pyperclip

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Language mappings supported by GoogleTranslator
lang_codes = {
    "Afrikaans": "af", "Albanian": "sq", "Arabic": "ar", "Armenian": "hy", "Azerbaijani": "az",
    "Basque": "eu", "Belarusian": "be", "Bengali": "bn", "Bosnian": "bs", "Bulgarian": "bg",
    "Catalan": "ca", "Cebuano": "ceb", "Chinese (Simplified)": "zh-CN", "Chinese (Traditional)": "zh-TW",
    "Croatian": "hr", "Czech": "cs", "Danish": "da", "Dutch": "nl", "English": "en", "Esperanto": "eo",
    "Estonian": "et", "Filipino": "tl", "Finnish": "fi", "French": "fr", "Galician": "gl", "Georgian": "ka",
    "German": "de", "Greek": "el", "Gujarati": "gu", "Haitian Creole": "ht", "Hausa": "ha", "Hebrew": "iw",
    "Hindi": "hi", "Hungarian": "hu", "Icelandic": "is", "Igbo": "ig", "Indonesian": "id", "Irish": "ga",
    "Italian": "it", "Japanese": "ja", "Kannada": "kn", "Kazakh": "kk", "Khmer": "km", "Korean": "ko",
    "Lao": "lo", "Latin": "la", "Latvian": "lv", "Lithuanian": "lt", "Macedonian": "mk", "Malay": "ms",
    "Maltese": "mt", "Maori": "mi", "Marathi": "mr", "Mongolian": "mn", "Nepali": "ne", "Norwegian": "no",
    "Persian": "fa", "Polish": "pl", "Portuguese": "pt", "Punjabi": "pa", "Romanian": "ro", "Russian": "ru",
    "Serbian": "sr", "Slovak": "sk", "Slovenian": "sl", "Somali": "so", "Spanish": "es", "Swahili": "sw",
    "Swedish": "sv", "Tamil": "ta", "Telugu": "te", "Thai": "th", "Turkish": "tr", "Ukrainian": "uk",
    "Urdu": "ur", "Vietnamese": "vi", "Welsh": "cy", "Yiddish": "yi", "Yoruba": "yo", "Zulu": "zu"
}

language_list = sorted(lang_codes.keys())

# Functions
def translate_text():
    try:
        src = lang_codes[source_lang.get()]
        tgt = lang_codes[target_lang.get()]
        text = source_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Empty Input", "Please enter text to translate.")
            return

        translate_btn.config(state="disabled")
        translated = GoogleTranslator(source=src, target=tgt).translate(text)
        translated_text.delete("1.0", tk.END)
        translated_text.insert(tk.END, translated)

    except Exception as e:
        messagebox.showerror("Translation Error", f"An error occurred:\n{str(e)}")
    finally:
        translate_btn.config(state="normal")

def copy_text():
    result = translated_text.get("1.0", tk.END).strip()
    if result:
        pyperclip.copy(result)
        messagebox.showinfo("Copied", "Translated text copied to clipboard!")

def speak_text():
    result = translated_text.get("1.0", tk.END).strip()
    if result:
        engine.say(result)
        engine.runAndWait()

def clear_text():
    source_text.delete("1.0", tk.END)
    translated_text.delete("1.0", tk.END)

# GUI Setup
root = tk.Tk()
root.title("Language Translation Tool")
root.geometry("600x520")
root.resizable(False, False)

# Title
tk.Label(root, text="Language Translator", font=("Helvetica", 18, "bold")).pack(pady=10)

# Language Selection Frame
frame1 = tk.Frame(root)
frame1.pack(pady=5)

tk.Label(frame1, text="From:").grid(row=0, column=0)
source_lang = ttk.Combobox(frame1, values=language_list, state='readonly', width=25)
source_lang.set("English")
source_lang.grid(row=0, column=1, padx=5)

tk.Label(frame1, text="To:").grid(row=0, column=2)
target_lang = ttk.Combobox(frame1, values=language_list, state='readonly', width=25)
target_lang.set("French")
target_lang.grid(row=0, column=3, padx=5)

# Text Input
tk.Label(root, text="Enter text:", font=("Helvetica", 12)).pack()
source_text = tk.Text(root, height=6, width=70)
source_text.pack(pady=5)

# Translate Button
translate_btn = tk.Button(root, text="Translate", command=translate_text, bg="lightblue", font=("Helvetica", 12), width=20)
translate_btn.pack(pady=10)

# Output
tk.Label(root, text="Translated text:", font=("Helvetica", 12)).pack()
translated_text = tk.Text(root, height=6, width=70, bg="#f0f0f0")
translated_text.pack(pady=5)

# Bottom Button Frame
frame2 = tk.Frame(root)
frame2.pack(pady=10)

copy_btn = tk.Button(frame2, text="Copy", command=copy_text, width=15)
copy_btn.grid(row=0, column=0, padx=10)

speak_btn = tk.Button(frame2, text="Speak", command=speak_text, width=15)
speak_btn.grid(row=0, column=1, padx=10)

clear_btn = tk.Button(frame2, text="Clear", command=clear_text, width=15)
clear_btn.grid(row=0, column=2, padx=10)

# Run GUI
root.mainloop()
