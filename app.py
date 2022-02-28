import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#make engine
#not sure if I need these arguments
#engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={"check_same_thread": False}, poolclass=StaticPool, echo=True)
engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={"check_same_thread": False})

#set up a base to use
Base = automap_base()

# use the base to reflect the database
Base.prepare(engine, reflect=True)
keys = Base.classes.keys()
print(keys)
#store the tables inside a variable
measurement = Base.classes.measurement
station = Base.classes.station

#start a session to begin exploratory analysis to begin queries
session = Session(engine)

#start flask
app = Flask(__name__)


##########

#Home page.
#List all routes that are available.
#use html
@app.route("/")
def home():
    return (
        f"All routes<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"Precipitation from August 2016-7<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"All Stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Temperature from August 2016-7<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"Start Date Summary Statistics<br/>"
        f"<br/>"
        f"/api/v1.0/startend<br/>"
        f"Start and End Date Summary Statistics<br/>"
    )

#precipitation api
#/api/v1.0/precipitation
#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
        # use date as a key and precipitation as the value 
        # calculate the start date by taking the last date known and rolling back a year 
        # it's 8/23/2017 from previous excercise
        start_date = dt.date(2017,8,23) - dt.timedelta(days=365)
        # make a query to get the precipitation dates and data
        precipitation_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= start_date).order_by(measurement.date).all()
        # covert the tuples 
        precipitation_dict = dict(precipitation_data)
        # Return JSON of dict
        return jsonify(precipitation_dict)

#/api/v1.0/stations
#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
        # get all stations
        all_station = session.query(station.station, station.name).all()
        # covert the tuples
        station_dict = dict(all_station)
        # Return JSON of dict
        return jsonify(station_dict)


#/api/v1.0/tobs
#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
        # same query and variable as precipitation
        start_date = dt.date(2017,8,23) - dt.timedelta(days=365)
        # make query of the values; similar as prcp but with tobs
        tobs_data = session.query(measurement.date, measurement.tobs).filter(measurement.date >= start_date).order_by(measurement.date).all()
        # covert the tuples
        tobs_dict = dict(tobs_data)
        # # Return JSON of dict
        return jsonify(tobs_dict)

#/api/v1.0/<start> 
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# requires user input ideally but for the sake of demonstration, a hard value will be given
@app.route("/api/v1.0/start")
def start_day():
        start = dt.date(2017,8,23) - dt.timedelta(days=365)
        start_data = session.query(measurement.date, 
        func.min(measurement.tobs), 
        func.avg(measurement.tobs), 
        func.max(measurement.tobs)).filter(measurement.date >= start).group_by(measurement.date).all()

         # due to the additional values; a for loop is needed to make the conversion to dict
        start_day_dict = {}
        for i in start_data:
            start_day_dict[i[0]] = i[1],i[2],i[3]
        # Return of dict
        return jsonify(start_day_dict)

#/api/v1.0/<start>/<end>
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
@app.route("/api/v1.0/startend")
def start_end_day():
        start = dt.date(2017,8,23) - dt.timedelta(days=365)
        end = dt.date(2017,8,23)
        start_and_end_day = session.query(measurement.date, 
        func.min(measurement.tobs), 
        func.avg(measurement.tobs), 
        func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).group_by(measurement.date).all()
        # due to the additional values; a for loop is needed to make the conversion to dict
        start_and_end_day_dict = {}
        for i in start_and_end_day:
            start_and_end_day_dict[i[0]] = i[1],i[2],i[3]
        # # Return JSON of dict
        return start_and_end_day_dict

if __name__ == "__main__":
    app.run(debug=True)
