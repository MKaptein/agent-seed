# Deployment Guide

## Initial Setup (First Time)

### 1. Create GitHub Repository

Go to GitHub and create a new repository:
- Name: `agent-seed` (or your preferred name)
- Description: "Self-modifying AI agent experiment"
- **DO NOT** initialize with README (we have our own)
- Public or Private (your choice)

### 2. Configure Git

```bash
# Set your identity (if not already done)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Initialize repository
git init
git add .
git commit -m "Initial commit: Self-modifying agent seed"

# Set main as default branch
git branch -M main

# Add remote (replace with your repo URL)
git remote add origin git@github.com:YOUR-USERNAME/agent-seed.git

# Push to GitHub
git push -u origin main
```

### 3. Create GitHub Labels

Go to your repository on GitHub:

1. Click "Issues" tab
2. Click "Labels"
3. Click "New label"
4. Create these labels:
   - **agent-task** (color: #0E8A16) - For evolution tasks
   - **agent-failed** (color: #D73A4A) - Auto-added on failures
   - **agent-retry** (color: #FBCA04) - To retry failed tasks

### 4. Set Up Secrets

**On your deployment machine:**

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env  # or vim, code, etc.
```

Add your actual values:
```bash
OPENAI_API_KEY=sk-your-actual-key
GITHUB_TOKEN=ghp_your-actual-token
REPO=YOUR-USERNAME/agent-seed
```

**Get credentials:**
- OpenAI: https://platform.openai.com/api-keys
- GitHub: https://github.com/settings/tokens (scope: `repo`)

**Set spending limits:**
- OpenAI: Set $50-100 limit in dashboard
- GitHub: Token is scoped to this repo only

### 5. Test Locally (Optional)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test agent works
python agent.py --test
# Should output: OK

# Run briefly to verify
python agent.py
# Press Ctrl+C after a few seconds
```

## Deployment Options

Choose ONE based on your needs:

### Option A: AWS EC2 Spot (Recommended for Experiments)

**Advantages:**
- Isolated from your machine
- Cheap ($0.01-0.02/hour)
- Easy to terminate
- Production-like environment

**Setup:**

1. Launch EC2 instance:
   ```
   Instance type: t3.micro
   AMI: Ubuntu 24.04 LTS
   Pricing: Spot instance
   Storage: 8GB
   ```

2. SSH in and setup:
   ```bash
   ssh ubuntu@YOUR-INSTANCE-IP
   
   # Install Python and Git
   sudo apt update
   sudo apt install -y python3-pip git
   
   # Clone your repo
   git clone https://github.com/YOUR-USERNAME/agent-seed.git
   cd agent-seed
   
   # Install dependencies
   pip3 install -r requirements.txt
   
   # Configure
   cp .env.example .env
   nano .env  # Add your credentials
   
   # Run in screen (persistent session)
   screen -S agent
   python3 agent.py
   # Press Ctrl+A then D to detach
   
   # To reattach: screen -r agent
   ```

3. Monitor:
   ```bash
   # Check it's running
   screen -ls
   
   # View output
   screen -r agent
   
   # Stop: Ctrl+C in screen session
   ```

4. When done:
   ```bash
   # Terminate instance from AWS Console
   # or via CLI:
   aws ec2 terminate-instances --instance-ids i-xxxxx
   ```

### Option B: Docker (Recommended for Local)

**Advantages:**
- Isolated sandbox
- Resource limits
- Easy to reset
- Runs on your machine

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install git
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent files
COPY agent.py SYSTEM_PROMPT.md .env ./

# Configure git
RUN git config --global user.name "Agent" && \
    git config --global user.email "agent@example.com"

# Run as non-root
RUN useradd -m agentuser && \
    chown -R agentuser:agentuser /app
USER agentuser

CMD ["python", "agent.py"]
```

**Run:**
```bash
# Build
docker build -t agent-seed .

# Run with limits
docker run \
  --name agent \
  --rm \
  --cpus=1 \
  --memory=1g \
  -v $(pwd):/app \
  agent-seed

# Stop: Ctrl+C or docker stop agent
```

### Option C: DigitalOcean Droplet (Simple Cloud)

**Advantages:**
- Simple web UI
- $6/month always-on
- Easy to destroy

**Setup:**

1. Create droplet:
   - Image: Ubuntu 24.04
   - Plan: Basic $6/month
   - Add SSH key

2. SSH and setup (same as EC2 above)

3. Keep running:
   ```bash
   # Use tmux instead of screen
   tmux new -s agent
   python3 agent.py
   # Press Ctrl+B then D to detach
   
   # Reattach: tmux attach -t agent
   ```

## First Evolution Test

After deployment:

1. **Create test issue on GitHub:**
   - Title: `add logging to agent.log file`
   - Label: `agent-task`

2. **Watch for activity:**
   ```bash
   # If using screen/tmux, attach to see output
   screen -r agent  # or tmux attach -t agent
   ```

3. **Within 30-60 seconds:**
   - ✓ Agent detects issue
   - ✓ Generates evolution script
   - ✓ Creates PR

4. **Review the PR:**
   - Check `evolve_v1.sh` - is it safe?
   - Check `agent_v1.py` - looks reasonable?
   - No secrets exposed?

5. **Merge if satisfied:**
   - Agent automatically switches to v1
   - Continues monitoring

## Monitoring

### Check Agent Status

```bash
# If using screen
screen -ls
screen -r agent

# If using tmux  
tmux ls
tmux attach -t agent

# If using Docker
docker logs agent
docker stats agent

# Check for PRs
# Visit: github.com/YOUR-USERNAME/agent-seed/pulls
```

### Check Costs

- **OpenAI**: https://platform.openai.com/usage
- **AWS**: CloudWatch / Billing Dashboard
- **DigitalOcean**: Billing section

### Emergency Stop

```bash
# Screen/tmux
screen -r agent  # attach
Ctrl+C  # stop agent
exit  # close session

# Docker
docker stop agent

# EC2
aws ec2 stop-instances --instance-ids i-xxxxx
# or terminate from console
```

## Ongoing Evolution

1. **Create issues** with `agent-task` label
2. **Agent processes** automatically
3. **Review PRs** before merging
4. **Merge** to deploy new version
5. **Repeat**

## Troubleshooting

### Agent not detecting issues

- Check `REPO` in `.env` exactly matches GitHub repo
- Verify `agent-task` label exists (case-sensitive)
- Wait 30 seconds (polling interval)

### PR creation fails

```bash
# Check git config
git config user.name
git config user.email

# If empty, set them:
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### API errors

- Check `.env` has correct tokens
- Verify OpenAI spending limit not hit
- Check GitHub token has `repo` scope

## Cleanup

When experiment is done:

```bash
# Stop agent (Ctrl+C)

# Terminate infrastructure
# - EC2: Terminate instance
# - DigitalOcean: Destroy droplet
# - Docker: docker rm agent

# Revoke GitHub token
# https://github.com/settings/tokens

# Optional: Archive GitHub repo
```

## Next Steps

See README.md for:
- Suggested evolutions
- Security best practices
- Research questions to explore

---

**Ready to deploy!** Choose your deployment option and start evolving. 🚀
