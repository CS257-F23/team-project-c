from ProductionCode.data_accessor import DataAccessor 
from flask import Flask, render_template, request, redirect, render_template_string
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
        str: HTML from /templates/search_by_company/form.html
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

@app.errorhandler(404)
def page_not_found(error):
    """
    Display the 404 error page with user submitted URL.

    Returns:
        str: the html page for 404 error.
    """
    return render_template('page-not-found.html')

@app.route("/search-by-location")
def search_by_location():
    """Render search by location form @ [/search-by-location]
    Author: Henry

    -- NOT YET BUILT -- 
    """
    return ""

@app.route("/leaderboard")
def leaderboard():
    """Render ranked list of companies @ [/leaderboard]
    Author: Henry

    -- NOT YET BUILT -- 
    """
    return 

@app.route("/map")
def map():
    """Render big map of all spills in the database @ [/map]
    Author: Henry

    -- NOT YET BUILT -- 
    """
    return ""

@app.route("/about")
def about():
    """Render about page @ [/about]
    Author: Henry

    -- NOT YET BUILT -- 
    """
    return ""

# HELPER FUNCTIONS --> all of these can probably be moved to another "middleware" file for clarity later -Henry 

def generate_map(coordinates):
    """Create Plotly Scattermapbox figure object with points for a list of coordinates
    Author: Henry 

    This function uses the Plotly library, for reference see https://plotly.com/python/scattermapbox/

    Args:
        coordinates (list of list): nested list of coordinates to display in format:
                                    [[lat_1, long_1], [lat_2, long_2], ... , [lat_n, long_n]]

    Returns:
        str: an HTML string with the map object (displayed in a <canvas> tag in HTML)
    """    
    mapbox_access_token = "pk.eyJ1IjoiYnVya2hhcmR0aCIsImEiOiJjbG5ydXUwOTIwdTJyMmtvMXVpZzFqdzg5In0.kUE_ksbHTedhgtgR7f8YVg"

    map = go.Figure(go.Scattermapbox(
            lat=[pair[0] for pair in coordinates], # gets only the latitude from lat/lon pairs 
            lon=[pair[1] for pair in coordinates], # gets only the longitude from lat/lon pairs   
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=10,
                # opacity=0.7,
                color='#FEBF00',

            ),
            name="Pipeline Spill"
        ), 
       )

    map.update_layout(
        mapbox_style="satellite",
        hovermode='closest',
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        geo_scope='usa',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,  
            center=go.layout.mapbox.Center(
                lat=39,
                lon=-98
            ),
            pitch=0,
            zoom=3
        )
    )
    return plotly_object_to_html(map)

                                    
def plotly_object_to_html(plotly_object):
    """Convert Plotly object to HTML that can be rendered in browser
    Author: Henry

    Args:
        plotly_object (Plotly.graph_objects.Figure): Plotly object (a map figure)

    Returns:
        str: An HTML string representing the object
    """    
    outHTML = plotly_object.to_html(full_html=False)
    return render_template_string(
        """ 
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>    
        {{ div_placeholder|safe }}
        """, 
        div_placeholder=outHTML)

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

if __name__ == '__main__':
    app.run()

