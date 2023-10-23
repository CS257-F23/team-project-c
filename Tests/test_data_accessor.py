import unittest
from ProductionCode.data_accessor import DataAccessor

sample_data = [ 
    # header row
    ['Report Number', 'Supplemental Number', 'Accident Year', 'Accident Date/Time', 'Operator ID', 'Operator Name', 'Pipeline/Facility Name', 'Pipeline Location', 'Pipeline Type', 'Liquid Type', 'Liquid Subtype', 'Liquid Name', 'Accident City', 'Accident County', 'Accident State', 'Accident Latitude', 'Accident Longitude', 'Cause Category', 'Cause Subcategory', 'Unintentional Release (Barrels)', 'Intentional Release (Barrels)', 'Liquid Recovery (Barrels)', 'Net Loss (Barrels)', 'Liquid Ignition', 'Liquid Explosion', 'Pipeline Shutdown', 'Shutdown Date/Time', 'Restart Date/Time', 'Public Evacuations', 'Operator Employee Injuries', 'Operator Contractor Injuries', 'Emergency Responder Injuries', 'Other Injuries', 'Public Injuries', 'All Injuries', 'Operator Employee Fatalities', 'Operator Contractor Fatalities', 'Emergency Responder Fatalities', 'Other Fatalities', 'Public Fatalities', 'All Fatalities', 'Property Damage Costs', 'Lost Commodity Costs', 'Public/Private Property Damage Costs', 'Emergency Response Costs', 'Environmental Remediation Costs', 'Other Costs', 'All Costs'], 
  
    # sample data row 1
    ['20100016', '17305', '2010', '1/1/2010 7:15 AM', '32109', 'ONEOK NGL PIPELINE LP', 'KINDER MORGAN JCT', 'ONSHORE', 'ABOVEGROUND', 'HVL OR OTHER FLAMMABLE OR TOXIC FLUID, GAS', 'LPG (LIQUEFIED PETROLEUM GAS) / NGL (NATURAL GAS LIQUID)', '', 'MCPHERSON', 'MCPHERSON', 'KS', '38.6707', '-97.78123', 'INCORRECT OPERATION', 'PIPELINE/EQUIPMENT OVERPRESSURED', '21', '0.1', '0', '21', 'NO', 'NO', 'NO', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '110', '1517', '0', '0', '0', '0', '1627'],
   
    # sample data row 2
    ['20100254', '17331', '2010', '1/4/2010 8:30 AM', '15786', 'PORTLAND PIPELINE CORP', '24-INCH MAIN LINE', 'ONSHORE', 'ABOVEGROUND', 'CRUDE OIL', '', '', 'RAYMOND', 'CUMBERLAND', 'ME', '43.94028', '-70.49336', 'MATERIAL/WELD/EQUIP FAILURE', 'PUMP OR PUMP-RELATED EQUIPMENT', '0.12', '0', '0.12', '0', 'NO', 'NO', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '4000', '8', '0', '0', '0', '0', '4008'],

    # sample data row 3
    ['20100292', '20387', '2010', '12/9/2010 4:17 PM', '32109', 'ONEOK NGL PIPELINE LP', 'ONEOK - LINE CREEK TO CALUMET 4 INCH 10149', 'ONSHORE', 'UNDERGROUND', '"HVL OR OTHER FLAMMABLE OR TOXIC FLUID, GAS"', 'LPG (LIQUEFIED PETROLEUM GAS) / NGL (NATURAL GAS LIQUID)', '', 'POCASSET', 'GRADY', 'OK', '35.203837', '-98.06593', 'EXCAVATION DAMAGE', 'OPERATOR/CONTRACTOR EXCAVATION DAMAGE', '286', '0', '0', '286', 'NO', 'NO', 'YES', '12/9/2010 22:38', '12/13/2010 22:00', '0', '', '', '', '', '', '', '', '', '', '', '', '', '74000', '12987', '0', '0', '0', '0', '86987']
]


# TODO Tests for get spill coordinates
class TestLookupByCompany(unittest.TestCase):
    def setUp(self):
        self.data_accessor = DataAccessor(csv_path='Data/OilPipelineAccidents.csv')


    def test_return_value(self):
        """ Test that it returns the right info for Portland Pipeline Corp. """
        result = self.data_accessor.lookup_company("PORTLAND PIPELINE CORP")
        self.assertEqual(result, {
                                    "accidentCount": 1,
                                    "totalUnintentionalRelease": 0.12,
                                    "totalNetLoss": 0.0,
                                    "totalCosts": 4008.0
                                 })
    

class TestGetSummaryStats(unittest.TestCase):
    def setUp(self):
        self.data_accessor = DataAccessor(csv_path='Data/OilPipelineAccidents.csv')


    def test_summary_stat_computation(self):
        """ Test that summary stats are computed as expected. """
        result = self.data_accessor.get_totals(sample_data[1:])
        self.assertEqual(result['accidentCount'], 2)
        self.assertEqual(result['totalUnintentionalRelease'], 21.12)
        self.assertEqual(result['totalNetLoss'], 21.0)
        self.assertEqual(result['totalCosts'], 5635.0)


    def test_mismatched_lengths(self):
        """ Edge Case: test that arrays that aren't the right size throws IndexError. """
        self.assertRaises(IndexError, self.data_accessor.get_totals, [[1,2,3,4]])


class TestGetNumericValue(unittest.TestCase):
    def setUp(self):
        self.data_accessor = DataAccessor(data=sample_data)
        self.row = sample_data[1]


    def test_get_values(self):
        """ Make sure correct row value gets returned from this helper function. """
        self.assertEqual(self.data_accessor.get_numeric_value(self.row, 'Report Number'), 20100016) 
        self.assertEqual(self.data_accessor.get_numeric_value(self.row, 'Accident Year'), 2010) 
        self.assertEqual(self.data_accessor.get_numeric_value(self.row, 'Operator ID'), 32109) 
    

    def test_out_of_bounds(self):
        """ Edge case: testing out of bounds indexing. """
        self.assertRaises(ValueError, self.data_accessor.get_numeric_value, self.row, "fake column")


    def test_empty_arrays(self):
        """ Edge case: testing empty row and column name values. """
        self.assertRaises(ValueError, self.data_accessor.get_numeric_value, [], "fake column")
        self.assertRaises(ValueError, self.data_accessor.get_numeric_value, [], "")


class TestLookupByCity(unittest.TestCase):
    """Author: Paul & Henry"""
    def setUp(self):
        self.data_accessor = DataAccessor(csv_path='Data/OilPipelineAccidents.csv')


    def test_output(self):
        """lookup_by_city(): Test whether lookup_by_city returns the right output."""
        self.assertEqual(self.data_accessor.lookup_by_city("FLOODWOOD", "MN"), {
            'accidentCount': 1, 
            'totalUnintentionalRelease': 0.36, 
            'totalNetLoss': 0.0, 
            'totalCosts': 31000.0
        })


    def test_invalid_city(self):
        """lookup_by_city(): Test for when we enter invalid city in test_by_city."""
        self.assertEqual(self.data_accessor.lookup_by_city("random", "MN"), None)


    def test_invalid_state(self):
        """lookup_by_city(): Test for when we enter the invalid state."""
        self.assertEqual(self.data_accessor.lookup_by_city("FLOODWOOD", "Random"), None)


    def test_invalid_city_and_state(self):
        """lookup_by_city(): Tests for invalid city and state arguments."""
        self.assertEqual(self.data_accessor.lookup_by_city("fake city", "fake state"), None)


class TestLookupByCounty(unittest.TestCase):
    """Author: Paul & Henry"""
    def setUp(self):
        self.data_accessor = DataAccessor(csv_path='Data/OilPipelineAccidents.csv')


    def test_output(self):
        """lookup_by_county(): Test that it returns the right output for Rice county."""
        self.assertEqual(self.data_accessor.lookup_by_county("Rice", "MN"), {
            'accidentCount': 1, 
            'totalUnintentionalRelease': 0.12, 
            'totalNetLoss': 0.0, 
            'totalCosts': 5025.0
        })


    def test_invalid_county(self):
        """lookup_by_county(): Test for when we enter invalid county"""
        self.assertEqual(self.data_accessor.lookup_by_city ("not a county", "MN"), None)


    def test_invalid_state(self):
        """lookup_by_county(): Test for when we enter the invalid state."""
        self.assertEqual(self.data_accessor.lookup_by_city("Rice", "not a state"), None)


    def test_invalid_county_and_state(self):
        """lookup_by_county(): Tests for invalid county and state arguments."""
        self.assertEqual(self.data_accessor.lookup_by_city ("fake county", "fake state"), None)

        
class TestLookupByLocation(unittest.TestCase):
    """Author: Paul & Henry"""
    def setUp(self):
        self.data_accessor = DataAccessor(csv_path='Data/OilPipelineAccidents.csv')


    def test_output(self):
        """lookup_by_location(): Test that it returns the right output. """
        self.assertEqual(self.data_accessor.lookup_by_location("FLOODWOOD", "ST. LOUIS", "MN"), {
            'accidentCount': 1, 
            'totalUnintentionalRelease': 0.36, 
            'totalNetLoss': 0.0, 
            'totalCosts': 31000.0
        })


    def test_invalid_state(self):
        """lookup_by_location(): Tests for invalid state argument. """        
        self.assertEqual(self.data_accessor.lookup_by_location("FLOODWOOD", "ST. LOUIS", "Random"), None)


    def test_invalid_county(self):
        """lookup_by_location(): Tests for invalid county argument. """        
        self.assertEqual(self.data_accessor.lookup_by_location(None, "fake county", "MN"), None)


    def test_invalid_city(self):
        """lookup_by_location(): Tests for invalid city argument. """        
        self.assertEqual(self.data_accessor.lookup_by_location("fake city", "ST. LOUIS", "MN"), None)


    def test_no_state(self):
        """lookup_by_location(): Test error is thrown when no state is passed. """
        self.assertRaises(ValueError, self.data_accessor.lookup_by_location, "Floodwood", "St. Louis", None)


    def test_not_enough_info(self):
        self.assertRaises(ValueError, self.data_accessor.lookup_by_location, None, None, None)


class TestGetSummaryStats(unittest.TestCase):
    def setUp(self):
        self.data_accessor = DataAccessor(data=sample_data)

    def test_summary_stat_computation(self):
        """ Test that summary stats are computed as expected. """
        result = self.data_accessor.get_totals(self.data_accessor.data[1:])
        self.assertEqual(result['accidentCount'], 3)
        self.assertEqual(result['totalUnintentionalRelease'], 307.12)
        self.assertEqual(result['totalNetLoss'], 307.0)
        self.assertEqual(result['totalCosts'], 92622.0)


    def test_mismatched_lengths(self):
        """ Edge Case: test that arrays that aren't the right size throws IndexError. """
        self.assertRaises(IndexError, self.data_accessor.get_totals, [[1,2,3,4]])


class TestList(unittest.TestCase):
    def setUp(self):
        self.sample_data_accessor = DataAccessor(data=sample_data)
        self.real_data_accessor = DataAccessor(csv_path='Data/OilPipelineAccidents.csv')

    
    def test_get_list_of_companies_no_dups(self):
        """ Tests that all companies in the data set are listed and no duplicates exists. """
        self.assertEqual(self.sample_data_accessor.get_list_of_companies(), 
                         ['ONEOK NGL PIPELINE LP', 'PORTLAND PIPELINE CORP'])
        
    
    def test_get_list_of_companies_sorted(self):
        """ Test that list of companies is sorted. """
        result = self.real_data_accessor.get_list_of_companies()
        self.assertEqual(result, sorted(result))

    
    def test_get_list_of_locations(self):
        """ Test that all locations in data set are listed. """
        self.assertEqual(self.sample_data_accessor.get_list_of_locations(), 
                         [['MCPHERSON', 'MCPHERSON', 'KS'], 
                          ['RAYMOND', 'CUMBERLAND', 'ME'], 
                          ['POCASSET', 'GRADY', 'OK']]
                        )


    def test_get_list_of_locations_no_dups(self):
        """ Test that there are no duplicates in the list of locations. """
        result = self.real_data_accessor.get_list_of_locations()
        locations = []
        for location in result:
            if location in locations:
                self.fail()
            else:
                locations.append(location)


    def test_get_list_of_locations_by_state_no_dups(self):
        """ Test that all locations in state are returned. """
        self.assertEqual(self.sample_data_accessor.get_list_of_locations_by_state('KS'), 
                         [['MCPHERSON', 'MCPHERSON', 'KS']])
        
    
    def test_get_list_by_state_invalid_arg(self):
        """ Test that empty list is returned when invalid state is given. """
        self.assertEqual(self.real_data_accessor.get_list_of_locations_by_state('AA'), [])


class TestSpillCoordinates(unittest.TestCase):
    def setUp(self):
        self.data_accessor = DataAccessor(data=sample_data)

    
    def test_get_company_spill_coordinates(self):
        """ Test that expected coordinates are returned when looking up a company. """
        self.assertEqual(self.data_accessor.get_company_spill_coordinates('OnEOK Ngl PIPeLINE lP'), [
            ['38.6707', '-97.78123'],
            ['35.203837', '-98.06593']
        ])