import csv
import psycopg2
import sys
import ProductionCode.psqlConfig as config

class DataAccessor:
    """ 
    The DataAccessor class provides a wrapper around our dataset, which is loaded on
    construction of a DataAccessor object. The class provides several methods for
    getting specific statistics, as well as many smaller helper functions.
    """

    def __init__(self, csv_path: str=None, data: list=None):
        """ 
        Constructs a new DataAccessor object for the OilPipelineAccidents dataset. 
        Immediately sets up a connection with the database.
        """
        self.connection = self._get_connection()


    def _get_connection(self):
        try:
            connection = psycopg2.connect(database=config.database, 
                                          user=config.user, 
                                          password=config.password, 
                                          host="localhost")
        except Exception as e:
            print("Error connecting to database. Connection error: ", e, file=sys.stderr)
            exit()
        return connection


    def get_totals(self, rows):
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
                totalUnintentionalRelease += row[0]
                totalNetLoss += row[1]
                totalCosts += row[2]
            
            return {'accidentCount': accidentCount, 
                    'totalUnintentionalRelease':totalUnintentionalRelease, 
                    'totalNetLoss': totalNetLoss, 
                    'totalCosts' : totalCosts
                    } 
        return None


    def lookup_company(self, company):
        """
        Return a dictionary with summary statistics about all accidents involving the given company.
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
        return self.get_totals(selected_rows)
    
    # TODO: add method that returns all of the rows we are interested in
    

    def lookup_by_location(self, city, county, state): 
        """
        Get info about spills in a give city, county or state. 
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
            raise ValueError("State argument is required for all location queries.") 

        if len(state) != 2:
            state = self.get_state_abbreviation_from_name(state)
   
        if city is not None:
            return self.lookup_by_city(city.upper(), state.upper())
        
        if county is not None: 
            return self.lookup_by_county(county.upper(), state.upper())
        
        if state is not None:
            return self.lookup_by_state(state.upper())
        
        return ValueError("Not enough enough information was provided to complete your query.")
    
    def get_state_abbreviation_from_name(self, name):
        cursor = self.connection.cursor()

        cursor.execute("SELECT abbreviation FROM states WHERE state_name = %s", (name,))

        state = cursor.fetchall()[0][0] 
        return state
    
    def empty_string_to_none(self, string) -> str:
        """
        Convert empty strings to None
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
        """
        Returns total spill stats for a city.

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
        return self.get_totals(selected_rows)
    

    def lookup_by_county(self, county, state):
        """
        Returns total spill stats for a county.

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
        return self.get_totals(selected_rows)
    

    def lookup_by_state(self, state):
        """
        Returns total spill stats for a state

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
        
        return self.get_totals(selected_rows)
    

    def get_list_of_locations(self) -> list:
        """
        Returns a list of all locations in the dataset sorted by state.

        Returns
            list: list of locations.
        """
        cursor = self.connection.cursor()

        cursor.execute("SELECT DISTINCT accident_city, accident_county, accident_state "
                       "FROM oil_pipeline_accidents "
                       "ORDER BY accident_state ASC", 
                       )

        return cursor.fetchall()
    

    def get_list_of_locations_by_state(self, state: str) -> list:
        """
        Returns a list of all locations in a state sorted by county.

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


    def get_list_of_companies(self) -> list:
        """ 
        Returns a sorted list of all companies in the dataset. 
        
        Returns:
            list: list of companies. 
        """
        cursor = self.connection.cursor()

        cursor.execute("SELECT DISTINCT operator_name FROM oil_pipeline_accidents ORDER BY operator_name ASC",)

        companies = [item[0] for item in cursor.fetchall()]
        return companies
    

    def get_company_spill_coordinates(self, company) -> list:
        """
        Gets a list of coordinates for all the spills caused by specified company.
        
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
        

    def get_location_spill_coordinates(self, city: str, county: str, state: str) -> list:
        """ 
        Gets a list of coordinates of all spills in a specific area. 
        
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
            return self.get_coordinates_by_city(city, state)
        elif county:
            return self.get_coordinates_by_county(county, state)
        else:
            return self.get_coordinates_by_state(state)
        
    
    def get_coordinates_by_city(self, city: str, state: str) -> list:
        """ 
        Gets a list of coordinates of all spills in city. 

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
    

    def get_coordinates_by_county(self, county: str, state: str) -> list:
        """ 
        Gets a list of coordinates of all spills in county. 

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
    

    def get_coordinates_by_state(self, state: str) -> list:
        """ 
        Gets a list of coordinates of all spills in state. 

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

