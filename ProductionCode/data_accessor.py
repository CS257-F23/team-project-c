import csv


class DataAccessor:
    """ 
    The DataAccessor class provides a wrapper around our dataset, which is loaded on
    construction of a DataAccessor object. The class provides several methods for
    getting specific statistics, as well as many helper smaller helper functions.
    """

    def __init__(self, csv_path: str=None, data: list=None):
        """ 
        Constructs a new DataAccessor object for the OilPipelineAccidents dataset. 
        Also provides a way to manually enter data through the data kwarg. If csv_path
        is provided, data is ignored.
        
        Args (kwargs):
            csv_path (str): the pathname for the csv file, defaults to None.
            data (list): a 2D list of user entered data resembling csv format.
        """
        if not csv_path and not data:
            raise ValueError('You must specify either a csv pathname or manually enter data.')
        
        if csv_path:
            self.data = []

            with open(csv_path, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    self.data.append(row)
            
            self.headers = self.data[0]
        else:
            self.data = data
            self.headers = []
            if self.data:
                self.headers = data[0]


    def get_index_of(self, column_name):
        return self.headers.index(column_name)


    def get_numeric_value(self, row, column_name):
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
        
        index = self.get_index_of(column_name)
        return float(row[index])


    def select_matching_rows(self, rules):
        """
        Subset rows from database based with string matching
        Author: Henry Burkhardt

        Pass an array of doubles (in the format below) to extract data from dataset by string matching columns.

        Args: 
            criteria (list of double): [(<column_name>, <string_to_match>), ...]
        """
        selected_rows = []
        for row in self.data:
            matches = []
            for rule in rules:
                columnIndex = self.get_index_of(rule[0])
                matches.append(row[columnIndex].upper().strip() == rule[1].upper().strip())

            if all(matches):
                selected_rows.append(row)
        return selected_rows


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
                totalUnintentionalRelease += self.get_numeric_value(row, "Unintentional Release (Barrels)")
                totalNetLoss += self.get_numeric_value(row, "Net Loss (Barrels)")
                totalCosts += self.get_numeric_value(row, "All Costs")
            
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
        relevant_rows = self.select_matching_rows([("Operator Name", company)])
        return self.get_totals(relevant_rows)
    

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
        if state is None: 
            raise ValueError("State argument is required for all location queries.") 

        if city is not None:
            return self.lookup_by_city(city, state)
        
        if county is not None: 
            return self.lookup_by_county(county, state)
        
        if state is not None:
            return self.lookup_by_state(state)
        
        return ValueError("Not enough enough information was provided to complete your query.")
    

    def lookup_by_city(self, city, state):
        """
        Returns total spill stats for a city.

        Args:
            city (str): name of city
            state (str): name of state

        Returns:
            dict: contains summary info from get_totals()
        """
        selected_rows = self.select_matching_rows([("Accident City", city), ("Accident State", state)])
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
        
        selected_rows = self.select_matching_rows([("Accident County", county), ("Accident State", state)])
        return self.get_totals(selected_rows)
    

    def lookup_by_state(self, state):
        """
        Returns total spill stats for a state

        Args:
            state (str): name of state

        Returns:
            dict: contains summary info from get_totals()
        """
        selected_rows = self.select_matching_rows([("Accident State", state)])
        return self.get_totals(selected_rows)
    

    def get_list_of_locations(self) -> list:
        """
        Returns a list of all locations in the dataset sorted by state.

        Returns
            list: list of locations.
        """
        start_index_row = self.get_index_of('Accident City')
        locations_with_duplicates = [row[start_index_row: start_index_row + 3] for row in self.data[1:]]
        locations = []
        [locations.append(location) for location in locations_with_duplicates if location not in locations]
        locations.sort(key=lambda location: location[2])

        return locations
    

    def get_list_of_locations_by_state(self, state: str) -> list:
        """
        Returns a list of all locations in a state sorted by county.

        Args:
            state (str): the two letter abbreviation for the state.

        Returns:
            list: list of locations in the state.
        """
        all_locations = self.get_list_of_locations()
        state = state.strip().upper()
        locations_in_state = [location for location in all_locations if location[2].strip().upper() == state]
        locations_in_state.sort(key=lambda location: location[1])

        return locations_in_state


    def get_list_of_companies(self) -> list:
        """ 
        Returns a sorted list of all companies in the dataset. 
        
        Returns:
            list: list of companies. 
        """
        companies_with_duplicates = [row[self.get_index_of('Operator Name')] for row in self.data[1:]]
        companies = []
        [companies.append(company) for company in companies_with_duplicates if company not in companies]
        companies.sort()
        return companies
    
    def get_spill_coordinates(self, company) -> list:
        """Hard coded coordinates for all of a companies spills
        Author: Henry
        
        Args:
            company (str): name of company

        Returns:
            list of list: A list of lists, in format [<latitude>, <longitude>]
        """
        longitudes = [[-95.17611], [-96.75427], [-117.35583], [-93.27546], [-101.35898], [-93.33989], [-93.39656], [-98.58654], [-94.60705], [-102.63968], [-93.277717], [-96.75007], [-106.246861], [-98.496906], [-90.589072], [-95.179264], [-108.47889], [-97.747128], [-98.496967], [-97.747511], [-120.45062247], [-121.672381], [-101.359211], [-98.262922], [-106.902904], [-101.7825], [-121.948261], [-93.290375], [-93.339919], [-118.249779], [-97.307172], [-93.268658], [-102.97538], [-120.444417]]

        latitudes = [[29.71478], [35.94466], [47.71696], [30.241], [35.68463], [30.15957], [38.63064], [33.07358], [39.12851], [31.98743], [30.239547], [35.94595], [42.855444], [33.936233], [38.501817], [29.717169], [45.79417], [36.221931], [33.936514], [36.029589], [34.83433167], [37.795178], [35.684911], [34.133131], [44.665449], [31.362222], [37.963297], [30.239269], [30.158686], [33.802717], [37.761233], [30.239319], [33.007092], [34.972892]]

        lat_lon = [[latitudes[i][0], longitudes[i][0]] for i in range (0, len(latitudes))]
        return lat_lon
    
