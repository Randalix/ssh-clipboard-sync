# SSH Clipboard Sync

A simple tool to copy data from a remote server back to your local machine's clipboard over SSH. Perfect for when you're working on a remote server and need to copy command output, file contents, or any text back to your local clipboard.

## Features

- 📋 Copy data from remote server to local clipboard over SSH
- 📦 Handles large outputs with chunked data transmission
- 🖥️ Cross-platform support (Linux, macOS, Android/Termux)
- 🔄 Can replace platform-specific clipboard tools (xclip, pbcopy) for cross-platform scripts
- 🔒 Secure transmission over existing SSH connection
- ⚡ Fast and lightweight with minimal dependencies

## How It Works

The system consists of two Python scripts:
- **Server** (`clip_server.py`): Runs on your local machine, receives data and sets your local clipboard
- **Client** (`clip_copy.py`): Runs on the remote server, sends data back to your local machine

Data is transmitted in chunks to handle large clipboard contents efficiently, using a length-prefixed protocol over TCP sockets tunneled through SSH.

**Example workflow:**
1. Start `clip_server.py` on your local machine
2. SSH to remote server (with RemoteForward configured)
3. On remote server: `echo "hello" | clip_copy.py`
4. "hello" appears in your local clipboard!

## Prerequisites

### Prerequisites

### Local Machine (where clip_server.py runs)
- Python 3.6+
- Clipboard utilities:
  - **Linux (X11)**: `xclip`
  - **Linux (Wayland)**: `wl-clipboard` 
  - **macOS**: `pbcopy` (built-in)
  - **Android/Termux**: `termux-api`

### Remote Server (where clip_copy.py runs)
- Python 3.6+
- SSH access from your local machine

## Installation

1. Clone this repository on both your local machine and remote server:
```bash
git clone https://github.com/yourusername/ssh-clipboard-sync.git
cd ssh-clipboard-sync
```

2. **On your local machine**, copy the server script:
```bash
cp clip_server.py ~/.local/bin/
chmod +x ~/.local/bin/clip_server.py
```

3. **On the remote server**, copy the client script:
```bash
cp clip_copy.py ~/.local/bin/
chmod +x ~/.local/bin/clip_copy.py
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

- **Port 9999**: Server listens on this port (local machine)
- **Port 9997**: Client connects to this port on remote server (tunneled back to local port 9999)

The SSH RemoteForward creates a tunnel so that when the remote server connects to its localhost:9997, it actually connects back to your local machine's port 9999.

## Usage

### Basic Setup

1. **On your local machine**, start the clipboard server:
```bash
python3 clip_server.py
```

2. **SSH to your remote server** (the RemoteForward will be established automatically)

3. **On the remote server**, copy data to your local clipboard:
```bash
echo "Hello from the server!" | clip_copy.py
cat /var/log/syslog | clip_copy.py
ls -la | clip_copy.py
```

The data will appear in your local machine's clipboard!

### Integration Examples

#### Shell Alias (on remote server)
Add to your `~/.bashrc` or `~/.zshrc` on the remote server:
```bash
alias clip_copy='python3 ~/.local/bin/clip_copy.py'
```

Usage:
```bash
cat important-file.txt | clip_copy
grep "error" /var/log/app.log | clip_copy
docker logs container-name | clip_copy
```

#### Vim Integration (on remote server)
Add to your `~/.vimrc` on the remote server:
```vim
" Send current line to local clipboard
nnoremap <leader>cl :.w !python3 ~/.local/bin/clip_copy.py<CR>

" Send visual selection to local clipboard  
vnoremap <leader>cl :w !python3 ~/.local/bin/clip_copy.py<CR>

" Send entire file to local clipboard
nnoremap <leader>ca :%w !python3 ~/.local/bin/clip_copy.py<CR>
```

#### Tmux Integration (on remote server)
```bash
# Send tmux buffer to local clipboard
tmux show-buffer | clip_copy

# Or bind to a key in ~/.tmux.conf
bind-key C-c run "tmux show-buffer | clip_copy"
```

#### Cross-Platform Scripts
One of the key benefits is using `clip_copy.py` as a universal clipboard tool in your scripts, replacing platform-specific commands:

**Instead of:**
```bash
# Platform-specific approach
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "data" | pbcopy
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "data" | xclip -selection clipboard
fi
```

**Use:**
```bash
# Works on any remote server, sends to your local clipboard
echo "data" | clip_copy
```

This makes your scripts portable across different server environments while always sending output to your local machine where you can easily access it.

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
