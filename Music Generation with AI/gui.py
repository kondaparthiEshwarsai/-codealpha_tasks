import tkinter as tk
from tkinter import filedialog, messagebox
from music_generator import MusicGenerator


class MusicGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎼 AI Music Generator")
        self.root.geometry("400x300")

        self.generator = MusicGenerator()
        self.pitchnames = []
        self.output_notes = []

        self.create_widgets()

    def create_widgets(self):
        tk.Button(self.root, text="🎵 Load MIDI Files", command=self.load_midi_files, width=25).pack(pady=10)
        tk.Button(self.root, text="🧪 Prepare Sequences", command=self.prepare_sequences, width=25).pack(pady=10)
        tk.Button(self.root, text="🏋️ Train Model", command=self.train_model, width=25).pack(pady=10)
        tk.Button(self.root, text="🎶 Generate Music", command=self.generate_music, width=25).pack(pady=10)
        tk.Button(self.root, text="💾 Save as MIDI", command=self.save_midi, width=25).pack(pady=10)

        self.status_label = tk.Label(self.root, text="Status: Ready")
        self.status_label.pack(pady=10)

    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")
        print(message)

    def load_midi_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select MIDI Files",
            filetypes=[("MIDI files", "*.mid *.midi")]
        )
        if not file_paths:
            return

        self.generator.load_midi_files(file_paths)
        self.update_status(f"Loaded {len(self.generator.notes)} new notes.")

    def prepare_sequences(self):
        self.pitchnames = self.generator.prepare_sequences(sequence_length=20)
        if not self.pitchnames:
            self.update_status("Sequence preparation failed.")
        else:
            self.update_status(f"Prepared {len(self.generator.network_input)} sequences.")

    def train_model(self):
        if self.generator.network_input.size == 0 or self.generator.network_output.size == 0:
            messagebox.showerror("Error", "No training data found.")
            return

        input_shape = (self.generator.network_input.shape[1], self.generator.network_input.shape[2])
        self.generator.build_model(input_shape)
        self.generator.train_model(epochs=5)

        if self.generator.model is None:
            messagebox.showerror("Error", "Model training failed.")
        else:
            self.update_status("Model trained.")

    def generate_music(self):
        if not self.pitchnames:
            messagebox.showerror("Error", "You must prepare sequences first.")
            return

        if self.generator.model is None:
            messagebox.showerror("Error", "You must train the model first.")
            return

        self.output_notes = self.generator.generate_music(self.pitchnames, length=300)
        self.update_status("Music generated.")

    def save_midi(self):
        if not self.output_notes:
            messagebox.showerror("Error", "No music to save.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".mid",
            filetypes=[("MIDI files", "*.mid")],
            title="Save MIDI File"
        )
        if not output_path:
            return

        self.generator.create_midi(self.output_notes, output_filename=output_path)
        self.update_status("MIDI file saved.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicGeneratorGUI(root)
    root.mainloop()
