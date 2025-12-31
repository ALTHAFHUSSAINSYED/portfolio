from PIL import Image, ImageOps, ImageDraw
import os

# Define paths
base_dir = r"C:\portfolio\portfolio"
input_path = os.path.join(base_dir, "frontend", "public", "profile-pic.jpg")
output_path = os.path.join(base_dir, "frontend", "public", "logo.png")

print(f"Processing: {input_path}")

try:
    # Open image
    img = Image.open(input_path).convert("RGBA")
    
    # Calculate size for square crop (use smallest dimension)
    min_dim = min(img.size)
    size = (min_dim, min_dim)
    
    # Create circular mask
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    
    # Crop and fit image to the mask size (centered)
    output = ImageOps.fit(img, size, centering=(0.5, 0.5))
    output.putalpha(mask)
    
    # Save as PNG
    output.save(output_path)
    print(f"✅ Successfully created circular logo at: {output_path}")

except ImportError:
    print("❌ Error: Pillow library not found. Please run 'pip install Pillow'")
except Exception as e:
    print(f"❌ Error processing image: {e}")
