import csv
import os
import boto3
import uuid
from urllib.parse import unquote_plus
from os import listdir
from os.path import isfile, join


def write_patch_header(yaml_file) :
    yaml_text = "patches:"+"\n"
    yaml_file.write(yaml_text)

def write_entry(yaml_file):
    yaml_text = " "*4 +"-"+"\n"
    yaml_file.write(yaml_text)

def lambda_handler(event, context):
    
    s3_client = boto3.client('s3')
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        tmpkey = key.replace('/', '')
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
        s3_client.download_file(bucket, key, download_path)
        transform_file(download_path)
        upload_files(s3_client,bucket)
        
def upload_files(s3_client,bucket) :
    for file in os.listdir("/tmp"):
        if file.endswith(".yaml"):
            upload_path = os.path.join("/tmp", file)
            print(upload_path)
            s3_client.upload_file(upload_path, '{}'.format(bucket),"output/" + file)
            os.remove(upload_path)
        
def transform_file(input_file) :
    
     # Open our data file in read-mode.
    csvfile = open(input_file, 'r')
    
    # Save a CSV Reader object.
    datareader = csv.reader(csvfile, delimiter=',', quotechar='"')
    
    # Empty array for data headings, which we will fill with the first row from our CSV.
    data_headings = []
    for row_index, row in enumerate(datareader):
       
    	# If this is the first row, populate our data_headings variable.
        if row_index == 0:
            data_headings = row
        else:
            # Only write approved patches
            if row[0] == "yes" :
                #
                # Try to append to an existing file or create a new one "a" mode.
                #
                if not os.path.exists("/tmp/"+row[18] + ".yaml") :
                    new_yaml =open("/tmp/"+row[18] + ".yaml","w")
                    write_patch_header(new_yaml)
    
                new_yaml = open("/tmp/"+row[18] + ".yaml","a")
                
                write_entry(new_yaml)
                yaml_text = " "*8
                # Loop through each cell in this row...
                for cell_index, cell in enumerate(row):
    
                    # Heading text is converted to lowercase. Spaces are converted to underscores and hyphens are removed.
                    # In the cell text, line endings are replaced with commas.
                    cell_heading = data_headings[cell_index].lower().replace(" ", "_").replace("-", "")
                    cell_text = cell_heading + ": '" + cell.replace("\n", ", ") + "'\n"
        
                    # Add this line of text to the current YAML string.
                    if cell_heading == "id" :
                        yaml_text += cell_text
    
                # Write our YAML string to the new text file and close it.
                new_yaml.write(yaml_text)   
    
    # We're done! Close the CSV file.
    csvfile.close()
    new_yaml.close()
