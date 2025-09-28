import json
import re

def fix_json_formatting(content):
    """Fix common JSON formatting issues"""
    # Replace newlines in strings with spaces
    content = re.sub(r'(?<="[^"]*)\n\s*(?=[^"]*")', ' ', content)
    
    # Add quotes to all property names
    content = re.sub(r'(?m)^(\s*)(\w+):', r'\1"\2":', content)
    
    # Remove trailing commas
    content = re.sub(r',(\s*[}\]])', r'\1', content)
    
    return content

def load_and_convert_js():
    """Load the JS file and convert it to proper JSON"""
    try:
        # Read the source JavaScript file
        with open('../frontend/src/data/mock.js', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extract the data object
        content = content.split('export const portfolioData =')[1].strip().rstrip(';')
        
        # Clean up the content
        content = fix_json_formatting(content)
        
        # Try to parse it as JSON to validate
        try:
            data = json.loads(content)
            print("Successfully parsed as JSON!")
            
            # Write the validated JSON with proper formatting
            with open('valid_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            # Write the problematic content for inspection
            with open('parse_error.json', 'w', encoding='utf-8') as f:
                f.write(content)
            print("Wrote problematic content to parse_error.json")
            return False
            
    except Exception as e:
        print(f"Error processing file: {e}")
        return False

if __name__ == "__main__":
    if load_and_convert_js():
        print("Successfully created valid_data.json!")
    else:
        print("Failed to create valid JSON. Check parse_error.json for details.")