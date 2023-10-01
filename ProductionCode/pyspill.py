import json
import csv

# we wan delete this sample data later, but it will make things easier while we wait for the load_data() function to be built
sample_data = [ 
    # header row
    ['Report Number', 'Supplemental Number', 'Accident Year', 'Accident Date/Time', 'Operator ID', 'Operator Name', 'Pipeline/Facility Name', 'Pipeline Location', 'Pipeline Type', 'Liquid Type', 'Liquid Subtype', 'Liquid Name', 'Accident City', 'Accident County', 'Accident State', 'Accident Latitude', 'Accident Longitude', 'Cause Category', 'Cause Subcategory', 'Unintentional Release (Barrels)', 'Intentional Release (Barrels)', 'Liquid Recovery (Barrels)', 'Net Loss (Barrels)', 'Liquid Ignition', 'Liquid Explosion', 'Pipeline Shutdown', 'Shutdown Date/Time', 'Restart Date/Time', 'Public Evacuations', 'Operator Employee Injuries', 'Operator Contractor Injuries', 'Emergency Responder Injuries', 'Other Injuries', 'Public Injuries', 'All Injuries', 'Operator Employee Fatalities', 'Operator Contractor Fatalities', 'Emergency Responder Fatalities', 'Other Fatalities', 'Public Fatalities', 'All Fatalities', 'Property Damage Costs', 'Lost Commodity Costs', 'Public/Private Property Damage Costs', 'Emergency Response Costs', 'Environmental Remediation Costs', 'Other Costs', 'All Costs'], 
  
    # sample data row 1
    ['20100016', '17305', '2010', '1/1/2010 7:15 AM', '32109', 'ONEOK NGL PIPELINE LP', 'KINDER MORGAN JCT', 'ONSHORE', 'ABOVEGROUND', 'HVL OR OTHER FLAMMABLE OR TOXIC FLUID, GAS', 'LPG (LIQUEFIED PETROLEUM GAS) / NGL (NATURAL GAS LIQUID)', '', 'MCPHERSON', 'MCPHERSON', 'KS', '38.6707', '-97.78123', 'INCORRECT OPERATION', 'PIPELINE/EQUIPMENT OVERPRESSURED', '21', '0.1', '0', '21', 'NO', 'NO', 'NO', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '110', '1517', '0', '0', '0', '0', '1627'],
   
    # sample data row 2
    ['20100254', '17331', '2010', '1/4/2010 8:30 AM', '15786', 'PORTLAND PIPELINE CORP', '24-INCH MAIN LINE', 'ONSHORE', 'ABOVEGROUND', 'CRUDE OIL', '', '', 'RAYMOND', 'CUMBERLAND', 'ME', '43.94028', '-70.49336', 'MATERIAL/WELD/EQUIP FAILURE', 'PUMP OR PUMP-RELATED EQUIPMENT', '0.12', '0', '0.12', '0', 'NO', 'NO', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '4000', '8', '0', '0', '0', '0', '4008']
]

headers = sample_data[0]

def load_data():
    rows = []
    with open('Data/OilPipelineAccidents.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            rows.append(row)
    return rows

def lookup_company(company):
    """
    Return a dictionary with summary statistics about all accidents involving the given company.
    Author: Henry
    """
     
    indexOfOperatorName = headers.index("Operator Name")
    relevant_rows = [accident for accident in sample_data if accident[indexOfOperatorName].lower() == company.lower()]
    return get_summary_stats(relevant_rows)

def get_summary_stats(rows):
    """
    Calculate summary statistics for a list of oil spill accidents.
    Author: Henry
    """
    accidentCount = len(rows)
    if accidentCount > 0:
        totalUnintentionalRelease = 0 
        totalNetLoss = 0
        totalCosts = 0

        for accident in rows:
            totalUnintentionalRelease += get_numeric_value(headers, accident, "Unintentional Release (Barrels)")
            totalNetLoss += get_numeric_value(headers, accident, "Net Loss (Barrels)")
            totalCosts += get_numeric_value(headers, accident, "All Costs")
        
        return {'accidentCount': accidentCount, 
                'totalUnintentionalRelease':totalUnintentionalRelease, 
                'totalNetLoss': totalNetLoss, 
                'totalCosts' : totalCosts
                } 
    else:
        return None

def get_numeric_value(headers, row, column_name):
    """
    Given a list of headers, a row of data, and a column name, returns the value in the specified column as a float.
    Author: Henry
    """
    
    index = headers.index(column_name)
    return float(row[index])
      
def lookup_by_location(city, county, state):
    
    """
    Author: Paul Claudel Izabayo
    Given a city, a county and a state, returns the total number of spills 
    as well as the total cost of all the spills that have happened in that city,
    in that county and in that state. 
    If the location (city, county, state) does not exist in the database, 
    return 0 for both the number of spills and their cost. 
    """
    city_data = lookup_by_city(city)
    county_data = lookup_by_county(county)
    state_data = lookup_by_state(state)

    return {        
        "city_spills": city_data["total_spills"],
        "city_costs": city_data["total_cost"],
        "county_spills": county_data["total_spills"],
        "county_costs": county_data["county_cost"],
        "state_spills": state_data["total_spills"], 
        "state_costs": state_data["total_cost"]
    }

def iterate_through_dataset(area_typ, col_index):
    """
    Author: Paul Claudel Izabayo
    This helper method allows you to iterate through the colums. 
    """

    total_spills = 0
    total_cost = 0
    raw_data = load_data()

    for i in range (1, len(raw_data)):
        if area_typ == raw_data[i][col_index]:
            total_spills = total_spills + 1
            total_cost = total_cost + raw_data[i][-1]

    return {
        "total_cost":total_cost, 
        "total_spills":total_spills
    }

def lookup_by_state(state):

    """
    Author: Paul Claudel Izabayo
    Given a state, return the total number of spills that have happened in that state, 
    as well as their total monetary cost. 
    """
    return iterate_through_dataset(state, 14)

    
def lookup_by_county(county):

    """
    Author: Paul Claudel Izabayo
    Given a state, return the total  number of spills that have happened in that county, 
    as well as ther total monetary cost. 
    """
    return iterate_through_dataset(county, 13)

def lookup_by_city(city):
    
    """
    Author: Paul Claudel Izabayo
    Given a city, return the total number of spills that have occured in that city, 
    as well as their monetary cost. 
    
    """
    return iterate_through_dataset(city, 12)

def parse_lookup_command(options):
    """ Given options, determine which lookup function to call and pass it require arguments. """
    
    parameters = options[::2]
    arguments = options[1::2]
    location_options = {
        'city': None,
        'county': None,
        'state': None
    }
    company = None
    
    for i, param in enumerate(parameters):
        if param == '--city':
            location_options['city'] = arguments[i]
        elif param == '--county':
            location_options['county'] = arguments[i]
        elif param == '--state':
            location_options['state'] = arguments[i]
        elif param == '--company' or '-c':
            company = arguments[i]
        else:
            print_help_statement()
            return

    location_args = list(location_options.values())
    location_options_is_empty = location_args.count(None) != len(location_args)

    if company != None and location_options_is_empty:
        print('You can only lookup by location or company, not both at the same time.')
        return
    
    if company != None:
        print(lookup_company(company))
    
    if not location_options_is_empty:
        lookup_by_location(location_options['city'], location_options['county'], location_options['state'])

def parse_argv(argv):
    """ Takes in the argv list as an argument and calls appropriate function based on command. """

    if len(argv) == 1:
        print_help_statement()
    elif argv[1] == 'help':
        print_help_statement()
    elif argv[1] == 'lookup':
        parse_lookup_command(argv[2:])
    else:
        print_help_statement()

def main():
    parse_argv(sys.argv)

if __name__ == '__main__':
    main()
