#!/usr/bin/env python3
"""Self-modifying AI agent that evolves through GitHub issues.

This agent monitors a GitHub repository for issues labeled 'agent-task',
generates shell scripts to modify itself, and creates pull requests with
the changes. Each evolution is tested before deployment.

Usage:
    python agent.py              # Start monitoring for issues
    python agent.py --test       # Test mode (validates agent works)

Environment Variables:
    OPENAI_API_KEY: OpenAI API key for GPT-4o
    GITHUB_TOKEN: GitHub personal access token with repo scope
    REPO: Repository in format 'owner/repo-name'

Security:
    - Run in isolated environment (Docker, VM, or cloud instance)
    - Use dedicated GitHub token (not your main account)
    - Set OpenAI spending limits
    - Review all PRs before merging

Author: Maurits Kaptein
License: MIT
"""

import os
import sys
import subprocess
import time
import re
import requests
from typing import Optional, Dict
from openai import OpenAI


def load_environment() -> None:
    """Load environment variables from .env file if it exists.
    
    Reads .env file line by line and sets environment variables.
    Ignores comments (lines starting with #) and empty lines.
    """
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value


# Load environment first
load_environment()

# Configuration from environment
API_KEY = os.environ.get("OPENAI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = os.environ.get("REPO")


def get_next_version() -> int:
    """Scan directory for existing agent versions, return next number.
    
    Looks for files matching pattern agent_v*.py and returns the next
    version number. For example, if agent_v1.py and agent_v2.py exist,
    returns 3.
    
    Returns:
        Next version number (integer starting at 1)
    """
    existing = [f for f in os.listdir('.') if f.startswith('agent_v') and f.endswith('.py')]
    if not existing:
        return 1
    
    versions = []
    for filename in existing:
        match = re.search(r'agent_v(\d+)\.py', filename)
        if match:
            versions.append(int(match.group(1)))
    
    return max(versions) + 1 if versions else 1


def github_api(method: str, path: str, json_data: Optional[Dict] = None) -> requests.Response:
    """Make authenticated request to GitHub API.
    
    Args:
        method: HTTP method (GET, POST, PATCH, DELETE)
        path: API path (e.g., '/issues')
        json_data: Optional JSON payload for request body
        
    Returns:
        Response object from requests library
        
    Raises:
        requests.exceptions.RequestException: If request fails
    """
    url = f"https://api.github.com/repos/{REPO}{path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    return requests.request(method, url, headers=headers, json=json_data, timeout=30)


def read_own_code() -> str:
    """Read this script's source code.
    
    Returns:
        String containing the complete source code of this file
    """
    with open(__file__, "r", encoding="utf-8") as source_file:
        return source_file.read()


def generate_evolution_script(task: str, previous_attempt: Optional[Dict] = None) -> str:
    """Generate shell script to evolve the agent.
    
    Asks GPT-4o to create a bash script that will modify the agent
    to accomplish the given task. The script should create a new
    version of the agent along with any supporting files.
    
    Args:
        task: Description of what to accomplish (from GitHub issue)
        previous_attempt: Optional dict with 'script' and 'error' from failed attempt
        
    Returns:
        Bash script as a string
        
    Raises:
        Exception: If API call fails or returns invalid response
    """
    current_code = read_own_code()
    current_filename = os.path.basename(__file__)
    
    # Load system prompt that instructs the LLM
    system_prompt = ""
    if os.path.exists("SYSTEM_PROMPT.md"):
        with open("SYSTEM_PROMPT.md", "r", encoding="utf-8") as prompt_file:
            system_prompt = prompt_file.read()
    
    # Build conversation for the LLM
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # Base request
    user_message = (
        f"Current agent filename: {current_filename}\n"
        f"Current agent code:\n```python\n{current_code}\n```\n\n"
        f"Task: {task}\n\n"
    )
    
    # Add previous failure context if this is a retry
    if previous_attempt:
        user_message += (
            f"\n**PREVIOUS ATTEMPT FAILED**\n\n"
            f"Previous script:\n```bash\n{previous_attempt['script']}\n```\n\n"
            f"Error: {previous_attempt['error']}\n\n"
            f"Generate a DIFFERENT approach that avoids this error.\n\n"
        )
    else:
        user_message += (
            f"Generate a bash script that creates agent_vN.py with the "
            f"modifications needed to accomplish this task. Remember to copy "
            f"from {current_filename} (the current agent), not from hardcoded 'agent.py'."
        )
    
    messages.append({"role": "user", "content": user_message})
    
    # Call OpenAI API
    client = OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=4000,
        temperature=0.7
    )
    
    script = response.choices[0].message.content
    
    # Extract bash script from markdown code blocks if present
    if "```bash" in script:
        script = script.split("```bash")[1].split("```")[0].strip()
    elif "```" in script:
        script = script.split("```")[1].split("```")[0].strip()
    
    return script


def create_new_version(evolution_script: str, version: int) -> str:
    """Execute evolution script to create new agent version.
    
    Writes the evolution script to a file, makes it executable,
    runs it, and returns the path to the newly created agent.
    
    Args:
        evolution_script: Bash script that creates new version
        version: Version number for the new agent
        
    Returns:
        Path to the newly created agent file (e.g., 'agent_v1.py')
        
    Raises:
        Exception: If script execution fails
    """
    script_filename = f"evolve_v{version}.sh"
    current_filename = os.path.basename(__file__)
    
    # Substitute version placeholders and current filename in script
    script_with_version = evolution_script.replace("agent_vN.py", f"agent_v{version}.py")
    script_with_version = script_with_version.replace("vN", f"v{version}")
    script_with_version = script_with_version.replace("CURRENT_AGENT", current_filename)
    
    # Write evolution script to file
    with open(script_filename, "w", encoding="utf-8") as script_file:
        script_file.write("#!/bin/bash\n")
        script_file.write("set -e  # Exit on any error\n\n")
        script_file.write(script_with_version)
    
    # Make script executable
    os.chmod(script_filename, 0o755)
    
    # Execute the evolution script
    result = subprocess.run(
        ["/bin/bash", script_filename],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if result.returncode != 0:
        raise Exception(f"Evolution script failed: {result.stderr}")
    
    return f"agent_v{version}.py"


def test_new_version(agent_path: str) -> bool:
    """Test if new agent version works correctly.
    
    Runs the new agent with --test flag to verify it can start
    and respond correctly.
    
    Args:
        agent_path: Path to the agent file to test
        
    Returns:
        True if test passes, False otherwise
    """
    try:
        result = subprocess.run(
            [sys.executable, agent_path, "--test"],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False


def create_pull_request(version: int, task: str, branch_name: str) -> None:
    """Create pull request with the new version.
    
    Creates a git branch, commits all changes, pushes to GitHub,
    and opens a pull request.
    
    Args:
        version: Version number of the new agent
        task: Task description (for commit message and PR title)
        branch_name: Name for the git branch
        
    Raises:
        subprocess.CalledProcessError: If git commands fail
    """
    # Ensure we're on main branch and up to date
    subprocess.run(["git", "checkout", "main"], check=True)
    subprocess.run(["git", "pull"], check=True)
    
    # Create and checkout new branch
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    
    # Stage all changes (agent, scripts, any helper files)
    subprocess.run(["git", "add", "."], check=True)
    
    # Commit changes
    commit_message = f"v{version}: {task}"
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    
    # Push to GitHub
    subprocess.run(["git", "push", "origin", branch_name], check=True)
    
    # Create pull request via GitHub API
    pr_data = {
        "title": f"Agent Evolution v{version}: {task}",
        "body": (
            f"**Automated evolution from agent**\n\n"
            f"Task: {task}\n\n"
            f"This PR was automatically created by the self-modifying agent. "
            f"Review the changes and merge to deploy the new version.\n\n"
            f"**Review checklist:**\n"
            f"- [ ] Evolution script looks safe (`evolve_v{version}.sh`)\n"
            f"- [ ] New agent code is reasonable (`agent_v{version}.py`)\n"
            f"- [ ] No secrets or credentials exposed\n"
            f"- [ ] Tests pass (agent ran `--test` successfully)\n"
        ),
        "head": branch_name,
        "base": "main"
    }
    github_api("POST", "/pulls", pr_data)
    
    # Return to main branch
    subprocess.run(["git", "checkout", "main"], check=True)


def main() -> None:
    """Main loop: monitor GitHub issues and evolve the agent.
    
    Continuously polls for GitHub issues labeled 'agent-task',
    processes each one by generating and executing an evolution
    script, then creates a PR and switches to the new version.
    
    The agent implements automatic retry logic (3 attempts) and
    leaves failed issues open for human review.
    """
    # Handle test mode
    if "--test" in sys.argv:
        print("OK")
        sys.exit(0)
    
    # Validate environment
    if not all([API_KEY, GITHUB_TOKEN, REPO]):
        print("Error: Missing required environment variables")
        print("Required: OPENAI_API_KEY, GITHUB_TOKEN, REPO")
        print("\nCreate .env file with:")
        print("  OPENAI_API_KEY=sk-...")
        print("  GITHUB_TOKEN=ghp_...")
        print("  REPO=username/repo-name")
        sys.exit(1)
    
    print(f"🤖 Agent monitoring {REPO} for 'agent-task' issues...")
    print("Press Ctrl+C to stop\n")
    
    while True:
        try:
            # Get next version number
            version = get_next_version()
            
            # Fetch open issues labeled 'agent-task'
            response = github_api("GET", "/issues?labels=agent-task&state=open")
            issues = response.json()
            
            for issue in issues:
                issue_number = issue["number"]
                task = issue["title"]
                labels = [label["name"] for label in issue.get("labels", [])]
                
                # Skip issues that previously failed unless they have 'agent-retry' label
                if "agent-failed" in labels and "agent-retry" not in labels:
                    continue
                
                # If retrying, remove the failed label
                if "agent-retry" in labels:
                    print(f"\n🔄 [v{version}] Retrying Issue #{issue_number}: {task}")
                    github_api("DELETE", f"/issues/{issue_number}/labels/agent-failed")
                    github_api("DELETE", f"/issues/{issue_number}/labels/agent-retry")
                else:
                    print(f"\n⚡ [v{version}] Processing Issue #{issue_number}: {task}")
                
                max_retries = 3
                previous_attempt = None
                
                for attempt in range(1, max_retries + 1):
                    try:
                        # Generate evolution script (with retry context if needed)
                        if attempt == 1:
                            print("  → Generating evolution script...")
                        else:
                            print(f"  → Retry {attempt}/{max_retries}: Generating new approach...")
                        
                        evolution_script = generate_evolution_script(task, previous_attempt)
                        
                        # Create new version
                        print(f"  → Creating version {version}...")
                        new_agent_path = create_new_version(evolution_script, version)
                        
                        # Test new version
                        print("  → Testing new version...")
                        if test_new_version(new_agent_path):
                            print("  ✓ Tests passed")
                            
                            # Create pull request
                            print("  → Creating pull request...")
                            branch_name = f"evolution-v{version}"
                            create_pull_request(version, task, branch_name)
                            
                            # Comment on issue
                            retry_msg = f" (succeeded on attempt {attempt})" if attempt > 1 else ""
                            comment = f"✓ Successfully created PR for v{version}{retry_msg}"
                            github_api("POST", f"/issues/{issue_number}/comments", 
                                     {"body": comment})
                            
                            # Close issue
                            github_api("PATCH", f"/issues/{issue_number}", 
                                     {"state": "closed"})
                            
                            print(f"  ✓ Complete - switching to {new_agent_path}\n")
                            
                            # Switch to new version (replaces this process)
                            os.execv(sys.executable, [sys.executable, new_agent_path])
                            
                        else:
                            # Test failed - prepare for retry
                            print(f"  ✗ Tests failed (attempt {attempt}/{max_retries})")
                            
                            # Capture failure details for next attempt
                            previous_attempt = {
                                "script": evolution_script,
                                "error": "New version failed --test flag (exit code non-zero)"
                            }
                            
                            # If out of retries, give up but leave issue open
                            if attempt == max_retries:
                                comment = (
                                    f"✗ Failed after {max_retries} attempts.\n\n"
                                    f"All generated versions failed testing. "
                                    f"**Leaving issue open for human review.**\n\n"
                                    f"You can:\n"
                                    f"- Add the `agent-retry` label to try again\n"
                                    f"- Close the issue if task is no longer needed\n"
                                    f"- Manually implement and close the issue"
                                )
                                github_api("POST", f"/issues/{issue_number}/comments",
                                         {"body": comment})
                                # Add 'agent-failed' label for visibility
                                github_api("POST", f"/issues/{issue_number}/labels",
                                         {"labels": ["agent-failed"]})
                                print(f"  ✗ Giving up - issue left open for review\n")
                                break
                            
                    except Exception as error:
                        print(f"  ✗ Error on attempt {attempt}: {error}")
                        
                        # Capture error for retry
                        previous_attempt = {
                            "script": evolution_script if 'evolution_script' in locals() else "N/A",
                            "error": str(error)
                        }
                        
                        # If out of retries, give up but leave issue open
                        if attempt == max_retries:
                            comment = (
                                f"✗ Failed after {max_retries} attempts.\n\n"
                                f"Last error: {error}\n\n"
                                f"**Leaving issue open for human review.**\n\n"
                                f"You can:\n"
                                f"- Add the `agent-retry` label to try again\n"
                                f"- Close the issue if task is no longer needed\n"
                                f"- Manually implement and close the issue"
                            )
                            github_api("POST", f"/issues/{issue_number}/comments",
                                     {"body": comment})
                            # Add 'agent-failed' label for visibility
                            github_api("POST", f"/issues/{issue_number}/labels",
                                     {"labels": ["agent-failed"]})
                            print(f"  ✗ Giving up - issue left open for review\n")
                            break
            
            # Poll every 30 seconds
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n\n👋 Agent stopped by user")
            sys.exit(0)
        except Exception as error:
            print(f"❌ Error in main loop: {error}")
            time.sleep(60)  # Wait longer on errors


if __name__ == "__main__":
    main()
