import datetime
from pymongo import MongoClient
import csv
client = MongoClient('localhost', 33000)
database = client['hackathon']
cbc_report_coll = database['cbc_report']
key_mapping = {
    "Serial Number": "sample_id",
    "Age": "age",
    "Gender": "gender",
    "WBC(10^3/uL)": "wbc",
    "RBC(10^6/uL)": "rbc",
    "HGB(g/dL)": "hgb",
    "HCT(%)": "hct",
    "Platelets": "platelets",
    "MCV(fL)": "mcv",
    "MCH(pg)": "mch",
    "MCHC(g/dL)": "mchc",
    "NEUT#(10^3/uL)": "neutrophil",
    "LYMPH#(10^3/uL)": "lymphocyte",
    "MONO#(10^3/uL)": "monocyte",
    "EO#(10^3/uL)": "eosinophil",
    "BASO#(10^3/uL)": "basophil",
    "NEUT%(%)": "neutrophil",
    "LYMPH%(%)": "lympocyte",
    "MONO%(%)": "monocyte",
    "EO%(%)": "eosinophil",
    "BASO%(%)": "basophil",
    "RDW-CV(%)": "rdw_cv"
    }

def upload_report_to_db():
    # inserted_ids = cbc_report_coll.insert_many([{'i': i} for i in range(10000)]).inserted_ids
    data_list = []
    global key_mapping
    with open('/tmp/train_data.csv', newline='') as csv_file:
        csvreader = csv.reader(csv_file, delimiter='"', quotechar='|')
        i = 0
        for row in csvreader:
            data_json = {}
            if not i:
                headers = row[0].split(',')
            else:
                data = row[0].split(',')
                # import pdb;pdb.set_trace()
                for index, item in enumerate(data):
                    if key_mapping[headers[index]] in ['gender']:
                        data_json[key_mapping[headers[index]]] = item
                    elif key_mapping[headers[index]] in ['age', 'sample_id', 'platelets']:
                        data_json[key_mapping[headers[index]]] = int(item)
                    else:
                        data_json[key_mapping[headers[index]]] = float(item)
                    data_json['upload_time'] = datetime.datetime.now()
                # print(data_json)
                # cbc_report_coll.insert_one(data_json)
                data_list.append(data_json)

            i += 1
    # a = cbc_report_coll.insert_many(data_list).inserted_ids
    # print(data_list)
    return data_list

def upload_report(data_list):
    print(type(l))
    a = cbc_report_coll.insert_many(l, ordered=True)
    print(cbc_report_coll.count())

l = upload_report_to_db()
upload_report(l)