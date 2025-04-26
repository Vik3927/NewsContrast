from PIL import Image

# Load the original image
input_path = 'ChatGPT Image Apr 22, 2025, 01_51_23 AM.png'  # Replace with the actual filename
output_sizes = [16, 48, 128]

# Open the image
img = Image.open(input_path)

# Save resized versions
for size in output_sizes:
    resized = img.resize((size, size), Image.LANCZOS)
    resized.save(f'icons/icon{size}.png')

print("Icons generated: icon16.png, icon48.png, icon128.png")
