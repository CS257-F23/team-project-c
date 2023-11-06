""" 
utils.py
Contains helper functions for routes defined in app.py 
10/30/2023
"""
from flask import render_template, render_template_string
import plotly.graph_objects as go

default_map_style = {
    'size':10, 
    'color':'#FEBF00',
    'map-type':'satellite-streets'
    }

def generate_map(coordinates, style=default_map_style):
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
                size=style['size'],
                color=style['color'],      
            ),
            name="Pipeline Spill"
        )
    )

    map.update_layout(
        mapbox_style=style['map-type'],
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
    outHTML = plotly_object.to_html(full_html=False, include_plotlyjs='cdn', div_id='plotlyjs-obj')
    return render_template_string(
        """ 
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>    
        {{ div_placeholder|safe }}
        """, 
        div_placeholder=outHTML)


def get_location_name(state, county, city):
    """
    Format a string to display a full locations' name
    Author: Henry

    Args:
        state (str): Name of state
        county (str): Name of county
        city (str): Name of county

    Returns:
        str: properly upper-cased string combining all inputs
    """
    if city == "" and county == "": 
        return state.upper()
    if city == "":
        return county.title() + " County, " + state.upper()
    if county == "":
        return city.title() + ", " + state.upper()
    return str(city.title() + ", " + county.title() + " County, " + state.upper())
