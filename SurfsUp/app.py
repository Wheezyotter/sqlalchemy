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
# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
base = automap_base()

# reflect the tables
base.prepare(autoload_with=engine)

# Save references to each table
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
@app.route("/")
def index():
    return (
            f"Available Routes:"
            f"<ul>"
            f"<li>Precipitation : /api/v1.0/precipitation</li>"
            f"<li>/api/v1.0/stations</li>"
            f"<li>/api/v1.0/tobs</li>"
            f"<li>/api/v1.0/<start></li>"
            f"<li>/api/v1.0/<start>/<end></li>"
            f"</ul>"
            )

@app.route("/api/v1.0/precipitation")
def precipitation():

    latest_date = session.query(measurement.date).\
                        order_by(measurement.date.desc()).\
                        first()
    
    # Converts latest date to datetime format
    latest_date_dt = dt.datetime.strptime(latest_date[0], '%Y-%m-%d').date()
    query_date = latest_date_dt - dt.timedelta(weeks = 52.2)

    latest_year_data =  session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= query_date).\
    order_by(measurement.date.desc()).all()

    latest_year_precip = []
    for date, prcp in latest_year_data:
        dates_precip = {}
        dates_precip["date"] = date
        dates_precip["prcp"] = prcp
        latest_year_precip.append(dates_precip)

    return jsonify(latest_year_precip)

@app.route("/api/v1.0/stations")
def stations():
    all_stations_query = session.query(station.id, 
                                       station.station, 
                                       station.name,
                                       station.latitude,
                                       station.longitude,
                                       station.elevation).\
                        all()

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

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():

    latest_date = session.query(measurement.date).\
                        order_by(measurement.date.desc()).\
                        first()
    
    # Converts latest date to datetime format
    latest_date_dt = dt.datetime.strptime(latest_date[0], '%Y-%m-%d').date()
    query_date = latest_date_dt - dt.timedelta(weeks = 52.2)

    station_query = session.query(measurement.station, func.count(measurement.station)).\
                            group_by(measurement.station).\
                            order_by(func.count(measurement.station).desc()).\
                            all()

    latest_year_temp_query =  session.query(measurement.date, measurement.tobs).\
                                filter(measurement.station == station_query[0][0]).\
                                filter((measurement.date >= query_date)).\
                                order_by(measurement.date).\
                                all()
    
    latest_year_temp = []
    for date, temp in latest_year_temp_query:
        dates_temp = {}
        dates_temp["date"] = date
        dates_temp["temp"] = temp
        latest_year_temp.append(dates_temp)  

    return jsonify(latest_year_temp)

@app.route("/api/v1.0/<start>")
def start(start):
    latest_date = session.query(measurement.date).\
                          order_by(measurement.date.desc()).\
                          first()
    
    latest_date_dt = dt.datetime.strptime(latest_date[0], '%Y-%m-%d').date()
    # Look into proper date conversions
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()

    start_temp_query = session.query(measurement.date, measurement.tobs).\
                               filter(measurement.date >= start_date).\
                               order_by(measurement.date).\
                               all()
    
    start_date_temp = []
    for date, temp in start_temp_query:
        dates_temp = {}
        dates_temp["date"] = date
        dates_temp["temp"] = temp
        start_date_temp.append(dates_temp)  

    return jsonify(start_date_temp)

@app.route("/api/v1.0/<start>/<end>")
def end(start, end):
    latest_date = session.query(measurement.date).\
                          order_by(measurement.date.desc()).\
                          first()
    
    latest_date_dt = dt.datetime.strptime(latest_date[0], '%Y-%m-%d').date()
    # Look into proper date conversions
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()

    start_end_temp_query = session.query(measurement.date, measurement.tobs).\
                               filter(measurement.date >= start_date).\
                               filter(measurement.date <= end_date).\
                               order_by(measurement.date).\
                               all()
    
    start_end_date_temp = []
    for date, temp in start_end_temp_query:
        dates_temp = {}
        dates_temp["date"] = date
        dates_temp["temp"] = temp
        start_end_date_temp.append(dates_temp)  

    return jsonify(start_end_date_temp)

if __name__ == "__main__":
    app.run(debug=True)