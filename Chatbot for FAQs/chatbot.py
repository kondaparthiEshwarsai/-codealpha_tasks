import tkinter as tk
from tkinter import scrolledtext
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Sample FAQ database
faq_data = {
    "What is your return policy?": "Our return policy allows returns within 30 days of purchase.",
    "How do I reset my password?": "Click on 'Forgot Password' at login and follow the instructions.",
    "What are your working hours?": "Our support team is available from 9 AM to 6 PM, Monday to Friday.",
    "Do you ship internationally?": "Yes, we ship to over 50 countries worldwide.",
    "How can I contact customer support?": "You can contact us at support@example.com or call 1800-123-456."
}

# Preprocess FAQ questions
questions = list(faq_data.keys())
answers = list(faq_data.values())

# Vectorize the questions
vectorizer = TfidfVectorizer()
question_vectors = vectorizer.fit_transform(questions)

# Matching function
def get_best_match(user_input):
    user_vec = vectorizer.transform([user_input])
    similarity = cosine_similarity(user_vec, question_vectors)
    max_index = similarity.argmax()
    confidence = similarity[0][max_index]
    if confidence < 0.3:
        return "Sorry, I couldn't understand your question. Please try rephrasing."
    return answers[max_index]

# GUI setup
root = tk.Tk()
root.title("FAQ Chatbot")
root.geometry("600x500")
root.resizable(False, False)

chat_log = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', font=("Helvetica", 11))
chat_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

def add_chat_entry(sender, text):
    chat_log.configure(state='normal')
    chat_log.insert(tk.END, f"{sender}: {text}\n")
    chat_log.configure(state='disabled')
    chat_log.yview(tk.END)

def on_send():
    user_input = user_entry.get().strip()
    if user_input:
        add_chat_entry("You", user_input)
        response = get_best_match(user_input)
        add_chat_entry("Bot", response)
        user_entry.delete(0, tk.END)

# Input field and button
input_frame = tk.Frame(root)
input_frame.pack(pady=5, padx=10, fill=tk.X)

user_entry = tk.Entry(input_frame, font=("Helvetica", 12))
user_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
user_entry.bind("<Return>", lambda event: on_send())

send_btn = tk.Button(input_frame, text="Send", width=10, command=on_send)
send_btn.pack(side=tk.RIGHT)

# Welcome message
add_chat_entry("Bot", "Hi! Ask me a question about our services.")

root.mainloop()
