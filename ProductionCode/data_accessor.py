import psycopg2
import sys
import ProductionCode.psqlConfig as config

class DataAccessor:
    """The DataAccessor class provides a wrapper around our dataset, which is loaded on
    construction of a DataAccessor object. The class provides several methods for
    getting specific statistics, as well as many smaller helper functions.
    """

    def __init__(self, csv_path: str=None, data: list=None):
        """ 
        Constructs a new DataAccessor object for the OilPipelineAccidents dataset. 
        Immediately sets up a connection with the database.
        """
        self.connection = self._get_connection()


    def _get_connection(self) -> psycopg2.connect:
        """Initiates psycopg2 connection to psql server

        Returns:
            psycopg2.connection: connection to the database
        """        
        try:
            connection = psycopg2.connect(database=config.database, 
                                          user=config.user, 
                                          password=config.password, 
                                          host="localhost")
        except Exception as e:
            print("Error connecting to database. Connection error: ", e, file=sys.stderr)
            exit()
        return connection


    def _get_totals(self, rows):
        """Calculate summary statistics for a list of oil spill accidents by summing columns.
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
                totalUnintentionalRelease += row[0]
                totalNetLoss += row[1]
                totalCosts += row[2]
            
            return {'accidentCount': accidentCount, 
                    'totalUnintentionalRelease':totalUnintentionalRelease, 
                    'totalNetLoss': totalNetLoss, 
                    'totalCosts' : totalCosts
                    } 
        raise ValueError("No data was passed in. If running from a query, this means the query returned no data.")


    def lookup_company(self, company):
        """Return a dictionary with summary statistics about all accidents involving the given company.
        Author: Henry Burkhardt

        Args:
            company (str): name of company (must be in dataset)

        Returns:
            dict: dictionary of summary data on company, from get_summary_stats()
        """
        company = company.upper()
        cursor = self.connection.cursor()

        cursor.execute("SELECT unintentional_release_barrels, net_loss_barrels, all_costs "
                       "FROM oil_pipeline_accidents "
                       "WHERE operator_name = %s", 
                       (company,))

        selected_rows = cursor.fetchall()    
        return self._get_totals(selected_rows)
        

    def lookup_by_location(self, city, county, state): 
        """Get info about spills in a give city, county or state. 
        Author: Paul Claudel Izabayo

        Args:
            city (str): name of city
            county (str): name of county
            state (str): name of state
        """

        # Ensure state argument was passed
        state = self.empty_string_to_none(state)
        county = self.empty_string_to_none(county)
        city = self.empty_string_to_none(city)

        if state == None:
            raise ValueError("State name was not given.")

        if len(state) != 2:
            state = self.get_state_abbreviation_from_name(state)

   
        if city is not None:
            return self.lookup_by_city(city.upper(), state.upper())
        
        if county is not None: 
            return self.lookup_by_county(county.upper(), state.upper())
        
        if state is not None:
            return self.lookup_by_state(state.upper())
        
        return ValueError("Not enough enough information was provided to complete your query.")
    
    
    def get_state_abbreviation_from_name(self, state_name) -> str:
        """Get the two letter abbreviation from the full state name 

        Args:
            state_name (str): full name of state

        Returns:
            str: two letter state abbreviation
        """        
        cursor = self.connection.cursor()

        cursor.execute("SELECT abbreviation FROM states WHERE state_name = %s", (state_name.title(),))

        try:
            state = cursor.fetchall()[0][0] 
        except IndexError:
            # Index error is throne when an invalid state name is passed.
            raise ValueError("State name did not resolve to an abreviation") 
        return state
    
    
    def empty_string_to_none(self, string) -> str:
        """Convert empty strings to None
        Author: Henry

        Args:
            string (str): string to convert

        Returns:
            (None OR str): returns original input if string is not empty, and None if input was was None or string is empty.
        """
        if string == " " or string == "":
            return None
        return string


    def lookup_by_city(self, city, state):
        """Returns total spill stats for a city.

        Args:
            city (str): name of city
            state (str): name of state

        Returns:
            dict: contains summary info from get_totals()
        """
        cursor = self.connection.cursor()

        cursor.execute("SELECT unintentional_release_barrels, net_loss_barrels, all_costs "
                       "FROM oil_pipeline_accidents "
                       "WHERE accident_city = %s AND accident_state = %s", 
                       (city, state))

        selected_rows = cursor.fetchall()    
        return self._get_totals(selected_rows)
    

    def lookup_by_county(self, county, state):
        """Returns total spill stats for a county.

        Args:
            county (str): name of county
            state (str): name of state

        Returns:
            dict: contains summary info from get_totals()
        """
        
        cursor = self.connection.cursor()

        cursor.execute("SELECT unintentional_release_barrels, net_loss_barrels, all_costs "
                       "FROM oil_pipeline_accidents "
                       "WHERE accident_county = %s AND accident_state = %s", 
                       (county, state))

        selected_rows = cursor.fetchall()
        return self._get_totals(selected_rows)
    

    def lookup_by_state(self, state):
        """Returns total spill stats for a state

        Args:
            state (str): name of state

        Returns:
            dict: contains summary info from get_totals()
        """
        cursor = self.connection.cursor()

        cursor.execute("SELECT unintentional_release_barrels, net_loss_barrels, all_costs "
                       "FROM oil_pipeline_accidents "
                       "WHERE accident_state = %s", 
                       (state,))

        selected_rows = cursor.fetchall()
        
        return self._get_totals(selected_rows)
    

    def get_list_of_locations(self) -> list[str]:
        """Returns a list of all locations in the dataset sorted by state.

        Returns
            list: list of locations.
        """
        cursor = self.connection.cursor()

        cursor.execute("SELECT DISTINCT accident_city, accident_county, accident_state "
                       "FROM oil_pipeline_accidents "
                       "ORDER BY accident_state ASC", 
                       )

        return cursor.fetchall()
    

    def get_list_of_locations_by_state(self, state: str) -> list[str]:
        """Returns a list of all locations in a state sorted by county.

        Args:
            state (str): the two letter abbreviation for the state.

        Returns:
            list: list of locations in the state.
        """
        cursor = self.connection.cursor()

        cursor.execute("SELECT DISTINCT accident_city, accident_county, accident_state "
                       "FROM oil_pipeline_accidents "
                       "WHERE accident_state = %s"
                       "ORDER BY accident_state ASC",
                       (state,)
                       )

        return cursor.fetchall()


    def get_list_of_companies(self) -> list[str]:
        """Returns a sorted list of all companies in the dataset. 
        
        Returns:
            list: list of companies. 
        """
        cursor = self.connection.cursor()

        cursor.execute("SELECT DISTINCT operator_name FROM oil_pipeline_accidents ORDER BY operator_name ASC",)

        companies = [item[0] for item in cursor.fetchall()]
        return companies
    

    def get_company_spill_coordinates(self, company) -> list[tuple[int, int]]:
        """Gets a list of coordinates for all the spills caused by specified company.
        
        Args:
            company (str): name of company

        Returns:
            list of list: A list of lists, in format [<latitude>, <longitude>]
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT accident_latitude, accident_longitude "
                       "FROM oil_pipeline_accidents "
                       "WHERE operator_name = %s", 
                       (company, ))
        return cursor.fetchall()
        

    def get_location_spill_coordinates(self, city: str, county: str, state: str) -> list[tuple[int, int]]:
        """Gets a list of coordinates of all spills in a specific area. 
        
        Args:
            city (str): specify the city, can be None.
            county (str): specify the county, can be None.
            state (str): specify the state, CANNOT be None (required).

        Returns:
            list: a list of coordinates in the format [<latitude>, <longitude>].
        """
        if not state:
            raise ValueError("State argument is required for all location queries.")
        
        if city:
            return self.get_coordinates_by_city(city.upper(), state.upper())
        elif county:
            return self.get_coordinates_by_county(county.upper(), state.upper())
        else:
            return self.get_coordinates_by_state(state.upper())
        
    
    def get_coordinates_by_city(self, city: str, state: str) -> list[tuple[int, int]]:
        """Gets a list of coordinates of all spills in city. 

        Args:
            city (str): the city.
            state (str): the state.

        Returns: 
            list: a list of coordinates in the format [<latitude>, <longitude>].
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT accident_latitude, accident_longitude "
                       "FROM oil_pipeline_accidents "
                       "WHERE accident_state=%s AND accident_city=%s", 
                       (state, city))
        return cursor.fetchall()
    

    def get_coordinates_by_county(self, county: str, state: str) -> list[tuple[int, int]]:
        """Gets a list of coordinates of all spills in county. 

        Args:
            county (str): the county.
            state (str): the state.

        Returns: 
            list: a list of coordinates in the format [<latitude>, <longitude>].
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT accident_latitude, accident_longitude "
                       "FROM oil_pipeline_accidents "
                       "WHERE accident_state=%s AND accident_county=%s", 
                       (state, county))
        return cursor.fetchall()
    

    def get_coordinates_by_state(self, state: str) -> list[tuple[int, int]]:
        """Gets a list of coordinates of all spills in state. 

        Args:
            state (str): the state.

        Returns: 
            list: a list of coordinates in the format [<latitude>, <longitude>].
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT accident_latitude, accident_longitude "
                       "FROM oil_pipeline_accidents "
                       "WHERE accident_state=%s", 
                       (state,))
        return cursor.fetchall()
    

    def get_spill_data_by_location(self, latitude: float, longitude: float) -> tuple:
        """
        Look up a specific location of an oil spill and return the entire row
        from the database. Assumes no two spills are in the exact same location.

        Args:
            latitude (float): latitude.
            longitude (float): longitude.

        Returns:
            tuple: the entire row corresponding to this location.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM oil_pipeline_accidents "
                       "WHERE accident_latitude = %s AND accident_longitude = %s", 
                       (latitude, longitude))
        return cursor.fetchall()[0]
    

    def get_all_spill_coordinates(self) -> list[tuple[float, float]]:
        """ 
        Get a list of all the coordinates (i.e. every spill) in the dataset.

        Returns:
            list: a list of tuples for coordinates.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT accident_latitude, accident_longitude "
                       "FROM oil_pipeline_accidents ")
        return cursor.fetchall()
    

    def get_leaders(self) -> list[tuple]:
        """ 
        Get all the data from the leaderboard. This returns the top 
        10 worst offending companies and summary statistics about them.

        Returns:
            list[tuple]: data for the top ten companies.
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM leaders")
        return cursor.fetchall()
    
    
    def _get_totals_for_all_companies(self) -> list:
        """ 
        A helper method to get summary statistics for every company and 
        compile it into a list. 

        Returns:
            list: returns a list of dictionaries of the same form as the get_totals()
                  method, with an additional key for companyName.
        """
        companies = self.get_list_of_companies()
        company_data = []
        for company in companies:
            summary_stats = self.lookup_company(company)
            summary_stats.update({'companyName': company})
            company_data.append(summary_stats)
        
        return company_data
    

    def _compute_leaders(self):
        """
        DO NOT CALL THIS FUNCTION IF YOU JUST WANT A LIST OF THE LEADERS.

        Computes the top ten worst offending companies in terms of total net loss,
        which most directly correlates to environmental damage. Injuries are not
        taken into account. This is a pretty inefficient way of doing this, so only
        run using the update_leaders.py script when the data changes.
        """
        
        company_data = self._get_totals_for_all_companies()
        company_data.sort(key=lambda company: company['totalNetLoss'], reverse=True)

        cursor = self.connection.cursor()        
        cursor.execute("DROP TABLE IF EXISTS leaders")
        cursor.execute("CREATE TABLE leaders ("
                       "company_name text, "
                       "accident_count int, "
                       "total_unintentional_release real, "
                       "total_net_loss real, "
                       "total_costs int)"
                       )

        for company in company_data[:10]:
            cursor.execute("INSERT INTO leaders VALUES (%s, %s, %s, %s, %s)", (
                company['companyName'], 
                company['accidentCount'], 
                company['totalUnintentionalRelease'], 
                company['totalNetLoss'], 
                company['totalCosts']
            ))

        self.connection.commit() # Tell the database that I want these changes to happen
        
