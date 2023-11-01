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

    company_data = data.lookup_company(company_name)
    company_spill_coordinates = data.get_company_spill_coordinates(company_name)
    map_html = generate_map(company_spill_coordinates)
    return render_template("/search-by-company/results.html", data=company_data, company_name=company_name, mapHTML=map_html)

@app.route("/search-by-location")
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
    location_data = data.lookup_by_location(city_name, county_name, state_name)
    if location_data == None:
        flash("The location you entered was not found in our database. Try searching the whole state.")
        return redirect("/search-by-location")

        

    location_spill_coordinates = data.get_location_spill_coordinates(city_name, county_name, state_name)
    map_html = generate_map(location_spill_coordinates)
    return render_template("/search-by-location/results.html", data=location_data, 
                           location_name=get_location_name(state_name, county_name, city_name), 
                           mapHTML=map_html)


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


@app.route("/leaderboard")
def leaderboard():
    """Render ranked list of companies @ [/leaderboard]
    Author: Henry

    -- NOT YET BUILT -- 
    """
    return "Not yet implemented"


@app.route("/map")
def map():
    """Render big map of all spills in the database @ [/map]
    Author: Henry

    -- NOT YET BUILT -- 
    """
    return "Not yet implemented"


@app.route("/about")
def about():
    """ Render about page @ [/about] """
    return render_template('about.html')

@app.route("/test")
def test ():
    return str(data.lookup_by_location("", "Rice", "MN"))

if __name__ == '__main__':
    app.secret_key = 'i promise we really need this or else the app doesnt work. trust me.'
    app.run(host='0.0.0.0', port=5015, debug=True)

