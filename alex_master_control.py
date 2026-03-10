import os
import subprocess
import time
import datetime
import sys

# Paths
BASE_DIR = "/home/fernandes/workspace/agenthub_py"
VENV_PYTHON = "/home/fernandes/my_env/bin/python3"
HUB_SERVER = os.path.join(BASE_DIR, "main.py")
EXPANSION_LOOP = os.path.join(BASE_DIR, "alex_eternal_expansion.py")
ISSUE_MANAGER = os.path.join(BASE_DIR, "alex_issue_manager.py")

def is_process_running(name):
    try:
        output = subprocess.check_output(["ps", "aux"])
        return name in output.decode()
    except:
        return False

def start_background_task(command, log_file):
    log_path = os.path.join(BASE_DIR, log_file)
    return subprocess.Popen(
        f"nohup {command} > {log_path} 2>&1 &",
        shell=True,
        preexec_fn=os.setpid
    )

def log_status(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 👑 MASTER CONTROL: {message}")

def run_control_cycle():
    log_status("Initiating Master Control Cycle...")

    # 1. Check AgentHub Server
    if not is_process_running("agenthub_py/main.py"):
        log_status("AgentHub Server is DOWN. Restarting...")
        start_background_task(f"{VENV_PYTHON} {HUB_SERVER}", "server.log")
    else:
        log_status("AgentHub Server is ONLINE.")

    # 2. Check Eternal Expansion Loop
    if not is_process_running("alex_eternal_expansion.py"):
        log_status("Expansion Loop is DOWN. Restarting...")
        start_background_task(f"{VENV_PYTHON} {EXPANSION_LOOP}", "eternal_loop.log")
    else:
        log_status("Expansion Loop is ONLINE.")

    # 3. Run Intelligence Maintenance
    log_status("Running system maintenance...")
    try:
        subprocess.run([VENV_PYTHON, ISSUE_MANAGER], check=True)
        log_status("Maintenance complete. Issues checked.")
    except Exception as e:
        log_status(f"Maintenance Error: {e}")

    log_status("Control cycle complete. System is STABLE.")

if __name__ == "__main__":
    while True:
        run_control_cycle()
        # Sleep for 15 minutes before the next check
        time.sleep(900)
