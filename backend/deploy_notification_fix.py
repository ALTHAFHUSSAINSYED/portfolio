
import os
import base64
import subprocess
import time

# Configuration
SSH_KEY = "c:/portfolio/portfolio/portfolio.key.pem"
SSH_USER = "ec2-user"
SSH_HOST = "15.207.107.6"
CONTAINER = "portfolio-backend"

FILES_TO_DEPLOY = [
    {
        "local": "c:/portfolio/portfolio/backend/auto_blogger/notifier.py",
        "remote": "/app/backend/auto_blogger/notifier.py"
    },
    {
        "local": "c:/portfolio/portfolio/backend/auto_blogger/scheduler.py",
        "remote": "/app/backend/auto_blogger/scheduler.py"
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
    print("Starting Notification Logic Deployment to EC2...")
    
    for item in FILES_TO_DEPLOY:
        local_path = item['local']
        remote_path = item['remote']
        
        print(f"\nProcessing {os.path.basename(local_path)}...")
        
        # Read Local
        try:
            with open(local_path, 'rb') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Could not read local file: {e}")
            continue
            
        # Encode Base64
        b64_content = base64.b64encode(content).decode('utf-8')
        
        if len(b64_content) < 2000:
            deploy_cmd = f"docker exec -i {CONTAINER} sh -c 'echo {b64_content} | base64 -d > {remote_path}'"
            if not run_ssh_command(deploy_cmd, f"Uploading {os.path.basename(remote_path)}"): return
        else:
            print(f"📦 File large ({len(b64_content)} chars). Chunking...")
            init_cmd = f"docker exec -i {CONTAINER} sh -c ': > {remote_path}'"
            if not run_ssh_command(init_cmd, f"Initializing {os.path.basename(remote_path)}"): return

            chunk_size = 2000
            for i in range(0, len(b64_content), chunk_size):
                chunk = b64_content[i:i+chunk_size]
                temp_b64_path = f"/tmp/{os.path.basename(remote_path)}.b64"
                op = ">" if i == 0 else ">>"
                chunk_cmd = f"docker exec -i {CONTAINER} sh -c 'echo {chunk} {op} {temp_b64_path}'"
                if not run_ssh_command(chunk_cmd, f"   chunk {i//chunk_size + 1}..."): return
            
            decode_cmd = f"docker exec -i {CONTAINER} sh -c 'base64 -d /tmp/{os.path.basename(remote_path)}.b64 > {remote_path} && rm /tmp/{os.path.basename(remote_path)}.b64'"
            if not run_ssh_command(decode_cmd, f"Decoding {os.path.basename(remote_path)}"): return

    print("\n✅ Deployment Complete. Restarting Service to apply changes...")
    
    # We must RESTART the container service processes or restart the container to reload Py files if they are in memory (Scheduler is waiting).
    # Since we are running test-all as a one-off command, code will be reloaded on next run.
    # But for the long-running background scheduler, we should restart the container.
    
    restart_cmd = f"docker restart {CONTAINER}"
    # run_ssh_command(restart_cmd, "Restarting Backend Container") // OPTIONAL - User asked for RCA/Status, not restart yet?
    # Actually, user wants to know failing reason. Let's just push files so next run has better logging.
    
    print("\n✅ Files Updated. Ready for next run.")

if __name__ == "__main__":
    deploy()
