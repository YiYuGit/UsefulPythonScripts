import gpxpy
import csv

# Function to extract data from GPX file and write to CSV
def extract_gpx_data(input_file, output_file):
    with open(input_file, 'r') as gpx_file, open(output_file, 'w', newline='') as csv_file:
        gpx = gpxpy.parse(gpx_file)

        # Create a CSV writer with headers
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["sequence", "latitude", "longitude", "elevation", "timestamp"])

        # Initialize sequence number
        sequence = 1

        # Iterate through GPX track points
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    latitude = point.latitude
                    longitude = point.longitude
                    elevation = point.elevation
                    timestamp = point.time.isoformat()

                    # Write data to CSV file
                    csv_writer.writerow([sequence, latitude, longitude, elevation, timestamp])

                    # Increment sequence number
                    sequence += 1

    print(f"Data extracted from '{input_file}' and saved to '{output_file}'")

# Input and output file paths
input_gpx_file = 'VID_20230731_165855_00_005.gpx'
output_csv_file = 'output2.csv'

# Call the function to extract GPX data and write to CSV
extract_gpx_data(input_gpx_file, output_csv_file)
