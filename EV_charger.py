# Author: Jingni Zhang
# Date Created: 04.10.2025

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from datetime import datetime
import os
import geopandas as gpd
import contextily as ctx
from shapely.geometry import Point

os.makedirs('data', exist_ok=True)
os.makedirs('graphs', exist_ok=True)

# Import data
df = pd.read_csv('alt_fuel_stations.csv')

# Filter for Electric charging stations (ELEC)
elec_df = df[df['Fuel Type Code'] == 'ELEC'].copy()

# Convert date to datetime and extract year
elec_df['Open Date'] = pd.to_datetime(elec_df['Open Date'], format='mixed', errors='coerce')
elec_df['Year'] = elec_df['Open Date'].dt.year

# Remove rows with missing coordinates for spatial analysis
elec_df_spatial = elec_df.dropna(subset=['Latitude', 'Longitude']).copy()

# Create a line graph showing the cumulative number of chargers by year
yearly_counts = elec_df['Year'].value_counts().sort_index()
yearly_cumulative = yearly_counts.cumsum()

plt.figure(figsize=(12, 8))
plt.plot(yearly_cumulative.index, yearly_cumulative.values, marker='o', linewidth=2)

# Add value labels on data points
for year, count in zip(yearly_cumulative.index, yearly_cumulative.values):
    plt.text(year, count + 50, f'{int(count)}', ha='center', va='bottom')

plt.title('Cumulative Number of Electric Vehicle Chargers Over Time', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Number of Chargers', fontsize=14)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('graphs/ev_chargers_timeline.png', dpi=300)
plt.close()

# Create a bar chart showing chargers installed each year
plt.figure(figsize=(16, 10))
bars = plt.bar(yearly_counts.index, yearly_counts.values, color='skyblue', edgecolor='navy')

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
            str(int(height)), ha='center', va='bottom', fontsize=10)

plt.xlabel('Year', fontsize=14)
plt.ylabel('Number of Chargers Installed', fontsize=14)
plt.title('EV Charger Installations by Year in New York', fontsize=18, pad=20)
plt.grid(axis='y', alpha=0.3)

# Define year ranges with colors for visual grouping
year_ranges = [
    ('2010-2014', 2010, 2014, 'purple'),
    ('2015-2018', 2015, 2018, 'blue'),
    ('2019-2021', 2019, 2021, 'green'),
    ('2022-2024', 2022, 2024, 'red')
]

# Highlight the year ranges with colored spans
for title, start_year, end_year, color in year_ranges:
    plt.axvspan(start_year-0.5, end_year+0.5, alpha=0.2, color=color)
    plt.text((start_year+end_year)/2, plt.gca().get_ylim()[1]*0.95, title, 
            ha='center', va='top', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('graphs/ev_chargers_by_year.png', dpi=300)
plt.close()

# Create a bar chart showing the number of ELEC chargers by ZIP code
zip_counts = elec_df['ZIP'].value_counts().head(20)  # Top 20 ZIP codes

plt.figure(figsize=(16, 10))
bars = plt.bar(range(len(zip_counts)), zip_counts.values, color='skyblue')
plt.xticks(range(len(zip_counts)), zip_counts.index, rotation=45, ha='right')

# Add value labels on top of bars
for i, bar in enumerate(bars):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.1, 
             str(int(height)), ha='center', va='bottom')

plt.title('Number of Electric Vehicle Chargers by ZIP Code (Top 20)', fontsize=16)
plt.xlabel('ZIP Code', fontsize=14)
plt.ylabel('Number of Chargers', fontsize=14)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('graphs/ev_chargers_by_zip.png', dpi=300)
plt.close()

# Create spatial visualizations using US Census TIGER/Line Shapefiles
# Load NY shapefile data
ny_counties = gpd.read_file('ny_tiger_shapfile/tl_2024_36_cousub.shp')

# Convert EV charger data to GeoDataFrame
geometry = [Point(xy) for xy in zip(elec_df_spatial.Longitude, elec_df_spatial.Latitude)]
gdf_chargers = gpd.GeoDataFrame(elec_df_spatial, geometry=geometry, crs="EPSG:4326")

# Project both datasets to Web Mercator for better visualization
ny_counties = ny_counties.to_crs(epsg=3857)
gdf_chargers = gdf_chargers.to_crs(epsg=3857)

# 4.1 Create EV charger density map by county
fig, ax = plt.subplots(1, figsize=(15, 12))

# Plot counties with a light color
ny_counties.plot(ax=ax, color='lightgray', edgecolor='white', linewidth=0.5)

# Plot charger points with color based on year
gdf_chargers.plot(
    ax=ax,
    column='Year',
    cmap='viridis',
    markersize=30,
    legend=True,
    legend_kwds={'label': 'Installation Year', 'orientation': 'horizontal'}
)

# Add contextily basemap for reference
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, alpha=0.5)

# Set title and remove axes
ax.set_title('EV Charger Density in New York', fontsize=20, pad=20)
ax.set_axis_off()

plt.tight_layout()
plt.savefig('graphs/ev_chargers_density.png', dpi=300)
plt.close()

# Create a heatmap showing charger density
fig, ax = plt.subplots(1, figsize=(15, 12))

# Plot counties 
ny_counties.plot(ax=ax, color='lightgray', edgecolor='white', linewidth=0.5)

# Create a heatmap-like visualization using kernel density estimation
sns.kdeplot(
    x=gdf_chargers.geometry.x,
    y=gdf_chargers.geometry.y,
    cmap='Reds',
    shade=True,
    bw_adjust=0.5,
    ax=ax
)

# Add contextily basemap
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, alpha=0.3)

# Set title and remove axes
ax.set_title('EV Charger Heatmap in New York', fontsize=20, pad=20)
ax.set_axis_off()

plt.tight_layout()
plt.savefig('graphs/ev_chargers_heatmap.png', dpi=300)
plt.close()

# 4.3 Create a map focused on NYC area
fig, ax = plt.subplots(1, figsize=(15, 12))

# Get NYC area bounds (approximate)
nyc_bounds = {
    'min_lon': -74.3, 'max_lon': -73.6,
    'min_lat': 40.5, 'max_lat': 40.9
}

# Convert bounds to Web Mercator
nyc_gdf = gpd.GeoDataFrame(
    geometry=[Point(nyc_bounds['min_lon'], nyc_bounds['min_lat']), 
              Point(nyc_bounds['max_lon'], nyc_bounds['max_lat'])],
    crs="EPSG:4326"
).to_crs(epsg=3857)

nyc_bounds_3857 = {
    'min_x': nyc_gdf.geometry[0].x, 'max_x': nyc_gdf.geometry[1].x,
    'min_y': nyc_gdf.geometry[0].y, 'max_y': nyc_gdf.geometry[1].y
}

# Filter counties in NYC area
nyc_counties = ny_counties.cx[
    nyc_bounds_3857['min_x']:nyc_bounds_3857['max_x'],
    nyc_bounds_3857['min_y']:nyc_bounds_3857['max_y']
]

# Filter chargers in NYC area
nyc_chargers = gdf_chargers.cx[
    nyc_bounds_3857['min_x']:nyc_bounds_3857['max_x'],
    nyc_bounds_3857['min_y']:nyc_bounds_3857['max_y']
]

# Plot counties
nyc_counties.plot(ax=ax, color='lightgray', edgecolor='white', linewidth=0.5)

# Plot charger points
nyc_chargers.plot(
    ax=ax,
    column='Year',
    cmap='viridis',
    markersize=50,
    alpha=0.7,
    edgecolor='black',
    linewidth=0.5,
    legend=True
)

# Add contextily basemap
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)

# Set title and remove axes
ax.set_title('EV Chargers in New York City Area', fontsize=20, pad=20)
ax.set_axis_off()

plt.tight_layout()
plt.savefig('graphs/ev_chargers_nyc.png', dpi=300)
plt.close()

# Create panels showing charger installation by year periods
fig, axes = plt.subplots(2, 2, figsize=(20, 16))
fig.suptitle('EV Chargers by Installation Year Period', fontsize=24, y=0.98)

# Flatten axes for easier iteration
axes = axes.flatten()

for idx, (title, start_year, end_year, color) in enumerate(year_ranges):
    ax = axes[idx]
    
    # Filter data for the year range
    year_data = gdf_chargers[(gdf_chargers['Year'] >= start_year) & (gdf_chargers['Year'] <= end_year)]
    
    # Plot counties
    ny_counties.plot(ax=ax, color='lightgray', edgecolor='white', linewidth=0.5, alpha=0.5)
    
    # Add contextily basemap
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, alpha=0.5)
    
    # Plot points for this period
    if len(year_data) > 0:
        year_data.plot(
            ax=ax, 
            column='Year', 
            cmap='viridis', 
            markersize=30,
            edgecolor='black', 
            linewidth=0.5, 
            alpha=0.8,
            legend=True, 
            legend_kwds={'label': 'Year', 'orientation': 'horizontal'}
        )
    
    ax.set_title(f'{title}\n({len(year_data)} chargers)', fontsize=16, pad=10)
    ax.set_axis_off()

plt.tight_layout()
plt.savefig('graphs/ev_chargers_by_year_panels.png', dpi=300)
plt.close()

# Save processed data
elec_df.to_csv('data/electric_charging_stations.csv', index=False)

# Create summary statistics
summary = {
    'Total Electric Chargers': len(elec_df),
    'Number of Unique ZIP Codes': elec_df['ZIP'].nunique(),
    'Earliest Open Date': elec_df['Open Date'].min(),
    'Latest Open Date': elec_df['Open Date'].max(),
    'Most Common ZIP': zip_counts.index[0],
    'Chargers in Most Common ZIP': zip_counts.values[0]
}

summary_df = pd.DataFrame([summary])
summary_df.to_csv('data/summary_statistics.csv', index=False)

print("Analysis complete! Graphs and data exported successfully.")
print(f"Total electric chargers: {summary['Total Electric Chargers']}")
print("Files created:")
print("- ev_chargers_timeline.png (cumulative chargers over time)")
print("- ev_chargers_by_year.png (bar chart by year)")
print("- ev_chargers_by_zip.png (bar chart by ZIP code)")
print("- ev_chargers_density.png (density map)")
print("- ev_chargers_heatmap.png (heatmap visualization)")
print("- ev_chargers_nyc.png (NYC area focus)")
print("- ev_chargers_by_year_panels.png (installation by time period)")