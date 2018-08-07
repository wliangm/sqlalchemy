# climate starter, by Lucas Liang
# Step 2 - Climate App

#########################################################
#import dependencies

import numpy as np
import sqlalchemy
import datetime as dt

from sqlalchemy.ext.automap import automap_base
#from sqlalchemy.pool import SingletonThreadPool
#from sqlalchemy.orm import Session, scoped_session,sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from datetime import datetime, timedelta

#########################################################
# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
Session = sessionmaker(bind=engine)
#session = Session()


#########################################################
#calculate last year and previous year start date and end date
#this is to get full 12 months of year's data

#step 1 -- last year
#query for the latest/max date as last year end date from measurement table
#max_date_query = session.query(Measurement.date, func.max(Measurement.date).label("latest_date"))

#from query result, store the latest/max date as end date
#max_date_result = max_date_query.one()

#last year end date is equal to the latest/max date of measurement table
#last_year_end_date_str = max_date_result.latest_date

#convert last year end date from string into datetime data type
#last_year_end_date_dt = datetime.strptime(last_year_end_date_str, '%Y-%m-%d')

# Calculate last year start date, which is equal to last year end date minus 365 days
#last_year_start_date_dt = last_year_end_date_dt - timedelta(days=365)

# convert last year start date from datetime into string data type
#last_year_start_date_str = last_year_start_date_dt.strftime('%Y-%m-%d')

#step 2 -- previous year
#calculate previous year start date and end date from last year start date:

#previous year end date is equal to last year start date
#prev_year_end_date_dt = last_year_start_date_dt.strftime('%Y-%m-%d')

# convert previous year end date from datetime into string data type
#prev_year_end_date_str = prev_year_end_date_dt 

#previous year start date is equal to last year start date minus 365 days
#prev_year_start_date_dt = last_year_start_date_dt - timedelta(days=365)

# convert previous year start date from datetime into string data type
#prev_year_start_date_str = prev_year_start_date_dt.strftime('%Y-%m-%d')


#########################################################
# Flask Setup

app = Flask(__name__)

#########################################################
# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
        )

#########################################################
#* `/api/v1.0/precipitation`
# Query for the dates and temperature observations from the last year.
# Convert the query results to a Dictionary using `date` as the key and `temperature` as the value.
# Return the JSON representation of your dictionary.
  
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    
     #calculate start date and end date (today and minus 365 days)
    prev_year = dt.date.today() - dt.timedelta(days=365)
    curr_year = dt.date.today() 

    # convert data type from datetime into string data type
    prev_year_str = prev_year.strftime('%Y-%m-%d')
    curr_year_str = curr_year.strftime('%Y-%m-%d')
    
    #open connection
    session = Session()
    # Query date and precipitation from last year start and end year
    prcp_results = session.query(Measurement.date,Measurement.prcp).\
                            filter(Measurement.date >= prev_year_str, Measurement.date <= curr_year_str).\
                            order_by(Measurement.date.asc()).all()
    session.close()
    
    all_prcp = {}
    for x_prcp in prcp_results:
        
        date = x_prcp[0]
        prcp = x_prcp[1]
        all_prcp[date] = prcp
        

    return jsonify(all_prcp)

    #close session/connection to avoid thread error - sqlite allow only one connection
    
#########################################################
#  Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    
    session = Session()
    stations_results = session.query(Station).all()
    session.close()
    
    all_stations = []

    for station in stations_results:
        stations_dict = {}
        stations_dict["id"] = station.id
        stations_dict["station"] = station.station
        stations_dict["name"] = station.name
        stations_dict["latitude"] = station.latitude
        stations_dict["longitude"] = station.longitude
        stations_dict["elevation"] = station.elevation
        all_stations.append(stations_dict)

    return jsonify(all_stations)

#########################################################
#Return a JSON list of Temperature Observations (tobs) for the previous year
@app.route("/api/v1.0/tobs")
def tobs():

  
    #calculate start date and end date (today and minus 365 days)
    prev_year = dt.date.today() - dt.timedelta(days=365)
    curr_year = dt.date.today() 

    # convert data type from datetime into string data type
    prev_year_str = prev_year.strftime('%Y-%m-%d')
    curr_year_str = curr_year.strftime('%Y-%m-%d')
    
    session = Session()
    # Query date and temperature from previous year start and end date
    tobs_results = session.query(Measurement.date,Measurement.tobs).\
                            filter(Measurement.date >= prev_year_str, Measurement.date <= curr_year_str).\
                            order_by(Measurement.date.asc()).all()
    session.close()
    
    all_tobs = {}
    for x_tobs in tobs_results:
        
        date = x_tobs[0]
        tobs = x_tobs[1]
        all_tobs[date] = tobs

    return jsonify(all_tobs)  

#########################################################
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.


#When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def start_dt(start=None, end=None):
    
    session = Session()
        # Query temperature in avg, max and min from start date
    start_tobs_results = session.query(func.min(Measurement.tobs).label('min_temp'),func.max(Measurement.tobs).label('max_temp')\
                                           ,func.avg(Measurement.tobs).label('avg_temp')).\
                            filter(Measurement.date >= start).all()
    session.close()
    
    all_start_tobs = []
    
    for x_start in start_tobs_results:
        start_dict = {}
        start_dict['min_temp'] = x_start.min_temp
        start_dict['max_temp'] = x_start.max_temp
        start_dict['avg_temp'] = x_start.avg_temp
        all_start_tobs.append(start_dict)
        
    return jsonify(all_start_tobs)

# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def start_end_dt(start=None, end=None):
    
    session = Session()
        # Query temperature in avg, max and min between start and end date
    start_end_tobs_results = session.query(func.min(Measurement.tobs).label('min_temp'),func.max(Measurement.tobs).label('max_temp')\
                                           ,func.avg(Measurement.tobs).label('avg_temp')).\
                            filter(Measurement.date >= start,Measurement.date <= end).all()
    session.close()
    
    all_start_end_tobs = []
    
    for x_start_end in start_end_tobs_results:
        start_end_dict = {}
        start_end_dict['min_temp'] = x_start_end.min_temp
        start_end_dict['max_temp'] = x_start_end.max_temp
        start_end_dict['avg_temp'] = x_start_end.avg_temp
        all_start_end_tobs.append(start_end_dict)
        
    return jsonify(all_start_end_tobs)
    
#########################################################

if __name__ == "__main__":
    app.run(debug=True)