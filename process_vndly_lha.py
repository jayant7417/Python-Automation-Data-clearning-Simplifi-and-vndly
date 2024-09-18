import os
from pathlib import Path
import pandas as pd
import re
from openpyxl import load_workbook

def extract_job_id(hyperlink_formula):
    match = re.search(r'HYPERLINK\("https://aah\.vndly\.com/vendor/applied-candidates/(\d+)/', str(hyperlink_formula))
    if match:
        return int(match.group(1))
    return None

def process_vndly_lah(folder_path):
    
    path3 = folder_path.joinpath('do not post', 'do_not_post_vndly_lah.csv')
    print(f"do not post: {path3}")
    
    try:
        df3 = pd.read_csv(path3)
    except FileNotFoundError:
        print(f"File not found: {path3}")
        return
    
    print(df3.columns)
    
    job_df = []
    path = folder_path.joinpath('job board')
    print(f"Processing VMS files from: {path}")

    for filename in os.listdir(path):
        if filename.endswith('.csv'):
            file_path = path.joinpath(filename)
            df = pd.read_csv(file_path)
            df['Source_File'] = filename
            job_df.append(df)

    job_dfs = pd.concat(job_df, ignore_index=True)
    
    replace_patterns = [
        '(48 hours)', '(48hours)', '(48 hrs)', '(48hrs)', "'", '(48 HOURS)', '(48HOURS)', '(48 HRS)', '(48HRS)',
        '(48 Hours)', '(48Hours)', '(48 Hrs)', '(48Hrs)', "''", '"', '(48 hour)', '(48hour)', '(48 Hour)', '(48Hour)', 'Backfill'
        ,')','(','()']
    for pattern in replace_patterns:
        job_dfs['External Job Posting Id'] = job_dfs['External Job Posting Id'].str.replace(pattern, "", regex=False)

    relevant_columns = ['External Job Posting Id', 'Job Status']
    job_dfs = job_dfs[relevant_columns]
    job_dfs = job_dfs.dropna(subset=['Job Status', 'External Job Posting Id'])

    # Filter out empty strings and non-numeric values
    job_dfs = job_dfs[job_dfs['External Job Posting Id'] != '']
    job_dfs = job_dfs[pd.to_numeric(job_dfs['External Job Posting Id'], errors='coerce').notnull()]
    job_dfs = job_dfs.sort_values(by='External Job Posting Id', ascending=True)
    job_dfs['External Job Posting Id'] = job_dfs['External Job Posting Id'].astype('Int64')
    job_dfs = job_dfs[job_dfs['External Job Posting Id'].apply(lambda x: len(str(x)) == 4)]

    # VMS processing
    path = folder_path.joinpath('vms', 'vndly', 'lah', 'lah.xlsx')
    print(f"Processing VMS files from: {path}")

    wb = load_workbook(path)
    ws = wb.active
    vndly_vms_lah_df = pd.DataFrame(ws.values)

    vndly_vms_lah_df[0] = vndly_vms_lah_df[0].apply(extract_job_id)
    vndly_vms_lah_df.at[0, 0] = "Job Id"
    vndly_vms_lah_df.iloc[1:, 0] = vndly_vms_lah_df.iloc[1:, 0].astype(int)
    vndly_vms_lah_df = vndly_vms_lah_df[vndly_vms_lah_df[0].apply(lambda x: len(str(x)) == 4 and str(x).startswith(('5', '6', '7','8')))]

    vndly_vms_lah_df[7] = vndly_vms_lah_df[7].replace('Active', 'Open')
    vndly_vms_lah_df[7] = vndly_vms_lah_df[7].replace('Hold', 'On-Hold')

    relevant_columns = [0, 1, 4, 7]
    vndly_vms_lah_df = vndly_vms_lah_df[relevant_columns]

    merged_df = pd.merge(vndly_vms_lah_df, job_dfs, left_on=0, right_on='External Job Posting Id', how='outer')

    
    status_dfs = merged_df[['External Job Posting Id', 7, 'Job Status']].drop_duplicates()
    status_dfs['result'] = status_dfs[7] == status_dfs['Job Status']
    status_dfs = status_dfs[status_dfs[7] == 'Closed']
    status_dfs = status_dfs[status_dfs['result'] == False]
    status_dfs = status_dfs.dropna(subset=['Job Status'])
    status_dfs = status_dfs.dropna(subset=[7])
    status_dfs  = status_dfs['External Job Posting Id']
    status_dfs = status_dfs.sort_values()



    output_file_path = folder_path.joinpath('result', 'vndly', 'Closing.csv')
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    status_dfs.to_csv(output_file_path, index=False)
    print(f"Updated file saved to {output_file_path}")

    
    status_dfs = merged_df[['External Job Posting Id', 7, 'Job Status']].drop_duplicates()
    status_dfs['result'] = status_dfs[7] == status_dfs['Job Status']
    status_dfs = status_dfs[status_dfs[7] != 'Closed']
    status_dfs = status_dfs[status_dfs['result'] == False]
    status_dfs = status_dfs.dropna(subset=['Job Status'])
    status_dfs = status_dfs.dropna(subset=[7])
    status_dfs = status_dfs.sort_values(by='External Job Posting Id')
    
    output_file_path = folder_path.joinpath('result', 'vndly', 'Status.csv')
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    status_dfs.to_csv(output_file_path, index=False)
    print(f"Updated file saved to {output_file_path}")
    
    #for posting
    merged_df = pd.merge(job_dfs, vndly_vms_lah_df, left_on='External Job Posting Id', right_on=0, how='outer')
    
    status_dfs = merged_df[['External Job Posting Id', 7, 'Job Status']].drop_duplicates()

    
    status_dfs = status_dfs[status_dfs[7] != 'Closed']
    status_dfs = status_dfs.dropna(subset=[7])
    status_dfs =  status_dfs[status_dfs['Job Status'].isnull()]
    '''status_dfs['result'] = status_dfs[7] != status_dfs['Job Status']
    status_dfs = status_dfs[status_dfs['result'] == True]'''
    status_dfs = status_dfs['External Job Posting Id']
    
    dnt_ids = df3['Job Id ']
    
    status_dfs = status_dfs[~status_dfs.isin(dnt_ids)]
    status_dfs = status_dfs.sort_values()

    
    output_file_path = folder_path.joinpath('result', 'vndly', 'Posting.csv')
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    status_dfs.to_csv(output_file_path, index=False)
    print(f"Updated file saved to {output_file_path}")
