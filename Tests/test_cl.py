import unittest
import subprocess
from ProductionCode.pyspill import *

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
    def test_output(self):
        """ Test whether lookup_by_city returns the right output. """
        self.assertEqual(lookup_by_city("FLOODWOOD", "ST. LOUIS", "MN"), {
            "total_spills": 1,
            "total_cost": 31000.0
        })

    def test_invalid_county(self):
        """ Test for when we enter the invalid county in test_by_city. """
        self.assertEqual(lookup_by_city ("FLOODWOOD", "Random", "MN"), {
            "total_spills": 1,
            "total_cost": 31000.0
        })

    def test_invalid_state(self):
        """ Test for when we enter the invalid state. """
        self.assertEqual(lookup_by_city ("FLOODWOOD", "ST. LOUIS", "Random"), {
            "total_spills": 1,
            "total_cost": 31000.0
        })
    
    def test_invalid_state_and_county(self):
        """ Tests for invalid county and state arguments. """
        self.assertEqual(lookup_by_city ("FLOODWOOD", "RAndom", "random"), {
            "total_spills": 0,
            "total_cost": 0
        })
    
    def test_invalid_city(self):
        """ Test for a invalid city argument. """

        self.assertEqual(lookup_by_city ("FLOODSSS", "ST. LOUIS", "MN"), {
            "total_spills": 0,
            "total_cost": 0
        })

    def test_invalid_city_and_county(self):
        """ Test for invalid city and invalidd county arguments. """
        self.assertEqual(lookup_by_city ("FLOODSS", "Randoom", "MN"), {
            "total_spills": 0,
            "total_cost": 0
        })

    def test_invalid_city_and_state(self):
        """ Tests for invalid city and state arguments. """
        self.assertEqual(lookup_by_city ("Random", "ST. LOUIS", "RANDOMMM"), {
            "total_spills": 0,
            "total_cost": 0
        })

    def test_invalid_arguments(self):
        """ Test when all the arguement inputs are invalid. """
        self.assertEqual(lookup_by_city ("FRandomD", "ST. random LOUIS", " random MN"), {
            "total_spills": 0,
            "total_cost": 0
        })


class TestLookupByStateOrCounty(unittest.TestCase):
    def test_output(self):
        """ Test whether lookup_by_state_or_county return the right output. """
        self.assertEqual(lookup_state_or_county("WV", 14), {
            'total_spills': 2, 
            'total_cost': 11827941.0
        })
        
        self.assertEqual(lookup_state_or_county("ST. LOUIS", 13), {
            'total_spills': 3, 
            'total_cost': 31275.0
        })

    def test_invalid_county_or_state(self):
        """ Test for invalid state input. """
        self.assertEqual(lookup_state_or_county("Randommm", 13), {
            'total_spills': 0, 
            'total_cost': 0
        })
        
        self.assertEqual(lookup_state_or_county("Randommm", 14), {
            'total_spills': 0, 
            'total_cost': 0
        })

    def test_index_out_of_range(self):
        """ Test for index out of range. """
        self.assertRaises(IndexError, lookup_state_or_county, "WV", 48)

    def test_wrong_column_index(self):
        """ Test when there is a wrong column index input. """
        self.assertEqual(lookup_state_or_county("WV", 8), {
                'total_spills': 0, 
                'total_cost': 0
        })
        
class TestLookupByLocation(unittest.TestCase):
    def test_output(self):
        """ Test if lookup_by_location return the right output. """
        self.assertEqual(lookup_by_location ("FLOODWOOD", "ST. LOUIS", "MN"), {
            "total_spills": 1,
            "total_cost": 31000.0
        })

    def test_invalid_state(self):
        """ Tests for invalid state argument. """        
        self.assertEqual(lookup_by_location ("FLOODWOOD", "ST. LOUIS", "Random"), {
            "total_spills": 1,
            "total_cost": 31000.0
        })

    def test_invalid_county(self):
        """ Tests for invalid county argument. """
        self.assertEqual(lookup_by_location ("FLOODWOOD", "Randomman", "MN"), {
            "total_spills": 1,
            "total_cost": 31000.0
        })

    def test_invalid_state_and_county(self):
        """ Tests for invalid state and county argument. """
        self.assertEqual(lookup_by_city ("FLOODWOOD", "Randomman", "Random"), {
            "total_spills": 0,
            "total_cost": 0
        })

    def test_invalid_city(self):
        """ Tests for invalid city argument. """
        self.assertEqual(lookup_by_city ("Random", "ST. LOUIS", "MN"), {
            "total_spills": 0,
            "total_cost": 0
        })

    def test_invalid_city_and_county(self):
        """ Tests for invalid city and county argument. """
        self.assertEqual(lookup_by_city ("FLOdsfs", "Random", "MN"), {
            "total_spills": 0,
            "total_cost": 0
        })

    def test_invalid_city_county_and_state(self):
        """ Tests for invalid city, county and state argument. """
        self.assertEqual(lookup_by_location("Random", "RANDOOM", "RANDOMMM"), {  
            "total_spills": 0,
            "total_cost": 0
        })
        
class TestCL(unittest.TestCase):
    """ Author: James Commons """

    def setUp(self):
        load_data()

    def test_no_args(self):
        """ Tests that help/usage is printed if no arguments are given. """
        code = subprocess.Popen(['python3', '-u', 'ProductionCode/pyspill.py'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()

        self.assertEqual(out[:6], "Usage:")

    def test_help(self):
        """ Tests that help/usage statement is printed with the help command. """
        code = subprocess.Popen(['python3', '-u', 'ProductionCode/pyspill.py', 'help'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()

        self.assertEqual(out[:6], "Usage:")

    def test_bad_command(self):
        """ Tests that help/usage printed if nonexistant command was given. """
        code = subprocess.Popen(['python3', '-u', 'ProductionCode/pyspill.py', 'dne'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()

        self.assertEqual(out[:6], "Usage:")

    def test_lookup_opt_c_upper(self):
        """ Test that lookup company works given option -c in command line. Upper case. """
        code = subprocess.Popen(['python3', '-u', 'ProductionCode/pyspill.py', 'lookup', '-c', 'CONOCOPHILLIPS'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()

        self.assertEqual(out, "{'accidentCount': 34, 'totalUnintentionalRelease': 4873.769999999997, " \
                              "'totalNetLoss': 4776.61, 'totalCosts': 8697383.0}\n")
        
    def test_lookup_opt_company_lower(self):
        """ Test that lookup company works given option --company in command line. Lower case. """
        code = subprocess.Popen(['python3', '-u', 'ProductionCode/pyspill.py', 'lookup', '-c', 'exxonmobil pipeline co'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()

        self.assertEqual(out, "{'accidentCount': 49, 'totalUnintentionalRelease': 5926.939999999999, " \
                              "'totalNetLoss': 3094.3799999999997, 'totalCosts': 149166535.0}\n")
        
    def test_lookup_company_and_location(self):
        """ Test that trying to lookup both company and location prints an error. """
        code = subprocess.Popen(['python3', '-u', 'ProductionCode/pyspill.py', 'lookup', '-c', 
                                 'exxonmobil pipeline co', '--state', 'tx'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()

        self.assertEqual(out, 'You can only lookup by location or company, not both at the same time.\n')
        
    def test_lookup_location(self):
        """ Test that lookup location works when all three parameters specified. """
        code = subprocess.Popen(['python3', '-u', 'ProductionCode/pyspill.py', 'lookup', '--city', 
                                 'COVE', '--county', 'chambers', '--state', 'Tx'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()

        self.assertEqual(out, "{'total_spills': 1, 'total_cost': 501600.0}\n")
    
    def test_lookup_location_by_state(self):
        """ Test lookup location by state prints all spills in a state. """
        code = subprocess.Popen(['python3', '-u', 'ProductionCode/pyspill.py', 'lookup', '--state', 'MA'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()

        self.assertEqual(out, "{'total_spills': 2, 'total_cost': 543943.0}\n")

if __name__ == "__main__":
    unittest.main() 
