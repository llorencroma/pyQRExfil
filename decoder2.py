import os
import json
import argparse
import base64
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image
import datetime

today = datetime.datetime.today()

'''
Decode QR code
Byte 1 is the ID of the origin file
Byte 2 and 3 are the data chunk identifier
It does not decode ZIP, binaries, ... properly
'''

def decode_qr_code(qr_path):
    # Decode the QR code and extract the header information
    qr_data = decode(Image.open(qr_path))[0].data
    file_id = qr_data[0]
    chunk_id = qr_data[1] * 256 + qr_data[2]

    print(qr_data)

    # Read the chunk data from the QR code

    #b.encode('utf-8').decode('unicode_escape').encode('utf-8') 
    chunk_data = qr_data[3:].decode("utf-8")
    return file_id, chunk_id, chunk_data


'''
If a directory is passed, it means that we got a folder with al the QR codes that we want to recover

A dictionary is generated, where the keys are the File ID. For each File ID there is a nested dictionary containing
the chunk ID and the data of the chunk.

File 0
    Chunk 0: filename
    Chunk 1: Data
File 1
    Chunk 0: filename
    Chunk1: Data
'''

def process_directory(qr_dir, decoded_files_folder,  output_file):
    # Create a dictionary to hold the decoded chunks
    decoded_chunks = {}

    # Loop over each file in the specified directory
    for file_name in os.listdir(qr_dir):
        # Only consider files with .png extension
        if file_name.endswith('.png'):
            qr_path = os.path.join(qr_dir, file_name)
            file_id, chunk_id, chunk_data = decode_qr_code(qr_path)

            # Add the chunk data to the dictionary
            if file_id in decoded_chunks:
                decoded_chunks[file_id]['chunks'][chunk_id] = chunk_data
            else:
                decoded_chunks[file_id] = {'chunks': {chunk_id: chunk_data}}

    # Write the decoded data of each qr code to a JSON file
    file_name = output_file   
    file_path = os.path.join(decoded_files_folder, file_name)

    with open(file_path, 'w') as f:
        json.dump(decoded_chunks_dict, f, indent=4)
    return decoded_chunks_dict


'''
If a GIF is used, the GIF frames are stored, and then each individual QR code is decoded.

A dictionary is generated, where the keys are the File ID. For each File ID there is a nested dictionary containing
the chunk ID and the data of the chunk.

File 0
    Chunk 0: Data
    Chunk 1: Data
File 1
    Chunk 0: Data
    Chunk1: Data
'''

def process_gif(gif_file, decoded_files_folder, output_file):
    # Create a dictionary to hold the decoded chunks
    decoded_chunks_dict = {}

    with Image.open(gif_file) as im:
        # Loop over each frame in the GIF
        for i in range(im.n_frames):
            im.seek(i)
            # Convert the frame to a PNG image
            png_path = f'{gif_file}_{i}.png'
            im.save(png_path)

            # Decode the QR code and extract the header information
            file_id, chunk_id, chunk_data = decode_qr_code(png_path)

            # Add the chunk data to the dictionary
            if file_id in decoded_chunks_dict:
                decoded_chunks_dict[file_id]['chunks'][chunk_id] = chunk_data
            else:
                decoded_chunks_dict[file_id] = {'chunks': {chunk_id: chunk_data}}

            # Remove the temporary PNG image
            os.remove(png_path)


    # Write the decoded chunks to a JSON file
    file_name = output_file   
    file_path = os.path.join(decoded_files_folder, file_name)
    
    #For debug
    with open(file_path, 'w') as f:
        json_sorted = json.dump(decoded_chunks_dict, f, sort_keys=True, indent=4)
    
    #Return unordered Dict
    return decoded_chunks_dict
    

'''
Data from QR code is put together according to header.
Exfiltrated files are recovered
'''
def recover_file_from_JSON(json_qr_code_chunks, decoded_files_folder):


    loaded_json = json.loads(json_qr_code_chunks)

    # iterate over the keys of the input dictionary
    for file_id in loaded_json.keys():
        # get the dictionary of chunks for the current file
        chunks_dict = loaded_json[file_id]['chunks']

        # extract the filename from the chunk with ID zero
        filename = chunks_dict.pop('0')

        # Up to this point, chunks are ordered and ready to reassemble

        # concatenate the data of all the chunks
        file_data = ''
        for chunk_id in chunks_dict.keys():
            #print(chunk_id)
            file_data += chunks_dict[chunk_id]
            #print(file_data)
           

        
        # write the concatenated data to a file with the current file ID as name
        file_path = os.path.join(decoded_files_folder, filename)
        #print(file_data)
        with open(file_path, 'w') as f:
            f.write(file_data)


def main(decoded_files_folder, directory=None, gif_filename=None, outpu_filename="decoded.json"):

    if directory:
        decoded_chunks_dict = process_directory(directory, decoded_files_folder,  outpu_filename)
        recover_file_from_JSON( json.dumps(decoded_chunks_dict, sort_keys=True), decoded_files_folder)

    elif gif_filename:
        decoded_chunks_dict = process_gif(gif_filename, decoded_files_folder, outpu_filename)
        recover_file_from_JSON( json.dumps(decoded_chunks_dict, sort_keys=True), decoded_files_folder)

    else:
        print(f'Unsupported input file type:')
        sys.exit()


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Description of your script')
    parser.add_argument('-d', '--directory', type=str, help='Input directory path')
    parser.add_argument('-g', '--gif', type=str, help='Input gif file path')
    parser.add_argument('-o', '--output_file', help='output JSON file')
    args = parser.parse_args()


    decoded_files_folder = os.path.join("./", "decoded_files")
    if not os.path.exists(decoded_files_folder):
        os.mkdir(decoded_files_folder)
    
    
    main(decoded_files_folder, args.directory, args.gif, args.output_file)