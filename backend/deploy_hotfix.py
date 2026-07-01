
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
        "local": "c:/portfolio/portfolio/backend/auto_blogger/writer.py",
        "remote": "/app/backend/auto_blogger/writer.py"
    }
]

def run_ssh_command(cmd, description):
    print(f"🚀 {description}...")
    full_cmd = f'ssh -i {SSH_KEY} -o StrictHostKeyChecking=no {SSH_USER}@{SSH_HOST} "{cmd}"'
    
    try:
        # Using shell=True for Windows to handle the command string correctly
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed: {result.stderr}")
            return False
        # print(f"✅ Success.")
        return True
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def deploy():
    print("Starting Hotfix Deployment to EC2...")
    
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
            # Short file: Single shot
            deploy_cmd = f"docker exec -i {CONTAINER} sh -c 'echo {b64_content} | base64 -d > {remote_path}'"
            if not run_ssh_command(deploy_cmd, f"Uploading {os.path.basename(remote_path)}"):
                 print("⛔ Aborting.")
                 return
        else:
            # Long file: Chunked upload
            print(f"📦 File too large for single cmd ({len(b64_content)} chars). Chunking...")
            
            # 1. Clear file
            init_cmd = f"docker exec -i {CONTAINER} sh -c ': > {remote_path}'"
            if not run_ssh_command(init_cmd, f"Initializing {os.path.basename(remote_path)}"): return

            chunk_size = 2000 # Safe limit for Windows cmd line
            total_chunks = (len(b64_content) + chunk_size - 1) // chunk_size
            
            for i in range(0, len(b64_content), chunk_size):
                chunk = b64_content[i:i+chunk_size]
                
                temp_b64_path = f"/tmp/{os.path.basename(remote_path)}.b64"
                
                if i == 0:
                     op = ">" # Overwrite start
                else:
                     op = ">>" # Append
                
                # We echo the BASE64 text to a temp file
                chunk_cmd = f"docker exec -i {CONTAINER} sh -c 'echo {chunk} {op} {temp_b64_path}'"
                if not run_ssh_command(chunk_cmd, f"   chunk {i//chunk_size + 1}/{total_chunks}"): return
            
            # Decode the full temp file to valid destination
            decode_cmd = f"docker exec -i {CONTAINER} sh -c 'base64 -d /tmp/{os.path.basename(remote_path)}.b64 > {remote_path} && rm /tmp/{os.path.basename(remote_path)}.b64'"
            if not run_ssh_command(decode_cmd, f"Decoding {os.path.basename(remote_path)}"): return

    print("\n✅ Deployment Complete. Triggering Test Run...")
    
    # Run Test (as module to fix imports)
    test_cmd = f"docker exec -i {CONTAINER} sh -c 'cd /app && python3 -m backend.auto_blogger.scheduler --test-all'"
    # We want to see output live if possible, or print it at end
    # subprocess.run handles this but we'll print output
    
    print(f"🧪 Executing: {test_cmd}")
    full_test_cmd = f'ssh -i {SSH_KEY} -o StrictHostKeyChecking=no {SSH_USER}@{SSH_HOST} "{test_cmd}"'
    
    # Run test and stream output
    process = subprocess.Popen(full_test_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
            
    rc = process.poll()
    if rc == 0:
        print("\n✅ TEST PASSED.")
    else:
        print(f"\n❌ TEST FAILED with code {rc}.")
        print(process.stderr.read())

if __name__ == "__main__":
    deploy()
