import random

import datetime
from django.http import HttpResponse
from .models import CbcReport
from django.shortcuts import render
from pymongo import MongoClient, DESCENDING, ASCENDING
import csv
from bson.json_util import dumps

client = MongoClient('localhost', 33000)
database = client['hackathon']
cbc_report_coll = database['cbc_report']
ref_range_coll = database['reference_range']
HIST_KEYS = ["rbc", "wbc", "platelets"]

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

def chart(request):
    context = {}
    return render(request, 'templates/chart.html', context)

def custom(request):
    if request.method == 'POST':
        file = request.FILES.get('report')
        file_path = handle_uploaded_file(file)
        return render(request, 'templates/custom_chart.html', context={})

def index(request):
    context = {}

    if request.method == 'POST':
        file = request.FILES.get('report')
        file_path = handle_uploaded_file(file)
    else:
        sample_id = random.randint(1, 10000)
        report = get_last_report(sample_id)
        old_reports = get_all_reports(sample_id)
        last_report = get_last_report(sample_id, i=1)
        ref = ref_range(report['gender'][0])
        context['looper'] = []
        context['old_reports'] = old_reports
        for key in report:
            if key not in ["_id"]:
                a = {
                    "name": key,
                    "value": report[key],
                    "ref_range": ref[0].get(key, random.randint(1, 1000)),
                    "last_value": last_report[key] if last_report else "not present"
                }
                context['looper'].append(a)
    # for key in HIST_KEYS:
    #     context[key] = _chart_data_provider(data_json, key)
    # context[ref_range] = {}
    # for key in data_json:
    #     context[ref_range][key] = ref_range(20, key)

    return render(request, 'templates/index.html', context)

def search(request):
    context = {}
    if request.method == 'GET':
        sample_id = int(request.GET.get('sample_id'))
    else:
        sample_id = random.randint(1, 10000)
    report = get_last_report(sample_id)
    old_reports = get_all_reports(sample_id)
    last_report = get_last_report(sample_id, i=1)
    ref = ref_range(report['gender'][0])
    context['looper'] = []
    context['old_reports'] = old_reports
    for key in report:
        if key not in ["_id"]:
            a = {
                "name": key,
                "value": report[key],
                "ref_range": ref[0].get(key, random.randint(1, 1000)),
                "last_value": last_report[key] if last_report else "not present"
            }
            context['looper'].append(a)
    return render(request, 'templates/index.html', context)

def report(request):
    context = {}
    # a = upload_report_to_db()
    if request.method == 'POST':
        file = request.FILES.get('report')
        file_path = handle_uploaded_file(file)
        data_json = get_json_from_csv(file_path)
        report_json = get_last_report(data_json['sample_id'])
        old_reports = get_all_reports(data_json['sample_id'])
        inserted_id = cbc_report_coll.insert_one(data_json).inserted_id
        # import pdb;pdb.set_trace()
        ref = ref_range(data_json['gender'][0])
        context['looper'] = []
        context['old_reports'] = old_reports
        for key in data_json:
            if key not in ["_id"]:
                a = {
                    "name": key,
                    "value": data_json[key],
                    "ref_range": ref[0].get(key, random.randint(1,1000)),
                    "last_value": report_json[key] if report_json else "not present"
                }
                context['looper'].append(a)
        context['chart_looper'] = HIST_KEYS
        # for key in HIST_KEYS:
        #     b = {'data': _chart_data_provider(data_json, key), 'name': key}
        #     context['chart_looper'].append(b)
    return render(request, 'templates/index.html', context)

def handle_uploaded_file(f):
    with open('/var/lib/tomcat7/webapps/custom-knowledge/data/hack_data.csv', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return '/var/lib/tomcat7/webapps/custom-knowledge/data/hack_data.csv'

def get_last_report(sample_id, i=0):
    report_json = cbc_report_coll.find({"sample_id": sample_id}, sort=[("upload_time", DESCENDING)])
    try:
        return report_json[i]
    except IndexError as e:
        return {}

def get_all_reports(sample_id):
    report_json = cbc_report_coll.find({"sample_id": sample_id}, sort=[("upload_time", DESCENDING)])
    return_list = []
    for report in report_json:
        report['id'] = report['_id']
        return_list.append(report)
    return return_list

def get_json_from_csv(file_pointer='/tmp/report_tmp.csv'):
    '''
    file_content: Serial Number	Age	Gender	WBC(10^3/uL)	RBC(10^6/uL)	HGB(g/dL)	HCT(%)	Platelets	MCV(fL)
    MCH(pg)	MCHC(g/dL)	NEUT#(10^3/uL)	LYMPH#(10^3/uL)	MONO#(10^3/uL)	EO#(10^3/uL)	BASO#(10^3/uL)	NEUT%(%)
    LYMPH%(%)	MONO%(%)	EO%(%)	BASO%(%)	RDW-CV(%)
    :param file_pointer:
    :return:takes file pointer and returns data.
    '''
    data_json = {}
    global key_mapping
    with open(file_pointer, newline='') as csv_file:
        csvreader = csv.reader(csv_file, delimiter='"', quotechar='|')
        i = 0
        for row in csvreader:
            if not i:
                headers = row[0].split(',')
            else:
                data = row[0].split(',')
                for index, item in enumerate(data):
                    if key_mapping[headers[index]] in ['gender']:
                        data_json[key_mapping[headers[index]]] = item
                    elif key_mapping[headers[index]] in ['age', 'sample_id', 'platelets']:
                        data_json[key_mapping[headers[index]]] = int(item)
                    else:
                        data_json[key_mapping[headers[index]]] = float(item)
            data_json['upload_time'] = datetime.datetime.now()
            i += 1

    return data_json


def _chart_data_provider(data_json, field):
    '''
    :param field:
    :return: all the values of fields in a list
    '''
    if field is not "gender":
        return [float(x) for x in data_json[field]]
    return data_json[field]

def ref_range(gender):
    '''
    :param age:
    :param field:
    :return: returns reference range of a item.
    '''
    query = {
        'gender': gender
    }
    doc = ref_range_coll.find(query)
    d = dumps(doc)
    d = eval(d)
    return d

def show_report(request, report_id):
    from bson import ObjectId
    id = ObjectId(report_id)
    report_json = cbc_report_coll.find_one({"_id": id})
    del report_json['_id']
    context = {'data': report_json}
    return render(request, 'templates/table.html', context)


def comments(data):
    pass

def suggestions(data):
    pass