import argparse
import csv
import json

def to_json(input_path, output_path, version):
    output = {}
    output['version'] = version
    output['categories'] = []
    with open(input_path) as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        next(reader, None)  # skip the headers

        for cat, cl, id in reader:
            row = {
                'category': cat.strip(),
                'classification':  cl.strip(),
                'harvest_id':  id.strip()
            }
            output['categories'].append(row)
    with open(output_path, 'w') as outfile:
        json.dump(output, outfile)
    return "Json saved to: {}".format(output_path)
        



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="example run: python bin/plaid_categorization_csv_to_json.py --input data/harvest_category_classification_v1.csv --version 1")
    parser.add_argument("-i", "--input", help="input csv, expects Heeader ['Category', 'Need/Want'] and data in csv format")
    parser.add_argument("-v", "--version", help="version of dataset")
    args = parser.parse_args()

    outpath = "data/harvest_category_classification_v{}.json".format(args.version)

    to_json(args.input, outpath, args.version)
