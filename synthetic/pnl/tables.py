import os
import pandas as pd

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the directory where the CSV files are stored
data_dir = os.path.join(current_dir, 'data')

# Initialize a dictionary to store the DataFrames
tables = {}

# Iterate through all CSV files in the 'syntetic data' folder
for filename in os.listdir(data_dir):
    if filename.endswith(".csv"):
        # Create the path to the CSV file
        file_path = os.path.join(data_dir, filename)
        
        # Load the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        
        # Use the filename (without extension) as the table name
        table_name = filename.replace(".csv", "")
        
        # Store the DataFrame in the dictionary
        tables[table_name] = df

