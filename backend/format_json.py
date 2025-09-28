def convert_to_json():
    with open('temp_data.json', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Add quotes to property names
    import re
    content = re.sub(r'(\s*)(\w+):', r'\1"\2":', content)
    
    # Write the properly formatted JSON
    with open('portfolio_data.json', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Created properly formatted JSON file.")
    
if __name__ == "__main__":
    convert_to_json()