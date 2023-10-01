import unittest
from ProductionCode.pyspill import *

sample_data = [ 
    # header row
    ['Report Number', 'Supplemental Number', 'Accident Year', 'Accident Date/Time', 'Operator ID', 'Operator Name', 'Pipeline/Facility Name', 'Pipeline Location', 'Pipeline Type', 'Liquid Type', 'Liquid Subtype', 'Liquid Name', 'Accident City', 'Accident County', 'Accident State', 'Accident Latitude', 'Accident Longitude', 'Cause Category', 'Cause Subcategory', 'Unintentional Release (Barrels)', 'Intentional Release (Barrels)', 'Liquid Recovery (Barrels)', 'Net Loss (Barrels)', 'Liquid Ignition', 'Liquid Explosion', 'Pipeline Shutdown', 'Shutdown Date/Time', 'Restart Date/Time', 'Public Evacuations', 'Operator Employee Injuries', 'Operator Contractor Injuries', 'Emergency Responder Injuries', 'Other Injuries', 'Public Injuries', 'All Injuries', 'Operator Employee Fatalities', 'Operator Contractor Fatalities', 'Emergency Responder Fatalities', 'Other Fatalities', 'Public Fatalities', 'All Fatalities', 'Property Damage Costs', 'Lost Commodity Costs', 'Public/Private Property Damage Costs', 'Emergency Response Costs', 'Environmental Remediation Costs', 'Other Costs', 'All Costs'], 
  
    # sample data row 1
    ['20100016', '17305', '2010', '1/1/2010 7:15 AM', '32109', 'ONEOK NGL PIPELINE LP', 'KINDER MORGAN JCT', 'ONSHORE', 'ABOVEGROUND', 'HVL OR OTHER FLAMMABLE OR TOXIC FLUID, GAS', 'LPG (LIQUEFIED PETROLEUM GAS) / NGL (NATURAL GAS LIQUID)', '', 'MCPHERSON', 'MCPHERSON', 'KS', '38.6707', '-97.78123', 'INCORRECT OPERATION', 'PIPELINE/EQUIPMENT OVERPRESSURED', '21', '0.1', '0', '21', 'NO', 'NO', 'NO', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '110', '1517', '0', '0', '0', '0', '1627'],
   
    # sample data row 2
    ['20100254', '17331', '2010', '1/4/2010 8:30 AM', '15786', 'PORTLAND PIPELINE CORP', '24-INCH MAIN LINE', 'ONSHORE', 'ABOVEGROUND', 'CRUDE OIL', '', '', 'RAYMOND', 'CUMBERLAND', 'ME', '43.94028', '-70.49336', 'MATERIAL/WELD/EQUIP FAILURE', 'PUMP OR PUMP-RELATED EQUIPMENT', '0.12', '0', '0.12', '0', 'NO', 'NO', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '4000', '8', '0', '0', '0', '0', '4008']
]


class Test_lookup_by_company(unittest.TestCase):
    def setUp(self):
        load_data()
        
    def test_return_value(self):
        # TODO: this will need to change once real data is added in
        """Test that it returns the right info for Portland Pipeline Corp"""
        result = lookup_company("PORTLAND PIPELINE CORP")
        self.assertEqual(result, {
                                    "accidentCount": 1,
                                    "totalUnintentionalRelease": 0.12,
                                    "totalNetLoss": 0.0,
                                    "totalCosts": 4008.0
                                })
    
class Test_get_summary_stats(unittest.TestCase):

    def test_summary_stat_computation(self):
        """Test that summary stats are computed as expected"""
        result = get_summary_stats(sample_data[1:])
        self.assertEqual(result['accidentCount'], 2)
        self.assertEqual(result['totalUnintentionalRelease'], 21.12)
        self.assertEqual(result['totalNetLoss'], 21.0)
        self.assertEqual(result['totalCosts'], 5635.0)

    def test_mismatched_lengths(self):
        """Edge Case: test that arrays that aren't the right size throws IndexError"""
        self.assertRaises(IndexError, get_summary_stats, [[1,2,3,4]])


class Test_get_numeric_value(unittest.TestCase):
    headers = ['Column 1', 'Column 2', 'Column 3']
    row = ['1', '2.5', '3']
    def test_get_values(self):
        """Make sure correct row value gets returned from this helper function"""
        self.assertEqual(get_numeric_value(self.headers, self.row, 'Column 1'), 1.0) 
        self.assertEqual(get_numeric_value(self.headers, self.row, 'Column 2'), 2.5) 
        self.assertEqual(get_numeric_value(self.headers, self.row, 'Column 3'), 3.0) 
    
    def test_out_of_bounds(self):
        """Edge case: testing out of bounds indexing"""
        self.assertRaises(ValueError, get_numeric_value, self.headers, self.row, "fake column")

    def test_empty_arrays(self):
        """Edge case: testing empty row, header and column name values"""
        self.assertRaises(ValueError, get_numeric_value, [], self.row, "fake column")
        self.assertRaises(ValueError, get_numeric_value, self.headers, [], "fake column")
        self.assertRaises(ValueError, get_numeric_value, [], [], "fake column")

class Test_iterate_through_dataset(unittest.TestCase):

    def test_iterare_through_dataset(self):
        """
        Tests if iterate_through_dataset return the right output.
        """
        self.assertEqual(iterate_through_dataset("WV", 14), {"total_spills":2, "total_cost": 11827941})
        self.assertEqual(iterate_through_dataset("RICE", 13), {"total_spills":6, "total_cost":49903})
        self.assertEqual(iterate_through_dataset("FARIBAULT", 12), {"total_spills":2, "total_cost": 63349})

    def test_iterate_out_of_bounds(self):
        """
        Tests for when the index for the column entered is out of bounds
        """
        self.assertRaises(IndexError, iterate_through_dataset, "WV", 30)

    def test_iterate_wrong_arguments(self):
        """
        Tests when the arguments are not either a state, a county or a city for 
        first argument and/or when the second argument is not the right index for a 
        column representing a city, county or state. 
        """
        self.assertEqual(iterate_through_dataset("WV", 12),{"total_spills":0, "total_cost":0} )
        self.assertEqual(iterate_through_dataset("Random", 34), {"total_spills":0, "total_cost":0})

class Test_lookup_by_location(unittest.TestCase):

    def test_output(self):
        """
        Test if lookup_by_location return the right output
        """
        self.assertEqual(lookup_by_location("FARIBAULT", "WV", "RICE"), 
                         { 
        "city_spills": 2,
        "city_costs": 63349,
        "county_spills":6,
        "county_costs": 49903,
        "state_spills": 2, 
        "state_costs": 11827941
            })
        
        self.assertEqual (lookup_by_location("RANDOM", "Wallah", "Nukuri"),
                          { 
        "city_spills": 0,
        "city_costs": 0,
        "county_spills": 0,
        "county_costs": 0,
        "state_spills": 0, 
        "state_costs": 0
            } )
        
class Test_lookup_by_state(unittest.TestCase):

    def test_lookup_by_state(self):

        """
        Tests if the function look_up_by_state return the right output
        """
        self.assertEqual(lookup_by_state("WV"), {"total_spills":2, "total_cost": 11827941})
        self.assertEqual(lookup_by_state("Random"), {"total_spills":0, "total_cost": 0})

class Test_lookup_by_county(unittest.TestCase):

    def test_lookup_by_county(self):
        """
        Tests of the function lookup_by_county returns the right output
        """
        self.assertEqual (lookup_by_county("Rice"), {"total_spills":6, "total_cost":49903})
        self.assertEqual (lookup_by_county("RANDOM"), {"total_spills":0, "total_cost":0})

class Test_lookup_by_city(unittest.TestCase):

    def test_lookup_by_city (self):
        """
        Tests if it generates the right output for lookup_by_city 
        """
        self.assertEqual(lookup_by_city("FARIBAULT", {"total_spills":2, "total_cost": 63349}))
        self.assertEqual(lookup_by_city("RANDOM"), {"total_spills":0, "total_cost": 0})

if __name__ == "__main__":
    unittest.main() 
