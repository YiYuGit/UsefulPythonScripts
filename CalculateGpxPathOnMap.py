"""
This script is designed to work with OpenStreetMap to prepare the path file for video with recorded GPX files.
To use this:
1. Export your MP4 videos with GPX files. Put the GPX files in Google Earth to view their combined area.
2. Find the same or slightly larger area on https://www.openstreetmap.org/.
3. Click the "Export" button on the upper left area of the webpage. This will bring up the Export tab and show the max and min latitude/longitude of the current map.
4. Click the "Share" button on the right side of the webpage to download your current map in PNG format.
5. !!! Don't drag or zoom on the map. Now, copy the boundary latitude and longitude numbers to a text file ("latlong.txt") and save it in the same folder as this script. 
   The four numbers (in decimal degrees) should be listed on four lines, without punctuation after them. Make sure they are listed in the sequence of two latitude lines first and two longitude lines next. 
   Like:
   41.87374
   41.81764
   -75.25282
   -75.13952
6. Copy your GPX files to the same folder as this script and the "latlong.txt".
7. Run this script to generate a CSV file for your path, ready for plotting your path on the OSM downloaded basemap.             
"""

import os
import csv
import math
import gpxpy
from pyproj import CRS, Transformer

def read_latlong_file(filename):
    """
    Read latitude and longitude boundaries from a file.
    The file should contain four lines: two latitude values followed by two longitude values.
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"{filename} not found.")
    
    with open(filename, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
    
    if len(lines) != 4:
        raise ValueError(f"Invalid format in {filename}. Expected 4 lines.")
    
    try:
        latitudes = [float(lines[0]), float(lines[1])]
        longitudes = [float(lines[2]), float(lines[3])]
    except ValueError:
        raise ValueError("Error converting latitude/longitude values to float.")
    
    return latitudes, longitudes

def get_min_max(latitudes, longitudes):
    """
    Get the minimum and maximum latitude and longitude from the lists.
    """
    min_lat = min(latitudes)
    max_lat = max(latitudes)
    min_lon = min(longitudes)
    max_lon = max(longitudes)
    return min_lat, max_lat, min_lon, max_lon

def calculate_distance(lat1, lon1, lat2, lon2, transformer):
    """
    Calculate the distance between two geographic coordinates in meters.
    """
    x1, y1 = transformer.transform(lat1, lon1)
    x2, y2 = transformer.transform(lat2, lon2)
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance, x1, y1

def process_gpx_file(gpx_file, transformer, min_lat, min_lon, min_x, min_y):
    """
    Process a GPX file and convert lat/lon to relative map coordinates.
    """
    if not os.path.isfile(gpx_file):
        raise FileNotFoundError(f"{gpx_file} not found.")
    
    try:
        with open(gpx_file, 'r') as file:
            gpx = gpxpy.parse(file)
    except gpxpy.gpx.GPXParseError as e:
        print(f"Error parsing GPX file {gpx_file}: {e}")
        return []
    
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for i, point in enumerate(segment.points):
                try:
                    pos_x, pos_y = transformer.transform(point.latitude, point.longitude)
                    rel_x = pos_x - min_x
                    rel_y = pos_y - min_y
                    
                    points.append({
                        "count": i,
                        "latitude": point.latitude,
                        "longitude": point.longitude,
                        "elevationM": point.elevation,
                        "timestamp": point.time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "northing": 0,
                        "easting": 0,
                        "elevationFt": 0,
                        "positionX": rel_x,
                        "positionY": rel_y,
                        "positionZ": point.elevation,
                        "xdimM": map_width,
                        "ydimM": map_height,
                        "filename": os.path.splitext(os.path.basename(gpx_file))[0]
                    })
                except Exception as e:
                    print(f"Error processing point {i} in file {gpx_file}: {e}")
    
    return points

def main():
    # Read lat/long boundaries from file
    latlong_file = 'latlong.txt'
    latitudes, longitudes = read_latlong_file(latlong_file)
    min_lat, max_lat, min_lon, max_lon = get_min_max(latitudes, longitudes)
    
    # Initialize transformer for lat/lon to map coordinates
    crs_wgs84 = CRS("epsg:4326")
    crs_web_mercator = CRS("epsg:3857")
    transformer = Transformer.from_crs(crs_wgs84, crs_web_mercator, always_xy=False)
    
    # Calculate map dimensions
    global map_width, map_height, min_x, min_y
    map_width, min_x, min_y = calculate_distance(min_lat, min_lon, min_lat, max_lon, transformer)
    map_height, _, _ = calculate_distance(min_lat, min_lon, max_lat, min_lon, transformer)
    
    # Prepare CSV file
    output_file = 'gpx_data.csv'
    all_points = []
    
    for filename in os.listdir('.'):
        if filename.lower().endswith('.gpx'):
            points = process_gpx_file(filename, transformer, min_lat, min_lon, min_x, min_y)
            all_points.extend(points)
    
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = [
            "count", "latitude", "longitude", "elevationM", "timestamp",
            "northing", "easting", "elevationFt", "positionX", "positionY",
            "positionZ", "xdimM", "ydimM", "filename"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_points)
    
    print(f"Data has been written to {output_file}")

if __name__ == "__main__":
    main()
