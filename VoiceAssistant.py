import speech_recognition as sr
import pyttsx3
import time
import datetime
import webbrowser
import os
import nltk
import pygame
import requests
import psutil
import subprocess
import random
import wikipedia
import warnings
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# Initialize the speech recognition and text-to-speech engines
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Ignore specific warning from wikipedia about HTML parser
warnings.filterwarnings("ignore", category=UserWarning, message=".*No parser was explicitly specified.*")

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Capture audio input from the user."""
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            print("Recognizing...")
            command = recognizer.recognize_google(audio, language='en-in')
            print(f"User said: {command}\n")
        except Exception as e:
            print("Sorry, I didn't catch that. Could you repeat please?")
            return "None"
        return command.lower()

def greet_user():
    """Greet the user based on the time of day."""
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good morning!")
    elif 12 <= hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")
    speak("How can I assist you today?")

def open_application(app_name):
    """Open a specific application based on the user's command."""
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "browser": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    }
    if app_name in apps:
        os.startfile(apps[app_name])
    else:
        speak("Application not recognized.")

def web_search(query):
    """Performs a web search using the default browser."""
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    speak(f"Here are the search results for {query}")

def get_system_info():
    """Return basic system information."""
    battery = psutil.sensors_battery()
    battery_status = f"Battery is at {battery.percent}% with {'plugged in' if battery.power_plugged else 'not plugged in'}."
    disk_usage = psutil.disk_usage('/')
    disk_status = f"Disk usage: {disk_usage.percent}%"
    return battery_status + " " + disk_status

def parse_time(time_str):
    """Parses the time string to handle both 12-hour and 24-hour formats."""
    try:
        # Try to parse the time in 12-hour format with AM/PM
        return datetime.datetime.strptime(time_str, "%I:%M %p")
    except ValueError:
        pass

    try:
        # Try to parse the time in 24-hour format
        return datetime.datetime.strptime(time_str, "%H:%M")
    except ValueError:
        # If both formats fail, raise an error
        raise ValueError("Time format is incorrect. Please use 'HH:MM a.m./p.m.' or 'HH:MM' format.")

def set_alarm(time_str):
    """Sets an alarm for a given time."""
    try:
        # Parse the input time string with the appropriate format
        alarm_time = parse_time(time_str)
        print(f"Alarm set for {alarm_time.strftime('%I:%M %p')}")

        while True:
            # Get the current time in the same format as the alarm time
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            
            if current_time == alarm_time.strftime("%I:%M %p"):
                speak("Alarm ringing!")
                play_alarm_sound()  # Function to play the alarm sound
                break

            print(f"Waiting for alarm time... Current time is {current_time}")
            time.sleep(30)  # Check every 30 seconds

    except ValueError as ve:
        speak(str(ve))

def play_alarm_sound():
    """Plays the alarm sound using the default media player."""
    sound_path = r"C:\Users\HP\Music\WhatsApp Audio 2024-08-23 at 16.19.46_b2a718b3.mp3"
    
    try:
        # Using subprocess to play the audio file with the default associated program
        subprocess.run(['explorer', sound_path], shell=True)
    except Exception as e:
        print(f"Error playing sound: {e}")

def tell_joke():
    """Return a random joke."""
    jokes = [
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Why don't skeletons fight each other? They don't have the guts.",
        "What do you call fake spaghetti? An impasta!"
    ]
    return random.choice(jokes)

def get_current_time():
    """Returns the current time."""
    now = datetime.datetime.now()  # Correct usage: module.class.method
    current_time = now.strftime("%I:%M %p")
    return f"The current time is {current_time}" 

def get_current_date():
    """Returns the current date."""
    today = datetime.datetime.today()  # Correct usage: module.class.method
    current_date = today.strftime("%B %d, %Y")
    return f"Today's date is {current_date}"

def get_wikipedia_summary(query):
    """Fetches summary from Wikipedia for a given query."""
    try:
        summary = wikipedia.summary(query, sentences=2)  # Fetch a brief summary (2 sentences)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Disambiguation error. Multiple results found for {query}: {e.options}"
    except wikipedia.exceptions.PageError:
        return f"Page not found for {query}."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def convert_units(value, from_unit, to_unit):
    """Converts units (e.g., kilometers to miles)."""

    # Dictionary for unit conversions
    conversions = {
        ('kilometers', 'miles'): lambda x: x * 0.621371,
        ('miles', 'kilometers'): lambda x: x / 0.621371,
        ('celsius', 'fahrenheit'): lambda x: (x * 9/5) + 32,
        ('fahrenheit', 'celsius'): lambda x: (x - 32) * 5/9
    }

    # Normalize input units to handle different representations
    unit_aliases = {
        'km': 'kilometers',
        'kilometers': 'kilometers',
        'mi': 'miles',
        'miles': 'miles',
        'c': 'celsius',
        'celsius': 'celsius',
        'f': 'fahrenheit',
        'fahrenheit': 'fahrenheit'
    }

    try:
        # Map the input units to their standard names
        from_unit = unit_aliases.get(from_unit.lower(), from_unit.lower())
        to_unit = unit_aliases.get(to_unit.lower(), to_unit.lower())
        
        # Perform conversion if supported
        result = conversions[(from_unit, to_unit)](value)
        return f"{value} {from_unit} is {result:.2f} {to_unit}."
    except KeyError:
        return f"Conversion from {from_unit} to {to_unit} is not supported."
    except Exception as e:
        return f"Error occurred: {str(e)}"

def set_volume(level):
    """Sets the system volume to a specific level (0-100)."""
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    # Set volume level, the range is 0.0 to 1.0
    volume.SetMasterVolumeLevelScalar(level / 100, None)

reminders = []
def add_reminder(task, time_str):
    """Adds a reminder to the list."""
    try:
        reminder_time = parse_time(time_str)
        reminders.append((task, reminder_time))
        speak(f"Reminder set for {task} at {reminder_time.strftime('%I:%M %p')}")
    except ValueError as ve:
        speak(str(ve))

def check_reminders():
    """Checks for reminders that are due."""
    current_time = datetime.datetime.now()
    for task, reminder_time in reminders:
        if current_time >= reminder_time:
            speak(f"Reminder: {task}")
            reminders.remove((task, reminder_time))
    
def execute_task(command):
    """Execute tasks based on the user's command."""
    if 'open youtube' in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
    elif 'open google' in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
    elif 'play music' in command:
        speak("Playing music")
        music_dir = "C:\\Users\\HP\\Music"
        try:
            songs = os.listdir(music_dir)
            music_files = [file for file in songs if file.endswith(('.mp3', '.wav', '.flac'))]

            if music_files:
                music_file_path = os.path.join(music_dir, music_files[0])
                
                # Initialize pygame mixer
                pygame.mixer.init()
                
                # Load and play the music
                pygame.mixer.music.load(music_file_path)
                pygame.mixer.music.play()
                
                # Keep the script running while the music is playing
                while pygame.mixer.music.get_busy():
                    time.sleep(1)
            else:
                speak("No music files found in the specified directory.")
        except FileNotFoundError:
            speak("The specified music directory was not found. Please check the path.")
    elif 'current time' in command:
        speak(get_current_time())
    elif 'current date' in command:
        speak(get_current_date())
    elif 'tell me about' in command:
        topic = command.replace('tell me about', '').strip()
        summary = get_wikipedia_summary(topic)
        speak(summary)
    elif 'open' in command:
        app_name = command.split("open")[-1].strip()
        open_application(app_name)
    elif 'system info' in command:
        system_info = get_system_info()
        speak(system_info)
    elif 'set alarm' in command:
        time_str = command.split("at")[-1].strip()
        set_alarm(time_str)
    elif 'joke' in command:
        joke = tell_joke()
        speak(joke)
    elif 'search for' in command:
        query = command.replace('search for', '').strip()
        web_search(query)
    elif 'convert' in command:
        parts = command.split()
        try:
            value = float(parts[1])
            from_unit = parts[2]
            to_unit = parts[4]
            result = convert_units(value, from_unit, to_unit)
            speak(result)
        except ValueError:
            speak("Invalid number format.")
        except IndexError:
            speak("Conversion command is incomplete.")
    elif 'set volume to' in command:
        try:
            level = int(command.replace('set volume to', '').strip())
            set_volume(level)
            speak(f"Volume set to {level} percent.")
        except ValueError:
            speak("Please provide a valid number for the volume level.")
    elif 'set reminder' in command:
        task_info = command.replace('set reminder', '').strip()
        task, time_str = task_info.rsplit(' at ', 1)
        add_reminder(task.strip(), time_str.strip())
    elif 'check reminders' in command:
        check_reminders()
    elif 'exit' in command or 'quit' in command:
        speak("Goodbye!")
        exit()
    else:
        speak("I'm not sure how to help with that. Please try again.")

if __name__ == "__main__":
    greet_user()
    while True:
        command = listen()
        if command != "None":
            execute_task(command)