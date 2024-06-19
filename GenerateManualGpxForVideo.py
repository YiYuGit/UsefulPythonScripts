
# This scirpt is designed to generate a gpx file for a video, based on manually picked points on GoogleMap.
# For picking points, right click point on google map and copy the coordiantes.
# The input.txt should look like this:
# 2024-06-11T13:48:07Z
# 00:00:00, 31.23707496971354, -84.19378741303396
# 00:01:30, 31.23682097772665, -84.19408312658024
# 00:02:42, 31.23692481424611, -84.19394499281438
# ... ...


import datetime

def interpolate_coords(start_coords, end_coords, fraction):
    """
    Linearly interpolate between two coordinates.
    :param start_coords: tuple of (lat, lon) for the start point
    :param end_coords: tuple of (lat, lon) for the end point
    :param fraction: the fraction of the way between start and end (0.0 - 1.0)
    :return: tuple of (lat, lon) for the interpolated point
    """
    lat = start_coords[0] + (end_coords[0] - start_coords[0]) * fraction
    lon = start_coords[1] + (end_coords[1] - start_coords[1]) * fraction
    return lat, lon

def parse_input_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        
    start_datetime_str = lines[0].strip()
    start_datetime = datetime.datetime.strptime(start_datetime_str, "%Y-%m-%dT%H:%M:%SZ")
    
    key_points = []
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue  # Skip any empty lines
        try:
            time_str, lat_str, lon_str = line.split(", ")
            time_parts = list(map(int, time_str.split(":")))
            coords = (float(lat_str), float(lon_str))
            key_time = datetime.timedelta(hours=time_parts[0], minutes=time_parts[1], seconds=time_parts[2])
            key_points.append((key_time, coords))
        except ValueError as e:
            print(f"Error parsing line: {line}")
            print(e)
            raise ValueError(f"Invalid line format: {line}")
        
    return start_datetime, key_points

def generate_gpx(start_datetime, key_points):
    gpx_content = []
    gpx_content.append('<?xml version="1.0" encoding="UTF-8"?>')
    gpx_content.append('<gpx version="1.1" creator="CompanyName" xmlns="http://www.topografix.com/GPX/1/1">')
    
    # Add metadata
    gpx_content.append('<metadata>')
    gpx_content.append('<link href="https://www.company.com">')
    gpx_content.append('<text>Description</text>')
    gpx_content.append('</link>')
    gpx_content.append(f'<time>{start_datetime.isoformat()}Z</time>')
    
    # Calculate bounds
    min_lat = min([coords[1][0] for coords in key_points])
    max_lat = max([coords[1][0] for coords in key_points])
    min_lon = min([coords[1][1] for coords in key_points])
    max_lon = max([coords[1][1] for coords in key_points])
    gpx_content.append(f'<bounds minlat="{min_lat}" maxlat="{max_lat}" minlon="{min_lon}" maxlon="{max_lon}"/>')
    
    gpx_content.append('</metadata>')
    
    # Add track information
    gpx_content.append('<trk>')
    gpx_content.append('<name>360 Video GPS Data</name>')
    gpx_content.append('<trkseg>')
    
    total_seconds = 0
    for i in range(len(key_points) - 1):
        start_time, start_coords = key_points[i]
        end_time, end_coords = key_points[i+1]
        segment_seconds = int((end_time - start_time).total_seconds())
        
        for second in range(segment_seconds):
            fraction = second / segment_seconds
            interpolated_coords = interpolate_coords(start_coords, end_coords, fraction)
            point_time = start_datetime + datetime.timedelta(seconds=total_seconds + second)
            
            # Assume elevation is constant for simplicity
            elevation = 1.0
            
            gpx_content.append('<trkpt lon="{:.9f}" lat="{:.9f}">'.format(interpolated_coords[1], interpolated_coords[0]))
            gpx_content.append(f'<ele>{elevation}</ele>')
            gpx_content.append(f'<time>{point_time.isoformat()}Z</time>')
            gpx_content.append('</trkpt>')
            
        total_seconds += segment_seconds
    
    # Add the final key point
    final_time, final_coords = key_points[-1]
    point_time = start_datetime + datetime.timedelta(seconds=total_seconds)
    gpx_content.append('<trkpt lon="{:.9f}" lat="{:.9f}">'.format(final_coords[1], final_coords[0]))
    gpx_content.append(f'<ele>{elevation}</ele>')
    gpx_content.append(f'<time>{point_time.isoformat()}Z</time>')
    gpx_content.append('</trkpt>')
    
    gpx_content.append('</trkseg>')
    gpx_content.append('</trk>')
    
    gpx_content.append('</gpx>')
    
    return "\n".join(gpx_content)

def main(input_filename, output_filename):
    start_datetime, key_points = parse_input_file(input_filename)
    gpx_content = generate_gpx(start_datetime, key_points)
    
    with open(output_filename, 'w') as output_file:
        output_file.write(gpx_content)

if __name__ == "__main__":
    input_filename = "input.txt"  # Replace with your input file path
    output_filename = "output.gpx"  # Replace with your desired output file path
    main(input_filename, output_filename)
