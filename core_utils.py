import os
import pyzipper as zipfile
import rarfile
import dotenv
from db_connection import DB
dotenv.load_dotenv()
db = DB(os.environ.get('DATABASE'))

def extract_archive(file_path, progress_callback, password=None) -> str:
    extracted_dir = os.path.splitext(file_path)[0] + '_extracted'
    # Create the directory for the extracted files if it does not exist
    if not os.path.exists(extracted_dir):
        os.mkdir(extracted_dir)
    # Extract the archive
    if file_path.endswith('.zip'):
        with zipfile.AESZipFile(file_path, 'r') as zip_ref:
            if any(zinfo.flag_bits & 0x1 for zinfo in zip_ref.infolist()) and not password:
                return 'PASSWORD_REQUIRED'
            # Use tqdm to show the progress bar
            if password:
                zip_ref.setpassword(password.encode('utf-8'))
            progress = zip_ref.namelist()
            cnt=0
            ttl = len(progress)
            for file in progress:
                try:
                    zip_ref.extract(file, extracted_dir)
                except Exception as e:
                    print(e, file, extracted_dir)
                cnt+=1
                progress_str = f'Extracting : {cnt/ttl*100:.2f}'
                progress_callback(progress_str)
    elif file_path.endswith('.rar'):
        with rarfile.RarFile(file_path, 'r') as rar_ref:
            print(f"Password: {password}")
            if rar_ref.needs_password() and not password:
                return 'PASSWORD_REQUIRED'
            if password:
                rar_ref.setpassword(password)
            # Use tqdm to show the progress bar
            progress = rar_ref.namelist()
            cnt=0
            ttl = len(progress)
            for file in progress:
                try:
                    rar_ref.extract(file, extracted_dir)
                except Exception as e:
                    print(e, file, extracted_dir)
                cnt+=1
                progress_str = f'Extracting : {cnt/ttl*100:.2f}'
                progress_callback(progress_str)
    else:
        print(f"Unsupported file type: {file_path}")
        return ''
    return extracted_dir


def insert_victims(victims, pcs):
    def progress_callback(current, total):
        progress_percent = current/total*100
        pcs(f'Insert progress: {progress_percent:.2f}%')
    return db.insert_victims(victims, progress_callback)


def check_hash(hash):
    return db.check_hash(hash)

def insert_hash(hash, name):
    return db.insert_hash(hash, name)