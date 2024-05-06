# This script can read all photos in the script/exe's folder, get their gps information and
# write a csv file with gps info and link to image
# this csv file can be imported into Google Earth for showing image by their location on map.
# And you can export the kmz for the photos from Google Earth.




import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import csv

# Function to convert GPS coordinates from degrees, minutes, seconds to decimal degrees
def convert_to_decimal_degrees(coord):
    degrees = coord[0]
    minutes = coord[1]
    seconds = coord[2]
    decimal_degrees = degrees + (minutes / 60.0) + (seconds / 3600.0)
    return decimal_degrees

# Function to extract GPS data from an image file and convert to decimal degrees
def extract_gps_data(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data and 34853 in exif_data:
                gps_data = exif_data[34853]  # GPSInfo tag
                latitude = convert_to_decimal_degrees(gps_data[2])  # GPS latitude
                # Pay attention to the hemisphere, west is "-" east has no sign
                longitude = -convert_to_decimal_degrees(gps_data[4])  # GPS longitude
                altitude = gps_data[6] if 6 in gps_data else None  # GPS altitude
                return latitude, longitude, altitude
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
    return None, None, None

# Folder containing your photos  (for builidng executables use this line for folder, and build the script into exe with pyinstaller)
folder_path = os.path.dirname(sys.executable)

# Folder containing your photos  ( for using script directly, use this line)
#folder_path = os.path.dirname(os.path.abspath(__file__))

# Create or open a CSV file to write the data
csv_file_path = "photo_data.csv"
with open(csv_file_path, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Photo Path", "Latitude", "Longitude", "Altitude"])
    
    image_link_string_front = r'<img style="max-width:1500px;" src="'
    image_link_string_rear = r'">'

    # Loop through the files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".JPG")):
            image_path = os.path.join(folder_path, filename)
            image_link = image_link_string_front + image_path + image_link_string_rear
            
            latitude, longitude, altitude = extract_gps_data(image_path)
            if latitude is not None and longitude is not None:
                csv_writer.writerow([image_link, latitude, longitude, altitude])

print(f"Data has been written to {csv_file_path}")
