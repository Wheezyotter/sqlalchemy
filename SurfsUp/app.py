# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# reflects hawaii.sqlite database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite", 
                       connect_args={'check_same_thread': False})
base = automap_base()

# reflects the tables
base.prepare(autoload_with=engine)

# Save references to each table, measurement and station
measurement = base.classes.measurement
station = base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Home page - gives list of possible routes
@app.route("/")
def index():
    return (
            f"Available Routes:"
            f"<ul>"
            f"<li>Precipitation : <a href='http://127.0.0.1:5000/api/v1.0/precipitation' target='_blank'> /api/v1.0/precipitation </a></li>"
            f"<li>Stations: <a href='http://127.0.0.1:5000/api/v1.0/stations' target='_blank'> /api/v1.0/stations</a></li>"
            f"<li>Temperature: <a href='http://127.0.0.1:5000/api/v1.0/tobs' target='_blank'> /api/v1.0/tobs</a></li>"
            f"<li>Insert Start Date (YYYY-MM-DD): /api/v1.0/<start></li>"
            f"<li>Insert Date Range (YYYY-MM-DD): /api/v1.0/<start>/<end></li>"
            f"</ul>"
            )

# Precipitation - gives latest year precipitation data in JSON format
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Finds the most recent date in the data
    latest_date = session.query(measurement.date).\
                        order_by(measurement.date.desc()).\
                        first()
    
    # Converts latest date to datetime format
    latest_date_dt = dt.datetime.strptime(latest_date[0], '%Y-%m-%d').date()
    # Finds the date exactly one year from the latest date
    query_date = latest_date_dt - dt.timedelta(weeks = 52.2)

    # Queries the date and precipitation from the latest year in descending order
    latest_year_data =  session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= query_date).\
    order_by(measurement.date.desc()).all()

    # Formats data into a dictionary
    latest_year_precip = []
    for date, prcp in latest_year_data:
        dates_precip = {}
        dates_precip["date"] = date
        dates_precip["prcp"] = prcp
        latest_year_precip.append(dates_precip)

    # Returns in json format
    return jsonify(latest_year_precip)

# Stations - gives all distinct stations in json format
@app.route("/api/v1.0/stations")
def stations():
    # Queries all station information
    all_stations_query = session.query(station.id, 
                                       station.station, 
                                       station.name,
                                       station.latitude,
                                       station.longitude,
                                       station.elevation).\
                        all()

    # Formats data into a dictionary
    all_stations = []
    for id, stn, name, lat, lng, elev in all_stations_query:
        stations_dict = {}
        stations_dict["id"] = id
        stations_dict["station"] = stn
        stations_dict["name"] = name
        stations_dict["lat"] = lat
        stations_dict["long"] = lng
        stations_dict["elevation"] = elev
        all_stations.append(stations_dict)

    # Returns in json format
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Finds the most recent date in the data
    latest_date_temp = session.query(measurement.date).\
                        order_by(measurement.date.desc()).\
                        first()
    
    # Converts latest date to datetime format
    latest_date_temp_dt = dt.datetime.strptime(latest_date_temp[0], '%Y-%m-%d').date()
    # Finds the date exactly one year from the latest date
    query_date_temp = latest_date_temp_dt - dt.timedelta(weeks = 52.2)

    # Queries most active stations and the number of measurements per station
    station_query = session.query(measurement.station, func.count(measurement.station)).\
                            group_by(measurement.station).\
                            order_by(func.count(measurement.station).desc()).\
                            all()

    # Queries temperature from the latest year and from the most active station
    latest_year_temp_query =  session.query(measurement.date, measurement.tobs).\
                                filter(measurement.station == station_query[0][0]).\
                                filter((measurement.date >= query_date_temp)).\
                                order_by(measurement.date).\
                                all()
    
    # Formats data into a dictionary
    latest_year_temp = []
    for date, temp in latest_year_temp_query:
        dates_temp = {}
        dates_temp["date"] = date
        dates_temp["temp"] = temp
        latest_year_temp.append(dates_temp)  

    # Returns in json format
    return jsonify(latest_year_temp)

@app.route("/api/v1.0/<start>")
def start(start):
    # Converts user date input into datetime format
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()

    # Queries all temperature measurement from start date to latest date
    start_temp_query = session.query(measurement.date, measurement.tobs).\
                               filter(measurement.date >= start_date).\
                               order_by(measurement.date).\
                               all()
    
    # Formats data into a dictionary
    start_date_temp = []
    for date, temp in start_temp_query:
        dates_temp = {}
        dates_temp["date"] = date
        dates_temp["temp"] = temp
        start_date_temp.append(dates_temp)  

    # Returns in json format
    return jsonify(start_date_temp)

@app.route("/api/v1.0/<start>/<end>")
def end(start, end):
    # Finds the most recent date in the data
    latest_date = session.query(measurement.date).\
                          order_by(measurement.date.desc()).\
                          first()
    
    # Converts latest date to datetime format
    latest_date_dt = dt.datetime.strptime(latest_date[0], '%Y-%m-%d').date()

    # Converts user date input into datetime format
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()

    # Queries all temperatures between start and end dates
    start_end_temp_query = session.query(measurement.date, measurement.tobs).\
                               filter(measurement.date >= start_date).\
                               filter(measurement.date <= end_date).\
                               order_by(measurement.date).\
                               all()

    # Formats data into a dictionary
    start_end_date_temp = []
    for date, temp in start_end_temp_query:
        dates_temp = {}
        dates_temp["date"] = date
        dates_temp["temp"] = temp
        start_end_date_temp.append(dates_temp)  

    # Returns in json format
    return jsonify(start_end_date_temp)

if __name__ == "__main__":
    app.run(debug=True)