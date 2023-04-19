import dotenv
import os
from log_parser import LogParser
from db_connection import DB
import argparse

dotenv.load_dotenv()

parser = argparse.ArgumentParser(description='Load already extracted folder')
parser.add_argument('--folder', type=str, help='Path to input folder', required=True)

args = parser.parse_args()

folder=args.folder

db = DB(os.environ.get('DATABASE'))

lp=LogParser(folder)
victims=lp.parse_all()
inserted = db.insert_victims(victims)

print(f'Inserted {inserted} victims!')
