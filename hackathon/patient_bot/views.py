import random

from django.http import HttpResponse
from .models import CbcReport
from django.shortcuts import render
from pymongo import MongoClient
import csv
from bson.json_util import dumps

client = MongoClient('localhost', 33000)
database = client['hackathon']
cbc_report_coll = database['cbc_report']
ref_range_coll = database['reference_range']
HIST_KEYS = ['Serial Number', 'Age', 'Platelets']

def index(request):
    context = {}
    data_json = get_json_from_csv()
    for key in HIST_KEYS:
        context[key] = _chart_data_provider(data_json, key)
    # context[ref_range] = {}
    # for key in data_json:
    #     context[ref_range][key] = ref_range(20, key)

    return render(request, 'templates/index.html', context)

def report(request):
    context = {}
    if request.method == 'POST':
        file = request.FILES.get('report')
        file_path = handle_uploaded_file(file)
        data_json = get_json_from_csv(file_path)
        ref = ref_range(data_json['Age'][0], data_json['Gender'][0])
        context['looper'] = []
        for key in data_json:
            a = {
                "name": key,
                "value": data_json[key],
                "ref_range": ref[0].get(key, random.randint(1,1000)),
                "score": 10
            }
            context['looper'].append(a)
        context['chart_looper'] = []
        for key in HIST_KEYS:
            b = {}
            b['data'] = _chart_data_provider(data_json, key)
            b['name'] = key
            context['chart_looper'].append(b)
    return  render(request, 'templates/index.html', context)

def handle_uploaded_file(f):
    with open('/tmp/report_tmp.csv', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return '/tmp/report_tmp.csv'

def get_json_from_csv(file_pointer='/tmp/report_tmp.csv'):
    '''
    file_content: Serial Number	Age	Gender	WBC(10^3/uL)	RBC(10^6/uL)	HGB(g/dL)	HCT(%)	Platelets	MCV(fL)
    MCH(pg)	MCHC(g/dL)	NEUT#(10^3/uL)	LYMPH#(10^3/uL)	MONO#(10^3/uL)	EO#(10^3/uL)	BASO#(10^3/uL)	NEUT%(%)
    LYMPH%(%)	MONO%(%)	EO%(%)	BASO%(%)	RDW-CV(%)
    :param file_pointer:
    :return:takes file pointer and returns data.
    '''
    data_json = {}
    with open(file_pointer, newline='') as csv_file:
        csvreader = csv.reader(csv_file, delimiter='"', quotechar='|')
        i = 0
        for row in csvreader:
            if not i:
                headers = row[0].split(',')
                for header in headers:
                    data_json[header] = []
            else:
                data = row[0].split(',')
                for index, item in enumerate(data):
                    data_json[headers[index]].append(item)
            i += 1
    return data_json


def _chart_data_provider(data_json, field):
    '''
    :param field:
    :return: all the values of fields in a list
    '''
    if field is not "Gender":
        return [float(x) for x in data_json[field]]
    return data_json[field]

def ref_range(age, gender):
    '''
    :param age:
    :param field:
    :return: returns reference range of a item.
    '''
    query = {
        'age_high': {'$gte':int(age)},
        'age_low': {'$lte':int(age)},
        'gender': gender
    }
    doc = ref_range_coll.find(query)
    d = dumps(doc)
    d = eval(d)
    return d

def comments(data):
    pass

def suggestions(data):
    pass