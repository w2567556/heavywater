import argparse
import csv
import json

def to_json(input_path, output_path, version):
    output = {}
    output['version'] = version
    output['plaid_to_harvest'] = {}
    with open(input_path) as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        next(reader, None)  # skip the headers


        for row in reader:
            output['plaid_to_harvest'][row[2].strip()] = row[0].strip()

    with open(output_path, 'w') as outfile:
        json.dump(output, outfile)
    return "Json saved to: {}".format(output_path)
        



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="example run: python bin/plaid_to_harvest_json.py --input data/plaid_to_harvest_v1.csv --version 1")
    parser.add_argument("-i", "--input", help="input csv, expects Heeader ['Harvest Category', 'Plaid Category Id'] and data in csv format", required=True)
    parser.add_argument("-v", "--version", help="version of dataset", required=True)
    args = parser.parse_args()

    outpath = "data/plaid_to_harvest_v{}.json".format(args.version)

    to_json(args.input, outpath, args.version)
