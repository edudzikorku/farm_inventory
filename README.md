## Introduction

This repository demonstrates a Web GIS application that displays mangrove farm locations in the Volta Region of Ghana using a Leaflet map. The project uses PostgreSQL with PostGIS extension for spatial data storage, FastAPI for the backend API, and Leaflet.js for the interactive web map interface. This implementation serves as a foundation for understanding core Web GIS concepts and spatial data management.

## Setup

To set up the project, you will need to install the dependencies as specified in the requirements.txt file 

You can install these dependencies using pip:

```
pip install -r requirements.txt
```

Next, you will need to create a PostgreSQL database and set up the necessary tables. You can use the `setup.py` script to create the a new geodatabase, postgis extention, a schema, a table, and finally import the geodata into the geodatabase.

## Running the project
To run the project, you will need to start the FastAPI server. You can do this using the following command:

```
uvicorn main:app --reload
```

This will start the server and you can access the map at `http://localhost:8000`.

## Contributing

If you would like to contribute to this project, please feel free to submit a pull request. We welcome contributions from anyone who is interested in improving the project.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.
