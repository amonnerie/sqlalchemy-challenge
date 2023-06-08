# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def prep():

    """Return a JSON representation of precipitaion from the last 12 months"""
    # Query all passengers
    one_year = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= "2016-08-23").all()
    
    one_year_prcp = list()
    one_year_dates = list()
    
    for date,prcp in one_year:
        one_year_prcp.append(prcp)
        one_year_dates.append(date)
        
    prcp_dict = {one_year_dates[i]: one_year_prcp[i] for i in range(len(one_year_dates))}
    session.close()
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():

    """Return a JSON list of stations"""
    # Query all passengers
    stations = session.query(station.station, station.name).all()
    
    station_list = list()
    station_name = list()
    
    for s,name in stations:
        station_list.append(s)
        station_name.append(name)
        
    station_dict = {station_list[i]: station_name[i] for i in range(len(station_list))}
    session.close()
    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def temps():

    """Return a JSON list of temperatures from the most active station"""
    active_station = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= "2016-08-23").all()
    
    dates = list()
    temp = list()
    
    for d,t in active_station:
        dates.append(d)
        temp.append(t)
        
    temp_dict = {dates[i]: temp[i] for i in range(len(dates))}
    session.close()
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>")
def calc_MAM(start):

    """Return a JSON list of min, avg, max of temperature from a start date"""
    if start > "2010-01-01":
        calc_temp = session.query(measurement.date, measurement.tobs).\
            filter(measurement.date >= start).all()

        dates = list()
        temp = list()

        for d,t in calc_temp:
            dates.append(d)
            temp.append(t)

        TMIN = min(temp)
        TAVG = sum(temp)/len(temp)
        TMAX = max(temp)

        calc_dict = {"Minimum Temp": TMIN,
                     "Average Temp": TAVG,
                     "Maximum Temp": TMAX}
        session.close()
        return jsonify(calc_dict)
    else:
        return "Error: No data before 2010-01-01"

@app.route("/api/v1.0/<start>/<end>")
def calc_MAM2(start, end):

    """Return a JSON list of min, avg, max of temperature from a start date and end date"""
    
    if start < end:
        calc_temp = session.query(measurement.date, measurement.tobs).\
            filter(measurement.date >= start).\
            filter(measurement.date <= end).all()

        dates = list()
        temp = list()

        for d,t in calc_temp:
            dates.append(d)
            temp.append(t)

        TMIN = min(temp)
        TAVG = sum(temp)/len(temp)
        TMAX = max(temp)

        calc_dict = {"Minimum Temp": TMIN,
                     "Average Temp": TAVG,
                     "Maximum Temp": TMAX}
        session.close()
        
        if start >= "2010-01-01":
            return jsonify(calc_dict)   
        else:
            return "No Data before 2010-01-01"
    else:
        return "Error: start date greater than end date"

if __name__ == "__main__":
    app.run(debug=True)