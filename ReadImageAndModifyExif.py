from exif import Image
import os

# This script can open each photo in the photo path, find the matching txt file in the text path.
# then convert the decimal gps information from the txt file to dms format
# use the dms format gps information and other information to write the photo's exif data
# all saved into the new photo folder


def decimal_to_dms(decimal_degree):
    degrees = int(decimal_degree)
    minutes_decimal = (decimal_degree - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = (minutes_decimal - minutes) * 60
    return degrees, minutes, seconds
# Modify this to fit your 
def read_and_convert_coordinates(file_path):
    with open(file_path, 'r') as file:
        # Read latitude and longitude from the file
        decimal_latitude = float(file.readline().strip())
        decimal_longitude = float(file.readline().strip())

    # Convert latitude to degrees, minutes, and decimal seconds
    dms_lat = decimal_to_dms(abs(decimal_latitude))
    lat_ref = 'N' if decimal_latitude >= 0 else 'S'

    # Convert longitude to degrees, minutes, and decimal seconds
    dms_long = decimal_to_dms(abs(decimal_longitude))
    long_ref = 'E' if decimal_longitude >= 0 else 'W'

    return dms_lat, lat_ref, dms_long, long_ref


# The first line is for just running the script, and the second line is for building exe with pyhinstaller
absolute_path = os.path.dirname(os.path.abspath(__file__))
#absolute_path = os.path.dirname(sys.executable)

# Subfolders for raw images, text files, and modified new images.
relative_photo_path = "capture"
relative_txt_path = "Txt_log"
relative_new_photo_path = "new_photo"

# Join the path.
photos_folder = os.path.join(absolute_path, relative_photo_path)
text_folder = os.path.join(absolute_path, relative_txt_path)
new_photo_folder = os.path.join(absolute_path, relative_new_photo_path)

# Create a list of photo filenames along with their creation dates
photo_files = os.listdir(photos_folder)
text_files = os.listdir(text_folder)



# List all JPG file in the folder
jpg_files = [file for file in photo_files if file.endswith('.jpg') and not file.lower().endswith('jpg.meta')]

for jpg_file in jpg_files:
    jpg_path = os.path.join(photos_folder, jpg_file)
    
    text_filename = os.path.splitext(jpg_file)[0] + '.txt'
    text_path = os.path.join(text_folder, text_filename)
    dms_lat, lat_ref, dms_long, long_ref = read_and_convert_coordinates(text_path)
    
    with open(jpg_path, 'rb') as image_file:
        my_image = Image(image_file)
        
    my_image.make = "Your Camera Make"
    my_image.model = "Your Camera Model"
    my_image.gps_latitude_ref = lat_ref
    my_image.gps_longitude_ref = long_ref
    my_image.gps_latitude = dms_lat
    my_image.gps_longitude = dms_long
    my_image.gps_altitude = 50.0 #in meters. Here used all same value, modify this to fit your txt file and functions.
    my_image.gps_altitude_ref = 0  # 0 means above sea level
    
    new_photo_name = os.path.splitext(jpg_file)[0] + '.jpg'
    new_photo_path = os.path.join(new_photo_folder, new_photo_name)
    with open(new_photo_path, 'wb') as new_photo_file:
        new_photo_file.write(my_image.get_file())
        
        

print("Photo exif update complete.")