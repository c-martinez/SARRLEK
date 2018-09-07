import os

def split(filehandler, delimiter=',', row_limit=10000, 
    output_name_template='output_%s.csv', output_path='.', keep_headers=True):
    """
    Splits a CSV file into multiple pieces.
    
    A quick bastardization of the Python CSV library.

    Arguments:

        `row_limit`: The number of rows you want in each output file. 10,000 by default.
        `output_name_template`: A %s-style template for the numbered output files.
        `output_path`: Where to stick the output files.
        `keep_headers`: Whether or not to print the headers in each output file.

    Example usage:
    
        >> from toolbox import csv_splitter;
        >> csv_splitter.split(open('/home/ben/input.csv', 'r'));
    
    """
    import csv
    reader = csv.reader(filehandler, delimiter=delimiter)
    current_piece = 1
    current_out_path = os.path.join(
         output_path,
         output_name_template  % current_piece
    )
    current_out_writer = csv.writer(open(current_out_path, 'w'), delimiter=delimiter)
    current_limit = row_limit
    if keep_headers:
        headers = reader.next()
        current_out_writer.writerow(headers)
    for i, row in enumerate(reader):
        if i + 1 > current_limit:
            current_piece += 1
            current_limit = row_limit * current_piece
            current_out_path = os.path.join(
               output_path,
               output_name_template  % current_piece
            )
            current_out_writer = csv.writer(open(current_out_path, 'w'), delimiter=delimiter)
            if keep_headers:
                current_out_writer.writerow(headers)
        current_out_writer.writerow(row)

#main loop for Sneha
#
#edit where does your big single file currently sit?
fileSingleCSVlocation = 'C:/Users/leonard.wee/OneDrive - Maastro - Clinic/Running_Grants/SARRLEK/ct_report_dmg_thoracic_only.csv'
#
#edit where is the folder you want the single results to go? REMEBER TO END WITH A "/" SYMBOL
outputLocation = 'C:/Users/leonard.wee/OneDrive - Maastro - Clinic/Running_Grants/SARRLEK/batch_test_folder/' #edit the path'
#
#this is the output filename format 1.csv, 2.csv, etc etc
outputNameTemplate='%s.csv'
#
#this executes the function above based on the input and output locations
split( open(fileSingleCSVlocation,'r'), row_limit=1,output_name_template=outputNameTemplate, output_path=outputLocation, keep_headers=False )

