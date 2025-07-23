# SSH Clipboard Sync

A simple tool to synchronize clipboard contents between local and remote machines over SSH. This allows you to copy text on your local machine and have it automatically available on the remote machine's clipboard, and vice versa.

## Features

- 🔄 Bidirectional clipboard synchronization over SSH
- 📦 Handles large clipboard contents with chunked data transmission
- 🖥️ Cross-platform support (Linux, macOS, Android/Termux)
- 🔒 Secure transmission over existing SSH connection
- ⚡ Fast and lightweight with minimal dependencies

## How It Works

The system consists of two Python scripts:
- **Client** (`clip_copy.py`): Copies data to local clipboard and sends it to the remote machine
- **Server** (`clip_server.py`): Receives data and sets it on the remote machine's clipboard

Data is transmitted in chunks to handle large clipboard contents efficiently, using a length-prefixed protocol over TCP sockets tunneled through SSH.

## Prerequisites

### Local Machine (Client)
- Python 3.6+
- Clipboard utilities:
  - **Linux (X11)**: `xclip`
  - **Linux (Wayland)**: `wl-clipboard` 
  - **macOS**: `pbcopy` (built-in)
  - **Android/Termux**: `termux-api`

### Remote Machine (Server)
- Python 3.6+
- Clipboard utilities (same as above based on the remote OS)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ssh-clipboard-sync.git
cd ssh-clipboard-sync
```

2. Copy the scripts to your preferred location:
```bash
# Copy to local bin directory
cp clip_copy.py ~/.local/bin/
cp clip_server.py ~/.local/bin/

# Make executable
chmod +x ~/.local/bin/clip_copy.py
chmod +x ~/.local/bin/clip_server.py
```

## Configuration

### SSH Config Setup

Add the following to your SSH client configuration (`~/.ssh/config`):

```ssh-config
Host *
  ForwardX11 yes
  ForwardX11Trusted yes
  RemoteForward 9997 localhost:9999
```

Or for specific hosts:
```ssh-config
Host myserver
  HostName example.com
  User myuser
  ForwardX11 yes
  ForwardX11Trusted yes
  RemoteForward 9997 localhost:9999
```

### Port Configuration

- **Port 9999**: Server listens on this port (remote machine)
- **Port 9997**: Client connects to this port (tunneled back to local port 9999)

You can change these ports by modifying the `PORT` variable in both scripts.

## Usage

### Basic Setup

1. **On the remote machine**, start the clipboard receiver:
```bash
python3 clip_server.py
```

2. **On your local machine**, send clipboard data:
```bash
echo "Hello, remote clipboard!" | python3 clip_copy.py
```

### Integration Examples

#### Shell Alias
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
alias rclip='python3 ~/.local/bin/clip_copy.py'
```

Usage:
```bash
echo "Some text" | rclip
cat file.txt | rclip
```

#### Vim Integration
Add to your `~/.vimrc`:
```vim
" Send current line to remote clipboard
nnoremap <leader>rl :.w !python3 ~/.local/bin/clip_copy.py<CR>

" Send visual selection to remote clipboard  
vnoremap <leader>rl :w !python3 ~/.local/bin/clip_copy.py<CR>
```

#### Tmux Integration
```bash
# Send tmux buffer to remote clipboard
tmux show-buffer | python3 ~/.local/bin/clip_copy.py
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```
Port 9999 is already in use. Exiting.
```
**Solution**: Kill the existing process or change the port in both scripts.

#### Connection Refused
```
Error sending data: [Errno 111] Connection refused
```
**Solutions**:
- Ensure the server script is running on the remote machine
- Check SSH port forwarding is working: `ssh -v yourhost` (look for "Remote forwarding" messages)
- Verify firewall settings allow the connection

#### Clipboard Not Working
**Linux**: Install required clipboard utilities:
```bash
# X11
sudo apt install xclip

# Wayland  
sudo apt install wl-clipboard
```

**Missing X11 Forwarding**: Ensure you have X11 forwarding enabled and working:
```bash
ssh -X yourhost
echo $DISPLAY  # Should show something like localhost:10.0
```

### Debug Mode

Add debug output by modifying the scripts to include verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

- All data is transmitted over your existing SSH connection, leveraging SSH's encryption
- The clipboard receiver only accepts connections from localhost (SSH tunnel)
- No data is stored persistently; everything stays in memory
- Consider the sensitivity of clipboard contents before using over untrusted networks

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the need for seamless clipboard sharing in remote development workflows
- Thanks to the SSH port forwarding feature that makes this possible
