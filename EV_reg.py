# Author: Jingni Zhang
# Date Created: 04.08.2025

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set plot style
plt.style.use('ggplot')
sns.set(font_scale=1.2)

def clean_ev_data():
    """
    Clean and preprocess EV registration data
    
    Returns:
    df (DataFrame): Cleaned DataFrame
    """
    # Read the CSV file from the data folder in GitHub
    print("Reading data from data/Vehicle_Registrations.csv...")
    df = pd.read_csv("Vehicle_Registrations.csv")
    
    # Print initial data info
    print(f"Initial data shape: {df.shape}")
    
    # Drop unnecessary variables
    print("Dropping unnecessary columns...")
    columns_to_drop = [
        'Maximum Gross Weight', 
        'Passengers', 
        'Color', 
        'Scofflaw Indicator', 
        'Suspension Indicator', 
        'Revocation Indicator'
    ]
    df = df.drop(columns=columns_to_drop)
    
    # Rename all variables
    print("Renaming columns...")
    column_rename_map = {
        'Record Type': 'record_type',
        'Registration Class': 'reg_class',
        'Model Year': 'model_year',
        'Body Type': 'body_type',
        'Fuel Type': 'fuel_type',
        'Unladen Weight': 'weight',
        'Reg Valid Date': 'reg_date',
        'Reg Expiration Date': 'exp_date'
    }
    df = df.rename(columns=column_rename_map)
    
    # Keep only when registration type is vehicle type, avoiding boats or other types
    print("Filtering for record_type = 'VEH'...")
    df = df[df['record_type'] == 'VEH']
    
    # Create reg_year from reg_date
    print("Creating reg_year from reg_date...")
    # Extract year from date (format MM/DD/YYYY)
    df['reg_year'] = df['reg_date'].str.split('/').str[2].astype(int)
    
    # Drop observations where reg_year is before 2000
    print("Dropping records before year 2000...")
    df = df[df['reg_year'] >= 2000]
    
    # Drop specific reg_class values
    print("Filtering reg_class values...")
    reg_class_to_drop = ['ATD', 'ATV', 'SNO', 'ORM', 'BOT', 'MOT', 'TRC']
    df = df[~df['reg_class'].isin(reg_class_to_drop)]
    
    # Drop specific body_type values
    print("Filtering body_type values...")
    body_type_to_drop = ['N/A', 'BOAT', 'FIRE', 'S/SP', 'SN/P', 'TRAV', 'MOBL', 'SNOW', 'MCY', 'LOCO', 'W/DR', 'W/SR', 'RBM']
    df = df[~df['body_type'].isin(body_type_to_drop)]
    
    # Save the cleaned data to the same folder
    output_file = "cleaned_EV_reg.csv"
    print(f"Saving cleaned data to {output_file}...")
    df.to_csv(output_file, index=False)
    print(f"Final data shape: {df.shape}")
    
    return df

def analyze_ev_data_basic(df):
    """
    Generate basic descriptive statistics and visualizations for the cleaned EV data
    
    Parameters:
    df (DataFrame): Cleaned DataFrame
    
    Returns:
    None (generates plots)
    """
    print("Analyzing EV registration data (basic visualizations)...")
    
    # Create output directory for graphs if it doesn't exist
    if not os.path.exists("graphs"):
        os.makedirs("graphs")
    
    # Count record_type by Zip
    print("Analyzing record types by ZIP code...")
    record_by_zip = df.groupby('Zip')['record_type'].count().sort_values(ascending=False).head(20)
    
    plt.figure(figsize=(12, 8))
    record_by_zip.plot(kind='bar')
    plt.title('Top 20 ZIP Codes by Number of Registrations', fontsize=16)
    plt.xlabel('ZIP Code', fontsize=14)
    plt.ylabel('Count', fontsize=14)
    plt.tight_layout()
    plt.savefig('graphs/record_by_zip.png')
    plt.close()
    
    # Count record_type by Zip and reg_year (starting from 2020)
    print("Analyzing record types by ZIP code and year from 2020...")
    # Get top 5 ZIP codes by count
    top_zips = df['Zip'].value_counts().head(5).index
    
    # Filter for top 5 ZIPs and years from 2020
    top_zip_df = df[(df['Zip'].isin(top_zips)) & (df['reg_year'] >= 2020)]
    
    # Group by Zip and reg_year to count records
    zip_year_counts = pd.crosstab(top_zip_df['reg_year'], top_zip_df['Zip'])
    
    # Plot with count labels
    plt.figure(figsize=(14, 10))
    
    for zip_code in zip_year_counts.columns:
        # Get the data for this ZIP code
        years = zip_year_counts.index
        counts = zip_year_counts[zip_code]
        
        # Plot the line
        line, = plt.plot(years, counts, marker='o', linewidth=2, markersize=8, label=f'ZIP {zip_code}')
        color = line.get_color()
        
        # Add count labels to the points
        for year, count in zip(years, counts):
            # Only add labels for non-zero counts
            if count > 0:
                plt.annotate(f'{count}', 
                            (year, count),
                            textcoords="offset points", 
                            xytext=(0, 10), 
                            ha='center',
                            fontweight='bold',
                            fontsize=9,
                            color=color)
    
    plt.title('Registration Trends by Year for Top 5 ZIP Codes', fontsize=18)
    plt.xlabel('Registration Year', fontsize=16)
    plt.ylabel('Count', fontsize=16)
    plt.legend(title='ZIP Code', fontsize=12, title_fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.xticks(years)
    plt.tight_layout()
    plt.savefig('graphs/reg_by_zip_and_year.png')
    plt.close()
    
    print("Basic analysis complete! Graphs saved to 'graphs' directory.")


def create_heatmap(df):
    """
    Create a heatmap showing registrations by type over years
    
    Parameters:
    df (DataFrame): Cleaned DataFrame
    
    Returns:
    None (generates heatmap)
    """
    print("Creating registration type heatmap by year...")
    
    # Create output directory for graphs if it doesn't exist
    if not os.path.exists("graphs"):
        os.makedirs("graphs")
    
    # Create a pivot table for the heatmap data
    # Using reg_year as rows and reg_class as columns
    # Fill NA values with 0
    heatmap_data = pd.pivot_table(
        df,
        values='record_type',
        index='reg_year',
        columns='reg_class',
        aggfunc='count',
        fill_value=0
    )
    
    # If there are too many registration classes, focus on the top ones
    if heatmap_data.shape[1] > 10:
        # Get the column sums
        col_sums = heatmap_data.sum()
        # Sort and take the top 10
        top_cols = col_sums.sort_values(ascending=False).head(10).index
        heatmap_data = heatmap_data[top_cols]
    
    # Calculate the figure size based on the data shape
    plt.figure(figsize=(max(12, heatmap_data.shape[1] * 1.2), 
                       max(8, heatmap_data.shape[0] * 0.5)))
    
    # Create the heatmap
    sns.heatmap(
        heatmap_data,
        annot=True,  # Show values in cells
        fmt='g',     # Format as general numbers
        cmap='viridis',
        linewidths=0.5,
        cbar_kws={'label': 'Count of Registrations'}
    )
    
    plt.title('Heat Map of Registration Types by Year', fontsize=18)
    plt.xlabel('Registration Class', fontsize=14)
    plt.ylabel('Registration Year', fontsize=14)
    plt.tight_layout()
    plt.savefig('graphs/reg_type_year_heatmap.png')
    plt.close()
    
    # Create another heatmap showing percentage distribution by year
    # This normalizes the data to show the changing composition over time
    heatmap_pct = heatmap_data.div(heatmap_data.sum(axis=1), axis=0) * 100
    
    plt.figure(figsize=(max(12, heatmap_data.shape[1] * 1.2), 
                       max(8, heatmap_data.shape[0] * 0.5)))
    
    # Create the percentage heatmap
    sns.heatmap(
        heatmap_pct,
        annot=True,
        fmt='.1f',  # Format as 1 decimal place
        cmap='YlGnBu',
        linewidths=0.5,
        cbar_kws={'label': 'Percentage (%)'}
    )
    
    plt.title('Distribution of Registration Types by Year (%)', fontsize=18)
    plt.xlabel('Registration Class', fontsize=14)
    plt.ylabel('Registration Year', fontsize=14)
    plt.tight_layout()
    plt.savefig('graphs/reg_type_year_pct_heatmap.png')
    plt.close()
    
    print("Heatmap analysis complete! Graphs saved to 'graphs' directory.")


def create_zip_heatmap(df):
    """
    Create a heatmap showing EV registrations by ZIP code and year
    
    """
    print("Creating ZIP code by year heatmap...")
    
    try:
        # Create output directory for graphs if it doesn't exist
        if not os.path.exists("graphs"):
            os.makedirs("graphs")
        
        # Create a simplified data frame for the heat map
        # Use reg_year for rows
        if 'reg_year' not in df.columns:
            print("No reg_year column found in the data")
            return
        
        # Create a ZIP code to registration count aggregation
        zip_counts = df.groupby(['Zip', 'reg_year']).size().reset_index(name='count')
        
        # Get top 20 ZIP codes by total count
        top_zips = zip_counts.groupby('Zip')['count'].sum().nlargest(20).index
        
        # Filter for top ZIP codes
        zip_year_heatmap = zip_counts[zip_counts['Zip'].isin(top_zips)]
        
        # Create pivot table
        pivot_data = zip_year_heatmap.pivot(index='Zip', columns='reg_year', values='count').fillna(0)
        
        # Create the heat map
        plt.figure(figsize=(14, 10))
        
        # Plot heatmap
        ax = sns.heatmap(pivot_data, cmap='viridis', linewidths=0.5, 
                          annot=True, fmt='g', cbar_kws={'label': 'Number of Registrations'})
        
        plt.title('Heat Map of EV Registrations by ZIP Code and Year', fontsize=16)
        plt.xlabel('Year', fontsize=14)
        plt.ylabel('ZIP Code', fontsize=14)
        plt.tight_layout()
        plt.savefig('graphs/zip_year_heatmap.png')
        plt.close()
        
        # Create a normalized version showing percentage distribution within each ZIP code
        # This shows year-over-year growth patterns
        norm_data = pivot_data.div(pivot_data.sum(axis=1), axis=0) * 100
        
        plt.figure(figsize=(14, 10))
        ax = sns.heatmap(norm_data, cmap='YlGnBu', linewidths=0.5, 
                          annot=True, fmt='.1f', cbar_kws={'label': 'Percentage of Total (%)'})
        
        plt.title('Distribution of EV Registrations by ZIP Code and Year (%)', fontsize=16)
        plt.xlabel('Year', fontsize=14)
        plt.ylabel('ZIP Code', fontsize=14)
        plt.tight_layout()
        plt.savefig('graphs/zip_year_pct_heatmap.png')
        plt.close()
        
        print("ZIP code heat maps created successfully!")
            
    except Exception as e:
        print(f"Error creating heat map: {e}")
        import traceback
        traceback.print_exc()
        print("Please ensure required libraries are installed")


def main():
    """
    Main function to run the data cleaning and analysis
    """
    # Clean the data and get cleaned DataFrame
    cleaned_df = clean_ev_data()
    
    # Run the basic analysis for ZIP code visualizations
    analyze_ev_data_basic(cleaned_df)
    
    # Create the registration type heatmap visualizations
    create_heatmap(cleaned_df)
    
    # Create the ZIP by year heat map (renamed from create_county_map)
    create_zip_heatmap(cleaned_df)
    
    print("Process completed successfully!")

if __name__ == "__main__":
    main()