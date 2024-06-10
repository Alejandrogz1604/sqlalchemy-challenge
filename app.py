# Import the dependencies.

import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model

base = automap_base()

# reflect the tables

base.prepare(engine, reflect = True)

# Save references to each table

measurement = base.classes.measurement

station = base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

################################################
# Flask Routes

@app.route("/")
def home():
    return (
        f"Available Routes to use: <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/2016-08-23<br/>"
        f"/api/v1.0/2016-08-23/2017-08-23"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    most_recent_date = session.query(func.max(measurement.date)).scalar()

    one_year_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days = 365)

    precipitation_query = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_date.strftime("%Y-%m-%d")).all()

    precipitation_dct = {date: pcrp for date, pcrp in precipitation_query}

    session.close()

    return jsonify(precipitation_dct)
    
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    stations_query = session.query(measurement.station).distinct().all()

    station_list = list(np.ravel(stations_query))

    session.close()

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    most_active_station = "USC00519281"

    most_recent_date = session.query(func.max(measurement.date)).scalar()

    one_year_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days = 365)

    most_active_results_query = session.query(measurement.tobs).filter(measurement.station == most_active_station).filter(measurement.date >= one_year_date).all()

    tobs_data_list = list(np.ravel(most_active_results_query))

    session.close()

    return jsonify(tobs_data_list)

@app.route("/api/v1.0/<start>")
def temp_start(start):
        
    session = Session(engine)

    most_active_min = session.query(func.min(measurement.tobs)).filter(measurement.date >= start).all()

    most_active_max = session.query(func.max(measurement.tobs)).filter(measurement.date >= start).all()

    most_active_mean = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start).all()

    start_temp_stats = list(np.ravel([most_active_min, most_active_max, most_active_mean]))

    session.close()

    return jsonify(start_temp_stats)
        

@app.route("/api/v1.0/<start>/<end>")
def start_to_end(start, end):

    session = Session(engine)

    most_active_min_end = session.query(func.min(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()

    most_active_max_end = session.query(func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()

    most_active_mean_end = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()

    start_temp_stats_end = list(np.ravel([most_active_min_end, most_active_max_end, most_active_mean_end]))

    session.close()

    return jsonify(start_temp_stats_end)

if __name__ == '__main__':
    app.run(debug = True)

#################################################
