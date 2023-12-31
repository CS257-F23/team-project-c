import unittest
import subprocess
from pyspill import *


class TestArgumentParser(unittest.TestCase):
    # Some tests can only be done through integration testing below since
    # argparse will automatically exit when options like -h are given, or
    # if arguments are not correct.

    def setUp(self):
        self.main_parser = setup_subparsers(get_main_parser())

    
    def test_lookup_parser_company(self):
        """ Test that the lookup company parser returns expected args. """
        args = self.main_parser.parse_args(['lookup', '-c', 'company_name'])
        self.assertEqual(args.company, 'company_name')


    def test_lookup_parser_location(self):
        """ Test that the lookup location parser returns expected args. """
        args = self.main_parser.parse_args(['lookup', '-l', 
                                            '--city', 'city', 
                                            '--county', 'county', 
                                            '--state', 'state'])
        self.assertEqual(args.city, 'city')
        self.assertEqual(args.county, 'county')
        self.assertEqual(args.state, 'state')


    def test_list_parser_location_by_state(self):
        """ Test that the list location by state parser returns expected args. """
        args = self.main_parser.parse_args(['list', '-s', 'state'])
        self.assertEqual(args.state, 'state')


class TestCLIntegration(unittest.TestCase):
    """ Author: James Commons """

    def test_no_args(self):
        """ Tests that help/usage is printed if no arguments are given. """
        code = subprocess.Popen(['python3', '-u', 'pyspill.py'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()

        self.assertEqual(out[:6], "usage:")


    def test_help(self):
        """ Tests that help/usage statement is printed with the help command. """
        code = subprocess.Popen(['python3', '-u', 'pyspill.py', 'help'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()

        self.assertEqual(out[:6], "usage:")


    def test_bad_command(self):
        """ Tests that help/usage printed if nonexistant command was given. """
        code = subprocess.Popen(['python3', '-u', 'pyspill.py', 'dne'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()

        self.assertEqual(err[:6], "usage:")


    def test_lookup_opt_c_upper(self):
        """ Test that lookup company works given option -c in command line. Upper case. """
        code = subprocess.Popen(['python3', '-u', 'pyspill.py', 'lookup', '-c', 'CONOCOPHILLIPS'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()

        self.assertEqual(out, 'Total accidents: 34\n'
                              'Total volume of oil released (barrels): 4,776.61\n'
                              'Total cost: $8,697,383\n')
        

    def test_lookup_opt_company_lower(self):
        """ Test that lookup company works given option --company in command line. Lower case. """
        code = subprocess.Popen(['python3', '-u', 'pyspill.py', 'lookup', '-c', 'exxonmobil pipeline co'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()
        
        self.assertEqual(out, 'Total accidents: 49\n'
                              'Total volume of oil released (barrels): 3,094.38\n'
                              'Total cost: $149,166,535\n')
        

    def test_lookup_company_and_location(self):
        """ Test that trying to lookup both company and location prints an error. """
        code = subprocess.Popen(['python3', '-u', 'pyspill.py', 'lookup', '-l', '-c', 
                                 'exxonmobil pipeline co', '--state', 'tx'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()

        self.assertEqual(err[:6], 'usage:')
        

    def test_lookup_location(self):
        """ Test that lookup location works when all three parameters specified. """
        code = subprocess.Popen(['python3', '-u', 'pyspill.py', 'lookup', '-l', '--city', 
                                 'COVE', '--county', 'chambers', '--state', 'Tx'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()

        self.assertEqual(out, 'Total accidents: 1\n'
                              'Total volume of oil released (barrels): 9.10\n'
                              'Total cost: $501,600\n')
    

    def test_lookup_location_by_state(self):
        """ Test lookup location by state prints all spills in a state. """
        code = subprocess.Popen(['python3', '-u', 'pyspill.py', 'lookup', '-l', '--state', 'MA'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()

        self.assertEqual(out, 'Total accidents: 2\n'
                              'Total volume of oil released (barrels): 0.00\n'
                              'Total cost: $543,943\n')
        

    def test_leaders(self):
        code = subprocess.Popen(['python3', '-u', 'pyspill.py', 'leaders'], 
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
        out, err = code.communicate()
        code.terminate()      

        self.assertIn('10. NUSTAR LOGISTICS, L.P.', out)

    
if __name__ == "__main__":
    unittest.main()