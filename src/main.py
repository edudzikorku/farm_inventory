"""
FastAPI Server for Mangrove Farm GIS Application

This script implements a REST API server that serves spatial data for the mangrove farms web application.
It provides the following functionality:
1. Establishes an async connection to the PostGIS database
2. Implements CORS middleware for cross-origin requests
3. Provides endpoints for:
   - Health check ("/")
   - Database connection test ("/test")
   - Spatial data retrieval ("/data")

The server converts PostGIS geometries to GeoJSON format, including farm attributes 
such as farmer name, age, community, contact information, and mangrove species.

Requirements:
    - FastAPI and uvicorn for API server
    - databases package for async PostgreSQL connection
    - geojson for spatial data formatting
    - Valid configuration in config.py

Usage:
Run with 'uvicorn main:app --reload' for development

"""

import json
import config
from fastapi import FastAPI
from databases import Database
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from geojson import Feature, FeatureCollection, dumps


# Specify the database url 
DATABASE_URL = f"postgresql://{config.USER}:{config.PASSWORD}@localhost:5432/{config.DATABASE}"

database = Database(DATABASE_URL)
# Instantiate the app 
app = FastAPI()

app.add_middleware(CORSMiddleware, 
                   allow_origins = ["*"], # Allow all origins
                   allow_credentials = True, 
                   allow_methods = ["*"], # Allow all methods (GET, POST, etc)
                   allow_headers = ["*"] # Allow all headers
                   )

@app.on_event("startup")
async def startup():
    await database.connect()
    await database.execute("SET SEARCH_PATH = farm_inventory")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def root():
    return {"message": "API running"}

# Test the server
@app.get("/test")
async def test_connection():
    query = "SELECT 1"
    result = await database.fetch_one(query)
    return {"status": "success", "result": result}


# Render the data as GeoJSON
@app.get("/data")
async def get_data():
    # Select some items from the database 
    try:
        query = f"""
            SELECT 
                name, 
                age, 
                community, 
                contact,
                species,
                ST_AsGeoJSON(geometry) as feature_geometry
            FROM {config.SCHEMA}.{config.TABLE}
        """
        rows = await database.fetch_all(query)
        if not rows:
            return {"type": "FeatureCollection", "features": []}
        
        features = []
        for row in rows:
            try:
                geometry = json.loads(row["feature_geometry"])
                feature = Feature(
                    geometry = geometry,
                    properties = {
                        "name": row["name"] if row["name"] else "",
                        "age": row["age"] if row["age"] else 0,
                        "community": row["community"] if row["community"] else "",
                        "contact": row["contact"] if row["contact"] else "",
                        "species": row["species"] if row["species"] else "",
                    }
                )
                features.append(feature)
            except Exception as e:
                print(f"Error processing row: {str(e)}")
                continue

        collection = FeatureCollection(features)
        # Use FastAPI's JSONResponse to ensure proper JSON serialization
        return JSONResponse(content = json.loads(dumps(collection)))
        
    except Exception as e:
        print(f"Error in get_data: {str(e)}")
        return {"error": str(e)}