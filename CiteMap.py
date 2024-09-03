"""
This script is designed to add attribution text to the lower right corner of the map image downloaded from OSM
You can change the script to write different text at differnt position with different color.

"""

from PIL import Image, ImageDraw, ImageFont

def add_attribution(image_path, output_path, attribution_text):
    # Open the image file
    with Image.open(image_path) as img:
        # Initialize ImageDraw
        draw = ImageDraw.Draw(img)
        
        # Define font and size (adjust the path to a valid font file if needed)
        try:
            font = ImageFont.truetype("arial.ttf", 20)  # Adjust size as needed
        except IOError:
            font = ImageFont.load_default()
        
        # Calculate text size and position
        text_bbox = draw.textbbox((0, 0), attribution_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        width, height = img.size
        x = width - text_width - 10  # 10 pixels from the right
        y = height - text_height - 10  # 10 pixels from the bottom
        
        # Draw text on image
        draw.text((x, y), attribution_text, font=font, fill=(255, 255, 255))  # White color text
        
        # Save the modified image
        img.save(output_path)

# Usage
image_path = 'map_image.png'
output_path = 'map_image_with_attribution.png'
attribution_text = "© OpenStreetMap contributors"

add_attribution(image_path, output_path, attribution_text)
