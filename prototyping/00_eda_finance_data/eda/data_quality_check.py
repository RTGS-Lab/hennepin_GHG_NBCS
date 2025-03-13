import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def check_data_quality(file_path):
    print(f"HENNEPIN COUNTY FINANCIAL DATA QUALITY REPORT")
    print(f"=============================================")
    print(f"Data file: {file_path}")
    print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"=============================================\n")
    
    # Load data
    print("Loading data...")
    df = pd.read_csv(file_path)
    
    # Basic info
    print(f"\n1. BASIC INFORMATION")
    print(f"-------------------")
    print(f"Number of records: {len(df):,}")
    print(f"Number of columns: {len(df.columns)}")
    print(f"Years represented: {', '.join(sorted(df['year'].astype(str).unique()))}")
    print(f"File size: {df.memory_usage(deep=True).sum() / (1024 * 1024):.2f} MB")
    
    # Data completeness
    print(f"\n2. DATA COMPLETENESS")
    print(f"-------------------")
    missing_data = df.isnull().sum()
    missing_percent = (missing_data / len(df)) * 100
    
    # Create a summary DataFrame for missing values
    missing_summary = pd.DataFrame({
        'Column': missing_data.index,
        'Missing Values': missing_data.values,
        'Missing Percentage': missing_percent.values
    })
    
    # Sort by percentage of missing values
    missing_summary = missing_summary.sort_values('Missing Percentage', ascending=False)
    
    # Print columns with missing values
    print("Columns with missing values:")
    missing_cols = missing_summary[missing_summary['Missing Values'] > 0]
    if len(missing_cols) > 0:
        for _, row in missing_cols.iterrows():
            print(f"  - {row['Column']}: {row['Missing Values']:,} missing values ({row['Missing Percentage']:.2f}%)")
    else:
        print("  No missing values detected!")
    
    # Data distribution
    print(f"\n3. KEY FIELD DISTRIBUTION")
    print(f"------------------------")
    
    # Fund distribution
    fund_counts = df['Fund'].value_counts().head(10)
    print("\nTop 10 Funds:")
    for fund, count in fund_counts.items():
        print(f"  - {fund}: {count:,} records ({count/len(df)*100:.2f}%)")
    
    # Department distribution
    dept_counts = df['DeptID'].value_counts().head(10)
    print("\nTop 10 Departments:")
    for dept, count in dept_counts.items():
        print(f"  - {dept}: {count:,} records ({count/len(df)*100:.2f}%)")
    
    # Account distribution
    account_counts = df['Account'].value_counts().head(10)
    print("\nTop 10 Accounts:")
    for account, count in account_counts.items():
        print(f"  - {account}: {count:,} records ({count/len(df)*100:.2f}%)")
    
    # Project distribution
    project_counts = df['Project'].value_counts().head(10)
    print("\nTop 10 Projects:")
    for project, count in project_counts.items():
        print(f"  - {project}: {count:,} records ({count/len(df)*100:.2f}%)")
    
    # Monetary amount analysis
    print(f"\n4. MONETARY AMOUNT ANALYSIS")
    print(f"---------------------------")
    
    # Convert Monetary Amount to numeric if it's not already
    if df['Monetary Amount'].dtype == 'object':
        df['Monetary Amount'] = pd.to_numeric(df['Monetary Amount'], errors='coerce')
    
    # Summary statistics
    print("\nSummary Statistics for Monetary Amount:")
    monetary_stats = df['Monetary Amount'].describe()
    print(f"  - Count: {monetary_stats['count']:,.0f}")
    print(f"  - Mean: ${monetary_stats['mean']:,.2f}")
    print(f"  - Median: ${monetary_stats['50%']:,.2f}")
    print(f"  - Min: ${monetary_stats['min']:,.2f}")
    print(f"  - Max: ${monetary_stats['max']:,.2f}")
    print(f"  - Standard Deviation: ${monetary_stats['std']:,.2f}")
    
    # Find zero and negative amounts
    zero_amount = (df['Monetary Amount'] == 0).sum()
    negative_amount = (df['Monetary Amount'] < 0).sum()
    positive_amount = (df['Monetary Amount'] > 0).sum()
    
    print(f"\nMonetary Amount Distribution:")
    print(f"  - Positive amounts: {positive_amount:,} ({positive_amount/len(df)*100:.2f}%)")
    print(f"  - Zero amounts: {zero_amount:,} ({zero_amount/len(df)*100:.2f}%)")
    print(f"  - Negative amounts: {negative_amount:,} ({negative_amount/len(df)*100:.2f}%)")
    
    # Calculate total
    total_amount = df['Monetary Amount'].sum()
    print(f"\nTotal Monetary Amount: ${total_amount:,.2f}")
    
    # Temporal analysis
    print(f"\n5. TEMPORAL ANALYSIS")
    print(f"-------------------")
    
    # Convert Journal Date to datetime if it's not already
    if df['Journal Date'].dtype == 'object':
        df['Journal Date'] = pd.to_datetime(df['Journal Date'], errors='coerce')
    
    # Extract month and year
    df['Month'] = df['Journal Date'].dt.month
    df['Year'] = df['Journal Date'].dt.year
    
    # Check date range
    print(f"Date Range: {df['Journal Date'].min().strftime('%Y-%m-%d')} to {df['Journal Date'].max().strftime('%Y-%m-%d')}")
    
    # Record counts by year
    year_counts = df['Year'].value_counts().sort_index()
    print("\nRecord counts by year:")
    for year, count in year_counts.items():
        print(f"  - {year}: {count:,} records")
    
    # Check for potential data quality issues
    print(f"\n6. POTENTIAL DATA QUALITY ISSUES")
    print(f"--------------------------------")
    
    # Check for duplicate records
    duplicate_records = df.duplicated().sum()
    print(f"Duplicate records: {duplicate_records:,} ({duplicate_records/len(df)*100:.2f}%)")
    
    # Check for potential inconsistencies in Journal ID format
    journal_id_patterns = df['Journal ID'].str.extract(r'([A-Za-z]+)')[0].value_counts()
    print("\nJournal ID prefix patterns:")
    for pattern, count in journal_id_patterns.head(10).items():
        print(f"  - {pattern}: {count:,} records")
    
    # Check Project field formatting
    project_patterns = df['Project'].str.match(r'\d+\s+-\s+.+').mean() * 100
    print(f"\nProject field formatting: {project_patterns:.2f}% match expected pattern")
    
    # Data by source file and sheet
    print(f"\n7. DATA BY SOURCE FILE AND SHEET")
    print(f"-------------------------------")
    
    source_counts = df.groupby(['source_file', 'source_sheet']).size().reset_index(name='count')
    for _, row in source_counts.iterrows():
        print(f"  - {row['source_file']}, Sheet: {row['source_sheet']}: {row['count']:,} records")
    
    print(f"\n=============================================")
    print(f"END OF REPORT")
    print(f"=============================================")

if __name__ == "__main__":
    check_data_quality("combined_financial_data.csv")