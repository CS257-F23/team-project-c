import unittest
import subprocess
from pyspill import *

sample_data = [ 
    # header row
    ['Report Number', 'Supplemental Number', 'Accident Year', 'Accident Date/Time', 'Operator ID', 'Operator Name', 'Pipeline/Facility Name', 'Pipeline Location', 'Pipeline Type', 'Liquid Type', 'Liquid Subtype', 'Liquid Name', 'Accident City', 'Accident County', 'Accident State', 'Accident Latitude', 'Accident Longitude', 'Cause Category', 'Cause Subcategory', 'Unintentional Release (Barrels)', 'Intentional Release (Barrels)', 'Liquid Recovery (Barrels)', 'Net Loss (Barrels)', 'Liquid Ignition', 'Liquid Explosion', 'Pipeline Shutdown', 'Shutdown Date/Time', 'Restart Date/Time', 'Public Evacuations', 'Operator Employee Injuries', 'Operator Contractor Injuries', 'Emergency Responder Injuries', 'Other Injuries', 'Public Injuries', 'All Injuries', 'Operator Employee Fatalities', 'Operator Contractor Fatalities', 'Emergency Responder Fatalities', 'Other Fatalities', 'Public Fatalities', 'All Fatalities', 'Property Damage Costs', 'Lost Commodity Costs', 'Public/Private Property Damage Costs', 'Emergency Response Costs', 'Environmental Remediation Costs', 'Other Costs', 'All Costs'], 
  
    # sample data row 1
    ['20100016', '17305', '2010', '1/1/2010 7:15 AM', '32109', 'ONEOK NGL PIPELINE LP', 'KINDER MORGAN JCT', 'ONSHORE', 'ABOVEGROUND', 'HVL OR OTHER FLAMMABLE OR TOXIC FLUID, GAS', 'LPG (LIQUEFIED PETROLEUM GAS) / NGL (NATURAL GAS LIQUID)', '', 'MCPHERSON', 'MCPHERSON', 'KS', '38.6707', '-97.78123', 'INCORRECT OPERATION', 'PIPELINE/EQUIPMENT OVERPRESSURED', '21', '0.1', '0', '21', 'NO', 'NO', 'NO', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '110', '1517', '0', '0', '0', '0', '1627'],
   
    # sample data row 2
    ['20100254', '17331', '2010', '1/4/2010 8:30 AM', '15786', 'PORTLAND PIPELINE CORP', '24-INCH MAIN LINE', 'ONSHORE', 'ABOVEGROUND', 'CRUDE OIL', '', '', 'RAYMOND', 'CUMBERLAND', 'ME', '43.94028', '-70.49336', 'MATERIAL/WELD/EQUIP FAILURE', 'PUMP OR PUMP-RELATED EQUIPMENT', '0.12', '0', '0.12', '0', 'NO', 'NO', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '4000', '8', '0', '0', '0', '0', '4008']
]


class TestLookupByCompany(unittest.TestCase):
    def setUp(self):
        load_data()


    def test_return_value(self):
        """ Test that it returns the right info for Portland Pipeline Corp. """
        result = lookup_company("PORTLAND PIPELINE CORP")
        self.assertEqual(result, {
                                    "accidentCount": 1,
                                    "totalUnintentionalRelease": 0.12,
                                    "totalNetLoss": 0.0,
                                    "totalCosts": 4008.0
                                 })
    

class TestGetSummaryStats(unittest.TestCase):
    def setUp(self):
        load_data()


    def test_summary_stat_computation(self):
        """ Test that summary stats are computed as expected. """
        result = get_totals(sample_data[1:])
        self.assertEqual(result['accidentCount'], 2)
        self.assertEqual(result['totalUnintentionalRelease'], 21.12)
        self.assertEqual(result['totalNetLoss'], 21.0)
        self.assertEqual(result['totalCosts'], 5635.0)


    def test_mismatched_lengths(self):
        """ Edge Case: test that arrays that aren't the right size throws IndexError. """
        self.assertRaises(IndexError, get_totals, [[1,2,3,4]])


class TestGetNumericValue(unittest.TestCase):
    row = sample_data[1]


    def test_get_values(self):
        """ Make sure correct row value gets returned from this helper function. """
        self.assertEqual(get_numeric_value(self.row, 'Report Number'), 20100016) 
        self.assertEqual(get_numeric_value(self.row, 'Accident Year'), 2010) 
        self.assertEqual(get_numeric_value(self.row, 'Operator ID'), 32109) 
    

    def test_out_of_bounds(self):
        """Edge case: testing out of bounds indexing"""
        self.assertRaises(ValueError, get_numeric_value, self.row, "fake column")


    def test_empty_arrays(self):
        """ Edge case: testing empty row and column name values. """
        self.assertRaises(ValueError, get_numeric_value, [], "fake column")
        self.assertRaises(ValueError, get_numeric_value, [], "")


class TestLookupByCity(unittest.TestCase):
    """Author: Paul & Henry"""
    def test_output(self):
        """lookup_by_city(): Test whether lookup_by_city returns the right output."""
        self.assertEqual(lookup_by_city("FLOODWOOD", "MN"), {
            'accidentCount': 1, 
            'totalUnintentionalRelease': 0.36, 
            'totalNetLoss': 0.0, 
            'totalCosts': 31000.0
            })


    def test_invalid_city(self):
        """lookup_by_city(): Test for when we enter invalid city in test_by_city."""
        self.assertEqual(lookup_by_city ("random", "MN"), None)


    def test_invalid_state(self):
        """lookup_by_city(): Test for when we enter the invalid state."""
        self.assertEqual(lookup_by_city ("FLOODWOOD", "Random"), None)


    def test_invalid_city_and_state(self):
        """lookup_by_city(): Tests for invalid city and state arguments."""
        self.assertEqual(lookup_by_city ("fake city", "fake state"), None)


class TestLookupByCounty(unittest.TestCase):
    """Author: Paul & Henry"""
    def test_output(self):
        """lookup_by_county(): Test that it returns the right output for Rice county."""
        self.assertEqual(lookup_by_county("Rice", "MN"), {
            'accidentCount': 1, 
            'totalUnintentionalRelease': 0.12, 
            'totalNetLoss': 0.0, 
            'totalCosts': 5025.0
                })


    def test_invalid_county(self):
        """lookup_by_county(): Test for when we enter invalid county"""
        self.assertEqual(lookup_by_city ("not a county", "MN"), None)


    def test_invalid_state(self):
        """lookup_by_county(): Test for when we enter the invalid state."""
        self.assertEqual(lookup_by_city ("Rice", "not a state"), None)


    def test_invalid_county_and_state(self):
        """lookup_by_county(): Tests for invalid county and state arguments."""
        self.assertEqual(lookup_by_city ("fake county", "fake state"), None)

        
class TestLookupByLocation(unittest.TestCase):
    """Author: Paul & Henry"""
    def test_output(self):
        """lookup_by_location(): Test that it returns the right output. """
        self.assertEqual(lookup_by_location ("FLOODWOOD", "ST. LOUIS", "MN"), {
            'accidentCount': 1, 
            'totalUnintentionalRelease': 0.36, 
            'totalNetLoss': 0.0, 
            'totalCosts': 31000.0
        })


    def test_invalid_state(self):
        """lookup_by_location(): Tests for invalid state argument. """        
        self.assertEqual(lookup_by_location ("FLOODWOOD", "ST. LOUIS", "Random"), None)


    def test_invalid_county(self):
        """lookup_by_location(): Tests for invalid county argument. """        
        self.assertEqual(lookup_by_location (None, "fake county", "MN"), None)


    def test_invalid_city(self):
        """lookup_by_location(): Tests for invalid city argument. """        
        self.assertEqual(lookup_by_location ("fake city", "ST. LOUIS", "MN"), None)


    def test_no_state(self):
        """lookup_by_location(): Test error is thrown when no state is passed. """
        self.assertRaises(ValueError, lookup_by_location, "Floodwood", "St. Louis", None)


    def test_not_enough_info(self):
        self.assertRaises(ValueError, lookup_by_location, None, None, None)


class TestGetSummaryStats(unittest.TestCase):
    def setUp(self):
        load_data()


    def test_summary_stat_computation(self):
        """ Test that summary stats are computed as expected. """
        result = get_totals(sample_data[1:])
        self.assertEqual(result['accidentCount'], 2)
        self.assertEqual(result['totalUnintentionalRelease'], 21.12)
        self.assertEqual(result['totalNetLoss'], 21.0)
        self.assertEqual(result['totalCosts'], 5635.0)


    def test_mismatched_lengths(self):
        """ Edge Case: test that arrays that aren't the right size throws IndexError. """
        self.assertRaises(IndexError, get_totals, [[1,2,3,4]])


class TestGetListOfCompanies(unittest.TestCase):
    """Author: Feraidon AbdulRahimzai"""
    def test_get_list_of_companies(self):
        # Call the function and get the result
        result = get_list_of_companies()

        # Check if the result is a non-empty list
        self.assertTrue(result)

        # Check if the result is sorted
        self.assertEqual(result, sorted(result))
