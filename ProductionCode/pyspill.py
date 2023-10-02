import json
import csv
import sys

data = []
headers = []

def load_data():
    rows = []
    with open('Data/OilPipelineAccidents.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            rows.append(row)

    global data
    data = rows

    global headers
    headers = data[0]

    return

def lookup_company(company):
    """
    Return a dictionary with summary statistics about all accidents involving the given company.
    Author: Henry
    """
     
    indexOfOperatorName = headers.index("Operator Name")
    relevant_rows = [accident for accident in data if accident[indexOfOperatorName].lower() == company.lower()]
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
    Given a city, county and/or state return the number of spills that happened in that city (county/state)
    as well as their monetary value. If there is not city, we return the number of spills in the state, 
    as well as their monetary value and if there neither the city nor a state, we return the number 
    of spills in the county as well as their monetary value. 
    
    """
    if city: 
        return lookup_by_city(city.upper(), county.upper(), state.upper())
    if county:
        return lookup_state_or_county(county.upper(), 13)
    if state:
        return lookup_state_or_county(state.upper(), 14)


def lookup_state_or_county (locat_typ, col_ind):
    """
    Given a location type i.e state or county or state as well as it column inde in the dataset, 
    this helper method returns a dictionary containing the number of spills in that state/state/county as well as their monetary value. 
    """
    total_spills = 0
    total_cost = 0

    for row_index in range (1,len(data)):
        if locat_typ == data[row_index][col_ind]:
            total_spills = total_spills + 1
            total_cost = total_cost + float (data[row_index][-1])

    return {
        "total_spills": total_spills,
        "total_cost": total_cost
    }

def lookup_by_city(city, county, state):
    """
    Given a city, a county and a state this methods returns the number of spills in that city and their total monetary cost
    if the city entered is located in the state or the county specified.  
    """
    total_spills = 0
    total_cost = 0
    for row_index in range (1, len(data)):
        curr_row = data[row_index]
        if city == curr_row[12] and (county == curr_row[13] or state == curr_row[14]):
            total_cost = total_cost + float(curr_row[-1])
            total_spills = total_spills+1

    return {
        "total_spills": total_spills,
        "total_cost": total_cost
    }

  

def print_help_statement():
    """ Print the help and usage statement to the command line. """

    print('Usage: python3 pyspill.py <command> [options]\n\n'\
          'Commands:\n\n'\
          'lookup                          Look up information about pipeline accidents by location or company.\n'\
          '  Options:\n'
          '    To look up by company:\n'
          '    -c --company                Specify the company.\n\n'
          '    To look up by location:\n'
          '    --city, --county, --state   Specify the location.\n'
          '                                If the city is specified, a county or state must also be specified.\n'
          '                                If no city is specified, all spills in the county are shown.\n'
          '                                If no county or city is specified, all spills in the state are shown.\n\n'
          'help                            Print this message.\n')
    
def print_lookup_data(data):
    """ Print the data. For now just simply prints the data object. """

    print(data)

def parse_lookup_command(options: list):
    """ Given options, determine which lookup function to call and pass it require arguments. """
    
    parameters = options[0::2]
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
    location_options_is_empty = location_args.count(None) == len(location_args)

    if company != None and not location_options_is_empty:
        print('You can only lookup by location or company, not both at the same time.')
        return
    
    if company != None:
        print_lookup_data(lookup_company(company))
    
    if not location_options_is_empty:
        print_lookup_data(
            lookup_by_location(
                location_options['city'], 
                location_options['county'], 
                location_options['state']
            )
        )
        
def parse_argv(argv):
    """ Takes in the argv list as an argument and calls appropriate function based on command. """

    if len(argv) == 1:
        print_help_statement()
    elif argv[1] == 'help':
        print_help_statement()
    elif argv[1] == 'lookup':
        try:
            parse_lookup_command(argv[2:])
        except IndexError as e:
            print('Remember arguments after options must be in quotes if it contains whitespace.')
            print(e)
    else:
        print_help_statement()

def main():
    load_data()
    parse_argv(sys.argv)

if __name__ == '__main__':
    main()
