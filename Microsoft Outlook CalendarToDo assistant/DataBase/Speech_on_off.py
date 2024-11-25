import speech_recognition as sr
import time
import threading

# Initialize recognizer and microphone
r = sr.Recognizer()
m = sr.Microphone()

# List to store recorded audio chunks
audio_chunks = []

# Flag to control recording state
is_recording = False

def start_recording():
    global audio_chunks, is_recording
    print("Recording started...\n")

    # Adjust for ambient noise before starting to record
    with m as source:
        r.adjust_for_ambient_noise(source)
        print("Listening...")

        # Record continuously until stopped
        while is_recording:
            try:
                # Capture each chunk of audio (non-blocking)
                audio_chunk = r.listen(source, timeout=5, phrase_time_limit=5)
                audio_chunks.append(audio_chunk)
            except Exception as e:
                print(f"Recording error: {e}")
                break

def stop_and_process():
    global audio_chunks, is_recording
    is_recording = False  # Stop the recording loop
    
    if audio_chunks:
        print("Processing recorded audio...")
        
        # Combine all recorded chunks into one AudioData object
        combined_audio = sr.AudioData(b''.join([chunk.get_raw_data() for chunk in audio_chunks]), 
                                      audio_chunks[0].sample_rate, 
                                      audio_chunks[0].sample_width)
        
        try:
            # Recognize speech from the combined audio
            text = r.recognize_google(combined_audio)
            print(f"You said: {text}")
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
    else:
        print("No audio was recorded.")
    
    # Clear the list of chunks after processing
    audio_chunks = []

# Function to start recording in a separate thread
def start_recording_thread():
    global is_recording
    if not is_recording:  # Only start if not already recording
        is_recording = True  # Set flag to True to start recording
        thread = threading.Thread(target=start_recording)  # Create a new thread for recording
        thread.start()  # Start the thread

# Main control loop
try:
    while True:
        command = input("Type 'start' to begin recording or 'stop' to end and process: ").strip().lower()
        
        if command == "start":
            start_recording_thread()  # Start capturing audio in a separate thread
            
        elif command == "stop":
            if is_recording:  # Only stop if currently recording
                stop_and_process()  # Stop recording and process the captured audio
            
        time.sleep(0.1)
except KeyboardInterrupt:
    pass  # Exit gracefully on Ctrl+C
