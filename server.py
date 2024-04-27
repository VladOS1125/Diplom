import cv2
import numpy as np
import socket
import pyaudio
import struct
import zlib

# PyAudio settings
p = pyaudio.PyAudio()
chunk = 1024
format = pyaudio.paInt16
channels = 1
rate = 44100

# Create a socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 1234))
server_socket.listen(5)

print("Server listening on port 1234...")

# Accept a client connection
client_socket, addr = server_socket.accept()
print(f"Connection from {addr} established.")

# Receive video dimensions and audio settings from the client
frame_width, frame_height = struct.unpack('II', client_socket.recv(8))
rate, chunk = struct.unpack('II', client_socket.recv(8))

# Create a video display window
cv2.namedWindow('Video')

# Create a PyAudio stream for playing audio
stream = p.open(format=format, channels=channels, rate=rate, output=True, frames_per_buffer=chunk)

while True:
    # Receive compressed image data from the client
    compressed_data = b''
    while len(compressed_data) < 4:
        compressed_data += client_socket.recv(4 - len(compressed_data))
    compressed_data_size = struct.unpack('I', compressed_data)[0]
    while len(compressed_data) < compressed_data_size + 4:
        compressed_data += client_socket.recv(compressed_data_size + 4 - len(compressed_data))
    buffer = zlib.decompress(compressed_data[4:])

    # Decode the image data and display the frame
    frame = cv2.imdecode(np.frombuffer(buffer, dtype=np.uint8), 1)
    cv2.imshow('Video', frame)

    # Receive audio data from the client
    audio_data = b''
    while len(audio_data) < 4:
        audio_data += client_socket.recv(4 - len(audio_data))
    audio_data_size = struct.unpack('I', audio_data)[0]
    while len(audio_data) < audio_data_size + 4:
        audio_data += client_socket.recv(audio_data_size + 4 - len(audio_data))

    # Play the audio data
    stream.write(audio_data[4:])

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Close all windows and streams
cv2.destroyAllWindows()
stream.stop_stream()
stream.close()
p.terminate()
client_socket.close()
server_socket.close()
