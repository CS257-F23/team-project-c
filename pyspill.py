import sys
from argparse import ArgumentParser
from ProductionCode.data_accessor import DataAccessor
    

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


def print_company_list(companies: list):
    """
    Prints the list of companies to the terminal.

    Args:
        companies (list): the list of companies.
    """
    print('List of all the companies in the data set:\n')
    for company in companies:
        print(company)


def print_location_list(locations: list):
    """
    Prints the list of locations to the terminal.

    Args:
        locations (list): the list of locations.
    """
    print('List of all the locations in the data set:\n')
    for location in locations:
        city = None
        county = None
        state = None
        if location[0] != '':
            city = location[0]
        if location[1] != '':
            county = location[1]
        if location[2] != '':
            state = location[2]
        print(f'City: {city}, County: {county}, State: {state}')


def print_location_by_state_list(locations: list):
    """
    Prints the list of locations in a state to the terminal.

    Args:
        locations (list): the list of locations.
    """
    if len(locations) == 0:
        print('This state has not had any oil spills.')
        return

    print(f'List of all the oil spill locations in {locations[0][2]}:\n')
    for location in locations:
        city = None
        county = None
        if location[0] != '':
            city = location[0]
        if location[1] != '':
            county = location[1]
        print(f'City: {city}, County: {county}')


def print_list(some_list: list, format: str):
    """
    Prints the given list based on the command the user inputted.
    Format is the list option the user specified (i.e. company, location, state).

    Args:
        some_list (list): the list to be printed.
        format (str): 'company', 'location', or 'state'
    """
    if format == 'company':
        print_company_list(some_list)
    elif format == 'location':
        print_location_list(some_list)
    elif format == 'state':
        print_location_by_state_list(some_list)
    else:
        raise ValueError('format must be "company", "location", or "state"')


def get_list(args: any, data: DataAccessor) -> (list, str):
    """ 
    Determine which list function should be called and pass along its return value.

    Args:
        args (any): arguments retrieved from parse_args().
        data (DataAccessor): the dataset object.

    Returns:
        (list, str): a list of companies or locations, type of list 
                    (i.e. company, location, state)
    """
    if args.company:
        return data.get_list_of_companies(), 'company'
    elif args.location:
        return data.get_list_of_locations(), 'location'
    else:
        return data.get_list_of_locations_by_state(args.state), 'state'
    

def lookup(args: any, data: DataAccessor) -> any:
    """
    Determine which lookup function should be called and call it.

    Args:
        args (any): arguments retrieved from parse_args().
        data (DataAccessor): the dataset object.

    Returns:
        any: the totals object returned by lookup_by_location() or lookup_company().
    """
    if args.location == True:
        try:
            return data.lookup_by_location(args.city, args.county, args.state)
        except ValueError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
    else:
        return data.lookup_company(args.company)


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
            help='list all locations in a given state. ' 
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


def execute_command(parser: ArgumentParser, data: DataAccessor):
    """ 
    Executes the given command, i.e. {help, list, lookup, etc.}.

    Args:
        parser (ArguentParser): the main parser object.
        data (DataAccessor): the dataset object.
    """
    args = parser.parse_args()
    if args.command == 'help':
        parser.print_help()
    elif args.command == 'lookup':
        print_totals(lookup(args, data))
    elif args.command == 'list':
        list_and_type = get_list(args, data)
        print_list(list_and_type[0], list_and_type[1])
    elif args.command == 'leaders':
        print('Feature currently under development.')
    else:
        pass # We should never reach this point thanks to argparse


def main():
    data = DataAccessor('Data/OilPipelineAccidents.csv')
    parser = setup_subparsers(get_main_parser())

    if len(sys.argv) == 1: # User did not provide any command line arguments
        parser.print_usage()
        return
    
    execute_command(parser, data)

if __name__ == '__main__':
    main()
