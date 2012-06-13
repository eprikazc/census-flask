from flask import Flask, render_template
from json import dumps
from census import Census
import urllib
from lxml import etree

CENSUS_API_KEY = "5f838435cbb575e00bd0cd4318bd344580a526bc"
api_schema_str = urllib.urlopen("http://www.census.gov/developers/data/2010acs5_variables.xml").read()
api_schema = etree.fromstring(api_schema_str)
#race_data = api_schema.find()

app = Flask(__name__)

#    return "Hello"
@app.route("/")
def hello():
    c = Census(CENSUS_API_KEY)
    states = c.acs.state(("NAME",), "*")
    return render_template("index.html", states = states)

@app.route("/counties/<state_id>")
def get_counties(state_id):
    c = Census(CENSUS_API_KEY)
    counties = c.acs.state_county(("NAME",), state_id, "*")
    return dumps(counties)

@app.route("/stat/<state_id>/<county_id>")
def get_statistics_for_county(state_id, county_id):
    c = Census(CENSUS_API_KEY)
    statistics = c.acs.state_county(("NAME", "B25034_002E", "B25034_003E"), state_id, county_id)
    return dumps(statistics)


if __name__ == "__main__":
    app.run(debug=True)