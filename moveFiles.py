import json
import traceback
from datetime import datetime
import shutil, os, glob
from progress.spinner import Spinner

now = datetime.now()
ignore_folders = []
ignore_flag = "false"

def copyTree( src, dst,state, symlinks=False, ignore=None):
    errors = []
    spinner = Spinner('Loading ')
    src_folder_size = get_size_format(get_directory_size(src))
    print("___ Folder Size: ",src_folder_size)
    
    while state != 'FINISHED':
        for item in os.listdir(src):
            if item in ignore_folders and ignore_flag.lower() == "true":
                continue
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            try:
                if os.path.isdir(s):
                    if os.path.isdir(d):
                        self.recursiveCopyTree(s, d, symlinks, ignore)
                    else:
                        shutil.copytree(s, d, symlinks, ignore)
                else:
                    shutil.copy2(s, d)
                spinner.next()
            except (IOError, os.error) as why:
                errors.append((srcname, dstname, str(why)))
            # catch the Error from the recursive copytree so that we can
            # continue with other files
            except Error as err:
                errors.extend(err.args[0])
            
        state= "FINISHED"
    print("___ Checking Errors: ",errors)
        
def get_directory_size(directory):
    """Returns the `directory` size in bytes."""
    total = 0
    try:
        # print("[+] Getting the size of", directory)
        for entry in os.scandir(directory):
            if entry.is_file():
                # if it's a file, use stat() function
                total += entry.stat().st_size
            elif entry.is_dir():
                # if it's a directory, recursively call this function
                total += get_directory_size(entry.path)
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        return 0
    return total

def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"  

print("\n********* Start *********")
config_file = 'config.json'
try:# trying to read config file to get folder names
    with open(config_file, 'r') as f:
        datastore = json.load(f)
except Exception:
    sys.exit("Failed to Load Data from Config file -->> File May not exist or it is empty")

target_folders = datastore["target_folders"]
source_folders = datastore["source_folders"]
ignore_folders = datastore["ignore_folders"]
ignore_flag =  datastore["ignore_flag"]

print("_______ This script moves files from Souce Folders to Target Folders ________")
print("___ Start time: ",now.strftime("%m-%d-%Y, %H:%M:%S"))

new_bk_with_timestamp = now.strftime("%m-%d-%Y-%H_%M_%S")
# check backup folder has current date as folder name
for num, trg_folder in enumerate(target_folders):
    print("\n___ Target Folder Path (Backup) : ",trg_folder)
    current_trg_path = os.path.join(trg_folder,now.strftime("%m-%d-%Y"))
    isExists = os.path.exists(current_trg_path)
    if isExists:
        print("___ Target Folder Path already exist with current date : ",current_trg_path)
        current_trg_path_timestamp = os.path.join(trg_folder,new_bk_with_timestamp)
        os.mkdir(current_trg_path_timestamp) 
        print("___ Created **NEW** Target path with timestamp : ",current_trg_path_timestamp)
        state= "NOT_FINISHED"
        copyTree( source_folders[num], current_trg_path_timestamp,state)
        
    else:
        os.mkdir(current_trg_path)
        print("___ Created **NEW** Target path with current date : ",current_trg_path)
        state= "NOT_FINISHED"
        copyTree( source_folders[num], current_trg_path,state)

print("\n___ End time: ",now.strftime("%m-%d-%Y, %H:%M:%S"))