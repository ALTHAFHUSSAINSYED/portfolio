import json

def convert_js_to_json():
    """Convert the JavaScript mock data file to JSON format"""
    with open('../frontend/src/data/mock.js', 'r', encoding='utf-8') as file:
        content = file.read()
        
    # Remove the export statement and comments
    content = content.split('export const portfolioData =')[1].strip().rstrip(';')
    
    # Write to a temporary JSON file
    with open('temp_data.json', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Created temporary JSON file for inspection.")
    
if __name__ == "__main__":
    convert_js_to_json()