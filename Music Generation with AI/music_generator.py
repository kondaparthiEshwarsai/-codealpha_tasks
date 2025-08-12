import glob
import pickle
import numpy as np
from music21 import converter, instrument, note, chord, stream
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, Activation
from keras.layers import BatchNormalization as BatchNorm


class MusicGenerator:
    def __init__(self):
        self.notes = []
        self.network_input = []
        self.network_output = []
        self.model = None

    def load_midi_files(self, path):
        import os
        os.makedirs('data', exist_ok=True)
        print("🎵 Loading MIDI files...")

        # Allow both single file path or list of paths
        if isinstance(path, str):
            midi_files = [path]
        else:
            midi_files = path

        print(f"📂 Found {len(midi_files)} MIDI files.")

        for file in midi_files:
            print(f"🎼 Parsing: {file}")
            try:
                midi = converter.parse(file)
                parts = instrument.partitionByInstrument(midi)
                notes_to_parse = parts.parts[0].recurse() if parts else midi.flat.notes

                for element in notes_to_parse:
                    if isinstance(element, note.Note):
                        self.notes.append(str(element.pitch))
                    elif isinstance(element, chord.Chord):
                        self.notes.append('.'.join(str(n) for n in element.normalOrder))
            except Exception as e:
                print(f"❌ Failed to parse {file}: {e}")

        print(f"✅ Total notes collected: {len(self.notes)}")

        with open('data/notes.pkl', 'wb') as f:
            pickle.dump(self.notes, f)

    def prepare_sequences(self, sequence_length=20):
        print("🧪 Preparing sequences...")

        if len(self.notes) < sequence_length:
            print("❌ Not enough notes to prepare sequences.")
            return []

        pitchnames = sorted(set(self.notes))
        note_to_int = {note: number for number, note in enumerate(pitchnames)}

        network_input = []
        network_output = []

        for i in range(len(self.notes) - sequence_length):
            sequence_in = self.notes[i:i + sequence_length]
            sequence_out = self.notes[i + sequence_length]
            network_input.append([note_to_int[char] for char in sequence_in])
            network_output.append(note_to_int[sequence_out])

        n_patterns = len(network_input)
        print(f"📊 Total sequences: {n_patterns}")

        self.network_input = np.reshape(network_input, (n_patterns, sequence_length, 1)) / float(len(pitchnames))
        self.network_output = to_categorical(network_output)

        return pitchnames

    def build_model(self, input_shape):
        print("🛠️ Building model...")
        model = Sequential()
        model.add(LSTM(512, input_shape=input_shape, return_sequences=True))
        model.add(Dropout(0.3))
        model.add(LSTM(512, return_sequences=True))
        model.add(Dropout(0.3))
        model.add(LSTM(512))
        model.add(Dense(256))
        model.add(Dropout(0.3))
        model.add(Dense(self.network_output.shape[1]))
        model.add(Activation('softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam')
        self.model = model
        print("✅ Model compiled.")

    def train_model(self, epochs=5):
        if not self.model:
            print("⚠️ Model not built. Call build_model() first.")
            return
        print(f"🏋️ Training model for {epochs} epochs...")
        self.model.fit(self.network_input, self.network_output, epochs=epochs, batch_size=64)
        print("✅ Training complete.")

    def generate_music(self, pitchnames, length=500):
        print("🎶 Generating music...")

        int_to_note = {number: note for number, note in enumerate(pitchnames)}
        start = np.random.randint(0, len(self.network_input) - 1)
        pattern = self.network_input[start].flatten().tolist()
        prediction_output = []

        for _ in range(length):
            prediction_input = np.reshape(pattern, (1, len(pattern), 1))
            prediction_input = prediction_input / float(len(pitchnames))
            prediction = self.model.predict(prediction_input, verbose=0)
            index = np.argmax(prediction)
            result = int_to_note[index]
            prediction_output.append(result)
            pattern.append(index)
            pattern = pattern[1:]

        print("✅ Music generation complete.")
        return prediction_output

    def create_midi(self, prediction_output, output_filename="output.mid"):
        print(f"💾 Saving generated music to {output_filename}")
        offset = 0
        output_notes = []

        for pattern in prediction_output:
            if '.' in pattern or pattern.isdigit():
                notes_in_chord = pattern.split('.')
                notes = [note.Note(int(n)) for n in notes_in_chord]
                for n in notes:
                    n.storedInstrument = instrument.Piano()
                new_chord = chord.Chord(notes)
                new_chord.offset = offset
                output_notes.append(new_chord)
            else:
                new_note = note.Note(pattern)
                new_note.offset = offset
                new_note.storedInstrument = instrument.Piano()
                output_notes.append(new_note)

            offset += 0.5

        midi_stream = stream.Stream(output_notes)
        midi_stream.write('midi', fp=output_filename)
        print("✅ MIDI file created.")
