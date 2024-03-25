import os
import shutil
import unicodedata
import zipfile
import mimetypes
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

# Constants for file extensions
IMAGE_EXTENSIONS = ['.JPEG', '.PNG', '.JPG', '.SVG']
VIDEO_EXTENSIONS = ['.AVI', '.MP4', '.MOV', '.MKV']
DOCUMENT_EXTENSIONS = ['.DOC', '.DOCX', '.TXT', '.PDF', '.XLSX', '.PPTX']
AUDIO_EXTENSIONS = ['.MP3', '.OGG', '.WAV', '.AMR']
ARCHIVE_EXTENSIONS = ['.ZIP', '.GZ', '.TAR']

# Function for normalizing file names
def normalize(name):
    base_name = os.path.basename(name)
    name_without_ext, ext = os.path.splitext(base_name)
    normalized_name = unicodedata.normalize('NFKD', name_without_ext).encode('ASCII', 'ignore').decode('utf-8')
    return normalized_name + ext

# Function for sorting files
def sort_files(folder):
    known_extensions = set()
    unknown_extensions = set()
    
    for root, dirs, files in os.walk(folder):
        for filename in files:
            filepath = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1].upper()  # Convert to uppercase
            known = False
            
            # Moving contents of archives to respective folders
            if ext in ARCHIVE_EXTENSIONS:
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(root)
                os.remove(filepath)
                shutil.move(os.path.join(root, os.path.splitext(filename)[0]), os.path.join(root, 'archives'))
                continue
            
            # Sorting files
            if ext in IMAGE_EXTENSIONS:
                shutil.move(filepath, os.path.join(root, 'images'))
                known = True
            elif ext in VIDEO_EXTENSIONS:
                shutil.move(filepath, os.path.join(root, 'videos'))
                known = True
            elif ext in DOCUMENT_EXTENSIONS:
                shutil.move(filepath, os.path.join(root, 'documents'))
                known = True
            elif ext in AUDIO_EXTENSIONS:
                shutil.move(filepath, os.path.join(root, 'audio'))
                known = True
            
            if known:
                known_extensions.add(ext)
            else:
                unknown_extensions.add(ext)
                
    return known_extensions, unknown_extensions

# Function for processing folder
def process_folder(folder):
    for root, dirs, files in os.walk(folder, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

# Main function for sorting files in a folder
def sort_files_in_folder(folder_path):
    known_extensions, _ = sort_files(folder_path)
    
    # Normalizing file names
    for root, dirs, files in os.walk(folder_path):
        for name in dirs + files:
            new_name = normalize(os.path.join(root, name))
            os.rename(os.path.join(root, name), os.path.join(root, new_name))
    
    # Processing folder
    process_folder(folder_path)
    
    # Creating report
    with open(os.path.join(folder_path, 'report.txt'), 'w') as f:
        f.write('Known Extensions:\n')
        f.write('\n'.join(known_extensions))

# Function for processing folders
def process_folders(folder_queue):
    while not folder_queue.empty():
        folder_path = folder_queue.get()
        sort_files_in_folder(folder_path)
        folder_queue.task_done()

if __name__ == "__main__":
    # Creating folder queue
    base_folder = "Messy_Folder"
    folder_queue = multiprocessing.JoinableQueue()
    for root, _, _ in os.walk(base_folder):
        folder_queue.put(root)

    # Creating and starting processes to process folders
    num_processes = multiprocessing.cpu_count()
    processes = []
    for _ in range(num_processes):
        process = multiprocessing.Process(target=process_folders, args=(folder_queue,))
        process.start()
        processes.append(process)

    # Waiting for all folders to be processed
    folder_queue.join()

    print("All folders sorted successfully.")