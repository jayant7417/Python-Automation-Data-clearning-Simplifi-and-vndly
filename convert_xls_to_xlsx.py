import win32com.client as win32
import os
import pathlib
import shutil



def convert_xls_to_xlsx(folder_path):
    path = folder_path.joinpath('vms').joinpath('simplifi')
    excel = win32.gencache.EnsureDispatch('Excel.Application')
    excel.Visible = False

    for filename in os.listdir(path):
        if filename.endswith('.xls'):
            file_path = os.path.join(path, filename)
            wb = excel.Workbooks.Open(str(file_path))
            new_file_path = folder_path.joinpath('merged').joinpath('vendor_job.xlsx')
            wb.SaveAs(str(new_file_path), FileFormat=51)  # 51 represents the .xlsx format
            wb.Close()
            #os.remove(file_path)  # Optionally remove the old .xls file
    print("done for convert")
    excel.Application.Quit()

'''current_directory = os.getcwd()
folder_path = pathlib.Path(current_directory)

convert_xls_to_xlsx(folder_path)'''
