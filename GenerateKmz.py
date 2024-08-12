import os
import zipfile
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import shutil

# This script can be built into a exe using pyinstaller. 
# Put the script or exe into the same folder with photos (photos with location data in their exif)
# double click the script or exe, it will generate a kmz file that contain photo and a kml file.
# you can then drag and drop the kmz to a Google Earth app window, and view the photos by location in Google Earth.

def convert_to_decimal_degrees(coord, ref):
    degrees = coord[0]
    minutes = coord[1]
    seconds = coord[2]
    decimal_degrees = degrees + (minutes / 60.0) + (seconds / 3600.0)
    
    # Adjust sign based on hemisphere reference
    if ref in ['S', 'W']:
        decimal_degrees = -decimal_degrees
    
    return decimal_degrees

def extract_gps_data(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data and 34853 in exif_data:
                gps_data = exif_data[34853]  # GPSInfo tag

                latitude = convert_to_decimal_degrees(gps_data[2], gps_data[1])  # GPS latitude
                longitude = convert_to_decimal_degrees(gps_data[4], gps_data[3])  # GPS longitude
                altitude = gps_data[6] if 6 in gps_data else None  # GPS altitude
                
                return latitude, longitude, altitude
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
    return None, None, None

def create_kml(kml_file_path, image_data):
    kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
    <name>photo_data.kmz</name>
    <Folder>
        <name>Photo Points</name>
    """

    for img_name, (lat, lon, alt) in image_data.items():
        kml_content += f"""
        <Placemark>
            <name>{img_name}</name>
            <description><![CDATA[<img style="max-width:1500px;" src="files/{img_name}">]]></description>
            <Point>
                <coordinates>{lon},{lat},{alt or 0}</coordinates>
            </Point>
        </Placemark>
        """
    
    kml_content += """
    </Folder>
</Document>
</kml>
"""
    with open(kml_file_path, 'w') as kml_file:
        kml_file.write(kml_content)

def create_kmz(output_path, kml_file, files_folder):
    with zipfile.ZipFile(output_path, 'w') as kmz:
        kmz.write(kml_file, arcname="doc.kml")
        for root, dirs, files in os.walk(files_folder):
            for file in files:
                kmz.write(os.path.join(root, file), arcname=os.path.join("files", file))

def main():
    # For direct use, use the following line
    #folder_path = os.path.dirname(os.path.abspath(__file__))
    # For pyinstaller build, use the following line.
    folder_path =os.path.dirname(sys.executable)
    files_folder = os.path.join(folder_path, "files")
    kml_file = os.path.join(folder_path, "doc.kml")
    kmz_file = os.path.join(folder_path, "photo_data.kmz")

    # Create the "files" directory if it doesn't exist
    if not os.path.exists(files_folder):
        os.makedirs(files_folder)

    image_data = {}
    
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp")):
            image_path = os.path.join(folder_path, filename)
            latitude, longitude, altitude = extract_gps_data(image_path)
            if latitude is not None and longitude is not None:
                image_data[filename] = (latitude, longitude, altitude)
                shutil.copy(image_path, os.path.join(files_folder, filename))

    create_kml(kml_file, image_data)
    create_kmz(kmz_file, kml_file, files_folder)

    # Clean up temporary files
    os.remove(kml_file)
    shutil.rmtree(files_folder)

    print(f"KMZ file has been created: {kmz_file}")

if __name__ == "__main__":
    main()
