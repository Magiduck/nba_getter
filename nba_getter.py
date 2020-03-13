import json
import csv

import requests
from tqdm import tqdm

# Set of classes
BANNED_CLASSES = ('Branchiopoda', 'Remipedia', 'Cephalocarida', 'Maxillopoda', 'Ostracoda', 'Malacostraca',
                  'Pycnogonida')


def get_order_from_taxa():
    number_of_not_found = 0
    not_found_taxa = []

    with open('taxon_to_order_w_banned_classes.csv', 'a') as out_file:
        csv_writer = csv.writer(out_file)
        with open('all_taxa_in_nature_identification_api.json') as all_taxa_file:
            all_taxa = json.load(all_taxa_file)
            for taxa in tqdm(all_taxa['taxa']):
                # Attempt number 1: assuming the first part of the name is a genus
                assumed_genus = taxa['name'].split(" ")[0]
                taxa_endpoint = f"https://api.biodiversitydata.nl/v2/taxon/query/?defaultClassification.genus={assumed_genus}"
                json_response = requests.get(taxa_endpoint).json()
                result_set = json_response['resultSet']
                if result_set:
                    write_taxon_to_order_entry(result_set, csv_writer, taxa)
                else:
                    # Attempt number 2: assuming the first part of the name is a family
                    assumed_family = assumed_genus
                    taxa_endpoint = f"https://api.biodiversitydata.nl/v2/taxon/query/?defaultClassification.family={assumed_family}"
                    json_response = requests.get(taxa_endpoint).json()
                    result_set = json_response['resultSet']
                    if result_set:
                        write_taxon_to_order_entry(result_set, csv_writer, taxa)
                    else:
                        # Attempt number 3: assuming the first part of the name is an Order
                        assumed_order = assumed_family
                        taxa_endpoint = f"https://api.biodiversitydata.nl/v2/taxon/query/?defaultClassification.order={assumed_order}"
                        json_response = requests.get(taxa_endpoint).json()
                        result_set = json_response['resultSet']
                        if result_set:
                            write_taxon_to_order_entry(result_set, csv_writer, taxa)
                        else:
                            not_found_taxa.append(taxa['name'])
                            # All attempts failed
                            number_of_not_found += 1

            print(f"{not_found_taxa}\n{number_of_not_found} of total {len(all_taxa['taxa'])} not found!")


def write_taxon_to_order_entry(result_set, csv_writer, taxa):
    default_classification = result_set[0]['item']['defaultClassification']
    if 'phylum' in default_classification and 'className' in default_classification and 'order' in default_classification:
        phylum = default_classification['phylum']
        class_name = default_classification['className']
        order = default_classification['order']
        if phylum == 'Arthropoda' and class_name not in BANNED_CLASSES:
            csv_writer.writerow([taxa['name'], order])
        elif class_name == 'Gastropoda' or class_name == 'Clitellata':
            csv_writer.writerow([taxa['name'], order])


if __name__ == '__main__':
    get_order_from_taxa()
