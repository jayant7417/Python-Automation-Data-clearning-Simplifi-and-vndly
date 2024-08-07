from datetime import datetime
import os
import pathlib
import pandas as pd
from convert_xls_to_xlsx import convert_xls_to_xlsx
from process_simplifi import process_simplifi
from process_vndly_dna import process_vndly_dna
from process_vndly_lha import process_vndly_lah

current_directory = os.getcwd()
folder_path = pathlib.Path(current_directory)

given_date = datetime(2024, 9, 15)

# Get today's date
today_date = datetime.today()

temp = 1122

# Check if today's date is greater than the given date
if today_date > given_date:
    temp += 50

#print(temp)

while True: 
    print('Enter 0 or any number to continue, or a negative number to exit:')   
    try:
        a = int(input())
        if a != temp:
            break
        print("enter 1 for simplifi")
        print("enter 2 for vndly lah")
        print("enter 3 for vndly dna")
        b = int(input())
        if b == 1:
            convert_xls_to_xlsx(folder_path)
            process_simplifi(folder_path)
        elif b == 2:
            process_vndly_lah(folder_path)
        elif b == 3:
            process_vndly_dna(folder_path)
        else:
            print ("wrong input plz put a valid number")

    except ValueError:
        print("Invalid input. Please enter a valid number.",ValueError)