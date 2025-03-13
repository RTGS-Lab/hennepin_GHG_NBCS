import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set the working directory to this file's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def analyze_no_project_data():
    print("Analyzing 'No Project' Records...")
    print("=================================")
    
    # Load data
    df = pd.read_csv('clean_financial_data.csv')
    
    # Filter to No Project records
    no_project = df[df['Project_Name'] == 'No Project']
    
    # Basic statistics
    print(f"Total 'No Project' records: {len(no_project):,} ({len(no_project)/len(df)*100:.2f}% of all records)")
    print(f"Total amount: ${no_project['Monetary Amount'].sum():,.2f}")
    print(f"Average transaction amount: ${no_project['Monetary Amount'].mean():,.2f}")
    
    # Transaction types
    print("\nTransactions by type:")
    trans_types = no_project['Transaction_Type'].value_counts()
    for type_name, count in trans_types.items():
        print(f"  - {type_name}: {count:,} records ({count/len(no_project)*100:.2f}%)")
    
    # Department breakdown
    print("\nDepartment breakdown:")
    dept_summary = no_project.groupby('Department_Name')['Monetary Amount'].agg(['sum', 'count'])
    dept_summary = dept_summary.sort_values('sum', ascending=False)
    
    for dept, row in dept_summary.iterrows():
        print(f"  - {dept}: ${row['sum']:,.2f} ({row['count']:,} records)")
    
    # Account categories
    print("\nTop 10 account categories in 'No Project':")
    account_summary = no_project.groupby('Account')['Amount_Abs'].sum().sort_values(ascending=False).head(10)
    
    for account, amount in account_summary.items():
        print(f"  - {account}: ${amount:,.2f}")
    
    # Year comparison
    print("\nComparison by year:")
    year_summary = no_project.groupby('Year')['Monetary Amount'].agg(['sum', 'count'])
    
    for year, row in year_summary.iterrows():
        print(f"  - {int(year)}: ${row['sum']:,.2f} ({row['count']:,} records)")
    
    # Journal sources
    print("\nTop journal sources:")
    source_summary = no_project.groupby('Journal Source')['Amount_Abs'].sum().sort_values(ascending=False).head(5)
    
    for source, amount in source_summary.items():
        print(f"  - {source}: ${amount:,.2f}")
    
    # Is this mainly payroll?
    payroll_count = no_project['Is_Payroll'].sum()
    print(f"\nPayroll transactions: {payroll_count:,} ({payroll_count/len(no_project)*100:.2f}% of No Project records)")
    
    # Get total payroll amount
    payroll_amount = no_project[no_project['Is_Payroll']]['Monetary Amount'].sum()
    print(f"Payroll amount: ${payroll_amount:,.2f} ({payroll_amount/no_project['Monetary Amount'].sum()*100:.2f}% of No Project amount)")
    
    # Find the most common transaction description
    print("\nMost common transaction descriptions:")
    desc_counts = no_project['Line Description'].value_counts().head(5)
    
    for desc, count in desc_counts.items():
        print(f"  - {desc}: {count:,} records")
    
    print("\n=================================")
    print("Analysis complete")

if __name__ == "__main__":
    analyze_no_project_data()