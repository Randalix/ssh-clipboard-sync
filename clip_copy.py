#!/usr/bin/env python3
import sys
import os
import platform
import subprocess
import socket
import struct

def set_clipboard(data):
    system = platform.system()
    
    if system == "Linux":
        session_type = os.getenv("XDG_SESSION_TYPE", "")
        if session_type.lower() == "wayland":
            cmd = ["wl-copy"]
        else:
            cmd = ["xclip", "-r", "-selection", "clipboard"]
    elif system == "Darwin":
        cmd = ["pbcopy"]
    elif system == "Linux" and "ANDROID_ROOT" in os.environ:
        cmd = ["termux-clipboard-set"]
    else:
        print("Unsupported OS")
        sys.exit(1)
    
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    process.communicate(input=data.encode("utf-8"))

def send_to_nc(data):
    """Send data to server with chunked transmission"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(("localhost", 9997))
            
            # Send the total length first (4 bytes, big-endian)
            data_bytes = data.encode('utf-8')
            total_length = len(data_bytes)
            sock.sendall(struct.pack('>I', total_length))
            
            # Send data in chunks
            chunk_size = 4096
            bytes_sent = 0
            
            while bytes_sent < total_length:
                chunk = data_bytes[bytes_sent:bytes_sent + chunk_size]
                sock.sendall(chunk)
                bytes_sent += len(chunk)
                
            print(f"Sent {total_length} bytes in {(total_length + chunk_size - 1) // chunk_size} chunks")
            
    except Exception as e:
        print(f"Error sending data: {e}")
        sys.exit(1)
    
if __name__ == "__main__":
    input_data = sys.stdin.read()
    if not input_data.strip():
        print("No input provided to copy.")
        sys.exit(1)
    
    set_clipboard(input_data)
    send_to_nc(input_data)
