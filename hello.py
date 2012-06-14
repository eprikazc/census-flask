from flask import Flask, render_template
from json import dumps
from census import Census
import urllib
from xml.etree import ElementTree

CENSUS_API_KEY = "5f838435cbb575e00bd0cd4318bd344580a526bc"
api_schema_str = urllib.urlopen("http://www.census.gov/developers/data/2010acs5_variables.xml").read()
api_schema = ElementTree.fromstring(api_schema_str)

api_params = {}
for concept_elem in api_schema.findall("concept"):
    concept_name = concept_elem.attrib['name'].split(". ")[-1].strip()
    api_params[concept_name] = {}
    for index, variable in enumerate(concept_elem.findall("variable")):
        api_params[concept_name][variable.attrib["name"]] = (index, variable.text)

app = Flask(__name__)

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

@app.route("/stat")
def get_statistics_types():
    return dumps(api_params.keys())

@app.route("/stat/<state_id>/<county_id>/<statistic_type>")
def get_statistics_for_county(state_id, county_id, statistic_type):
    c = Census(CENSUS_API_KEY)
    res = []
    for i in range(0, len(api_params[statistic_type].keys()), 5):
        j = min(len(api_params[statistic_type].keys()), i+5)
        part_res = c.acs.state_county(
            tuple(api_params[statistic_type].keys()[i:j]),
            state_id,
            county_id
        )[0]
        for key, value in part_res.items():
            if key in ("county", "state"):
                continue
            res.append([api_params[statistic_type][key][0], api_params[statistic_type][key][1], value])
    res = sorted(res, key=lambda elem: elem[0])
    return dumps(res)


if __name__ == "__main__":
    app.run(debug=True)