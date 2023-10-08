from flask import Flask, render_template
from ProductionCode.pyspill import * 



app = Flask(__name__)

@app.route("/")
def homepage():
    """Homepage ("/")

    Returns:
        str: Homepage text 
    """
    return "welcome to PySpill"

@app.route('/<input_name>', strict_slashes=False)
def company(input_name):
    """Show summary stats on a companies pipeline accidents, formatted in HTML string

    Args:
        input_name (str): Name of company to get data on

            Returns:
        str: simple HTML that displays the data
    """    
    load_data()
    _data = lookup_company(input_name)
    return render_template('lookupByCompany.html', company_name=input_name, data=_data)

if __name__ == "__main__":
    app.run()
    main()

