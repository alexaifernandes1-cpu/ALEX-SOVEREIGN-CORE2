import requests
import os
import json
import subprocess
import tempfile

class AgentHubClient:
    def __init__(self, server_url="http://localhost:8000", api_key=None):
        self.server_url = server_url.rstrip("/")
        self.api_key = api_key

    def register_agent(self, agent_id, admin_key):
        url = f"{self.server_url}/api/admin/agents"
        headers = {"Authorization": f"Bearer {admin_key}"}
        resp = requests.post(url, json={"id": agent_id}, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            self.api_key = data["api_key"]
            self._save_config(agent_id)
            return data
        else:
            print(f"Error: {resp.text}")
            return None

    def _save_config(self, agent_id):
        config_path = os.path.expanduser("~/.agenthub_alex.json")
        with open(config_path, "w") as f:
            json.dump({"server_url": self.server_url, "api_key": self.api_key, "agent_id": agent_id}, f)

    def load_config(self):
        config_path = os.path.expanduser("~/.agenthub_alex.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                cfg = json.load(f)
                self.server_url = cfg["server_url"]
                self.api_key = cfg["api_key"]
                return cfg
        return None

    def post_message(self, channel, content):
        url = f"{self.server_url}/api/channels/{channel}/posts"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        resp = requests.post(url, json={"content": content}, headers=headers)
        return resp.json()

    def push_code(self, repo_path, message="Autonomous update"):
        """Creates a git bundle and pushes it to the Hub."""
        # 1. Ensure it's a git repo and commit changes
        try:
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
            # Check if there are changes to commit
            status = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True).stdout
            if not status:
                return {"status": "skipped", "message": "No changes to push"}
            
            subprocess.run(["git", "commit", "-m", message], cwd=repo_path, check=True)
            
            # 2. Create bundle
            with tempfile.NamedTemporaryFile(suffix=".bundle", delete=False) as tmp:
                bundle_path = tmp.name
            
            subprocess.run(["git", "bundle", "create", bundle_path, "HEAD"], cwd=repo_path, check=True)
            
            # 3. Upload
            url = f"{self.server_url}/api/git/push"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/octet-stream"}
            with open(bundle_path, "rb") as f:
                resp = requests.post(url, data=f, headers=headers)
            
            os.remove(bundle_path)
            return resp.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    client = AgentHubClient()
    client.load_config()
    if client.api_key:
        print("🚀 Testing Autonomous Push...")
        # Self-push the upgraded client
        res = client.push_code("/home/fernandes/workspace/agenthub_py", "EVOLUTION: Added push_code capability to ah_client.py")
        print(f"✅ Result: {res}")
        client.post_message("results", f"Autonomous Code Evolution Complete. Result: {res}")
