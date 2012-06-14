from flask import Flask, render_template
from json import dumps
from census import Census
import urllib
from xml.etree import ElementTree

CENSUS_API_KEY = "5f838435cbb575e00bd0cd4318bd344580a526bc"
api_schema_str = urllib.urlopen("http://www.census.gov/developers/data/2010acs5_variables.xml").read()
api_schema = ElementTree.fromstring(api_schema_str)

variables = []
api_params = {}
for concept_elem in api_schema.findall("concept"):
    concept_name = concept_elem.attrib['name'].split(". ")[-1].strip()
    api_params[concept_name] = {}
    for variable in concept_elem.findall("variable"):
        api_params[concept_name][variable.attrib["name"]] = variable.text
        variables.append(variable.attrib["name"])
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
    res = {}
    for concept, params in api_params.items():
        if concept not in ("Race", "Household Income"):
            continue
        res[concept] = c.acs.state_county(tuple(params.keys()), state_id, county_id)
    return dumps(res)


if __name__ == "__main__":
    app.run(debug=True)