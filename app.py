from ProductionCode.data_accessor import DataAccessor 
from ProductionCode.utils import *
from flask import Flask, render_template, request, redirect, render_template_string, flash
import plotly.graph_objects as go


app = Flask(__name__)
data = DataAccessor(csv_path='Data/OilPipelineAccidents.csv')


@app.route("/")
def homepage():
    """Render homepage @ [/]
    Author: Henry 

    Returns: 
        str: HTML from /templates/home.html    
    """
    return render_template("home.html")


@app.route("/search-by-company")
def search_by_company():
    """Render search by company form @ [/search-by-company]
    Author: Henry

    Includes drop down list and search box with autocomplete. 

    Returns:
        str: HTML from /templates/search-by-company/form.html
    """
    return render_template("/search-by-company/form.html", rows=data.get_list_of_companies())


@app.route("/search-by-company/results", methods=['GET'])
def search_by_company_results():
    """Render company results page @ [/search-by-company/results]
    Author: Henry

    HTTP Request Args:
        company-name (str): name of company to get results for

    Returns:
        str: HTML from /template/search-by-company/results.html
    """

    company_name = ""

    # this logic is needed because of how the HTTP params from my form get auto completed
    # it prevents errors about HTTP args not existing
    if 'company-name-dropdown' in request.args:
        company_name = request.args['company-name-dropdown']
    elif 'company-name-search' in request.args:
        if request.args['company-name-search'] == "" and 'company-name-dropdown' not in request.args:
            return redirect("/search-by-company")
        company_name = request.args['company-name-search']
    
    try:
        company_data = data.lookup_company(company_name)
    except ValueError:
        return redirect("/search-by-company/bad-input")
    
    company_spill_coordinates = data.get_company_spill_coordinates(company_name)
    map_html = generate_map(company_spill_coordinates, style={'size':8, 'color':'red', 'map-type':'satellite'})
    return render_template("/search-by-company/results.html", data=company_data, company_name=company_name, mapHTML=map_html)


@app.route("/search-by-company/bad-input", strict_slashes=False)
def search_by_company_bad_input():
   """ 
    Returns the search by location page with an added error message 
    directing the user to input a correct location. 
    """
   return render_template("/search-by-company/form.html", bad_input=True, rows=data.get_list_of_companies())


@app.route("/search-by-location", strict_slashes=False)
def search_by_location():
    """Render search by location search page  @ [/search-by-location/]
    Author: Henry

    Returns: 
        str: HTML page @ /templates/search-by-location/form.html
    """
    return render_template("/search-by-location/form.html")


@app.route("/search-by-location/results", methods=['GET'])
def search_by_location_results():
    """Render search by location results page from @ [/search-by-location/results]
    Author: Henry

        Returns: 
            str: HTML page @ /templates/search-by-location/results.html
    """
    state_name = request.args["state-search"]
    county_name = request.args["county-search"]
    city_name = request.args["city-search"]

    # this try/catch block makes sure that the location_data provided is valid. 
    # the method that chahnges full state names to abreviations is in the data_accessor.py files - Henry 
    try:
        location_data = data.lookup_by_location(city_name, county_name, state_name)
    except ValueError:
        return redirect("/search-by-location/bad-input")
    
    if len(state_name) != 2:
        state_name = data.get_state_abbreviation_from_name(state_name)
    
    location_spill_coordinates = data.get_location_spill_coordinates(city_name, county_name, state_name)
    map_html = generate_map(location_spill_coordinates, style={'size':8, 'color':'red', 'map-type':'satellite'})
    return render_template("/search-by-location/results.html", data=location_data, 
                           location_name=get_location_name(state_name, county_name, city_name), 
                           mapHTML=map_html)


@app.route("/search-by-location/bad-input", strict_slashes=False)
def search_by_location_bad_input():
    """ 
    Returns the search by location page with an added error message 
    directing the user to input a correct location. 
    """
    return render_template("/search-by-location/form.html", bad_input=True)


@app.route("/spillinfo/<latitude>/<longitude>", strict_slashes=False)
def spillinfo(latitude, longitude):
    """ 
    A page that lists all available information about an oil spill at a 
    particular location.

    Args:
        latitude
        longitude
    """
    return render_template("spillinfo.html", 
                           lat=latitude, 
                           lon= longitude, 
                           data=data.get_spill_data_by_location(latitude, longitude),
                           mapHTML=generate_map([(latitude, longitude)], style={
                                'size':8, 'color':'red','map-type':'satellite-streets'
                           })
                          )


@app.route("/leaderboard")
def leaderboard():
    """Render ranked list of companies @ [/leaderboard]
    """
    return render_template("leaderboard.html", leaders=data.get_leaders())


# TODO: frontend. Backend is done. Just call data.get_all_spill_coordinates()
@app.route("/map")
def map():
    """Render big map of all spills in the database @ [/map]
    """
    coordinates = data.get_all_spill_coordinates()
    map_html = generate_map(coordinates, {'size':4, 'color':'red', 'map-type':'dark'})
    return render_template('map.html', mapHTML=map_html)


@app.route("/about")
def about():
    """ Render about page @ [/about] """
    return render_template('about.html')


@app.errorhandler(404)
def page_not_found(error):
    """
    Display the 404 error page with user submitted URL.

    Returns:
        str: the html page for 404 error.
    """
    return render_template('page-not-found.html')


@app.errorhandler(500)
def internal_error(error):
    """
    Display the 500 error page with user caused an error. Yes it's the user's fault. 

    Returns:
        str: the html page for 505 error.
    """
    return render_template('internal-error.html', error=error)


if __name__ == '__main__':

    # IN GENERAL DO NOT JUST RUN THIS FILE. USE THE COMMAND:
    # flask --app app.py run --host 0.0.0.0 --port <YOURPORTNUMBER>
    app.run(host='0.0.0.0', port=5015)

