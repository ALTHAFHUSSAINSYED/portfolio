def format_mock_data():
    """Read mock.js and format it as JSON manually"""
    from pathlib import Path
    import json
    
    # Read the mock data
    with open('../frontend/src/data/mock.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the data part
    data_part = content.split('export const portfolioData =')[1].strip().rstrip(';')
    
    # Basic cleanup
    lines = []
    for line in data_part.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Add quotes to property names at start of lines
        if line and line[0].isalpha():
            property_name = line.split(':')[0].strip()
            rest_of_line = ':'.join(line.split(':')[1:])
            line = f'"{property_name}":{rest_of_line}'
            
        lines.append(line)
    
    # Join back together
    formatted = '\n'.join(lines)
    
    # Write the formatted content
    with open('formatted_data.json', 'w', encoding='utf-8') as f:
        f.write(formatted)
    
    print("Created formatted_data.json")
    print("\nFirst few lines:")
    print('\n'.join(lines[:10]))

if __name__ == "__main__":
    format_mock_data()