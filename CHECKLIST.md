# Pre-Deployment Checklist

Use this checklist before your first commit to ensure everything is ready.

## ✅ Files Present

- [ ] `agent.py` - Main agent (executable)
- [ ] `SYSTEM_PROMPT.md` - GPT-4o instructions  
- [ ] `README.md` - User documentation
- [ ] `DEPLOY.md` - Deployment guide
- [ ] `EXAMPLES.md` - Example evolution tasks
- [ ] `requirements.txt` - Python dependencies
- [ ] `.env.example` - Environment template
- [ ] `.gitignore` - Ignores secrets
- [ ] `LICENSE` - MIT license
- [ ] This file (`CHECKLIST.md`)

## ✅ Code Quality

- [ ] `agent.py` is executable (`chmod +x agent.py`)
- [ ] `agent.py --test` returns "OK"
- [ ] All imports work
- [ ] No syntax errors
- [ ] No hardcoded secrets

## ✅ Documentation

- [ ] README explains what this does
- [ ] README has setup instructions
- [ ] README has security warnings
- [ ] DEPLOY.md has deployment options
- [ ] EXAMPLES.md has starter tasks

## ✅ Git Configuration

- [ ] `.gitignore` includes `.env`
- [ ] `.gitignore` includes Python artifacts
- [ ] `.gitignore` includes virtual environments
- [ ] `.env` is NOT in git (check: `git status`)

## ✅ Before First Commit

```bash
# 1. Verify files
ls -la

# Should see all files listed above
# Should NOT see .env (only .env.example)

# 2. Test agent
python agent.py --test
# Output: OK

# 3. Check git status
git status

# .env should be ignored (red in untracked, not to be committed)

# 4. Initialize git
git init
git add .
git commit -m "Initial commit: Self-modifying agent seed"

# 5. Ready to push!
```

## ✅ After GitHub Push

On GitHub:

- [ ] Repository created
- [ ] Code pushed to `main` branch
- [ ] README.md displays correctly
- [ ] Create `agent-task` label (Issues → Labels → New label)
- [ ] Create `agent-failed` label (auto-added on failures)
- [ ] Create `agent-retry` label (for manual retries)

## ✅ Deployment Environment

Choose ONE:

### Option A: AWS EC2
- [ ] Spot instance launched (t3.micro)
- [ ] Ubuntu 24.04
- [ ] SSH access configured
- [ ] Security group allows outbound HTTPS

### Option B: Docker
- [ ] Docker installed
- [ ] Dockerfile created
- [ ] Image builds successfully
- [ ] Container runs

### Option C: DigitalOcean
- [ ] Droplet created ($6/month)
- [ ] Ubuntu 24.04
- [ ] SSH key added

### Option D: Local VM
- [ ] VirtualBox/UTM installed
- [ ] Ubuntu VM created
- [ ] Snapshot taken

## ✅ Credentials

- [ ] OpenAI API key obtained
- [ ] OpenAI spending limit set ($50-100)
- [ ] GitHub personal access token created
- [ ] Token has `repo` scope
- [ ] Token is dedicated (not main account)
- [ ] `.env` file created (from `.env.example`)
- [ ] `.env` has all three variables filled in
- [ ] `.env` is gitignored (verify with `git status`)

## ✅ Security

- [ ] Running in isolated environment (NOT main laptop)
- [ ] Resource limits configured (if Docker/cloud)
- [ ] Spending limits set (OpenAI)
- [ ] Ready to monitor costs
- [ ] Know how to emergency stop
- [ ] Know how to revoke GitHub token

## ✅ First Run Test

```bash
# In deployment environment:

# 1. Clone repo
git clone https://github.com/YOUR-USERNAME/agent-seed.git
cd agent-seed

# 2. Install deps
pip3 install -r requirements.txt

# 3. Configure
cp .env.example .env
nano .env  # Add credentials

# 4. Test
python3 agent.py --test
# Output: OK

# 5. Run briefly
python3 agent.py
# Should see: "🤖 Agent monitoring ..."
# Press Ctrl+C after 5 seconds

# 6. Create test issue on GitHub:
#    Title: "add logging to agent.log file"
#    Label: "agent-task"

# 7. Run agent for real
python3 agent.py
# Wait 30-60 seconds
# Should detect issue and create PR

# 8. Review PR on GitHub
#    - Check evolve_v1.sh looks safe
#    - Check agent_v1.py looks reasonable
#    - Merge if satisfied

# 9. Agent switches to v1 automatically
```

## ✅ Monitoring Setup

- [ ] Know how to view agent output (screen/tmux/docker logs)
- [ ] Bookmarked OpenAI usage dashboard
- [ ] Bookmarked GitHub repository
- [ ] Know how to check for PRs
- [ ] Set up calendar reminder to check costs

## ✅ Research Planning

- [ ] Decide experiment duration (1 week? 2 weeks?)
- [ ] Set budget limit ($50? $100?)
- [ ] Plan which metrics to track
- [ ] Set up spreadsheet for observations
- [ ] Decide when to write up results

## ✅ Backup Plan

- [ ] Know how to stop agent (Ctrl+C)
- [ ] Know how to revoke GitHub token
- [ ] Know how to terminate cloud resources
- [ ] Have cost limit alerts set
- [ ] Know who to contact if issues

---

## 🎯 You're Ready When...

All checkboxes above are checked, AND:
- ✅ Code is in GitHub
- ✅ Labels are created
- ✅ Deployment environment is ready
- ✅ `.env` is configured
- ✅ Security measures in place
- ✅ Monitoring plan ready

Then create your first `agent-task` issue and watch it evolve! 🚀

## 📝 After First Successful Evolution

Document:
- Time from issue creation to PR
- Any errors encountered
- Cost of first evolution (check OpenAI)
- Quality of generated code
- Whether you merged the PR

This is valuable research data!

## 🆘 If Something Goes Wrong

1. **Ctrl+C** to stop agent
2. **Check logs** for errors
3. **Verify .env** has correct values
4. **Check DEPLOY.md** troubleshooting section
5. **Review PR carefully** before merging
6. **Add `agent-retry` label** if evolution failed

Good luck with your experiment! 🌱→🌿→🌳
