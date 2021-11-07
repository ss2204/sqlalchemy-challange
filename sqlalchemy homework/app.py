# Import Flask
from flask import Flask, jsonify

# Dependencies and Setup
import numpy as np
import datetime as dt
import re

# Python SQL Toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql import exists

#################################################
# Database Setup
#################################################
# Reference: https://stackoverflow.com/questions/33055039/using-sqlalchemy-scoped-session-in-theading-thread
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect Existing Database Into a New Model
Base = automap_base()
# Reflect the Tables
Base.prepare(engine, reflect=True)

# Save References to Each Table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create Session (Link) From Python to the DB
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
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"

    )

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
        # Convert the Query Results to a Dictionary Using `date` as the Key and `prcp` as the Value
        # Calculate the Date 1 Year Ago from the Last Data Point in the Database
        one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
        # Design a Query to Retrieve the Last 12 Months of Precipitation Data Selecting Only the `date` and `prcp` Values
        prcp_data = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= one_year_ago).\
                order_by(Measurement.date).all()
        # Convert List of Tuples Into a Dictionary
        prcp_data_list = dict(prcp_data)
        # Return JSON Representation of Dictionary
        return jsonify(prcp_data_list)

@app.route("/api/v1.0/stations") #Return a JSON list of stations from the dataset
def stations():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query Stations
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    station_details = list(np.ravel(results))

    return jsonify(station_details)

# TOBs Route
@app.route("/api/v1.0/tobs")
def tobs():
    # Query for the Dates and Temperature Observations from a Year from the Last Data Point
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Design a Query to Retrieve the Last 12 Months of Precipitation Data Selecting Only the `date` and `prcp` Values
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.date >= one_year_ago).\
            order_by(Measurement.date).all()
    # Convert List of Tuples Into Normal List
    tobs_data_list = dict(tobs_data)
    # Return JSON List of Temperature Observations (tobs) for the Previous Year
    return jsonify(tobs_data_list)

@app.route("/api/v1.0/<start>") # Calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date
def start_only(start):

    # Create session (link) from Python to the DB
    session = Session(engine)

    # Date Range (only for help to user in case date gets entered wrong)
    date_range_max = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_range_max_str = str(date_range_max)
    date_range_max_str = re.sub("'|,", "",date_range_max_str)
    print (date_range_max_str)

    date_range_min = session.query(Measurement.date).first()
    date_range_min_str = str(date_range_min)
    date_range_min_str = re.sub("'|,", "",date_range_min_str)
    print (date_range_min_str)


    # Check for valid entry of start date
    valid_entry = session.query(exists().where(Measurement.date == start)).scalar()
 
    if valid_entry:

    	results = (session.query(func.min(Measurement.tobs)
    				 ,func.avg(Measurement.tobs)
    				 ,func.max(Measurement.tobs))
    				 	  .filter(Measurement.date >= start).all())

    	tmin =results[0][0]
    	tavg ='{0:.4}'.format(results[0][1])
    	tmax =results[0][2]
    
    	result_printout =( ['Entered Start Date: ' + start,
    						'The lowest Temperature was: '  + str(tmin) + ' F',
    						'The average Temperature was: ' + str(tavg) + ' F',
    						'The highest Temperature was: ' + str(tmax) + ' F'])
    	return jsonify(result_printout)

    return jsonify({"error": f"Input Date {start} not valid. Date Range is {date_range_min_str} to {date_range_max_str}"}), 404

@app.route("/api/v1.0/<start>/<end>") # Calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive
def start_end(start, end):

    # Create session (link) from Python to the DB
    session = Session(engine)

    # Date Range (only for help to user in case date gets entered wrong)
    date_range_max = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_range_max_str = str(date_range_max)
    date_range_max_str = re.sub("'|,", "",date_range_max_str)
    print (date_range_max_str)

    date_range_min = session.query(Measurement.date).first()
    date_range_min_str = str(date_range_min)
    date_range_min_str = re.sub("'|,", "",date_range_min_str)
    print (date_range_min_str)

    # Check for valid entry of start date
    valid_entry_start = session.query(exists().where(Measurement.date == start)).scalar()
 	
 	# Check for valid entry of end date
    valid_entry_end = session.query(exists().where(Measurement.date == end)).scalar()

    if valid_entry_start and valid_entry_end:

    	results = (session.query(func.min(Measurement.tobs)
    				 ,func.avg(Measurement.tobs)
    				 ,func.max(Measurement.tobs))
    					  .filter(Measurement.date >= start)
    				  	  .filter(Measurement.date <= end).all())

    	tmin =results[0][0]
    	tavg ='{0:.4}'.format(results[0][1])
    	tmax =results[0][2]
    
    	result_printout =( ['Entered Start Date: ' + start,
    						'Entered End Date: ' + end,
    						'The lowest Temperature was: '  + str(tmin) + ' F',
    						'The average Temperature was: ' + str(tavg) + ' F',
    						'The highest Temperature was: ' + str(tmax) + ' F'])
    	return jsonify(result_printout)

    if not valid_entry_start and not valid_entry_end:
    	return jsonify({"error": f"Input Start {start} and End Date {end} not valid. Date Range is {date_range_min_str} to {date_range_max_str}"}), 404

    if not valid_entry_start:
    	return jsonify({"error": f"Input Start Date {start} not valid. Date Range is {date_range_min_str} to {date_range_max_str}"}), 404

    if not valid_entry_end:
    	return jsonify({"error": f"Input End Date {end} not valid. Date Range is {date_range_min_str} to {date_range_max_str}"}), 404

if __name__ == '__main__':
    app.run(debug=True)