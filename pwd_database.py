import csv
import glob
import os

breached_pwd_list = []

# Path to the folder containing all 99 CSV files
csv_folder = os.path.join('password-data-master', 'passwords')

# Get all CSV files in the folder
csv_files = glob.glob(os.path.join(csv_folder, '*.csv'))

for csv_file in csv_files:
    with open(csv_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            breached_pwd_list.append(row)


