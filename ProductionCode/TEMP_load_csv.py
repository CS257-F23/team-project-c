import csv

rows = []

with open('/Users/henry/Desktop/cs257/team-project-c/Data/OilPipelineAccidents.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        rows.append(row)

print(rows[2])