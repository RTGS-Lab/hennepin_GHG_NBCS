import pandas as pd
import numpy as np
from datetime import datetime

def clean_financial_data(input_file, output_file):
    print(f"CLEANING FINANCIAL DATA")
    print(f"======================")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"======================\n")
    
    # Load the data
    print("Loading data...")
    df = pd.read_csv(input_file)
    original_shape = df.shape
    print(f"Original dataset shape: {original_shape[0]:,} rows x {original_shape[1]} columns")
    
    # 1. Remove rows with missing critical values
    print("\n1. Removing rows with missing critical values...")
    critical_columns = ['Fund', 'DeptID', 'Account', 'Monetary Amount', 'Journal Date']
    before_count = len(df)
    df = df.dropna(subset=critical_columns)
    after_count = len(df)
    print(f"  Removed {before_count - after_count:,} rows with missing critical values")
    
    # 2. Remove rows where 'Fund' contains 'Data Source' or 'Overall - Summary'
    print("\n2. Removing metadata rows...")
    before_count = len(df)
    df = df[~df['Fund'].str.contains('Data Source|Overall - Summary', na=False)]
    after_count = len(df)
    print(f"  Removed {before_count - after_count:,} metadata rows")
    
    # 3. Convert Journal Date to datetime
    print("\n3. Converting date fields...")
    df['Journal Date'] = pd.to_datetime(df['Journal Date'], errors='coerce')
    df['Invoice Date'] = pd.to_datetime(df['Invoice Date'], errors='coerce')
    
    # Extract month and year as separate columns
    df['Month'] = df['Journal Date'].dt.month
    df['Year'] = df['Journal Date'].dt.year
    df['Quarter'] = df['Journal Date'].dt.quarter
    
    # 4. Ensure Monetary Amount is numeric
    print("\n4. Ensuring Monetary Amount is numeric...")
    df['Monetary Amount'] = pd.to_numeric(df['Monetary Amount'], errors='coerce')
    
    # 5. Clean and standardize text fields
    print("\n5. Cleaning and standardizing text fields...")
    
    # Fill empty Projects with "No Project"
    df['Project'] = df['Project'].replace('  -  ', 'No Project')
    
    # Strip whitespace from string columns
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        df[col] = df[col].str.strip() if hasattr(df[col], 'str') else df[col]
    
    # 6. Create additional useful fields
    print("\n6. Creating additional useful fields...")
    
    # Extract account category
    df['Account_Category'] = df['Account'].str.extract(r'(\d+)\s+-\s+', expand=False)
    
    # Extract department name
    df['Department_Name'] = df['DeptID'].str.extract(r'-\s+(.*)', expand=False)
    
    # Extract project name
    df['Project_Name'] = df['Project'].str.extract(r'-\s+(.*)', expand=False)
    df.loc[df['Project'] == 'No Project', 'Project_Name'] = 'No Project'
    
    # Create a flag for payroll vs. non-payroll transactions
    df['Is_Payroll'] = df['Journal Source'].str.contains('PAY', na=False)
    
    # Create a transaction type flag (positive = expense, negative = revenue)
    df['Transaction_Type'] = np.where(df['Monetary Amount'] >= 0, 'Expense', 'Revenue')
    
    # Calculate absolute amount for easier aggregation
    df['Amount_Abs'] = df['Monetary Amount'].abs()
    
    # 7. Remove any duplicate records
    print("\n7. Checking for duplicate records...")
    before_count = len(df)
    df = df.drop_duplicates()
    after_count = len(df)
    print(f"  Removed {before_count - after_count:,} duplicate records")
    
    # 8. Sort the data
    print("\n8. Sorting the data...")
    df = df.sort_values(by=['Year', 'Month', 'DeptID', 'Project'])
    
    # Summary of changes
    print(f"\nCleaning complete!")
    print(f"Original dataset: {original_shape[0]:,} rows x {original_shape[1]} columns")
    print(f"Cleaned dataset: {len(df):,} rows x {len(df.columns)} columns")
    print(f"Records removed: {original_shape[0] - len(df):,}")
    print(f"New columns added: {len(df.columns) - original_shape[1]}")
    
    # Save the cleaned data
    print(f"\nSaving cleaned data to {output_file}...")
    df.to_csv(output_file, index=False)
    print(f"Data successfully saved!")
    
    # Print summary of cleaned data
    print(f"\nSUMMARY OF CLEANED DATASET")
    print(f"==========================")
    print(f"Total records: {len(df):,}")
    print(f"Date range: {df['Journal Date'].min().strftime('%Y-%m-%d')} to {df['Journal Date'].max().strftime('%Y-%m-%d')}")
    print(f"Total expenses: ${df[df['Transaction_Type'] == 'Expense']['Monetary Amount'].sum():,.2f}")
    print(f"Total revenue: ${abs(df[df['Transaction_Type'] == 'Revenue']['Monetary Amount'].sum()):,.2f}")
    print(f"Net amount: ${df['Monetary Amount'].sum():,.2f}")
    print(f"Number of departments: {df['Department_Name'].nunique():,}")
    print(f"Number of projects: {df['Project_Name'].nunique():,}")
    
    print(f"\n======================")
    print(f"CLEANING COMPLETED")
    print(f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"======================")
    
    return df

if __name__ == "__main__":
    clean_financial_data("combined_financial_data.csv", "clean_financial_data.csv")