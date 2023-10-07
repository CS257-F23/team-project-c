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

def get_index_of(column_name):
    return headers.index(column_name)

def get_numeric_value(row, column_name):
    """
    Given a list of headers, a row of data, and a column name, returns the value in the specified column as a float.
    Author: Henry Burkhardt

    Args:
        headers (list): list of strings indicating column names 
        row (list): a single row from the dataset
        column_name (str): name of column to extract data from

    Returns:
        float: numeric value to extract
    """    
    
    index = get_index_of(column_name)
    return float(row[index])


def select_matching_rows(rules):
    """
    Subset rows from database based with string matching
    Author: Henry Burkhardt

    Pass an array of doubles (in the format below) to extract data from dataset by string matching columns.

    Args: 
        criteria (list of double): [(<column_name>, <string_to_match>), ...]
    """
    selected_rows = []
    for row in data:
        matches = []
        for rule in rules:
            columnIndex = get_index_of(rule[0])
            matches.append(row[columnIndex].upper().strip() == rule[1].upper().strip())

        if all(matches):
            selected_rows.append(row)
    return selected_rows


def get_totals(rows):
    """
    Calculate summary statistics for a list of oil spill accidents by summing columns.
    Author: Henry Burkhardt

    Args:
        rows (list): list of selected rows from the table

    Returns:
        dict: dictionary with, accidentCount, totalUnintentionalRelease, totalNetLoss and totalCosts
    """   

    accidentCount = len(rows)
    if accidentCount > 0:
        totalUnintentionalRelease = 0 
        totalNetLoss = 0
        totalCosts = 0

        for row in rows:
            totalUnintentionalRelease += get_numeric_value(row, "Unintentional Release (Barrels)")
            totalNetLoss += get_numeric_value(row, "Net Loss (Barrels)")
            totalCosts += get_numeric_value(row, "All Costs")
        
        return {'accidentCount': accidentCount, 
                'totalUnintentionalRelease':totalUnintentionalRelease, 
                'totalNetLoss': totalNetLoss, 
                'totalCosts' : totalCosts
                } 
    return None

def print_totals(totals: any):
    """ 
    Prints the totals dictionary from get_totals() in a user friendly way. 
    
    Args:
        totals (any): the totals dictionary to print to the terminal.
    """
    if not totals:
        print('No spills associated with lookup query')
        return
    
    print(f'Total accidents: {totals["accidentCount"]:,}')
    print(f'Total volume of oil released (barrels): {totals["totalNetLoss"]:,.2f}')
    print(f'Total cost: ${int(totals["totalCosts"]):,}')

def lookup_company(company):
    """
    Return a dictionary with summary statistics about all accidents involving the given company.
    Author: Henry Burkhardt

    Args:
        company (str): name of company (must be in dataset)

    Returns:
        dict: dictionary of summary data on company, from get_summary_stats()
    """    
    relevant_rows = select_matching_rows([("Operator Name", company)])
    return get_totals(relevant_rows)

      
def lookup_by_location(city, county, state): 
    """
    Get info about spills in a give city, county or state. 
    Author: Paul Claudel Izabayo

    Args:
        city (str): name of city
        county (str): name of county
        state (str): name of state
    """

    # Ensure state argument was passed
    if state is None: 
        raise ValueError("State argument is required for all location queries.") 

    if city is not None:
        return lookup_by_city(city, state)
    
    if county is not None: 
        return lookup_by_county(county, state)
    
    if state is not None:
        return lookup_by_state(state)
    
    return ValueError("Not enough enough information was provided to complete your query.")
    

def lookup_by_city(city, state):
    """Returns total spill stats for a city

    Args:
        city (str): name of city
        state (str): name of state

    Returns:
        dict: contains summary info from get_totals()
    """
    selected_rows = select_matching_rows([("Accident City", city), ("Accident State", state)])
    return get_totals(selected_rows)


def lookup_by_county(county, state):
    """Returns total spill stats for a county

    Args:
        county (str): name of county
        state (str): name of state

    Returns:
        dict: contains summary info from get_totals()
    """
    
    selected_rows = select_matching_rows([("Accident County", county), ("Accident State", state)])
    return get_totals(selected_rows)


def lookup_by_state(state):
    """
    Returns total spill stats for a state

    Args:
        state (str): name of state

    Returns:
        dict: contains summary info from get_totals()
    """
    selected_rows = select_matching_rows([("Accident State", state)])
    return get_totals(selected_rows)

def lookup(args: any) -> any:
    """
    Determine which lookup function should be called and call it.

    Args:
        args (any): arguments retrieved from parse_args().

    Returns:
        any: the totals object returned by lookup_by_location() or lookup_company().
    """
    if args.location == True:
        try:
            return lookup_by_location(args.city, args.county, args.state)
        except ValueError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
    else:
        return lookup_company(args.company)

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

def add_leaders_subparser(subparsers: ArgumentParser) -> ArgumentParser:
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

def add_list_subparser(subparsers: ArgumentParser) -> ArgumentParser:
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

def add_lookup_subparser(subparsers: ArgumentParser) -> ArgumentParser:
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
    subparsers = main_parser.add_subparsers(title='available subcommands', dest='command')
    subparsers.add_parser('help', help='print the help message and exit')
    subparsers = add_lookup_subparser(subparsers)
    subparsers = add_list_subparser(subparsers)
    subparsers = add_leaders_subparser(subparsers)
    
    return main_parser

def execute_command(parser: ArgumentParser):
    """ 
    Executes the given command, i.e. {help, list, lookup, etc.}.

    Args:
        parser (ArguentParser): the main parser object.
    """
    args = parser.parse_args()
    if args.command == 'help':
        parser.print_help()
    elif args.command == 'lookup':
        print_totals(lookup(args))
    elif args.command == 'list':
        print('Feature currently under development.')
    elif args.command == 'leaders':
        print('Feature currently under development.')
    else:
        pass # We should never reach this point thanks to argparse

def main():
    load_data()
    parser = setup_subparsers(get_main_parser())

    if len(sys.argv) == 1: # User did not provide any command line arguments
        parser.print_usage()
        return
    
    execute_command(parser)

if __name__ == '__main__':
    main()
