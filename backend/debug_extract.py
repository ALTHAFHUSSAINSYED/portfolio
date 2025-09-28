def extract_data():
    with open('../frontend/src/data/mock.js', 'r', encoding='utf-8') as file:
        content = file.read()
        
    print("Original content:")
    print(content[:500])  # Print first 500 characters
    
    # Extract the object part
    obj_part = content.split('export const portfolioData =')[1].strip().rstrip(';')
    
    print("\nExtracted object part:")
    print(obj_part[:500])  # Print first 500 characters
    
    return obj_part

if __name__ == "__main__":
    extract_data()