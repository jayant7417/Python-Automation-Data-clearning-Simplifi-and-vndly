import os
import pandas as pd
from pathlib import Path

def process_simplifi(folder_path):
    
    vms_df = []
    path1 = Path(folder_path).joinpath('merged', 'vendor_job.xlsx')
    print(f"Processing VMS files from: {path1}")
    # Read the Excel file
    vms_df = pd.read_excel(path1, sheet_name=None)  # If multiple sheets, use sheet_name=None to get all sheets
    
    job_df = []
    path = folder_path.joinpath('job board')
    print(f"Processing VMS files from: {path}")

    for filename in os.listdir(path):
        if filename.endswith('.csv'):
            file_path = os.path.join(path, filename)
            df = pd.read_csv(file_path) 
            df['Source_File'] = filename
            job_df.append(df)

    path3 = folder_path.joinpath('do not post', 'do_not_post_simplifi.csv')
    print(f"do not post: {path3}")
    
    try:
        df3 = pd.read_csv(path3)
    except FileNotFoundError:
        print(f"File not found: {path3}")
        return
    
    print(df3.columns)
    
    if vms_df and job_df:
        vms_dfs = pd.concat(vms_df, ignore_index=True)
        # Adjust column selection based on identified headers
        
        #Status
        relevant_columns = ['Contract ID#', 'Need Status']  # Change based on actual headers
        vms_dfs = vms_dfs[relevant_columns]
        
        vms_dfs['Need Status'] = vms_dfs['Need Status'].replace('Interviewing', 'Open')
        vms_dfs['Need Status'] = vms_dfs['Need Status'].replace('Not Accepting Submissions', 'On-Hold')
        vms_dfs['Contract ID#'] = vms_dfs['Contract ID#'].astype('Int64')
        job_dfs = pd.concat(job_df, ignore_index=True)
        
        replace_patterns = ['(48 hours)', '(48hours)', '(48 hrs)', '(48hrs)', "'",'(48 HOURS)', '(48HOURS)', '(48 HRS)', '(48HRS)'
                            ,'(48 Hours)', '(48Hours)', '(48 Hrs)', '(48Hrs)', "''", '"','(48 hour)','(48hour)','(48 Hour)','(48Hour)','Backfill'
                            ,')','(','()']
        for pattern in replace_patterns:
            job_dfs['External Job Posting Id'] = job_dfs['External Job Posting Id'].str.replace(pattern, "", regex=False)
        
        relevant_columns = ['External Job Posting Id', 'Job Status']  # Change based on actual headers
        job_dfs = job_dfs[relevant_columns]
        job_dfs = job_dfs.dropna(subset=['Job Status'])
        job_dfs = job_dfs.dropna(subset=['External Job Posting Id'])
        
        # Filter out empty strings and non-numeric values
        job_dfs = job_dfs[job_dfs['External Job Posting Id'] != '']
        job_dfs = job_dfs[pd.to_numeric(job_dfs['External Job Posting Id'], errors='coerce').notnull()]
        job_dfs = job_dfs.sort_values(by='External Job Posting Id', ascending=True)
        job_dfs['External Job Posting Id'] = job_dfs['External Job Posting Id'].astype('Int64')
        
        merged_df = pd.merge(vms_dfs, job_dfs, left_on='Contract ID#', right_on='External Job Posting Id', how='outer')
    
        status_dfs = merged_df[['Contract ID#', 'Need Status', 'Job Status']]
        status_dfs['result'] = status_dfs['Need Status'] == status_dfs['Job Status']
        status_dfs = status_dfs[status_dfs['result'] == False]
        status_dfs = status_dfs.dropna(subset=['Job Status'])
        status_dfs = status_dfs.dropna(subset=['Need Status'])
        status_dfs  = status_dfs['Contract ID#']
        
        output_file_path = Path(folder_path).joinpath('result').joinpath('simplifi', 'Status.csv')
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        status_dfs.to_csv(output_file_path, index=False)
        
        
        #Posting
        posting_dfs = merged_df[['Contract ID#', 'Need Status', 'Job Status']]
        posting_dfs = posting_dfs[posting_dfs['Job Status'].isna()]
        remaining_dfs = pd.DataFrame(posting_dfs['Contract ID#'])

        dnt_ids = df3['Job Id']
        remaining_dfs = remaining_dfs[~remaining_dfs['Contract ID#'].isin(dnt_ids)]

        
        #add dnt if requied
        output_file_path = Path(folder_path).joinpath('result').joinpath('simplifi', 'Posting.csv')
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        remaining_dfs.to_csv(output_file_path, index=False)
        
        
        #Status1
        status_df1 = pd.merge(job_dfs, vms_dfs, left_on='External Job Posting Id', right_on='Contract ID#', how='outer')
        status_df1 = status_df1[status_df1['Contract ID#'].isna()]
        six_digit_df = status_df1[status_df1['External Job Posting Id'].apply(lambda x: len(str(x)) == 6)]
        six_digit_df = six_digit_df[relevant_columns]
        six_digit_df = six_digit_df.sort_values(by='Job Status', ascending = True)
        
        output_file_path = Path(folder_path).joinpath('result').joinpath('simplifi', 'Status1.csv')
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        six_digit_df.to_csv(output_file_path, index=False)
        
