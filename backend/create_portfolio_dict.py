import json
import re

def extract_section(content, section_name):
    """Extract a section from the content"""
    pattern = rf'{section_name}:\s*{{([^}}]+)}}'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1)
    return None

def parse_object(text):
    """Parse a JavaScript object into a Python dictionary"""
    result = {}
    lines = text.split('\n')
    current_key = None
    current_value = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if ':' in line and not line.strip().startswith('"'):
            if current_key and current_value:
                result[current_key] = '\n'.join(current_value)
                current_value = []
            
            key, value = line.split(':', 1)
            current_key = key.strip().strip('"')
            value = value.strip().strip('",')
            if value:
                current_value.append(value)
        elif current_key:
            current_value.append(line.strip('",'))
    
    if current_key and current_value:
        result[current_key] = '\n'.join(current_value)
    
    return result

def parse_array(text):
    """Parse a JavaScript array into a Python list"""
    items = []
    current_item = {}
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('{'):
            if current_item:
                items.append(current_item)
            current_item = {}
        elif line.endswith('},') or line.endswith('}'):
            if current_item:
                items.append(current_item)
            current_item = {}
        elif ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().strip('"')
            value = value.strip().strip('",')
            if value:
                current_item[key] = value
    
    if current_item:
        items.append(current_item)
    
    return items

def create_portfolio_dict():
    """Create a dictionary of portfolio data"""
    with open('../frontend/src/data/mock.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    portfolio_data = {}
    
    # Personal Info
    personal_section = extract_section(content, 'personalInfo')
    if personal_section:
        portfolio_data['personalInfo'] = parse_object(personal_section)
    
    # Skills
    skills_section = extract_section(content, 'skills')
    if skills_section:
        skills = {}
        current_category = None
        
        for line in skills_section.split('\n'):
            line = line.strip()
            if line.endswith(': ['):
                current_category = line.rstrip(': [')
                skills[current_category] = []
            elif line.startswith('{') and current_category:
                skill = {}
                parts = line.strip('{}').split(',')
                for part in parts:
                    if ':' in part:
                        k, v = part.split(':', 1)
                        k = k.strip()
                        v = v.strip().strip('"')
                        if v.isdigit():
                            v = int(v)
                        skill[k] = v
                if skill:
                    skills[current_category].append(skill)
        portfolio_data['skills'] = skills
    
    # Experience
    experience_pattern = r'experience:\s*\[(.*?)\],'
    experience_match = re.search(experience_pattern, content, re.DOTALL)
    if experience_match:
        experience_text = experience_match.group(1)
        portfolio_data['experience'] = parse_array(experience_text)
    
    # Projects
    projects_pattern = r'projects:\s*\[(.*?)\],'
    projects_match = re.search(projects_pattern, content, re.DOTALL)
    if projects_match:
        projects_text = projects_match.group(1)
        portfolio_data['projects'] = parse_array(projects_text)
    
    # Certifications
    certifications_pattern = r'certifications:\s*\[(.*?)\]'
    certifications_match = re.search(certifications_pattern, content, re.DOTALL)
    if certifications_match:
        certifications_text = certifications_match.group(1)
        portfolio_data['certifications'] = parse_array(certifications_text)
    
    # Write the data as JSON
    with open('portfolio_data.json', 'w', encoding='utf-8') as f:
        json.dump(portfolio_data, f, indent=2)
    
    print("Created portfolio_data.json with sections:", list(portfolio_data.keys()))
    return True

if __name__ == "__main__":
    create_portfolio_dict()