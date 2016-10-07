"""
Very simple Flask web site, with one page
displaying a course schedule.

"""

import flask
from flask import render_template
from flask import request
from flask import url_for

import json
import logging

# Date handling
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
from dateutil import tz  # For interpreting local times

# Our own module
import pre  # Preprocess schedule file


###
# Globals
###
app = flask.Flask(__name__)
import CONFIG


###
# Pages
###

@app.route("/")
@app.route("/index")
@app.route("/schedule")
def index():
  app.logger.debug("Main page entry")
  if 'schedule' not in flask.session:
      app.logger.debug("Processing raw schedule file")
      raw = open(CONFIG.schedule)
      flask.session['schedule'] = pre.process(raw)

  return flask.render_template('syllabus.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] =  flask.url_for("index")
    return flask.render_template('page_not_found.html'), 404

#################
#
# Functions used within the templates
#
#################

#
@app.context_processor
def the_date():
    '''
    Get the current date
    '''
    current = arrow.utcnow()
    return dict(date=current)

@app.context_processor
def compare_date():
    '''
    pass compare_date as a function to flask
    '''
    def compare_date(firstDate, secondDate):
        '''
        Compare two date arguments passed in the html
        '''
        firstDate = arrow.get( firstDate )
        secondDate = arrow.get( secondDate)
        if firstDate.week == secondDate.week:
            return True
        else:
            return False
    return dict(compare_date=compare_date)


@app.template_filter( 'fmtdate' )
def format_arrow_date( date ):
    try:
        normal = arrow.get( date )
        return normal.format("ddd MM/DD/YYYY")
    except:
        return "(bad date)"

@app.context_processor
def inc_date():
    '''
    Pass inc_date as a function to flask
    '''
    def increment_date( date, n ):
        '''
        Takes a date and an integer argument and increments
        the the date by n weeks
        '''
        try:
            i = int(n)
            i -= 1
            normal = arrow.get(date)
            return normal.replace(weeks=+i)
        except:
            return "(b-bad date)"
    return dict(inc_date=increment_date)


#############
#
# Set up to run from cgi-bin script, from
# gunicorn, or stand-alone.
#
app.secret_key = CONFIG.secret_key
app.debug=CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)
if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
