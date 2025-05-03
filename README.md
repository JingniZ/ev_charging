# EV Charging Infrastructure in NY

## I. Overview
This project analyzes the electric vehicle (EV) charging infrastructure in New York State in relation to EV adoption rates. By examining the distribution of EV registrations and public charging stations, this project aims to identify areas with high EV adoption but limited charging infrastructure, potentially informing future infrastructure development.

## II. Data Source & Input Data Files

### Raw Data

#### EV Registration Data
* Obtained from NY Open Data Transportation Category
* Data Source: [NY DMV Vehicle Registration Data](https://data.ny.gov/Transportation/Vehicle-Snowmobile-and-Boat-Registrations/w4pv-hbkt/about_data)
* Updated quarterly with vehicle registration information
* Contains vehicle type, fuel type, and registration location by ZIP code

#### EV Public Charging Station Data
* Obtained from The U.S. Department of Energy's (DOE) Alternative Fuels Data Center (AFDC)
* Data Source: [NYSERDA EV Station Locator](https://www.nyserda.ny.gov/All-Programs/Drive-Clean-Rebate-For-Electric-Cars-Program/Charging-Options/Electric-Vehicle-Station-Locator#/analyze?region=US-NY&show_map=true)
* Provides information on all public charging stations in NY State
* Includes station location, charging type (Level 1, 2, DC Fast), number of ports, and operational status

#### Geographic Boundary Data
* Obtained from US Census Bureau's 2024 TIGER/Line Shapefiles
* Data Source: [US Census TIGER/Line Shapefiles](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)
* Provides detailed geographic boundary data for New York state
* Includes county, ZIP code, and census tract boundaries for precise mapping

### Input Data Files
* `ny_ev_registrations.csv`: Processed dataset of EV registrations by ZIP code
* `ny_charging_stations.csv`: Compiled dataset of public charging stations with geographical coordinates
* `ny_tiger_shapefile.zip`: US Census 2024 TIGER/Line Shapefiles for precise NY state boundaries

## III. Script Descriptions
* `data_processing.py`: Cleans and preprocesses the raw DMV registration data and AFDC charging station data
* `trend_graph.py`: Visualize the EV adoption trend and number of public charging over time
* `spatial_analysis.py`: Performs geospatial analysis to map EV registrations and charging stations by county/ZIP using TIGER/Line geographic boundaries



## IV. Visualizations


## V. Conclusion


This repository provides the code and methodology for conducting similar analyses in other regions or updating the New York analysis as new data becomes available.