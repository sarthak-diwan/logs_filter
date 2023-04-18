import rarfile
from tqdm import tqdm
import os
with rarfile.RarFile('./xmyqb3ey05.vnd.rar', 'r') as rar_ref:
    # Use tqdm to show the progress bar
    extracted_dir='test_ex'
    if not os.path.exists(extracted_dir):
        os.mkdir(extracted_dir)
    progress = tqdm(rar_ref.namelist(), desc='Extracting files', unit=' files')
    for file in progress:
        rar_ref.extract(file, extracted_dir)
        progress_str = progress.format_meter(n=progress.n, total=progress.total, elapsed=progress.format_dict['elapsed'])
        print(progress_str)