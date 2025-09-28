def fix_json():
    """Fix the JSON format issues"""
    import re
    
    with open('temp_data.json', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add quotes to property names (one step at a time)
    lines = []
    for line in content.split('\n'):
        # Skip empty lines
        if not line.strip():
            continue
        
        # Add quotes to property names at the start of lines
        line = re.sub(r'^\s*(\w+):', r'  "\1":', line)
        
        # Remove trailing commas in arrays and objects
        line = re.sub(r',(\s*[\]}])', r'\1', line)
        
        lines.append(line)
    
    # Join back together
    content = '\n'.join(lines)
    
    # Write the fixed content
    with open('fixed_data.json', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Created fixed JSON file")
    print("\nFirst few lines of fixed content:")
    print('\n'.join(content.split('\n')[:10]))

if __name__ == "__main__":
    fix_json()