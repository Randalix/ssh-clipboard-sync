#!/usr/bin/env python3
import socket
import subprocess
import sys
import struct

HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 9999       # Port to listen on

def is_port_in_use(host, port):
    """Check if the specified port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def set_clipboard(data):
    """Set the macOS clipboard content."""
    process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    process.communicate(input=data.encode('utf-8'))

def recv_exact(sock, num_bytes):
    """Receive exactly num_bytes from socket"""
    data = b''
    while len(data) < num_bytes:
        chunk = sock.recv(num_bytes - len(data))
        if not chunk:
            raise ConnectionError("Connection closed unexpectedly")
        data += chunk
    return data

def receive_chunked_data(client_socket):
    """Receive data in chunks with length prefix"""
    try:
        # First, receive the total length (4 bytes)
        length_data = recv_exact(client_socket, 4)
        total_length = struct.unpack('>I', length_data)[0]
        
        print(f"Expecting {total_length} bytes")
        
        # Now receive the actual data
        received_data = b''
        bytes_received = 0
        
        while bytes_received < total_length:
            remaining = total_length - bytes_received
            chunk_size = min(4096, remaining)
            chunk = client_socket.recv(chunk_size)
            
            if not chunk:
                raise ConnectionError("Connection closed before all data received")
                
            received_data += chunk
            bytes_received += len(chunk)
            
        print(f"Received {bytes_received} bytes")
        return received_data.decode('utf-8')
        
    except Exception as e:
        print(f"Error receiving data: {e}")
        return None

if is_port_in_use(HOST, PORT):
    print(f"Port {PORT} is already in use. Exiting.")
    sys.exit(1)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Listening on port {PORT}...")
    
    while True:
        client_socket, addr = server_socket.accept()
        with client_socket:
            print(f"Connection from {addr}")
            
            data = receive_chunked_data(client_socket)
            if data is not None:
                # Remove trailing newlines and set clipboard
                clean_data = data.rstrip('\n')
                set_clipboard(clean_data)
                print("Clipboard updated.")
            else:
                print("Failed to receive data")
