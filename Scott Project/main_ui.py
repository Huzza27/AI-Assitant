import tkinter as tk
from tkinter import ttk, simpledialog
import os
import speech_recognition as sr
import threading
import simpleaudio as sa
from spotify_control import SpotifyController
from browser_controller import open_firefox, login_to_canvas_with_2fa
from google_api import add_event_to_calendar, google_calendar_authenticate
import creds

WAKE_WORD = "kyle"
BEEP_SOUND_PATH = "D:\\Scott Project\\beep.wav"
APPLICATIONS_FILE = "D:\\Scott Project\\applications.txt"  # Update with your correct path
spotify = SpotifyController(creds.spotify_key, creds.other_sportify_key, 'http://localhost:8888/callback')

def play_beep_sound():
    wave_obj = sa.WaveObject.from_wave_file(BEEP_SOUND_PATH)
    wave_obj.play()

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        try:
            command = recognizer.recognize_google(audio).lower()
            return command
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None

def listen_for_wake_word():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            try:
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=2)
                spoken_text = recognizer.recognize_google(audio).lower()

                if WAKE_WORD in spoken_text:
                    play_beep_sound()
                    command = listen_for_command()
                    process_voice_command(command)
            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"Could not request results; {e}")

def process_voice_command(command):
    if "play" in command:
        print("Play was heard")
        song_name = command.replace("play", "", 1).strip()
        spotify.play_song(song_name)
    elif "pause" in command:
        spotify.pause_song()
    elif "open" in command:
        app_name = command.replace("open", "", 1).strip()
        app_path = ui.app_paths.get(app_name)
        if app_path:
            try:
                os.startfile(app_path)
                print(f"Opening {app_name}")
            except Exception as e:
                print(f"Error opening application: {e}")
        else:
            print(f"Application '{app_name}' not found.")  
            
    elif "search for" in command:
        search_query = command.replace("search for", "", 1).strip()
        search_url = f"https://www.google.com/search?q={search_query}"
        open_firefox(search_url)
        #print(f"Searching for {search_query}")   
        
    elif "log me in to canvas" in command:
        # Replace with your actual Canvas credentials and email details
        # It's highly recommended to use a secure method to store and retrieve these details
        
        # Call the function to log in to Canvas with 2FA
        login_to_canvas_with_2fa(creds.canvas_username, creds.canvas_password, creds.email_user, creds.email_pass, creds.imap_server)  
    """
    else:
        response_text = openai_response(command)
        print("OpenAI Response:", response_text)
        audio_content = text_to_speech(response_text)
        audio_file_path = 'response.mp3'
        with open(audio_file_path, "wb") as audio_file:
            audio_file.write(audio_content)
        audio = AudioSegment.from_mp3(audio_file_path)
        play(audio)
    """

class AddAppDialog:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Add Application")
        tk.Label(self.top, text="Application Name:").pack()
        self.name_entry = tk.Entry(self.top)
        self.name_entry.pack()
        tk.Label(self.top, text="Application Path:").pack()
        self.path_entry = tk.Entry(self.top)
        self.path_entry.pack()
        self.submit_button = tk.Button(self.top, text="Add", command=self.on_submit)
        self.submit_button.pack()
        self.app_name = None
        self.app_path = None

    def on_submit(self):
        self.app_name = self.name_entry.get()
        self.app_path = self.path_entry.get()
        self.top.destroy()

class MainUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Assistant")
        self.tab_control = ttk.Notebook(root)
        self.app_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.app_tab, text='Applications')
        self.app_listbox = tk.Listbox(self.app_tab)
        self.app_listbox.pack(expand=True, fill='both')
        self.add_app_button = tk.Button(self.app_tab, text='Add Application', command=self.open_add_app_dialog)
        self.add_app_button.pack(side='left')
        self.open_app_button = tk.Button(self.app_tab, text='Open Application', command=self.open_application)
        self.open_app_button.pack(side='left')
        self.tab_control.pack(expand=1, fill="both")
        self.app_paths = {}
        self.load_applications()  # Load applications from file on start

    def load_applications(self):
        try:
            with open(APPLICATIONS_FILE, "r") as file:
                for line in file:
                    name, path = line.strip().split(',')
                    self.app_listbox.insert(tk.END, name)
                    self.app_paths[name] = path
        except FileNotFoundError:
            print("Applications file not found. Creating a new one.")
            open(APPLICATIONS_FILE, "w").close()

    def open_add_app_dialog(self):
        dialog = AddAppDialog(self.root)
        self.root.wait_window(dialog.top)
        app_name, app_path = dialog.app_name, dialog.app_path
        if app_name and app_path:
            self.app_listbox.insert(tk.END, app_name)
            self.app_paths[app_name] = app_path
            self.add_application_to_file(app_name, app_path)

    def add_application_to_file(self, name, path):
        with open(APPLICATIONS_FILE, "a") as file:
            file.write(f"{name},{path}\n")

    def open_application(self):
        selected_app = self.app_listbox.get(tk.ANCHOR)
        if selected_app:
            app_path = self.app_paths.get(selected_app, "")
            if app_path:
                try:
                    os.startfile(app_path)
                except Exception as e:
                    print(f"Error opening application: {e}")

# Start listening for the wake word in a separate thread
listening_thread = threading.Thread(target=listen_for_wake_word)
listening_thread.daemon = True
listening_thread.start()

if __name__ == '__main__':
    root = tk.Tk()
    ui = MainUI(root)
    root.mainloop()