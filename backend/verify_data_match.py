import json
import os
import sys

def verify_portfolio_data():
    # 1. Locate the file
    file_path = 'portfolio_data.json'
    if not os.path.exists(file_path):
        file_path = 'backend/portfolio_data.json'
    
    if not os.path.exists(file_path):
        print(f"❌ CRITICAL: Could not find portfolio_data.json in current or backend/ folder.")
        return

    print(f"📂 Reading: {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        return

    projects = data.get("projects", [])
    print(f"🔍 Found {len(projects)} projects in file.\n")

    # 2. Define the EXACT Expected Data (IDs and Names)
    expected_projects = {
        "aws-terraform-ansible-automation": {
            "name": "AWS Infrastructure Automation with Terraform || Ansible",
            "snippet": "Terraform used to create full AWS infrastructure"
        },
        "1265481c-8697-4d42-b39a-f533801bb0d9": {
            "name": "Cloud-Native Microservices CI/CD Pipeline on AWS",
            "snippet": "Automated CI/CD pipeline for microservices using Jenkins"
        },
        "aws-cloudwatch-grafana-monitoring": {
            "name": "AWS CloudWatch & Grafana Monitoring Automation",
            "snippet": "Automated end-to-end monitoring for EC2-based web servers"
        }
    }

    # 3. Verify Each Project
    all_matched = True
    
    for p_id, expected in expected_projects.items():
        # Find project by ID
        found = next((p for p in projects if p.get("id") == p_id), None)
        
        if not found:
            print(f"❌ MISSING: Project ID '{p_id}' NOT FOUND.")
            all_matched = False
            continue

        # Check Name
        name_match = (found.get("name") == expected["name"])
        # Check if Details exist and contain keywords
        details = found.get("details", "")
        has_details = len(details) > 100
        
        print(f"✅ FOUND: {p_id}")
        print(f"   Name Match: {'✅ Yes' if name_match else f'❌ No (Found: {found.get('name')})'}")
        print(f"   Has Details: {'✅ Yes' if has_details else '❌ No (Empty)'}")
        
        if not name_match:
            print(f"   ⚠️ WARNING: Name mismatch.\n      Expected: {expected['name']}\n      Found:    {found.get('name')}")
            all_matched = False

    print("-" * 40)
    if all_matched:
        print("🎉 CONFIRMED: All 3 projects are present with correct IDs and Names.")
    else:
        print("⚠️ ISSUE: Some data is missing or mismatched. Check the logs above.")

if __name__ == "__main__":
    verify_portfolio_data()
