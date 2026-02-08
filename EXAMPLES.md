# Example Evolution Tasks

Copy these into GitHub issues with the `agent-task` label.

## Beginner (Test the System)

### 1. Add Basic Logging
**Title:** `add logging to agent.log file`

**Description:**
Create a logging system that writes agent activity to `agent.log`. Log when the agent starts, when it processes issues, and when it creates PRs.

**Expected Outcome:** 
- New file: `logging_helper.py` or `logging_config.py`
- Agent logs activity to `agent.log`
- Version bump to v1

---

### 2. Track Version Number
**Title:** `track version number and display in output`

**Description:**
Add a version number that increments with each evolution. Display it when the agent starts and in PR messages.

**Expected Outcome:**
- Version tracking in agent
- Output shows current version
- Version bump to v2

---

### 3. Add Error Handling
**Title:** `add comprehensive error handling with try-except blocks`

**Description:**
Wrap risky operations in try-except blocks with informative error messages. Log errors to help with debugging.

**Expected Outcome:**
- Better error messages
- Graceful failure handling
- Version bump to v3

---

## Intermediate (Build Features)

### 4. Cost Tracking
**Title:** `add token usage tracking and cost estimation`

**Description:**
Track OpenAI API token usage and estimate costs. Log total tokens used and running cost estimate.

**Expected Outcome:**
- Token counting for API calls
- Cost estimation logged
- Version bump to v4

---

### 5. Test Suite
**Title:** `create tests/ directory with pytest tests`

**Description:**
Set up a proper test suite with pytest. Add tests for core functions like `read_own_code()`, `load_environment()`, etc.

**Expected Outcome:**
- `tests/` directory created
- `pytest.ini` configuration
- Basic test coverage
- Version bump to v5

---

### 6. Configuration System
**Title:** `add JSON configuration file for agent settings`

**Description:**
Create `config.json` for configurable settings like poll interval, max retries, feature flags. Load on startup.

**Expected Outcome:**
- `config.json` file
- `config_loader.py` module
- Configurable behavior
- Version bump to v6

---

### 7. Refactor to Helpers
**Title:** `create helpers.py and refactor common utilities`

**Description:**
Extract utility functions into a separate `helpers.py` module. Keep `agent.py` focused on core logic.

**Expected Outcome:**
- `helpers.py` with extracted functions
- Cleaner `agent.py`
- Version bump to v7

---

## Advanced (Meta-Reasoning)

### 8. Self-Analysis
**Title:** `analyze own code quality and suggest improvements`

**Description:**
Add a function that analyzes the agent's own code for:
- Code complexity
- Function length
- Docstring coverage
- Type hint coverage
Post analysis as a GitHub issue comment.

**Expected Outcome:**
- Code analysis functionality
- Self-awareness about code quality
- Version bump to v8

---

### 9. Evolution History
**Title:** `maintain CHANGELOG.md with evolution history`

**Description:**
Automatically update a CHANGELOG.md file with each evolution. Include version, date, task description, and changes made.

**Expected Outcome:**
- `CHANGELOG.md` file
- Automatic updates on evolution
- Version bump to v9

---

### 10. Smart Retry Logic
**Title:** `implement exponential backoff for API retries`

**Description:**
When API calls fail, retry with exponential backoff (1s, 2s, 4s, 8s). Add jitter to prevent thundering herd.

**Expected Outcome:**
- Exponential backoff implemented
- More resilient to API issues
- Version bump to v10

---

## Expert (Autonomous)

### 11. Create Test Plan
**Title:** `before evolving, create and run test plan for changes`

**Description:**
Before each evolution, generate a test plan:
- What could break?
- What should be tested?
- Run tests before committing
If tests fail, try alternative approach.

**Expected Outcome:**
- Test planning logic
- Pre-evolution testing
- Self-correction capability
- Version bump to v11

---

### 12. Issue Prioritization
**Title:** `analyze open issues and prioritize by difficulty and impact`

**Description:**
When multiple `agent-task` issues exist, analyze them and choose which to tackle first based on:
- Estimated difficulty
- Potential impact
- Dependencies
Post prioritization as comment.

**Expected Outcome:**
- Issue analysis capability
- Smart prioritization
- Version bump to v12

---

### 13. Self-Optimization
**Title:** `optimize own prompt to GPT-4o for better code generation`

**Description:**
Analyze past evolutions to identify patterns in successful vs failed attempts. Update SYSTEM_PROMPT.md to improve future generations.

**Expected Outcome:**
- Prompt analysis
- Self-improving system prompt
- Meta-optimization
- Version bump to v13

---

## Usage Tips

1. **Start with beginner tasks** - Test the system works
2. **One at a time** - Let each evolution complete before adding next
3. **Review every PR** - Safety first
4. **Add retry label** - If evolution fails, add `agent-retry` to try again
5. **Monitor costs** - Check OpenAI usage dashboard

## Creating Your Own Tasks

Good task format:
```
Title: [Verb] [what to do] [optional: how/where]

Description:
- What to create/modify
- Expected behavior
- Any constraints
```

Examples:
- ✓ `add rate limiting to API calls`
- ✓ `create backup system for agent state`
- ✓ `implement feature flags for experimental features`
- ✗ `make it better` (too vague)
- ✗ `fix everything` (too broad)

## Observing Evolution

Track these metrics:
- How many evolutions succeed vs fail?
- What types of tasks work best?
- How does code size change over time?
- Does cost per evolution increase?
- Do evolutions take longer as code grows?

Document your findings - this is valuable research!
