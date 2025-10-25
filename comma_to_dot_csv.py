import csv

input_file = r"electricityData\tibber_data.csv"
output_file = r"electricityData\tibber_data_new.csv"

with open(input_file, "r", encoding="utf-8", newline="") as infile, \
     open(output_file, "w", encoding="utf-8", newline="") as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        new_row = []
        for cell in row:
            # If cell is quoted numeric with comma decimal → replace
            if cell.replace(",", "").replace(".", "").replace("-", "").isdigit() or "," in cell:
                try:
                    new_row.append(cell.replace(",", "."))
                except:
                    new_row.append(cell)
            else:
                new_row.append(cell)
        writer.writerow(new_row)
