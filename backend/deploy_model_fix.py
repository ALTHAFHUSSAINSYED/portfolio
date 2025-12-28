
import os
import base64
import subprocess
import time

# Configuration
SSH_KEY = "c:/portfolio/portfolio/PORTFOLIO.pem"
SSH_USER = "ec2-user"
SSH_HOST = "13.233.54.210"
CONTAINER = "portfolio-backend"

FILES_TO_DEPLOY = [
    {
        "local": "c:/portfolio/portfolio/backend/auto_blogger/models/model_config.py",
        "remote": "/app/backend/auto_blogger/models/model_config.py"
    },
    {
        "local": "c:/portfolio/portfolio/backend/auto_blogger/writer.py",
        "remote": "/app/backend/auto_blogger/writer.py"
    }
]

def run_ssh_command(cmd, description):
    print(f"🚀 {description}...")
    full_cmd = f'ssh -i {SSH_KEY} -o StrictHostKeyChecking=no {SSH_USER}@{SSH_HOST} "{cmd}"'
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def deploy():
    print("Starting Model Config & Writer Logic Deployment...")
    for item in FILES_TO_DEPLOY:
        local_path = item['local']
        remote_path = item['remote']
        print(f"\nProcessing {os.path.basename(local_path)}...")
        try:
            with open(local_path, 'rb') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Read Error: {e}")
            continue
        
        b64_content = base64.b64encode(content).decode('utf-8')
        if len(b64_content) < 2000:
            cmd = f"docker exec -i {CONTAINER} sh -c 'echo {b64_content} | base64 -d > {remote_path}'"
            run_ssh_command(cmd, f"Uploading {os.path.basename(remote_path)}")
        else:
            print(f"📦 Chunking ({len(b64_content)} chars)...")
            run_ssh_command(f"docker exec -i {CONTAINER} sh -c ': > {remote_path}'", "Init")
            chunk_size = 2000
            for i in range(0, len(b64_content), chunk_size):
                chunk = b64_content[i:i+chunk_size]
                temp = f"/tmp/{os.path.basename(remote_path)}.b64"
                op = ">" if i == 0 else ">>"
                cmd = f"docker exec -i {CONTAINER} sh -c 'echo {chunk} {op} {temp}'"
                run_ssh_command(cmd, f"chunk {i//chunk_size+1}...")
            run_ssh_command(f"docker exec -i {CONTAINER} sh -c 'base64 -d /tmp/{os.path.basename(remote_path)}.b64 > {remote_path} && rm /tmp/{os.path.basename(remote_path)}.b64'", "Decoding")

    print("\n✅ Deployment Complete.")

if __name__ == "__main__":
    deploy()
