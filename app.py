from flask import Flask, render_template, request
from ProductionCode.pyspill import * 

app = Flask(__name__)

@app.route("/")
def homepage():
    """Homepage ("/")

    Returns:
        str: Homepage text 
    """
    return render_template("home.html")

#FEATURE 1: [/lookup/company], lookup spill data about companies
@app.route('/lookup/company/<input_name>', strict_slashes=False)
def company_page(input_name):
    """Show summary stats on a companies pipeline accidents

    Args:
        input_name (str): Name of company to get data on

    Returns:
        str: the HTML page ./template/lookupByCompany.html
    """    
    load_data()
    _data = lookup_company(input_name)
    return render_template('lookupByCompany.html', company_name=input_name, data=_data)

#FEATURE 2: [/lookup/location], lookup spill data about locations
@app.route('/lookup/location/<state>/', strict_slashes=False)
@app.route('/lookup/location/<state>/<county>', strict_slashes=False)
@app.route('/lookup/location/<state>/<county>/<city>', strict_slashes=False)
def location_page(state, county=None, city=None):
    """Show summary stats on a pipeline accidents in a location. Lookup can be by state/county, state/city or state/city/county.
    Author: Henry

    Args:
        state (str): Name of state to lookup
        county (str, optional): Name of county to lookup
        city (str, optional): Name of city to lookup 

        Returns:
            str: the HTML page ./template/lookupByLocation.html
    """ 
    

    state = empty_string_to_none(state)
    county = empty_string_to_none(county)
    city = empty_string_to_none(city)   

    _location_name = get_location_name(state, county, city)

    load_data()
    _data = lookup_by_location(city, county, state)
    return render_template('lookupByLocation.html', location_name=_location_name, data=_data)

@app.errorhandler(404)
def page_not_found(error):
    """
    Display the 404 error page with user submitted URL.

    Returns:
        str: the html page for 404 error.
    """
    return render_template('pageNotFound.html', url=request.url)

def empty_string_to_none(string):
    """Convert empty strings to None
    Author: Henry

    Args:
        string (str): string to convert

    Returns:
        (None OR str): returns original input if string is not empty, and None if input was was None or string is empty.
    """
    if string == " ":
        return None
    return string


def get_location_name(state, county, city):
    """Format a string to display a full locations' name
    Author: Henry

    Args:
        state (str): Name of state
        county (str): Name of county
        city (str): Name of county

    Returns:
        str: properly upper-cased string combining all inputs
    """

    if city is None and county is None: 
        return state.upper()
    if city is None:
        return county.title() + " County, " + state.upper()
    if county is None:
        return city.title() + ", " + state.upper()
    return str(city.title() + ", " + county.title() + " County, " + state.upper())


if __name__ == "__main__":
    app.run()
    main()

