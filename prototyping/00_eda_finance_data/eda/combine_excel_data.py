import pandas as pd
import os

def process_excel_files():
    # Define file paths
    excel_files = [
        "LWU Revenues & Expenditures Transactions Detail Export Report_2023(1).xlsx",
        "LWU Revenues & Expenditures Transactions Detail Export Report_2024(1).xlsx"
    ]

    all_data = []

    # Process each Excel file
    for file_path in excel_files:
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} not found.")
            continue
        
        # Get all sheet names
        try:
            xls = pd.ExcelFile(file_path)
            sheet_names = xls.sheet_names
            
            print(f"Processing file: {file_path}")
            print(f"Found sheets: {sheet_names}")
            
            # Process each sheet in the file
            for sheet_name in sheet_names:
                print(f"  Reading sheet: {sheet_name}")
                
                # Read the sheet, skip the first 5 rows (header starts at row 6)
                df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=5)
                
                # Add source file and sheet information
                df['source_file'] = file_path
                df['source_sheet'] = sheet_name
                df['year'] = '2023' if '2023' in file_path else '2024'
                
                # Append to our list of dataframes
                all_data.append(df)
                
                # Print some info about this sheet
                print(f"    Columns: {df.columns.tolist()}")
                print(f"    Shape: {df.shape}")
        
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    # Combine all dataframes if we have any
    if all_data:
        print("\nCombining all data...")
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Save to CSV
        output_path = "combined_financial_data.csv"
        combined_df.to_csv(output_path, index=False)
        print(f"Combined data saved to {output_path}")
        print(f"Final dataset shape: {combined_df.shape}")
        
        # Display the first few rows of the combined data
        print("\nPreview of combined data:")
        print(combined_df.head())
    else:
        print("No data was processed. Check the file paths and formats.")

if __name__ == "__main__":
    process_excel_files()