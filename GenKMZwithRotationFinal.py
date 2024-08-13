import os
import zipfile
from PIL import Image
import piexif
import shutil

# This script can be built into a exe using pyinstaller. 
# Put the script or exe into the same folder with photos (photos with location data in their exif)
# double click the script or exe, it will generate a kmz file that contain photo and a kml file.
# you can then drag and drop the kmz to a Google Earth app window, and view the photos by location in Google Earth.
# This version added the "rotate_image" to solve the problem of vertical image showing horizontally. 



# Enable loading of truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True


# Function to convert GPS coordinates to decimal degrees
def convert_to_decimal_degrees(coord, ref):
    """
    Convert GPS coordinates stored in degrees, minutes, and seconds (DMS) to decimal degrees.

    Parameters:
    coord (tuple): A tuple containing (degrees, minutes, seconds).
    ref (str): Reference for latitude or longitude (e.g., 'N', 'S', 'E', 'W').

    Returns:
    float: The decimal degree representation of the coordinates.
    """
    degrees = coord[0]
    minutes = coord[1]
    seconds = coord[2]
    decimal_degrees = degrees + (minutes / 60.0) + (seconds / 3600.0)
    
    # Adjust sign based on hemisphere reference
    if ref in ['S', 'W']:
        decimal_degrees = -decimal_degrees
    
    return decimal_degrees

# Function to extract GPS data from an image
def extract_gps_data(image_path):
    """
    Extract GPS latitude, longitude, and altitude from the EXIF data of an image.

    Parameters:
    image_path (str): Path to the image file.

    Returns:
    tuple: A tuple containing latitude, longitude, and altitude.
    """
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

# Function to get the orientation of an image from its EXIF data
def get_image_orientation(image_path):
    """
    Get the orientation of an image from its EXIF data.

    Parameters:
    image_path (str): Path to the image file.

    Returns:
    int: The orientation value (1, 3, 6, 8) from EXIF data.
    """
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                orientation = exif_data.get(274)  # Orientation tag
                return orientation
    except Exception as e:
        print(f"Error getting orientation for {image_path}: {e}")
    return None

# Function to rotate an image based on the provided angle and preserve EXIF data
def rotate_image(input_image_path, output_image_path, angle):
    """
    Rotate an image by a specified angle and save the rotated image with preserved EXIF data.

    Parameters:
    input_image_path (str): Path to the input image file.
    output_image_path (str): Path to save the rotated image file.
    angle (int): The angle by which to rotate the image (e.g., 90, 180, 270 degrees).
    """
    # Open the image
    image = Image.open(input_image_path)
    
    # Load existing EXIF data
    exif_data = image.info.get("exif", b'')
    exif_dict = piexif.load(exif_data)
    
    # Rotate the image
    rotated_image = image.rotate(angle, expand=True)
    
    # Convert EXIF data back to bytes
    exif_bytes = piexif.dump(exif_dict)
    
    # Save the rotated image with EXIF data
    rotated_image.save(output_image_path, exif=exif_bytes)

# Function to create a KML file containing the GPS data of images
def create_kml(kml_file_path, image_data):
    """
    Create a KML (Keyhole Markup Language) file containing GPS coordinates and corresponding images.

    Parameters:
    kml_file_path (str): Path to save the generated KML file.
    image_data (dict): A dictionary containing image file names and their corresponding GPS data.
    """
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

# Function to create a KMZ file, which is a zipped KML file with image data
def create_kmz(output_path, kml_file, files_folder):
    """
    Create a KMZ file by zipping the KML file and associated image files.

    Parameters:
    output_path (str): Path to save the generated KMZ file.
    kml_file (str): Path to the KML file.
    files_folder (str): Path to the folder containing image files.
    """
    with zipfile.ZipFile(output_path, 'w') as kmz:
        kmz.write(kml_file, arcname="doc.kml")
        for root, dirs, files in os.walk(files_folder):
            for file in files:
                kmz.write(os.path.join(root, file), arcname=os.path.join("files", file))

# Main function to process images, rotate them if necessary, and create a KMZ file
def main():
    """
    Main function to process images in the current directory, extract their GPS data,
    rotate them according to their EXIF orientation, and create a KMZ file containing
    a KML file with the image GPS data and the rotated images.
    """
    # For pyinstaller build, use the following line.
    #folder_path =os.path.dirname(sys.executable)
    # For direct use, use the following line
    folder_path = os.path.dirname(os.path.abspath(__file__))
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
                orientation = get_image_orientation(image_path)
                
                if orientation:
                    if orientation == 3:
                        angle = 180  # Rotate 180 degrees
                    elif orientation == 6:
                        angle = 270  # Rotate 270 degrees (or -90)
                    elif orientation == 8:
                        angle = 90  # Rotate 90 degrees
                    else:
                        angle = 0  # No rotation needed
                else:
                    angle = 0  # No rotation needed
                
                rotated_image_path = os.path.join(files_folder, filename)
                rotate_image(image_path, rotated_image_path, angle)
                
                # Update the orientation to "Horizontal (normal)" in EXIF data
                with Image.open(rotated_image_path) as img:
                    exif_data = img.info.get("exif", b'')
                    exif_dict = piexif.load(exif_data)
                    exif_dict['0th'][piexif.ImageIFD.Orientation] = 1  # Set to "Horizontal (normal)"
                    exif_bytes = piexif.dump(exif_dict)
                    img.save(rotated_image_path, exif=exif_bytes)
                
                image_data[filename] = (latitude, longitude, altitude)

    create_kml(kml_file, image_data)
    create_kmz(kmz_file, kml_file, files_folder)

    # Clean up temporary files
    os.remove(kml_file)
    shutil.rmtree(files_folder)

    print(f"KMZ file has been created: {kmz_file}")

if __name__ == "__main__":
    main()
