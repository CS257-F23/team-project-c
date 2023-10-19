import csv


class DataAccessor:
    """ 
    The DataAccessor class provides a wrapper around our dataset, which is loaded on
    construction of a DataAccessor object. The class provides several methods for
    getting specific statistics, as well as many helper smaller helper functions.
    """
    def __init__(self, csv_path: str):
        """ 
        Constructs a new DataAccessor object for the OilPipelineAccidents dataset. 
        
        Args:
            csv_path (str): the pathname for the csv file.
        """
        self.data = []

        with open(csv_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                self.data.append(row)
        
        self.headers = self.data[0]


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
    
