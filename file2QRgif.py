import os
import sys
import qrcode
from PIL import Image, ImageSequence
import argparse

   

# TODO we can pass that also as an argument
# Define chunk size
chunk_size = 50


'''
quite self-explanatory
'''
def generate_qr(data):
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)  
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    return qr_img


'''
Used on the decoder to reassemble the files
This header indicates the file id (byte 1) and the chunk of data of such file (bytes 2 and 3)

TODO Think of a better header format to be able to handle files with larger number of chunks, using the minimum number of overhead bytes
'''
def generate_header(file_id, chunk_id):
    file_id_bytes = bytes([file_id])
    chunk_id_bytes = chunk_id.to_bytes(2, byteorder='big')
    
    # Concatenate file ID and chunk ID bytes
    header_bytes = file_id_bytes + chunk_id_bytes
    
    return header_bytes


'''
Iterate over the files inside the directory and generate QR codes of each of them
'''
def process_directory(folder_path, qr_images):

    file_id = 0
    for filename in os.listdir(folder_path):
        # Check if file is binary
        if os.path.isdir(os.path.join(folder_path, filename)):
            continue
        elif os.path.isfile(os.path.join(folder_path, filename)):
            # Open file in binary mode
            process_file(file_id, filename, qr_images, folder_path)
            print(len(qr_images))

'''
Generate qr codes from a file

TODO Need to find a way files containing non readable files
'''
def process_file(file_id, filename, qr_images, folder_path):

    global chunk_size
    
    ## Generate first QR code of a file containing filename
    header = generate_header(file_id, 0) 
    data = header + filename.split("/")[-1].encode()
    padded_data = bytes(data.ljust(10, b'\0'))
    qr_img = generate_qr(padded_data)
    qr_images.append(qr_img)

    
    with open(os.path.join(folder_path, filename), "rb") as file:
        # Read file contents
        file_data = file.read()

        # Calculate number of chunks
        num_chunks = len(file_data) // chunk_size + 1

        # Loop through chunks
        for i in range(num_chunks):
            # Get chunk data
            chunk_data = file_data[i*chunk_size : (i+1)*chunk_size]               
            chunk_id = i + 1 ## chunk 0 is  filename

            # Generate header and add it to chunk data
            header = generate_header(file_id, chunk_id)         
            chunk_data = header + chunk_data

            print(chunk_data)

            # Generate QR code
            qr_img = generate_qr(chunk_data)
            
            # Add QR code image to list
            qr_images.append(qr_img)
        return qr_images


'''
Create a GIF folder
Generate a GIF using all the files from a directory

TODO Option to generate multiple GIFs from multiple files
'''
def main():

    if len(sys.argv) < 2:
        print("Usage: python3 file2QRgif.py [qr_directory] [file]")
        return

    argument = sys.argv[1]

    #### PROCESSING DIRECTORY
    if os.path.isdir(argument):
        print("Processing Directory")
        folder_path = argument
        qr_images = []
        process_directory(folder_path, qr_images)

        gif_folder = os.path.join(folder_path + "/../", "gifs")
        if not os.path.exists(gif_folder):
            os.mkdir(gif_folder)

        
        # Create GIF inside gifs folder
        gif_filename = "final.gif" # all files QR codes will be joined in this GIF TODO split in different GIFS per file
        gif_filepath = os.path.join(gif_folder, gif_filename)
        qr_images[0].save(gif_filepath, save_all=True, append_images=qr_images[1:], duration=500, loop=0)


    #### PROCESSING ONLY ONE FILE    
    else:
        print("Processing File")
        filename = argument
        folder_path = "./"
        file_id = 0
        qr_images = [] ## This will store the qr code images to put them all togehter later
        process_file(file_id, filename, qr_images, folder_path)

    ## Create GIF folder on the running directory 
        gif_folder = os.path.join("./", "gifs")
        if not os.path.exists(gif_folder):
            os.mkdir(gif_folder)

    ## Create GIF inside gifs folder
        gif_filename = "final.gif" # all files QR codes will be joined in this GIF TODO split in different GIFS per file
        gif_filepath = os.path.join(gif_folder, gif_filename)
        qr_images[1].save(gif_filepath, save_all=True, append_images=qr_images[0:], duration=1000, loop=0)



## TODO Improve process if input is directory or file
if __name__ == '__main__':
    # Call the main function
    main()