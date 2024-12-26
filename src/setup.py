"""
Database Setup and Data Import Script

This script handles the initial setup of the spatial database for the mangrove farms web application.
It performs the following operations:
1. Establishes connection to PostgreSQL default database
2. Creates a new spatial database if it doesn't exist
3. Configures PostGIS extension and creates required schema/table structure
4. Imports mangrove farm geometries and attributes from shapefile to PostGIS

Requirements:
- PostgreSQL with PostGIS extension
- Python libraries: SQLAlchemy, geopandas
- Valid configuration in config.py
- Input shapefile with mangrove farm data

The script expects the shapefile to contain fields for farm name, farmer age, community,
shape metrics, contact information, farmer sex, and mangrove species.
"""

# Standard library imports
import os

# Database connection library
from sqlalchemy import create_engine, text

# Spatial data handling
import geopandas as gpd

# Local configuration
import config


# Connect to default database
engine = create_engine(f"postgresql://{config.USER}:{config.PASSWORD}@localhost:5432/postgres")

# Check if database exists and create if it doesn't
with engine.connect() as connection:
    connection.execution_options(isolation_level = "AUTOCOMMIT")
    result = connection.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{config.DATABASE}'"))
    if not result.fetchone():
        connection.execute(text(f"CREATE DATABASE {config.DATABASE}"))
        print("Database created")
    else:
        print("Database already exists")

# Create engine with database
target_engine = create_engine(f"postgresql://{config.USER}:{config.PASSWORD}@localhost:5432/{config.DATABASE}")

# Create PostGIS extension, schema and table
with target_engine.connect() as connection:
    # PostGIS extention
    connection.execution_options(isolation_level = "AUTOCOMMIT")
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    print("PostGIS extension created")
    # Schema
    connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {config.SCHEMA}"))
    # Table
    connection.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {config.SCHEMA}.{config.TABLE} (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INTEGER NOT NULL,
            community VARCHAR(100) NOT NULL,
            Shape_Leng FLOAT NOT NULL,
            Shape_Area FLOAT NOT NULL,
            contact VARCHAR(100) NOT NULL,
            sex VARCHAR(100) NOT NULL,
            species VARCHAR(100) NOT NULL,
            geom GEOMETRY(POLYGON, 4326) NOT NULL                     
        )
    """))
    print("Table created")

# Load data from shapefile
gdf = gpd.read_file(config.SHAPEFILE_PATH)

# Convert all column names to lower case names
gdf.columns = gdf.columns.str.lower()

# Convert geometry to PostGIS format
gdf = gdf.set_geometry(gdf.geometry.to_crs(epsg = 4326))

# Save data to database
gdf.to_postgis(config.TABLE, target_engine, schema = config.SCHEMA, if_exists = 'replace', index = False)
print("Data saved to database") 