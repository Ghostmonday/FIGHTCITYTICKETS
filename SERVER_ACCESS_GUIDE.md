
# DigitalOcean Server Access Guide

**Last Updated:** January 9, 2026  
**Server:** FightCity-ubuntu-s-2vcpu-4gb-sfo3-01  
**IP:** 146.190.141.126

---

## Quick Connect (Copy-Paste)

### From Windows Local Machine

```bash
# Set environment variable
set DO_TOKEN=[YOUR_DO_TOKEN_HERE]

# SSH as admin user with key
ssh -i /c/Users/Amirp/.ssh/do_key_ed25519 admin@146.190.141.126
```

---

## DO Token (Persistent)

```bash
# Add to system environment (Windows)
setx DO_TOKEN "[YOUR_DO_TOKEN_HERE]"

# Or add to user profile
echo 'export DO_TOKEN="[YOUR_DO_TOKEN_HERE]"' >> ~/.bashrc
source ~/.bashrc
```

---

## doctl CLI Setup

### 1. Install doctl

**Windows (winget):**
```bash
winget install doctl
```

**macOS (Homebrew):**
```bash
brew install doctl
```

**Linux (Snap):**
```bash
sudo snap install doctl
```

### 2. Configure Authentication

Create config file at `%APPDATA%\doctl\config.yaml` (Windows) or `~/.config/doctl/config.yaml` (Linux/macOS):

```yaml
contexts:
  sfo3-droplet:
    [YOUR_DO_TOKEN_HERE]
current-context: sfo3-droplet
```

### 3. Verify Connection

```bash
doctl account get
doctl compute droplet list
```

### 4. Connect via doctl

```bash
# SSH as admin
doctl compute ssh FightCity-ubuntu-s-2vcpu-4gb-sfo3-01 --ssh-user admin --ssh-key-path /c/Users/Amirp/.ssh/do_key_ed25519

# Run a command
doctl compute ssh FightCity-ubuntu-s-2vcpu-4gb-sfo3-01 --ssh-user admin --ssh-key-path /c/Users/Amirp/.ssh/do_key_ed25519 --ssh-command "whoami && pwd"
```

---

## SSH Key Location

**Local Machine (Windows):**
```
C:\Users\Amirp\.ssh\do_key_ed25519
```

**Server (root):**
```
/root/.ssh/id_ed25519
```

**Server (admin user):**
```
/home/admin/.ssh/authorized_keys
```

---

## Server Credentials

| Property | Value |
|----------|-------|
| **IP Address** | 146.190.141.126 |
| **Username** | admin |
| **Private Key** | /c/Users/Amirp/.ssh/do_key_ed25519 |
| **Password** | BloodyH3lls (fallback) |
| **Region** | SFO3 |
| **OS** | Ubuntu 24.04 LTS |

---

## Fallback: Console Access

If SSH fails completely:

1. Go to: https://cloud.digitalocean.com/droplets/543204909/console
2. Click "Launch Droplet Console"
3. Login: `root` / `BloodyH3lls`
4. Run: `sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config && systemctl restart ssh`

---

## Common Commands

```bash
# Check server status
doctl compute droplet list

# SSH into server
ssh -i /c/Users/Amirp/.ssh/do_key_ed25519 admin@146.190.141.126

# Run remote command
doctl compute ssh FightCity-ubuntu-s-2vcpu-4gb-sfo3-01 --ssh-user admin --ssh-key-path /c/Users/Amirp/.ssh/do_key_ed25519 --ssh-command "free -h"

# Update system
doctl compute ssh FightCity-ubuntu-s-2vcpu-4gb-sfo3-01 --ssh-user admin --ssh-key-path /c/Users/Amirp/.ssh/do_key_ed25519 --ssh-command "sudo apt update && sudo apt upgrade -y"

# Check disk space
doctl compute ssh FightCity-ubuntu-s-2vcpu-4gb-sfo3-01 --ssh-user admin --ssh-key-path /c/Users/Amirp/.ssh/do_key_ed25519 --ssh-command "df -h"

# View logs
doctl compute ssh FightCity-ubuntu-s-2vcpu-4gb-sfo3-01 --ssh-user admin --ssh-key-path /c/Users/Amirp/.ssh/do_key_ed25519 --ssh-command "sudo journalctl -xe"
```

---

## Security Configuration

The server is configured with:
- ✅ SSH key-only authentication (no password auth)
- ✅ Root login disabled
- ✅ Non-root admin user with sudo privileges
- ✅ DO_TOKEN environment variable set

---

## Troubleshooting

**"Permission denied (publickey)":**
- Verify key path is correct
- Run: `ssh -vvv -i /c/Users/Amirp/.ssh/do_key_ed25519 admin@146.190.141.126`

**"Connection refused":**
- Check if SSH is running: `systemctl status ssh`
- Restart SSH: `systemctl restart ssh`

**"Host key verification failed":**
- Remove old host key: `ssh-keygen -R 146.190.141.126`
- Try again

---

## Emergency Reset

If completely locked out:

1. Go to DigitalOcean Console
2. Login as root with password `BloodyH3lls`
3. Re-enable password auth:
   ```bash
   sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
   systemctl restart ssh
   ```
4. Generate new SSH keys and distribute as needed

---

**记住：** 每次新会话都从这份文档开始，永不再迷路了。
