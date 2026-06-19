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
    
    # --- LOGO.PNG (Favicon - Zoomed) ---
    # Calculate size for square crop (use smallest dimension)
    min_dim = min(img.size)
    
    # ZOOM LOGIC: Crop a smaller center square to simulate zoom
    # 1.0 = No Zoom (100% show)
    # 0.8 = 1.25x Zoom (80% show) -> Matches Hero/LinkedIn 1.25x scale
    zoom_factor = 0.8
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
    output.save(output_path)
    print(f"✅ Created zoomed favicon: {output_path}")

    # --- PROFILE-TRANSPARENT.PNG (LinkedIn - Full Face) ---
    output_profile_path = os.path.join(base_dir, "frontend", "public", "profile-transparent.png")
    
    # Use full image square crop
    size_full = (min_dim, min_dim)
    mask_full = Image.new('L', size_full, 0)
    draw_full = ImageDraw.Draw(mask_full)
    draw_full.ellipse((0, 0) + size_full, fill=255)
    
    output_profile = ImageOps.fit(img, size_full, centering=(0.5, 0.5))
    output_profile.putalpha(mask_full)
    output_profile.save(output_profile_path)
    print(f"✅ Created transparent profile: {output_profile_path}")

except ImportError:
    print("❌ Error: Pillow library not found. Please run 'pip install Pillow'")
except Exception as e:
    print(f"❌ Error processing image: {e}")
