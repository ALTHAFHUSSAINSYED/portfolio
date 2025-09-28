import re
import json

def clean_js_to_json(content):
    """Convert JavaScript object to valid JSON string"""
    # Add quotes to property names
    content = re.sub(r'(\s*)(\w+):', r'\1"\2":', content)
    
    # Fix newlines in strings
    content = re.sub(r'"\s*\n\s*([^"]*)"', lambda m: '"' + m.group(1).replace('\n', ' ') + '"', content)
    
    # Remove any remaining newlines within string values
    content = re.sub(r'(?<="[^"]*)\n(?=[^"]*")', ' ', content)
    
    return content

def convert_js_to_json():
    """Convert JavaScript export to JSON"""
    try:
        # Read the JavaScript file
        with open('../frontend/src/data/mock.js', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extract the data object
        content = content.split('export const portfolioData =')[1].strip().rstrip(';')
        
        # Clean and format
        content = clean_js_to_json(content)
        
        # Parse as JSON to validate
        data = json.loads(content)
        
        # Write the validated JSON
        with open('portfolio_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        print("Successfully converted JavaScript to JSON!")
        return True
            
    except Exception as e:
        print(f"Error converting file: {e}")
        return False

if __name__ == "__main__":
    convert_js_to_json()