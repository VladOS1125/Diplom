import cv2
import numpy as np
import socket
import pyaudio
import struct
import zlib

# Create a socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 1234))

# PyAudio settings
p = pyaudio.PyAudio()
chunk = 1024
format = pyaudio.paInt16
channels = 1
rate = 44100

# Choose a specific microphone
device_index = 2 # Change this to the desired device index

# Create a stream for recording audio
stream = p.open(format=format, channels=channels, rate=rate, input=True, input_device_index=device_index, frames_per_buffer=chunk)

# Send video dimensions and audio settings to the server
frame_width = 640  # Assuming a default width
frame_height = 480  # Assuming a default height
client_socket.sendall(struct.pack('II', frame_width, frame_height))
client_socket.sendall(struct.pack('II', rate, chunk))

# Initialize the video capture device
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    # Compress the image data
    _, buffer = cv2.imencode('.jpg', frame)
    compressed_data = zlib.compress(buffer)

    # Send the image data to the server
    client_socket.sendall(struct.pack('I', len(compressed_data)) + compressed_data)

    # Read audio data from the microphone
    audio_data = stream.read(chunk)

    # Send the audio data to the server
    client_socket.sendall(struct.pack('I', len(audio_data)) + audio_data)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Close the stream and PyAudio
stream.stop_stream()
stream.close()
p.terminate()

# Close the connection and socket
client_socket.close()
cv2.destroyAllWindows()
