#!/usr/bin/env python3

import iso8601
import requests
from flask import Flask, request

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from prometheus_flask_exporter import PrometheusMetrics

from healthcheck import HealthCheck, EnvironmentDump

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservations.sqlite3'

metrics = PrometheusMetrics(app)

db = SQLAlchemy(app)

health = HealthCheck()

app.add_url_rule("/health", "health", view_func=lambda: health.run())

'''
Define the database model that is used to store the temperature.
'''
class reservation(db.Model):
    datetime = db.Column(db.DateTime, primary_key=True, default=datetime.utcnow())
    confirmation_number = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)

def southwest_reservation_check(confirmation_number, last_name):
    uri = 'https://mobile.southwest.com/middleware/MWServlet'           
    headers = {
                'Host':'mobile.southwest.com:443',
                'user-agent':'Apache-HttpClient/UNAVAILABLE (java 1.4)'
              }
    data = {
             'appID':'swa',
             'appver':'10.9.1',
             'channel':'rc',
             'confirmationNumber':confirmation_number,
             'confirmationNumberLastName':last_name,
             'submitButton':'Continue',
             'searchType':'ConfirmationNumber',
             'serviceID':'viewAirReservation'
           }

    response = requests.post(uri, headers=headers, data=data)

    if response.status_code < 400:
        return response.json(), None

    print(f"Response Reason: {response.reason}")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.content.decode()}")

    return response.reason, True

def southwest_reservation_checkin(confirmation_number, last_name):
    uri = 'https://mobile.southwest.com/middleware/MWServlet'           
    data = {
             'appID':'swa',
             'appver':'10.9.1',
             'channel':'rc',
             'recordLocator':confirmation_number,
             'lastName':lastname,
             'serviceID':'flightcheckin_new'
           }    

    response = requests.post(uri, headers=headers, data=data)

    if response.status_code < 400:
        return response.json()

    print(f"Response Reason: {response.reason}")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.content.decode()}")

'''
Add a reservation to the database
'''
def add_reservation(confirmation_number, last_name):
    msg, failed = southwest_reservation_check(confirmation_number, last_name)
    if failed:
        print(f"Reservation check failed: {msg}")
    else:
        db.create_all()
        new_entry = reservation(datetime=iso8601.parse_date(date), confirmation_number=confirmation_number, last_name=last_name)
        db.session.merge(new_entry)
        db.session.commit()

'''
In main we first get the current temperature and then create a new object that we can add to the database. 
'''
@app.route("/")
def main():
    return '''
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
        <html>
          <head>
            <link href="{{ url_for('static', filename='css/master.css') }}" rel="stylesheet" type="text/css" />
            <title>Automated Airline Check-in</title>
          </head>
          <body>
            <h3>Welcome to the Automated Airline Check-in</h3>
            <p>
              Please enter your Southwest flight details (confirmation number, last name). <br />
              Then click Add Reservation and 24-hours prior to your flight, check-in will automatically complete. <br />
              This ensures you get priority boarding which allows you the best seat selection and room for your luggage. <br />
            </p>
            <br />
            <form action="/add_reservation" method="POST">
              Confirmation Number: <input name="confirmation_number"> <br />
              Last Name: <input name="last_name"> <br />
              <input type="submit" value="Add Reservation">
            </form>
          </body>
        </html> 
     '''

@app.route("/add_reservation", methods=["POST"])
def process_reservation():
    confirmation_number = request.form.get("confirmation_number", "")
    last_name = request.form.get("last_name", "")

    add_reservation(confirmation_number, last_name)

    return '''
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
        <html>
          <head>
            <link href="{{ url_for('static', filename='css/master.css') }}" rel="stylesheet" type="text/css" />
            <title>Reservation Confirmation</title>
          </head>
          <body>
            <h3>Reservation has been added!</h3>
          </body>
        </html> 
     '''


if __name__ == '__main__':
   db.create_all()
   app.run(debug = True)

