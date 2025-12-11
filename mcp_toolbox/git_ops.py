import subprocess
import os

def _run_git(args, cwd=None):
    if cwd is None:
        cwd = os.getcwd()
    
    cmd = ["git"] + args
    try:
        res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
        return {"status": "success", "output": res.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr.strip()}

def git_status(cwd=None):
    return _run_git(["status"], cwd)

def git_log(limit=5, cwd=None):
    return _run_git(["log", f"-n {limit}", "--oneline"], cwd)

def git_diff(cached=False, cwd=None):
    args = ["diff"]
    if cached:
        args.append("--cached")
    # Limit output size for agent sanity
    res = _run_git(args, cwd)
    if res["status"] == "success" and len(res["output"]) > 5000:
        res["output"] = res["output"][:5000] + "\n... (truncated)"
    return res

def git_create_branch(branch_name, cwd=None):
    """
    Creates a new branch.
    """
    return _run_git(["checkout", "-b", branch_name], cwd)

def git_checkout(branch_name, cwd=None):
    return _run_git(["checkout", branch_name], cwd)

def git_list_branches(cwd=None):
    return _run_git(["branch", "-a"], cwd)
