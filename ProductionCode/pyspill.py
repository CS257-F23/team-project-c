import json

sample_data = [ 
    # header row
    ['Report Number', 'Supplemental Number', 'Accident Year', 'Accident Date/Time', 'Operator ID', 'Operator Name', 'Pipeline/Facility Name', 'Pipeline Location', 'Pipeline Type', 'Liquid Type', 'Liquid Subtype', 'Liquid Name', 'Accident City', 'Accident County', 'Accident State', 'Accident Latitude', 'Accident Longitude', 'Cause Category', 'Cause Subcategory', 'Unintentional Release (Barrels)', 'Intentional Release (Barrels)', 'Liquid Recovery (Barrels)', 'Net Loss (Barrels)', 'Liquid Ignition', 'Liquid Explosion', 'Pipeline Shutdown', 'Shutdown Date/Time', 'Restart Date/Time', 'Public Evacuations', 'Operator Employee Injuries', 'Operator Contractor Injuries', 'Emergency Responder Injuries', 'Other Injuries', 'Public Injuries', 'All Injuries', 'Operator Employee Fatalities', 'Operator Contractor Fatalities', 'Emergency Responder Fatalities', 'Other Fatalities', 'Public Fatalities', 'All Fatalities', 'Property Damage Costs', 'Lost Commodity Costs', 'Public/Private Property Damage Costs', 'Emergency Response Costs', 'Environmental Remediation Costs', 'Other Costs', 'All Costs'], 
  
    # sample data row 1
    ['20100016', '17305', '2010', '1/1/2010 7:15 AM', '32109', 'ONEOK NGL PIPELINE LP', 'KINDER MORGAN JCT', 'ONSHORE', 'ABOVEGROUND', 'HVL OR OTHER FLAMMABLE OR TOXIC FLUID, GAS', 'LPG (LIQUEFIED PETROLEUM GAS) / NGL (NATURAL GAS LIQUID)', '', 'MCPHERSON', 'MCPHERSON', 'KS', '38.6707', '-97.78123', 'INCORRECT OPERATION', 'PIPELINE/EQUIPMENT OVERPRESSURED', '21', '0.1', '0', '21', 'NO', 'NO', 'NO', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '110', '1517', '0', '0', '0', '0', '1627'],
   
    # sample data row 2
    ['20100254', '17331', '2010', '1/4/2010 8:30 AM', '15786', 'PORTLAND PIPELINE CORP', '24-INCH MAIN LINE', 'ONSHORE', 'ABOVEGROUND', 'CRUDE OIL', '', '', 'RAYMOND', 'CUMBERLAND', 'ME', '43.94028', '-70.49336', 'MATERIAL/WELD/EQUIP FAILURE', 'PUMP OR PUMP-RELATED EQUIPMENT', '0.12', '0', '0.12', '0', 'NO', 'NO', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '4000', '8', '0', '0', '0', '0', '4008']
]

headers = sample_data[0]


def load_dada():
    """
    Assigned: Feraidon 
    """
    return

       
def lookup_by_company(company):
    """Return a dictionary with summary statistics about all accidents involving the given company.

    Args:
        company (str): The name of the company to search for.

    Returns:
        dict: the output dictionary creates by get_summary_stats()
        If no accidents are found for the given company, returns None.
    
    Author: Henry
    """
     
    indexOfOperatorName = headers.index("Operator Name")
    relevant_rows = [accident for accident in sample_data if accident[indexOfOperatorName].lower() == company.lower()]
    return get_summary_stats(relevant_rows)

def get_summary_stats(rows):
    """Calculate summary statistics for a list of oil spill accidents.

    Args:
        rows (list of lists): a list of rows to compute stats for

    Returns:
        dict: 
            - 'accidentCount': The total number of accidents.
            - 'totalUnintentionalRelease': The total amount of unintentional release in barrels.
            - 'totalNetLoss': The total net loss in barrels.
            - 'totalCosts': The total cost of all accidents.
        If the input list is empty, returns None.

    Author: Henry
    """
    
    accidentCount = len(rows)
    if accidentCount > 0:
        totalUnintentionalRelease = 0 
        totalNetLoss = 0
        totalCosts = 0

        for accident in rows:
            totalUnintentionalRelease += get_numeric_value(headers, accident, "Unintentional Release (Barrels)")
            totalNetLoss += get_numeric_value(headers, accident, "Net Loss (Barrels)")
            totalCosts += get_numeric_value(headers, accident, "All Costs")
        
        return {'accidentCount': accidentCount, 
                'totalUnintentionalRelease':totalUnintentionalRelease, 
                'totalNetLoss': totalNetLoss, 
                'totalCosts' : totalCosts
                } 
    else:
        return None

def get_numeric_value(headers, row, column_name):
    """Given a list of headers, a row of data, and a column name, returns the value in the specified column as a float.

    Args:
        headers (list of str): A list of column headers.
        row (list of str): A list of values corresponding to a single row of data.
        column_name (str): The name of the column to retrieve the value from.

    Returns:
        float: The value in the specified column as a float.
    """
    index = headers.index(column_name)
    return float(row[index])

print(json.dumps(lookup_by_company("PORTLAND PIPELINE CORP"), indent=4))
      

def lookup_by_location(city, county, state):
    """
    Assigned: Paul
    """
    return


# Command Line stuff - James


