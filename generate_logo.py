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
    # Calculate size for square crop (use smallest dimension)
    min_dim = min(img.size)
    
    # ZOOM LOGIC: Crop a smaller center square (e.g., 60% of original) to zoom in
    zoom_factor = 0.6  # Lower value = Higher Zoom
    crop_size = int(min_dim * zoom_factor)
    
    # Calculate crop box (left, upper, right, lower)
    left = (img.width - crop_size) // 2
    top = (img.height - crop_size) // 2
    right = left + crop_size
    bottom = top + crop_size
    
    # Crop the center
    img_cropped = img.crop((left, top, right, bottom))
    
    # Resize back to high res for crispness
    size = (512, 512)
    img_resized = img_cropped.resize(size, Image.Resampling.LANCZOS)
    
    # Create circular mask
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    
    # Fit image to mask
    output = ImageOps.fit(img_resized, size, centering=(0.5, 0.5))
    output.putalpha(mask)
    
    # Save as PNG
    output.save(output_path)
    print(f"✅ Successfully created circular logo at: {output_path}")

except ImportError:
    print("❌ Error: Pillow library not found. Please run 'pip install Pillow'")
except Exception as e:
    print(f"❌ Error processing image: {e}")
