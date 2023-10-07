import sys
import csv
from argparse import ArgumentParser

data = []
headers = []

def load_data():
    """ Read data from the CSV file and load it into the data and headers global variables. """
    rows = []
    with open('Data/OilPipelineAccidents.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            rows.append(row)

    global data
    data = rows

    global headers
    headers = data[0]

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
        city = city.upper()
    if county:
        county = county.upper()
    if state:
        state = state.upper()

    if city: 
        return lookup_by_city(city, county, state)
    if county:
        return lookup_state_or_county(county, 13)
    if state:
        return lookup_state_or_county(state, 14)


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

# TODO: when all three parameters are specified, should not look up by county OR state.
# instead, look up by county AND state
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
    """ 
    Print the help and usage statement to the command line. 
    Author: James Commons
    """

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
          '                                If no county or city is specified, all spills in the state are shown.\n'
          '                                If state is specified, it must be the two letter abbreviation (i.e. CO).\n\n'
          'help                            Print this message.\n')
    
def print_lookup_data(data):
    """ 
    Print the data. For now just simply prints the data object. 
    Author: James Commons
    """
    print(data)

def parse_lookup_command(options):
    """ 
    Given options, determine which lookup function to call and pass it require arguments. 
    Author: James Commons
    """ 
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
    """ 
    Takes in the argv list as an argument and calls appropriate function based on command. 
    Author: James Commons
    """
    if len(argv) == 1:
        print_help_statement()
    elif argv[1] == 'help':
        print_help_statement()
    elif argv[1] == 'lookup':
        try:
            parse_lookup_command(argv[2:])
        except IndexError as e:
            print('Arguments after options must be in quotes if it contains whitespace.')
            print(e) # Print error in case the issue had nothing to do with quotes
            return
    else:
        print_help_statement()

def get_main_parser() -> ArgumentParser:
    """ 
    Setup and return the main parser object, which is responsible for parsing the entire command. 

    Returns: 
        ArgumentParser: the parser object.
    """
    return ArgumentParser( 
                description='PySpill is an application to look up statistics about ' 
                            'oil pipeline accidents in the United States. Use this '
                            'program to lookup information by company or location, '
                            'and checkout our leaderboard feature, where we call out '
                            'the worst offenders.',
                epilog='Authors: Henry Burkhardt, Paul Claudel Izabayo, '
                        'Feraidon Abdul Rahimzai, James Commons'
            )

def get_leaders_subparser(subparsers: ArgumentParser) -> ArgumentParser:
    """ 
    Add the leaders subparser to the subparsers object.

    Args:
        subparsers (ArgumentParser): the subparser object attatched to the main parser.

    Returns:
        ArgumentParser: the modified subparser object.
    """
    parser_leaders = subparsers.add_parser('leaders', 
            help='list the top 10 worst polluters by state OR company')
    
    # Allow user to list top ten in a certain category
    mutex_group_leaders_by = parser_leaders.add_mutually_exclusive_group(required=True)
    mutex_group_leaders_by.add_argument('-n', '--number', action='store_true',
            help='list the top 10 polluters by total number of spills')
    mutex_group_leaders_by.add_argument('-a', '--amount', action='store_true',
            help='list the top 10 polluters by total volume of oil released')
    mutex_group_leaders_by.add_argument('-p', '--price', action='store_true',
            help='list the top 10 polluters by total cost of pipeline accidents')
    
    # Do not allow user to list both locations and companies
    mutex_group_leaders_type = parser_leaders.add_mutually_exclusive_group(required=True)
    mutex_group_leaders_type.add_argument('-c', '--company', action='store_true',
            help='list the top 10 companies')
    mutex_group_leaders_type.add_argument('-s', '--state', action='store_true',
            help='list the top 10 states')
    
    return subparsers

def get_list_subparser(subparsers: ArgumentParser) -> ArgumentParser:
    """
    Add the list subparser to the subparsers object.

    Args:
        subparsers (ArgumentParser): the subparser object attatched to the main parser.

    Returns:
        ArgumentParser: the modified subparser object.
    """
    parser_list = subparsers.add_parser('list',
            help='list information about the data set')
    
    # Do not allow user to list both a location and company
    mutex_group = parser_list.add_mutually_exclusive_group(required=True)
    mutex_group.add_argument('-c', '--company', action='store_true', 
            help='list all companies in the dataset')
    mutex_group.add_argument('-l', '--location', action='store_true',
            help='list all locations in the dataset')
    mutex_group.add_argument('-s', '--state', 
            help='list all cities, counties, and companies in a given state. ' 
                 'Must be a two letter abbreviation (i.e. CO)')
    
    return subparsers

def get_lookup_subparser(subparsers: ArgumentParser) -> ArgumentParser:
    """ 
    Add the lookup subparser to the subparsers object.

    Args:
        subparsers (ArgumentParser): the subparser object attatched to the main parser.

    Returns:
        ArgumentParser: the modified subparser object.
    """
    parser_lookup = subparsers.add_parser('lookup', 
            help='look up information about pipeline accidents by location OR company')
    
    # Do not allow user to lookup by both location and company
    mutex_group = parser_lookup.add_mutually_exclusive_group(required=True)
    mutex_group.add_argument('-c', '--company', help='specifies the company to lookup by')
    mutex_group.add_argument('-l', '--location', action='store_true', 
            help='flag indicating you want to look up by location')
    location_args_group = parser_lookup.add_argument_group(title='available location options')
    location_args_group.add_argument('--city')
    location_args_group.add_argument('--county')
    location_args_group.add_argument('--state', help='must be a two letter abbreviation (i.e. CO)')

    return subparsers

def setup_subparsers(main_parser: ArgumentParser) -> ArgumentParser:
    """ 
    Add subparsers for each subcommand in PySpill (i.e. lookup, help, list, etc.).

    Args:
        main_parser (ArgumentParser): the object responsible for handling the entire command.

    Returns: 
        ArgumentParser: the modified parser with subcommands added.
    """
    subparsers = main_parser.add_subparsers(title='available subcommands')
    subparsers.add_parser('help', help='print the help message and exit')
    subparsers = get_lookup_subparser(subparsers)
    subparsers = get_list_subparser(subparsers)
    subparsers = get_leaders_subparser(subparsers)
    
    return main_parser

def main():
    load_data()
    parser = setup_subparsers(get_main_parser())

    if len(sys.argv) == 1: # User did not provide any command line arguments
        parser.print_usage()
        return
    
    args = parser.parse_args()

if __name__ == '__main__':
    main()
