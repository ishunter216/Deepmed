import json
from collections import OrderedDict
from pymongo import MongoClient
from bson.son import SON
from pprint import pprint

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'bcancer'
COLLECTION_NAME = 'dataset2'

STATES_NAME_ABRS = {
    "Alabama": "AL",
    "Alaska": "AK",
    "American Samoa": "AS",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District Of Columbia": "DC",
    "Federated States Of Micronesia": "FM",
    "Florida": "FL",
    "Georgia": "GA",
    "Guam": "GU",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Marshall Islands": "MH",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Northern Mariana Islands": "MP",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Palau": "PW",
    "Pennsylvania": "PA",
    "Puerto Rico": "PR",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virgin Islands": "VI",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY"
}

STATES_ABRS = ["AL", "AK", "AS", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FM", "FL", "GA", "GU", "HI", "ID", "IL",
               "IN",
               "IA", "KS", "KY", "LA", "ME", "MH", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
               "NM",
               "NY", "NC", "ND", "MP", "OH", "OK", "OR", "PW", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
               "VI",
               "VA", "WA", "WV", "WI", "WY"]


def aggregate(request):
    mongo_client = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = mongo_client[DBS_NAME][COLLECTION_NAME]
    response = []
    data = collection.aggregate(request)
    for row in data:
        response.append(row)
    mongo_client.close()
    return json.dumps(response)


def find(request, **kwargs):
    mongo_client = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = mongo_client[DBS_NAME][COLLECTION_NAME]
    response = []
    data = collection.find(request, **kwargs)
    for row in data:
        response.append(row)
    mongo_client.close()
    return response


def get_age_group(age):
    age_group = None
    if age >= 80:
        age_group = ["80-84 years", "85+ years"]
    elif age >= 70:
        age_group = ["70-74 years", "75-79 years"]
    elif age >= 60:
        age_group = ["60-64 years", "65-69 years"]
    elif age >= 50:
        age_group = ["50-54 years", "55-59 years"]
    elif age >= 40:
        age_group = ["40-44 years", "45-49 years"]
    elif age >= 30:
        age_group = ["30-34 years", "35-39 years"]
    elif age >= 20:
        age_group = ["20-24 years", "25-29 years"]
    elif age >= 10:
        age_group = ["10-14 years", "15-19 years"]
    elif age >= 0:
        age_group = ["00-04 years", "05-09 years"]

    return age_group


def get_t_size_cm(size_mm):
    t_size_cm = None
    if size_mm >= 50:
        t_size_cm = ">5cm"
    elif size_mm >= 20:
        t_size_cm = {"$in": ["<3cm", ">3cm"]}
    elif size_mm >= 10:
        t_size_cm = "<2cm"
    elif size_mm < 10:
        t_size_cm = "<1cm"

    return t_size_cm


def get_node_range(number):
    """
    90	>9
    95	N/A
    97	>1
    98	N/A
    99	N/A
    :param number:
    :return:
    """
    n_size = None
    if number >= 10:
        # n_size = {"$gte": 10}
        range_list = [x for x in range(10, 90)]
        range_list.append('>9')
        n_size = {"$in": range_list}
    elif number >= 4:
        n_size = {"$in": [4, 5, 6, 7, 8, 9]}
    elif number >= 1:
        n_size = {"$in": [1, 2, 3, '>1']}
    elif number == 0:
        n_size = {"$eq": 0}
    return n_size


def create_filter(input_data, operator='$and'):
    """
    Converts json request to list of dicts formated for use as a match filter in mongodb.
    "age" takes integer age, and groups ages by decades, ex: input 44 (years), outputs ["40-44 years", "45-49 years"]
    "tumor_size_in_mm" takes integer size in mm, and groups by size in cm, ex: input 18 (mm), outputs "<2cm"
    "num_pos_nodes" takes integer number, and groups by custom groups, ex: input 4, output {"$in": [4, 5, 6, 7, 8, 9]}
    :param input_data: json = '{"age": int, ' \
                   '"sex": string, ' \
                   '"tumor_grade": int, ' \
                   '"er_status": "+" or "-", ' \
                   '"pr_status": "+" or "-", ' \
                   '"tumor_size_in_mm": int, ' \
                   '"num_pos_nodes": int, ' \
                   '"her2_status": "+" or "-", ' \
                   '"ethnicity": string}'
    :param operator: {"$and"} or {"or"} as filtering operators
    :return: list of dicts
    """
    input_data = json.loads(input_data)
    filter_list = []
    if 'age' in input_data.keys():
        age = get_age_group(input_data['age'])
        filter_list.append({"age-recode-with-1-year-olds": {"$in": age}})
    if 'tumor_size_in_mm' in input_data.keys():
        t_size_cm = get_t_size_cm(input_data['tumor_size_in_mm'])
        filter_list.append({"t-size-cm": t_size_cm})
    if 'sex' in input_data.keys():
        filter_list.append({"sex": input_data["sex"]})
    if 'tumor_grade' in input_data.keys():
        filter_list.append({"grade": input_data["tumor_grade"]})
    if 'er_status' in input_data.keys():
        filter_list.append({"er-status-recode-breast-cancer-1990": input_data["er_status"]})
    if 'pr_status' in input_data.keys():
        filter_list.append({"pr-status-recode-breast-cancer-1990": input_data["pr_status"]})
    if 'her2_status' in input_data.keys():
        filter_list.append({"derived-her2-recode-2010": input_data['her2_status']})
    if 'num_pos_nodes' in input_data.keys():
        n_size = get_node_range(input_data['num_pos_nodes'])
        filter_list.append({"regional-nodes-positive-1988": n_size})
    if 'ethnicity' in input_data.keys():
        filter_list.append({"race-recode-w-b-ai-api": input_data["ethnicity"]})
    if 'type' in input_data.keys():
        filter_list.append({"type": input_data["type"]})
    if 'breast-adjusted-ajcc-6th-stage-1988' in input_data.keys():
        filter_list.append({"breast-adjusted-ajcc-6th-stage-1988": input_data["breast-adjusted-ajcc-6th-stage-1988"]})
    if 'chemo' in input_data.keys():
        filter_list.append({"chemo": input_data["chemo"]})
    if 'radiation' in input_data.keys():
        filter_list.append({"radiation": input_data["radiation"]})
    if 'surgery' in input_data.keys():
        filter_list.append({"surgery": input_data["surgery"]})

    return {operator: filter_list}


def diagnosis(input_json, limit=20):
    """
    Returned values are grouped by these groups:
    "ethnicity": "White" -> "Caucasian", "Black" -> "African American", "Asian or Pacific Islander" -> "Asian",
        ['Unknown', 'American Indian/Alaska Native'] -> "Other"
    "cod": "Alive" -> "Alive", "Breast" -> "Breast", any_other_value -> "Other"
    Other values are returned as in database
    :param input_json: json
    :param limit: int
    :return: list
    """

    def get_race(race):
        if race == "White":
            return "Caucasian"
        elif race == "Black":
            return "African American"
        elif race == "Asian or Pacific Islander":
            return "Asian"
        elif race in ['Unknown', 'American Indian/Alaska Native']:
            return "Other"
        else:
            return race

    def get_cod(cod):
        if cod not in ['Alive', 'Breast']:
            return "Other"
        else:
            return cod

    def build_dict(item):
        return {'age': item['age-recode-with-single-ages-and-85'],
                'ethnicity': get_race(item['race-recode-w-b-ai-api']),
                'size': item['t-size-cm'],
                'grade': item['grade'],
                'er': item['er-status-recode-breast-cancer-1990'],
                'pr': item['pr-status-recode-breast-cancer-1990'],
                'her2': item['derived-her2-recode-2010'],
                'lat': item['laterality'],
                'site': item['primary-site-labeled'],
                'type': item['type'],
                'stage': item['breast-adjusted-ajcc-6th-stage-1988'],
                '+nodes': item['regional-nodes-positive-1988'],
                'surgery': item['surgery'],
                'chemo': item['chemo'],
                'radiation': item['radiation'],
                'year dx': item['year-of-diagnosis'],
                'survival mos.': item['survival-months'],
                'cod': get_cod(item['cod-to-site-recode'])}

    filters = create_filter(input_json)
    dataset = find(filters, limit=limit)
    results = []
    for item in dataset:
        d = build_dict(item)
        results.append(d)

    if len(results) < 20:
        # print(len(results))
        filters['$and'] = [d for d in filters['$and'] if 't-size-cm' not in d]
        # ts_mm = json.loads(input_json)['tumor_size_in_mm']
        # ts_min = round(ts_mm * 0.8)
        # ts_max = round(ts_mm *1.2)
        # filters['$and'].append({"$and": [{"tumor_size_in_mm": {"$gte": ts_min}},
        #                                  {"tumor_size_in_mm": {"$lte": ts_max}}]})
        dataset = find(filters, limit=limit)
        results = []
        for item in dataset:
            d = build_dict(item)
            results.append(d)
        if len(results) < 20:
            filters['$and'] = [d for d in filters['$and'] if 'race-recode-w-b-ai-api' not in d]
            dataset = find(filters, limit=limit)
            results = []
            for item in dataset:
                d = build_dict(item)
                results.append(d)
            if len(results) < 20:
                filters['$and'] = [d for d in filters['$and'] if 'age-recode-with-single-ages-and-85' not in d]
                dataset = find(filters, limit=limit)
                results = []
                for item in dataset:
                    d = build_dict(item)
                    results.append(d)
                return results
            return results
        return results
    return results


def breast_cancer_at_a_glance():
    result = json.loads(aggregate([
        {"$group": {
            "_id": "$year-of-diagnosis",
            "count": {"$sum": 1}}},
        {"$sort": SON([("_id", 1)])}]))

    return {
        'labels': list(map(lambda x: x['_id'], result)),
        'datasets': [{
            'data': list(map(lambda x: x['count'], result)),
            'label': "Diagnosed",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def breast_cancer_at_a_glance2():
    json_data = {
        "Year": [1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991,
                 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008,
                 2009, 2010, 2011, 2012, 2013, 2014],
        "New Cases": [105.1, 101.9, 100.8, 100.6, 102.1, 102.2, 106.4, 106.5, 111.1, 116, 124.3, 126.8, 134.5, 131.3,
                      127.2, 131.9, 133.9, 132.1, 129.2, 131, 132.7, 133.8, 138.1, 141.5, 141.5, 136.6, 138.8, 135.9,
                      127.1, 128.2, 126.7, 126.4, 128.3, 128.5, 130.9, 127, 130.4, 130.1, 130.8, 130.6],
        "Deaths - US": [31.4, 31.8, 32.5, 31.7, 31.2, 31.7, 31.9, 32.2, 32.1, 32.9, 33, 32.9, 32.7, 33.2, 33.2, 33.1,
                        32.7, 31.6, 31.4, 30.9, 30.6, 29.5, 28.2, 27.5, 26.6, 26.6, 26, 25.6, 25.3, 24.5, 24.1, 23.6,
                        23, 22.6, 22.2, 21.9, 21.5, 21.3, 20.7, 20.5]
    }
    return {
        'labels': [1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991,
                   1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008,
                   2009, 2010, 2011, 2012, 2013, 2014],
        'datasets': [{
            'data': [105.1, 101.9, 100.8, 100.6, 102.1, 102.2, 106.4, 106.5, 111.1, 116, 124.3, 126.8, 134.5, 131.3,
                     127.2, 131.9, 133.9, 132.1, 129.2, 131, 132.7, 133.8, 138.1, 141.5, 141.5, 136.6, 138.8, 135.9,
                     127.1, 128.2, 126.7, 126.4, 128.3, 128.5, 130.9, 127, 130.4, 130.1, 130.8, 130.6]
            ,
            'label': ["New Cases"],
            'borderColor': '#48ccf5',
            'fill': False
        }, {
            'data': [31.4, 31.8, 32.5, 31.7, 31.2, 31.7, 31.9, 32.2, 32.1, 32.9, 33, 32.9, 32.7, 33.2, 33.2, 33.1,
                     32.7, 31.6, 31.4, 30.9, 30.6, 29.5, 28.2, 27.5, 26.6, 26.6, 26, 25.6, 25.3, 24.5, 24.1, 23.6,
                     23, 22.6, 22.2, 21.9, 21.5, 21.3, 20.7, 20.5]
            ,
            'label': ["Deaths - US"],
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def breast_cancer_by_age():
    result = json.loads(aggregate([
        {"$group": {
            "_id": "$age-recode-with-1-year-olds",
            "count": {"$sum": 1}}},
        {"$sort": SON([("_id", 1)])}]))

    return {
        'labels': list(map(lambda x: x['_id'], result)),
        'datasets': [{
            'data': list(map(lambda x: x['count'], result)),
            'label': "Diagnosed",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def breast_cancer_by_state():
    result = json.loads(aggregate([
        {"$group": {
            "_id": "$state",
            "count": {"$sum": 1}}},
        {"$sort": SON([("count", -1), ("_id", -1)])}]))

    values = {}
    for state in STATES_NAME_ABRS:
        st = STATES_NAME_ABRS[state]
        if state in [x['_id'] for x in result]:
            c = [x for x in result if state in x['_id']]
            values["US-" + st] = c[0]['count']
        else:
            values["US-" + st] = 0

    # for row in result:
    #     pprint(row)
    #     if row['_id'] in STATES_NAME_ABRS:
    #         state = STATES_NAME_ABRS[row['_id']]
    #         values["US-" + state] = row['count']

    return {
        'regions': [{
            'scale': ['#47cfd1', '#48ccf5', '#88d0d1', '#b8e8f5'],
            'attribute': 'fill',
            'values': values
        }]
    }


def breast_cancer_by_state2(option):
    if option == 1:
        json_data = [
            {
                "State": "AK",
                "Range": "125.9 to 132.0",
                "Rate": 127.1
            },
            {
                "State": "AL",
                "Range": "118.7 to 125.5",
                "Rate": 120.5
            },
            {
                "State": "AR",
                "Range": "106.6 to 118.3",
                "Rate": 113.9
            },
            {
                "State": "AZ",
                "Range": "106.6 to 118.3",
                "Rate": 115
            },
            {
                "State": "CA",
                "Range": "118.7 to 125.5",
                "Rate": 118.7
            },
            {
                "State": "CO",
                "Range": "118.7 to 125.5",
                "Rate": 124.9
            },
            {
                "State": "CT",
                "Range": "132.3 to 144.9",
                "Rate": 142
            },
            {
                "State": "DC",
                "Range": "132.3 to 144.9",
                "Rate": 139.6
            },
            {
                "State": "DE",
                "Range": "132.3 to 144.9",
                "Rate": 136.9
            },
            {
                "State": "FL",
                "Range": "106.6 to 118.3",
                "Rate": 114.8
            },
            {
                "State": "GA",
                "Range": "118.7 to 125.5",
                "Rate": 124.4
            },
            {
                "State": "HI",
                "Range": "132.3 to 144.9",
                "Rate": 138
            },
            {
                "State": "IA",
                "Range": "125.9 to 132.0",
                "Rate": 125.9
            },
            {
                "State": "ID",
                "Range": "118.7 to 125.5",
                "Rate": 123.2
            },
            {
                "State": "IL",
                "Range": "132.3 to 144.9",
                "Rate": 133.5
            },
            {
                "State": "IN",
                "Range": "118.7 to 125.5",
                "Rate": 121.6
            },
            {
                "State": "KS",
                "Range": "118.7 to 125.5",
                "Rate": 125.5
            },
            {
                "State": "KY",
                "Range": "125.9 to 132.0",
                "Rate": 127.3
            },
            {
                "State": "LA",
                "Range": "118.7 to 125.5",
                "Rate": 122.7
            },
            {
                "State": "MA",
                "Range": "132.3 to 144.9",
                "Rate": 138.4
            },
            {
                "State": "MD",
                "Range": "125.9 to 132.0",
                "Rate": 129.8
            },
            {
                "State": "ME",
                "Range": "125.9 to 132.0",
                "Rate": 127.9
            },
            {
                "State": "MI",
                "Range": "106.6 to 118.3",
                "Rate": 117
            },
            {
                "State": "MN",
                "Range": "125.9 to 132.0",
                "Rate": 130.9
            },
            {
                "State": "MO",
                "Range": "125.9 to 132.0",
                "Rate": 128.9
            },
            {
                "State": "MS",
                "Range": "106.6 to 118.3",
                "Rate": 113.8
            },
            {
                "State": "MT",
                "Range": "125.9 to 132.0",
                "Rate": 128
            },
            {
                "State": "NC",
                "Range": "125.9 to 132.0",
                "Rate": 129.9
            },
            {
                "State": "ND",
                "Range": "106.6 to 118.3",
                "Rate": 114
            },
            {
                "State": "NE",
                "Range": "118.7 to 125.5",
                "Rate": 124
            },
            {
                "State": "NH",
                "Range": "132.3 to 144.9",
                "Rate": 144.9
            },
            {
                "State": "NJ",
                "Range": "132.3 to 144.9",
                "Rate": 134.3
            },
            {
                "State": "NM",
                "Range": "106.6 to 118.3",
                "Rate": 108.2
            },
            {
                "State": "NV",
                "Range": "106.6 to 118.3",
                "Rate": 106.6
            },
            {
                "State": "NY",
                "Range": "132.3 to 144.9",
                "Rate": 132.3
            },
            {
                "State": "OH",
                "Range": "125.9 to 132.0",
                "Rate": 126.6
            },
            {
                "State": "OK",
                "Range": "118.7 to 125.5",
                "Rate": 120.4
            },
            {
                "State": "OR",
                "Range": "106.6 to 118.3",
                "Rate": 118.3
            },
            {
                "State": "PA",
                "Range": "125.9 to 132.0",
                "Rate": 132
            },
            {
                "State": "RI",
                "Range": "132.3 to 144.9",
                "Rate": 133.2
            },
            {
                "State": "SC",
                "Range": "118.7 to 125.5",
                "Rate": 125.1
            },
            {
                "State": "SD",
                "Range": "118.7 to 125.5",
                "Rate": 122.3
            },
            {
                "State": "TN",
                "Range": "106.6 to 118.3",
                "Rate": 118
            },
            {
                "State": "TX",
                "Range": "106.6 to 118.3",
                "Rate": 110.7
            },
            {
                "State": "UT",
                "Range": "106.6 to 118.3",
                "Rate": 117.1
            },
            {
                "State": "VA",
                "Range": "125.9 to 132.0",
                "Rate": 131.1
            },
            {
                "State": "VT",
                "Range": "132.3 to 144.9",
                "Rate": 135.9
            },
            {
                "State": "WA",
                "Range": "132.3 to 144.9",
                "Rate": 134.8
            },
            {
                "State": "WI",
                "Range": "125.9 to 132.0",
                "Rate": 126.9
            },
            {
                "State": "WV",
                "Range": "106.6 to 118.3",
                "Rate": 111.4
            },
            {
                "State": "WY",
                "Range": "118.7 to 125.5",
                "Rate": 124.4
            }
        ]
    elif option == 2:
        json_data = {
            "AK": {
                "Range": "125.9 to 132.0",
                "Rate": 127.1
            },
            "AL": {
                "Range": "118.7 to 125.5",
                "Rate": 120.5
            },
            "AR": {
                "Range": "106.6 to 118.3",
                "Rate": 113.9
            },
            "AZ": {
                "Range": "106.6 to 118.3",
                "Rate": 115
            },
            "CA": {
                "Range": "118.7 to 125.5",
                "Rate": 118.7
            },
            "CO": {
                "Range": "118.7 to 125.5",
                "Rate": 124.9
            },
            "CT": {
                "Range": "132.3 to 144.9",
                "Rate": 142
            },
            "DC": {
                "Range": "132.3 to 144.9",
                "Rate": 139.6
            },
            "DE": {
                "Range": "132.3 to 144.9",
                "Rate": 136.9
            },
            "FL": {
                "Range": "106.6 to 118.3",
                "Rate": 114.8
            },
            "GA": {
                "Range": "118.7 to 125.5",
                "Rate": 124.4
            },
            "HI": {
                "Range": "132.3 to 144.9",
                "Rate": 138
            },
            "IA": {
                "Range": "125.9 to 132.0",
                "Rate": 125.9
            },
            "ID": {
                "Range": "118.7 to 125.5",
                "Rate": 123.2
            },
            "IL": {
                "Range": "132.3 to 144.9",
                "Rate": 133.5
            },
            "IN": {
                "Range": "118.7 to 125.5",
                "Rate": 121.6
            },
            "KS": {
                "Range": "118.7 to 125.5",
                "Rate": 125.5
            },
            "KY": {
                "Range": "125.9 to 132.0",
                "Rate": 127.3
            },
            "LA": {
                "Range": "118.7 to 125.5",
                "Rate": 122.7
            },
            "MA": {
                "Range": "132.3 to 144.9",
                "Rate": 138.4
            },
            "MD": {
                "Range": "125.9 to 132.0",
                "Rate": 129.8
            },
            "ME": {
                "Range": "125.9 to 132.0",
                "Rate": 127.9
            },
            "MI": {
                "Range": "106.6 to 118.3",
                "Rate": 117
            },
            "MN": {
                "Range": "125.9 to 132.0",
                "Rate": 130.9
            },
            "MO": {
                "Range": "125.9 to 132.0",
                "Rate": 128.9
            },
            "MS": {
                "Range": "106.6 to 118.3",
                "Rate": 113.8
            },
            "MT": {
                "Range": "125.9 to 132.0",
                "Rate": 128
            },
            "NC": {
                "Range": "125.9 to 132.0",
                "Rate": 129.9
            },
            "ND": {
                "Range": "106.6 to 118.3",
                "Rate": 114
            },
            "NE": {
                "Range": "118.7 to 125.5",
                "Rate": 124
            },
            "NH": {
                "Range": "132.3 to 144.9",
                "Rate": 144.9
            },
            "NJ": {
                "Range": "132.3 to 144.9",
                "Rate": 134.3
            },
            "NM": {
                "Range": "106.6 to 118.3",
                "Rate": 108.2
            },
            "NV": {
                "Range": "106.6 to 118.3",
                "Rate": 106.6
            },
            "NY": {
                "Range": "132.3 to 144.9",
                "Rate": 132.3
            },
            "OH": {
                "Range": "125.9 to 132.0",
                "Rate": 126.6
            },
            "OK": {
                "Range": "118.7 to 125.5",
                "Rate": 120.4
            },
            "OR": {
                "Range": "106.6 to 118.3",
                "Rate": 118.3
            },
            "PA": {
                "Range": "125.9 to 132.0",
                "Rate": 132
            },
            "RI": {
                "Range": "132.3 to 144.9",
                "Rate": 133.2
            },
            "SC": {
                "Range": "118.7 to 125.5",
                "Rate": 125.1
            },
            "SD": {
                "Range": "118.7 to 125.5",
                "Rate": 122.3
            },
            "TN": {
                "Range": "106.6 to 118.3",
                "Rate": 118
            },
            "TX": {
                "Range": "106.6 to 118.3",
                "Rate": 110.7
            },
            "UT": {
                "Range": "106.6 to 118.3",
                "Rate": 117.1
            },
            "VA": {
                "Range": "125.9 to 132.0",
                "Rate": 131.1
            },
            "VT": {
                "Range": "132.3 to 144.9",
                "Rate": 135.9
            },
            "WA": {
                "Range": "132.3 to 144.9",
                "Rate": 134.8
            },
            "WI": {
                "Range": "125.9 to 132.0",
                "Rate": 126.9
            },
            "WV": {
                "Range": "106.6 to 118.3",
                "Rate": 111.4
            },
            "WY": {
                "Range": "118.7 to 125.5",
                "Rate": 124.4
            }
        }
    elif option == 3:
        json_data = [
            ["AK", "125.9 to 132.0", 127.1],
            ["AL", "118.7 to 125.5", 120.5],
            ["AR", "106.6 to 118.3", 113.9],
            ["AZ", "106.6 to 118.3", 115],
            ["CA", "118.7 to 125.5", 118.7],
            ["CO", "118.7 to 125.5", 124.9],
            ["CT", "132.3 to 144.9", 142],
            ["DC", "132.3 to 144.9", 139.6],
            ["DE", "132.3 to 144.9", 136.9],
            ["FL", "106.6 to 118.3", 114.8],
            ["GA", "118.7 to 125.5", 124.4],
            ["HI", "132.3 to 144.9", 138],
            ["IA", "125.9 to 132.0", 125.9],
            ["ID", "118.7 to 125.5", 123.2],
            ["IL", "132.3 to 144.9", 133.5],
            ["IN", "118.7 to 125.5", 121.6],
            ["KS", "118.7 to 125.5", 125.5],
            ["KY", "125.9 to 132.0", 127.3],
            ["LA", "118.7 to 125.5", 122.7],
            ["MA", "132.3 to 144.9", 138.4],
            ["MD", "125.9 to 132.0", 129.8],
            ["ME", "125.9 to 132.0", 127.9],
            ["MI", "106.6 to 118.3", 117],
            ["MN", "125.9 to 132.0", 130.9],
            ["MO", "125.9 to 132.0", 128.9],
            ["MS", "106.6 to 118.3", 113.8],
            ["MT", "125.9 to 132.0", 128],
            ["NC", "125.9 to 132.0", 129.9],
            ["ND", "106.6 to 118.3", 114],
            ["NE", "118.7 to 125.5", 124],
            ["NH", "132.3 to 144.9", 144.9],
            ["NJ", "132.3 to 144.9", 134.3],
            ["NM", "106.6 to 118.3", 108.2],
            ["NV", "106.6 to 118.3", 106.6],
            ["NY", "132.3 to 144.9", 132.3],
            ["OH", "125.9 to 132.0", 126.6],
            ["OK", "118.7 to 125.5", 120.4],
            ["OR", "106.6 to 118.3", 118.3],
            ["PA", "125.9 to 132.0", 132],
            ["RI", "132.3 to 144.9", 133.2],
            ["SC", "118.7 to 125.5", 125.1],
            ["SD", "118.7 to 125.5", 122.3],
            ["TN", "106.6 to 118.3", 118],
            ["TX", "106.6 to 118.3", 110.7],
            ["UT", "106.6 to 118.3", 117.1],
            ["VA", "125.9 to 132.0", 131.1],
            ["VT", "132.3 to 144.9", 135.9],
            ["WA", "132.3 to 144.9", 134.8],
            ["WI", "125.9 to 132.0", 126.9],
            ["WV", "106.6 to 118.3", 111.4],
            ["WY", "118.7 to 125.5", 124.4]
        ]
    elif option == 4:
        json_data = {
            "State": ["AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN",
                      "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ",
                      "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA",
                      "WI", "WV", "WY"],
            "Range": ["125.9 to 132.0", "118.7 to 125.5", "106.6 to 118.3", "106.6 to 118.3", "118.7 to 125.5",
                      "118.7 to 125.5", "132.3 to 144.9", "132.3 to 144.9", "132.3 to 144.9", "106.6 to 118.3",
                      "118.7 to 125.5", "132.3 to 144.9", "125.9 to 132.0", "118.7 to 125.5", "132.3 to 144.9",
                      "118.7 to 125.5", "118.7 to 125.5", "125.9 to 132.0", "118.7 to 125.5", "132.3 to 144.9",
                      "125.9 to 132.0", "125.9 to 132.0", "106.6 to 118.3", "125.9 to 132.0", "125.9 to 132.0",
                      "106.6 to 118.3", "125.9 to 132.0", "125.9 to 132.0", "106.6 to 118.3", "118.7 to 125.5",
                      "132.3 to 144.9", "132.3 to 144.9", "106.6 to 118.3", "106.6 to 118.3", "132.3 to 144.9",
                      "125.9 to 132.0", "118.7 to 125.5", "106.6 to 118.3", "125.9 to 132.0", "132.3 to 144.9",
                      "118.7 to 125.5", "118.7 to 125.5", "106.6 to 118.3", "106.6 to 118.3", "106.6 to 118.3",
                      "125.9 to 132.0", "132.3 to 144.9", "132.3 to 144.9", "125.9 to 132.0", "106.6 to 118.3",
                      "118.7 to 125.5"],
            "Rate": [127.1, 120.5, 113.9, 115, 118.7, 124.9, 142, 139.6, 136.9, 114.8, 124.4, 138, 125.9, 123.2, 133.5,
                     121.6, 125.5, 127.3, 122.7, 138.4, 129.8, 127.9, 117, 130.9, 128.9, 113.8, 128, 129.9, 114, 124,
                     144.9, 134.3, 108.2, 106.6, 132.3, 126.6, 120.4, 118.3, 132, 133.2, 125.1, 122.3, 118, 110.7,
                     117.1, 131.1, 135.9, 134.8, 126.9, 111.4, 124.4]
        }
    return json_data


def breast_cancer_by_grade(input_json):
    only_age = {"age": json.loads(input_json)['age']}
    filters = create_filter(json.dumps(only_age))
    stages = [1.0, 2.0, 3.0, 4.0]
    filters['$and'].append({"grade": {"$in": stages}})
    result = json.loads(aggregate([
        {"$match": filters},
        {"$group": {
            "_id": "",
            "total": {"$sum": 1},
            "subset": {"$push": "$grade"}
        }},
        {"$unwind": "$subset"},
        {"$group": {
            "_id": {"grade": "$subset", "total": "$total"},
            "count": {"$sum": 1}
        }},
        {"$project": {
            "count": 1,
            "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
        }},
        {"$sort": SON([("percentage", -1)])}]))

    data = {'Grade 1': 0, 'Grade 2': 0, 'Grade 3': 0}
    for i, label in enumerate(list(map(lambda x: x['_id']['grade'], result))):
        if label == 1.0:
            data['Grade 1'] += result[i]['percentage']
        elif label == 2.0:
            data['Grade 2'] += result[i]['percentage']
        elif label in [3.0, 4.0]:
            data['Grade 3'] += result[i]['percentage']

    return {
        'labels': list(map(lambda x: x, data.keys())),
        'datasets': [{
            'data': list(map(lambda x: x, data.values())),
            'label': "Diagnosed",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def percent_of_women_with_cancer_by_race_overall():
    diag_request = '{"sex": "Female"}'
    return percent_race_with_cancer_by_age(diag_request)


def cause_of_death_overall():
    """
    Does not need any input parameters
    Returns percentage of Breast and Others
    :return: json
    """
    result = json.loads(aggregate([{"$match": {
        "cod-to-site-recode": {"$nin": ["Alive"]}}
    },
        {"$group": {
            "_id": "",
            "total": {"$sum": 1},
            "data_subset": {"$push": "$cod-to-site-recode"}
        }},
        {"$unwind": "$data_subset"},
        {"$group": {
            "_id": {"cod-to-site-recode": "$data_subset", "total": "$total"},
            "count": {"$sum": 1}}},
        {"$project": {
            "count": 1,
            "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
        }},
        {"$sort": SON([("count", -1)])}]))

    data = {"Breast": 0, "Other": 0}
    for i, label in enumerate(list(map(lambda x: x['_id']['cod-to-site-recode'], result))):
        if label == 'Breast':
            data['Breast'] = result[i]['percentage']
        else:
            data['Other'] += result[i]['percentage']

    return {
        'labels': list(map(lambda x: x, data.keys())),
        'datasets': [{
            'data': list(map(lambda x: x, data.values())),
            'label': "Deaths",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def er_pos_pr_neg_her2_neg_annual_diagnoses():
    """
    Does not needs an input parameter
    :return: json
    """
    result = json.loads(aggregate([{"$match": {
        "$and": [
            {"er-status-recode-breast-cancer-1990": "+"},
            {"pr-status-recode-breast-cancer-1990": "-"},
            {"derived-her2-recode-2010": "-"}
        ]
    }},
        {"$group": {
            "_id": "$year-of-diagnosis",
            "count": {"$sum": 1}}},
        {"$sort": SON([("_id", 1)])}]))

    return {
        'labels': list(map(lambda x: x['_id'], result)),
        'datasets': [{
            'data': list(map(lambda x: x['count'], result)),
            'label': "Diagnosed",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def cause_of_death(input_json):
    """
    sample request input_json = '{"age": 48, ' \
                   '"sex": "Female", ' \
                   '"tumor_grade": 1, ' \
                   '"er_status": "+", ' \
                   '"pr_status": "+", ' \
                   '"tumor_size_in_mm": 22, ' \
                   '"num_pos_nodes": 0, ' \
                   '"her2_status": "+", ' \
                   '"ethnicity": "White"}'
    :param input_json:
    :return: json
    """
    filters = create_filter(input_json)
    result = json.loads(aggregate([
        {"$match": filters},
        {"$group": {
            "_id": "",
            "total": {"$sum": 1},
            "data_subset": {"$push": "$cod-to-site-recode"}
        }},
        {"$unwind": "$data_subset"},
        {"$group": {
            "_id": {"cod-to-site-recode": "$data_subset", "total": "$total"},
            "count": {"$sum": 1}}},
        {"$project": {
            "count": 1,
            "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
        }},
        {"$sort": SON([("count", -1)])}]))

    data = {"Alive": 0, "Breast": 0, "Other": 0}
    for i, label in enumerate(list(map(lambda x: x['_id']['cod-to-site-recode'], result))):
        if label == 'Breast':
            data['Breast'] += result[i]['percentage']
        elif label == 'Alive':
            data['Alive'] += result[i]['percentage']
        else:
            data['Other'] += result[i]['percentage']

    return {
        'labels': list(map(lambda x: x, data.keys())),
        'datasets': [{
            'data': list(map(lambda x: x, data.values())),
            'label': "Deaths",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def helper_get_positive_nodes(input_json):
    """
    sample request input_json = '{"age": 48, ' \
                   '"sex": "Female", ' \
                   '"tumor_grade": 1, ' \
                   '"er_status": "+", ' \
                   '"pr_status": "+", ' \
                   '"tumor_size_in_mm": 22, ' \
                   '"num_pos_nodes": 0, ' \
                   '"her2_status": "+", ' \
                   '"ethnicity": "White"}'
    :param input_json:
    :return: json
    """
    filters = create_filter(input_json)
    result = json.loads(aggregate([
        # {"$match": filters},
        {"$group": {
            "_id": "$regional-nodes-positive-1988",
            "count": {"$sum": 1}}},
        {"$sort": SON([("_id", -1)])}]))
    return result


def survival_months(input_json):
    """
    sample request input_json = '{"age": 48, ' \
                   '"sex": "Female", ' \
                   '"tumor_grade": 1, ' \
                   '"er_status": "+", ' \
                   '"pr_status": "+", ' \
                   '"tumor_size_in_mm": 22, ' \
                   '"num_pos_nodes": 0, ' \
                   '"her2_status": "+", ' \
                   '"ethnicity": "White"}'
    :param input_json:
    :return: json
    """
    filters = create_filter(input_json)
    result = json.loads(aggregate([
        {"$match": filters},
        {"$group": {
            "_id": "$survival-months",
            "count": {"$sum": 1}}},
        {"$sort": SON([("_id", -1)])}]))

    res = {'> 120 months': 0, '> 96 months': 0, '> 48 months': 0, '> 24 months': 0}
    for i in result:
        if isinstance(i['_id'], int) and i['_id'] > 120:
            res['> 120 months'] += i['count']
        elif isinstance(i['_id'], int) and i['_id'] > 96:
            res['> 96 months'] += i['count']
        elif isinstance(i['_id'], int) and i['_id'] > 48:
            res['> 48 months'] += i['count']
        elif isinstance(i['_id'], int) and i['_id'] > 24:
            res['> 24 months'] += i['count']

    return {
        'labels': list(map(lambda x: x, res.keys())),
        'datasets': [{
            'data': list(map(lambda x: x, res.values())),
            'label': "Diagnosed",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def breast_cancer_by_size(input_json):
    """
    sample request input_json = '{"age": 48, ' \
                   '"sex": "Female", ' \
                   '"tumor_grade": 1, ' \
                   '"er_status": "+", ' \
                   '"pr_status": "+", ' \
                   '"tumor_size_in_mm": 22, ' \
                   '"num_pos_nodes": 0, ' \
                   '"her2_status": "+", ' \
                   '"ethnicity": "White"}'
    :param input_json:
    :return: json
    """
    only_age = {"age": json.loads(input_json)['age']}
    filters = create_filter(json.dumps(only_age))
    sizes = ['< 1cm', '<2cm', '<3cm', '>3cm', '>5cm', 'Micro']
    filters['$and'].append({"t-size-cm": {"$in": sizes}})
    result = json.loads(aggregate([
        {"$match": filters},
        {"$group": {
            "_id": "",
            "total": {"$sum": 1},
            "subset": {"$push": "$t-size-cm"}
        }},
        {"$unwind": "$subset"},
        {"$group": {
            "_id": {"t-size-cm": "$subset", "total": "$total"},
            "count": {"$sum": 1}
        }},
        {"$project": {
            "count": 1,
            "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
        }},
        {"$sort": SON([("percentage", -1)])}]))

    data = {'< 1cm': 0, '< 2cm': 0, '< 5cm': 0, '> 5cm': 0}
    for i, label in enumerate(list(map(lambda x: x['_id']['t-size-cm'], result))):
        if label == '< 1cm':
            data['< 1cm'] += result[i]['percentage']
        elif label == '<2cm':
            data['< 2cm'] += result[i]['percentage']
        elif label == '<3cm':
            data['< 5cm'] += result[i]['percentage']
        elif label == '>3cm':
            data['< 5cm'] += result[i]['percentage']
        elif label == '>5cm':
            data['> 5cm'] += result[i]['percentage']
        elif label == 'Micro':
            data['< 1cm'] += result[i]['percentage']

    return {
        'labels': list(map(lambda x: x, data.keys())),
        'datasets': [{
            'data': list(map(lambda x: x, data.values())),
            'label': "Diagnosed",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def radiation():
    """
    :return: json
    """
    result = json.loads(aggregate([
        {"$group": {
            "_id": "",
            "total": {"$sum": 1},
            "data_subset": {"$push": "$radiation"}
        }},
        {"$unwind": "$data_subset"},
        {"$group": {
            "_id": {"radiation": "$data_subset", "total": "$total"},
            "count": {"$sum": 1}}},
        {"$project": {
            "count": 1,
            "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
        }},
        {"$sort": SON([("_id", -1)])}]))

    return {
        'labels': list(map(lambda x: x['_id']['radiation'], result)),
        'datasets': [{
            'data': list(map(lambda x: x['percentage'], result)),
            'label': "Radiation",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def chemotherapy():
    """
    :return:
    """
    result = json.loads(aggregate([
        {"$group": {
            "_id": "",
            "total": {"$sum": 1},
            "chemo_set": {"$push": "$chemo"}
        }},
        {"$unwind": "$chemo_set"},
        {"$group": {
            "_id": {"chemo": "$chemo_set", "total": "$total"},
            "count": {"$sum": 1}}},
        {"$project": {
            "count": 1,
            "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
        }},
        {"$sort": SON([("_id", -1)])}]))

    return {
        'labels': list(map(lambda x: x['_id']['chemo'], result)),
        'datasets': [{
            'data': list(map(lambda x: x['percentage'], result)),
            'label': "Chemotherapy",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def surgery_decisions(input_json):
    """
    sample request input_json = '{"age": 48, ' \
                   '"sex": "Female", ' \
                   '"tumor_grade": 1, ' \
                   '"er_status": "+", ' \
                   '"pr_status": "+", ' \
                   '"tumor_size_in_mm": 22, ' \
                   '"num_pos_nodes": 0, ' \
                   '"her2_status": "+", ' \
                   '"ethnicity": "White"}'
    :param input_json:
    :return: json
    """
    filters = create_filter(input_json)
    excluded = ['None']
    filters['$and'].append({"surgery": {"$nin": excluded}})
    result = json.loads(aggregate([
        {"$match": filters},
        {"$group": {
            "_id": "",
            "total": {"$sum": 1},
            "surgery_set": {"$push": "$surgery"}
        }},
        {"$unwind": "$surgery_set"},
        {"$group": {
            "_id": {"surgery": "$surgery_set", "total": "$total"},
            "count": {"$sum": 1}
        }},
        {"$project": {
            "count": 1,
            "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
        }},
        {"$sort": SON([("percentage", -1)])}]))

    data = OrderedDict()
    data['Lumpectomy'] = 0
    data['Mastectomy'] = 0
    data['Other'] = 0
    for i, label in enumerate(list(map(lambda x: x['_id']['surgery'], result))):
        if label in ['Lumpectomy', 'Partial Mastectomy']:
            data['Lumpectomy'] += result[i]['percentage']
        elif label in ['Single Mastectomy', 'Mastectomy ', 'Simple Mastectomy']:
            data['Mastectomy'] += result[i]['percentage']
        # elif label == 'Simple Mastectomy':
        #     data['Simple Mastectomy'] = result[i]['percentage']
        elif label == 'Bi-Lateral Mastectomy':
            data['Bi-Lateral Mastectomy'] = result[i]['percentage']
        elif label in ['Other', 'Surgery']:
            data['Other'] += result[i]['percentage']
    data.move_to_end("Other")

    return {
        'labels': list(map(lambda x: x, data.keys())),
        'datasets': [{
            'data': list(map(lambda x: x, data.values())),
            'label': "Surgeries",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def distribution_of_stage_of_cancer(input_json):
    """
    sample request input_json = '{"age": 48, ' \
                   '"sex": "Female", ' \
                   '"tumor_grade": 1, ' \
                   '"er_status": "+", ' \
                   '"pr_status": "+", ' \
                   '"tumor_size_in_mm": 22, ' \
                   '"num_pos_nodes": 0, ' \
                   '"her2_status": "+", ' \
                   '"ethnicity": "White"}'
    :param input_json:
    :return:
    """
    filters = create_filter(input_json)
    stages = ['I', 'IIA', 'IIB', 'IIIA', 'IIIB', 'IIIC', 'IV']
    filters['$and'].append({"breast-adjusted-ajcc-6th-stage-1988": {"$in": stages}})
    result = json.loads(aggregate([
        {"$match": filters},
        {"$group": {
            "_id": "",
            "total": {"$sum": 1},
            "subset": {"$push": "$breast-adjusted-ajcc-6th-stage-1988"}
        }},
        {"$unwind": "$subset"},
        {"$group": {
            "_id": {"breast-adjusted-ajcc-6th-stage-1988": "$subset", "total": "$total"},
            "count": {"$sum": 1}
        }},
        {"$project": {
            "count": 1,
            "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
        }},
        {"$sort": SON([("percentage", -1)])}]))

    data = {"I": 0, "II": 0, "III": 0, "IV": 0}
    for i, label in enumerate(list(map(lambda x: x['_id']['breast-adjusted-ajcc-6th-stage-1988'], result))):
        if label == 'I':
            data['I'] = result[i]['percentage']
        elif label in ['IIA', 'IIB']:
            data['II'] += result[i]['percentage']
        elif label in ['IIIA', 'IIIB', 'IIIC', 'IIINOS']:
            data['III'] += result[i]['percentage']
        elif label == 'IV':
            data['IV'] = result[i]['percentage']
        elif label in [0] or label is None:
            data['0'] += result[i]['percentage']

    return {
        'labels': list(map(lambda x: x, data.keys())),
        'datasets': [{
            'data': list(map(lambda x: x, data.values())),
            'label': "Stage",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def percent_women_annualy_diagnosed2(input_json):
    only_age = {"age": json.loads(input_json)['age']}
    filters = create_filter(json.dumps(only_age))
    filters['$and'].append({"year-of-diagnosis": {"$gte": 1975}})
    # filters = {"year-of-diagnosis": {"$gte": 1975}}
    result = json.loads(aggregate([
        {"$match": filters},
        {"$group": {
            "_id": "",
            "total": {"$sum": 1},
            "subset": {"$push": "$year-of-diagnosis"}
        }},
        {"$unwind": "$subset"},
        {"$group": {
            "_id": {"year-of-diagnosis": "$subset", "total": "$total"},
            "count": {"$sum": 1}
        }},
        {"$project": {
            "count": 1,
            "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
        }},
        {"$sort": SON([("_id", 1)])}]))

    data = {"1975-1979": 0, "1980-1984": 0, "1985-1989": 0, "1990-1994": 0, "1995-1999": 0,
            "2000-2004": 0, "2005-2009": 0, "2010-2014": 0}
    for i, label in enumerate(list(map(lambda x: x['_id']['year-of-diagnosis'], result))):
        if i < 5:
            data['1975-1979'] += result[i]['percentage']
        elif i < 10:
            data['1980-1984'] += result[i]['percentage']
        elif i < 15:
            data['1985-1989'] += result[i]['percentage']
        elif i < 20:
            data['1990-1994'] += result[i]['percentage']
        elif i < 25:
            data['1995-1999'] += result[i]['percentage']
        elif i < 30:
            data['2000-2004'] += result[i]['percentage']
        elif i < 35:
            data['2005-2009'] += result[i]['percentage']
        elif i < 40:
            data['2010-2014'] += result[i]['percentage']

    return {
        'labels': list(map(lambda x: x, data.keys())),
        'datasets': [{
            'data': list(map(lambda x: x, data.values())),
            'label': "Diagnosed",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def woman_annualy_diagnosed(input_json):
    """
    sample request input_json = '{"age": 48, ' \
                   '"sex": "Female", ' \
                   '"tumor_grade": 1, ' \
                   '"er_status": "+", ' \
                   '"pr_status": "+", ' \
                   '"tumor_size_in_mm": 22, ' \
                   '"num_pos_nodes": 0, ' \
                   '"her2_status": "+", ' \
                   '"ethnicity": "White"}'
    :param input_json:
    :return: json
    """
    filters = create_filter(input_json)
    result = json.loads(aggregate([
        {"$match": filters},
        {"$group": {
            "_id": "$year-of-diagnosis",
            "count": {"$sum": 1}}},
        {"$sort": SON([("_id", 1)])}]))

    return {
        'labels': list(map(lambda x: x['_id'], result)),
        'datasets': [{
            'data': list(map(lambda x: x['count'], result)),
            'label': "Diagnosed",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def growth_by_specific_type(input_json, operator="$and"):
    """
    Sample requests:
    input_json = '{"type": "IDC"}'
    input_json = '{"type": "In-Situ"}'
    input_json = '{"type": "ILC"}'
    input_json = '{"type": "Other", "type": "Mixed", "type": "IBC", "type": "Mixed "}'
    :param input_json:
    :param operator:
    :return: json
    """
    filters = create_filter(input_json, operator)
    result = json.loads(aggregate([
        {"$match": filters},
        {"$group": {
            "_id": "$year-of-diagnosis",
            "count": {"$sum": 1}}},
        {"$sort": SON([("_id", 1)])}]))

    return {
        'labels': list(map(lambda x: x['_id'], result)),
        'datasets': [{
            'data': list(map(lambda x: x['count'], result)),
            'label': "Diagnosed",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def percent_race_with_cancer_by_age(input_json):
    """
    sample request input_json = '{"age": 48, ' \
                   '"sex": "Female", ' \
                   '"tumor_grade": 1, ' \
                   '"er_status": "+", ' \
                   '"pr_status": "+", ' \
                   '"tumor_size_in_mm": 22, ' \
                   '"num_pos_nodes": 0, ' \
                   '"her2_status": "+", ' \
                   '"ethnicity": "White"}'
    :param input_json:
    :return: json
    """
    filters = create_filter(input_json)
    result = json.loads(aggregate([
        {"$match": filters},
        {"$group": {
            "_id": "",
            "total": {"$sum": 1},
            "race_set": {"$push": "$race-recode-w-b-ai-api"}
        }},
        {"$unwind": "$race_set"},
        {"$group": {
            "_id": {"race-recode-w-b-ai-api": "$race_set", "total": "$total"},
            "count": {"$sum": 1}
        }},
        {"$project": {
            "count": 1,
            "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
        }},
        {"$sort": SON([("percentage", -1)])}]))

    data = OrderedDict()
    data['Other'] = 0
    data['Caucasian'] = 0
    data['African American'] = 0
    data['Asian'] = 0
    for i, label in enumerate(list(map(lambda x: x['_id']['race-recode-w-b-ai-api'], result))):
        if label == 'White':
            data['Caucasian'] += result[i]['percentage']
        elif label == 'Black':
            data['African American'] += result[i]['percentage']
        elif label == 'Asian or Pacific Islander':
            data['Asian'] += result[i]['percentage']
        elif label in ['Unknown', 'American Indian/Alaska Native'] or label is None:
            data['Other'] += result[i]['percentage']
    data.move_to_end("Other")

    return {
        'labels': list(map(lambda x: x, data.keys())),
        'datasets': [{
            'data': list(map(lambda x: x, data.values())),
            'label': "Diagnosed",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def breakout_by_stage(input_json):
    """
    Returns breakeout by stage discarding the nulls and "Blank" fields
    example filter:
    input_json = '{"age": 48, ' \
                 '"chemo": "Yes", ' \
                 '"breast-adjusted-ajcc-6th-stage-1988": {"$in": ' \
                 '["I", "IIA", "IIB", "IIIA", "IIIB", "IIIC", "IIINOS", "IV", 0]}}'
    :param input_json: json
    :return: json
    """
    filters = create_filter(input_json, "$and")
    result = json.loads(aggregate([
        {"$match": filters},
        {"$group": {
            "_id": "",
            "total": {"$sum": 1},
            "subset": {"$push": "$breast-adjusted-ajcc-6th-stage-1988"}
        }},
        {"$unwind": "$subset"},
        {"$group": {
            "_id": {"breast-adjusted-ajcc-6th-stage-1988": "$subset", "total": "$total"},
            "count": {"$sum": 1}
        }},
        {"$project": {
            "count": 1,
            "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
        }},
        {"$sort": SON([("percentage", -1)])}]))

    data = {"0": 0, "I": 0, "II": 0, "III": 0, "IV": 0}
    for i, label in enumerate(list(map(lambda x: x['_id']['breast-adjusted-ajcc-6th-stage-1988'], result))):
        if label == 'I':
            data['I'] = result[i]['percentage']
        elif label in ['IIA', 'IIB']:
            data['II'] += result[i]['percentage']
        elif label in ['IIIA', 'IIIB', 'IIIC', 'IIINOS']:
            data['III'] += result[i]['percentage']
        elif label == 'IV':
            data['IV'] = result[i]['percentage']
        elif label in [0] or label is None:
            data['0'] += result[i]['percentage']

    return {
        'labels': list(map(lambda x: x, data.keys())),
        'datasets': [{
            'data': list(map(lambda x: x, data.values())),
            'label': "Diagnosed",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def percent_women_by_type():
    result = json.loads(aggregate([
        {"$group": {
            "_id": "",
            "total": {"$sum": 1},
            "subset": {"$push": "$type"}
        }},
        {"$unwind": "$subset"},
        {"$group": {
            "_id": {"type": "$subset", "total": "$total"},
            "count": {"$sum": 1}
        }},
        {"$project": {
            "count": 1,
            "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
        }},
        {"$sort": SON([("percentage", -1)])}]))

    data = {"IDC": 0, "DCIS": 0, "ILC": 0, "Other": 0}
    for i, label in enumerate(list(map(lambda x: x['_id']['type'], result))):
        if label == 'IDC':
            data['IDC'] += result[i]['percentage']
        elif label == 'In-Situ':
            data['DCIS'] += result[i]['percentage']
        elif label in ['Other', 'Mixed', 'IBC', 'Mixed ']:
            data['Other'] += result[i]['percentage']
        elif label == 'ILC':
            data['ILC'] += result[i]['percentage']

    return {
        'labels': list(map(lambda x: x, data.keys())),
        'datasets': [{
            'data': list(map(lambda x: x, data.values())),
            'label': "Diagnosed",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def radiation_filter(input_json):
    """
    sample request input_json = '{"age": 48, ' \
                   '"sex": "Female", ' \
                   '"tumor_grade": 1, ' \
                   '"er_status": "+", ' \
                   '"pr_status": "+", ' \
                   '"tumor_size_in_mm": 22, ' \
                   '"num_pos_nodes": 0, ' \
                   '"her2_status": "+", ' \
                   '"ethnicity": "White"}'
    :param input_json:
    :return: json
    """
    filters = create_filter(input_json)
    result = json.loads(aggregate([
        {"$match": filters},
        {"$group": {
            "_id": "",
            "total": {"$sum": 1},
            "data_subset": {"$push": "$radiation"}
        }},
        {"$unwind": "$data_subset"},
        {"$group": {
            "_id": {"radiation": "$data_subset", "total": "$total"},
            "count": {"$sum": 1}}},
        {"$project": {
            "count": 1,
            "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
        }},
        {"$sort": SON([("_id", -1)])}]))

    return {
        'labels': list(map(lambda x: x['_id']['radiation'], result)),
        'datasets': [{
            'data': list(map(lambda x: x['percentage'], result)),
            'label': "Radiation",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def chemotherapy_filter(input_json):
    """
    sample request input_json = '{"age": 48, ' \
                   '"sex": "Female", ' \
                   '"tumor_grade": 1, ' \
                   '"er_status": "+", ' \
                   '"pr_status": "+", ' \
                   '"tumor_size_in_mm": 22, ' \
                   '"num_pos_nodes": 0, ' \
                   '"her2_status": "+", ' \
                   '"ethnicity": "White"}'
    :param input_json:
    :return:
    """
    filters = create_filter(input_json)
    result = json.loads(aggregate([
        {"$match": filters},
        {"$group": {
            "_id": "",
            "total": {"$sum": 1},
            "chemo_set": {"$push": "$chemo"}
        }},
        {"$unwind": "$chemo_set"},
        {"$group": {
            "_id": {"chemo": "$chemo_set", "total": "$total"},
            "count": {"$sum": 1}}},
        {"$project": {
            "count": 1,
            "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
        }},
        {"$sort": SON([("_id", -1)])}]))

    return {
        'labels': list(map(lambda x: x['_id']['chemo'], result)),
        'datasets': [{
            'data': list(map(lambda x: x['percentage'], result)),
            'label': "Chemotherapy",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


def percent_women_annualy_diagnosed(input_json):
    def get_total(year):
        ff = {"$and": [{"year-of-diagnosis": {"$gte": year}},
                       {"year-of-diagnosis": {"$lt": year + 5}}]}
        total = json.loads(aggregate([
            {"$match": ff},
            {"$group": {
                "_id": "",
                "count": {"$sum": 1}}},
            {"$sort": SON([("_id", 1)])}]))
        return total[0]['count']

    def get_by_age(only_age, year):
        ff = create_filter(json.dumps(only_age))
        ff['$and'].append({"$and": [{"year-of-diagnosis": {"$gte": year}},
                                    {"year-of-diagnosis": {"$lt": year + 5}}]})
        by_age = json.loads(aggregate([
            {"$match": ff},
            {"$group": {
                "_id": "",
                "count": {"$sum": 1}}},
            {"$sort": SON([("_id", 1)])}]))
        return by_age[0]['count']

    def get_percent(only_age, year):
        return get_by_age(only_age, year) / get_total(year) * 100

    only_age = {"age": json.loads(input_json)['age']}

    data = {"1975-1979": 0, "1980-1984": 0, "1985-1989": 0, "1990-1994": 0, "1995-1999": 0,
            "2000-2004": 0, "2005-2009": 0, "2010-2014": 0}
    for year in [1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010]:
        if year == 1975:
            data['1975-1979'] = get_percent(only_age, year)
        if year == 1980:
            data['1980-1984'] = get_percent(only_age, year)
        if year == 1985:
            data['1985-1989'] = get_percent(only_age, year)
        if year == 1990:
            data['1990-1994'] = get_percent(only_age, year)
        if year == 1995:
            data['1995-1999'] = get_percent(only_age, year)
        if year == 2000:
            data['2000-2004'] = get_percent(only_age, year)
        if year == 2005:
            data['2005-2009'] = get_percent(only_age, year)
        if year == 2010:
            data['2010-2014'] = get_percent(only_age, year)

    return {
        'labels': list(map(lambda x: x, data.keys())),
        'datasets': [{
            'data': list(map(lambda x: x, data.values())),
            'label': "Diagnosed",
            'borderColor': '#48ccf5',
            'fill': False
        }]
    }


if __name__ == '__main__':
    diag_request = '{"age": 32, ' \
                   '"sex": "Female", ' \
                   '"tumor_grade": 1, ' \
                   '"er_status": "+", ' \
                   '"pr_status": "+", ' \
                   '"tumor_size_in_mm": 22, ' \
                   '"num_pos_nodes": 1, ' \
                   '"her2_status": "+", ' \
                   '"ethnicity": "White"}'

    diag_request_age_only = '{"age": 85}'
    age_only = '{"age": 55}'

    # pprint(radiation())
    exit()

    # pprint(breast_cancer_by_size(diag_request_age_only))

    # d = diagnosis(diag_request, limit=25)
    # pprint(d)
    type_idc = '{"type": "IDC"}'
    type_insitu = '{"type": "In-Situ"}'
    type_ilc = '{"type": "ILC"}'
    type_others = '{"type": "Other", "type": "Mixed", "type": "IBC", "type": "Mixed "}'

    # pprint(growth_by_specific_type(type_others, "$or"))
    diag_request_age_for_stage = '{"age": 48, ' \
                                 '"breast-adjusted-ajcc-6th-stage-1988": {"$in": ' \
                                 '["I", "IIA", "IIB", "IIIA", "IIIB", "IIIC", "IIINOS", "IV", 0]}}'

    # pprint(breakout_by_stage(diag_request_age_for_stage))
    # pprint(cause_of_death_within_ages_30_40())

    input_json = '{"age": 48, ' \
                 '"chemo": "Yes", ' \
                 '"breast-adjusted-ajcc-6th-stage-1988": {"$in": ' \
                 '["I", "IIA", "IIB", "IIIA", "IIIB", "IIIC", "IIINOS", "IV", 0]}}'

    # pprint(breakout_by_stage(input_json))

    # diag_request = '{"sex": "Female"}'
    # pprint(breast_cancer_by_size(age_only))
    # pprint(percent_of_women_with_cancer_by_race_overall())
    # pprint(surgery_decisions(age_only))

    # def wrapper(full_request):
    #     only_age = {"age": json.loads(full_request)['age']}
    #     return woman_annualy_diagnosed(json.dumps(only_age))
    #
    #
    # pprint(wrapper(diag_request))

    # pprint(growth_by_specific_type('{"type": "Other", "type": "IDC", "type": "ILC", "type": "In Situ"}', operator="$and"))

    # type_others = '{"type": "Other", "type": "Mixed", "type": "IBC", "type": "Mixed "}'
    # pprint(growth_by_specific_type(age_only, "$and"))

    # pprint(diagnosis(diag_request, limit=20))
    # age_and_race = '{"age": 48, "ethnicity":"White"}'
    # pprint(distribution_of_stage_of_cancer(age_and_race))
    # pprint(breast_cancer_by_size(age_only))
    # pprint(percent_women_by_type())
    # pprint(percent_women_annualy_diagnosed(diag_request))
    # diag = diagnosis(diag_request, limit=20)
    # print(len(diag))
    # pprint(diag)
    pprint(helper_get_positive_nodes(age_only))

# def cause_of_death_within_ages_30_40():
#     result = json.loads(aggregate([{"$match": {
#         "$and": [{"cod-to-site-recode": {"$nin": ["Alive"]}},
#                  {"$or": [
#                      {"age-recode-with-1-year-olds": "35-39 years"},
#                      {"age-recode-with-1-year-olds": "30-34 years"}
#                  ]}]
#     }},
#         {"$group": {
#             "_id": "",
#             "total": {"$sum": 1},
#             "data_subset": {"$push": "$cod-to-site-recode"}
#         }},
#         {"$unwind": "$data_subset"},
#         {"$group": {
#             "_id": {"cod-to-site-recode": "$data_subset", "total": "$total"},
#             "count": {"$sum": 1}}},
#         {"$project": {
#             "count": 1,
#             "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
#         }},
#         {"$sort": SON([("count", -1)])}]))
#
#     data = {"Breast": 0, "Other": 0}
#     for i, label in enumerate(list(map(lambda x: x['_id']['cod-to-site-recode'], result))):
#         if label == 'Breast':
#             data['Breast'] = result[i]['percentage']
#         else:
#             data['Other'] += result[i]['percentage']
#
#     return {
#         'labels': list(map(lambda x: x, data.keys())),
#         'datasets': [{
#             'data': list(map(lambda x: x, data.values())),
#             'label': "Diagnosed",
#             'borderColor': '#48ccf5',
#             'fill': False
#         }]
#     }


# def surgery_decisions_within_ages_30_40():
#     result = json.loads(aggregate([{"$match": {
#         "$or": [
#             {"age-recode-with-1-year-olds": "35-39 years"},
#             {"age-recode-with-1-year-olds": "30-34 years"}
#         ]
#     }},
#         {"$group": {
#             "_id": "",
#             "total": {"$sum": 1},
#             "surgery_set": {"$push": "$surgery"}
#         }},
#         {"$unwind": "$surgery_set"},
#         {"$group": {
#             "_id": {"surgery": "$surgery_set", "total": "$total"},
#             "count": {"$sum": 1}
#         }},
#         {"$project": {
#             "count": 1,
#             "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
#         }},
#         {"$sort": SON([("percentage", -1)])}]))
#
#     return {
#         'labels': list(map(lambda x: x['_id']['surgery'], result)),
#         'datasets': [{
#             'data': list(map(lambda x: x['percentage'], result)),
#             'label': "Diagnosed",
#             'borderColor': '#48ccf5',
#             'fill': False
#         }]
#     }


# def chemotherapy_for_ages_30_40():
#     result = json.loads(aggregate([{"$match": {
#         "$or": [
#             {"age-recode-with-1-year-olds": "35-39 years"},
#             {"age-recode-with-1-year-olds": "30-34 years"}
#         ]
#     }},
#         {"$group": {
#             "_id": "",
#             "total": {"$sum": 1},
#             "chemo_set": {"$push": "$chemo"}
#         }},
#         {"$unwind": "$chemo_set"},
#         {"$group": {
#             "_id": {"chemo": "$chemo_set", "total": "$total"},
#             "count": {"$sum": 1}}},
#         {"$project": {
#             "count": 1,
#             "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
#         }},
#         {"$sort": SON([("_id", 1)])}]))
#
#     return {
#         'labels': list(map(lambda x: x['_id']['chemo'], result)),
#         'datasets': [{
#             'data': list(map(lambda x: x['percentage'], result)),
#             'label': "Diagnosed",
#             'borderColor': '#48ccf5',
#             'fill': False
#         }]
#     }


# def radiation_for_ages_30_40():
#     result = json.loads(aggregate([{"$match": {
#         "$or": [
#             {"age-recode-with-1-year-olds": "35-39 years"},
#             {"age-recode-with-1-year-olds": "30-34 years"}
#         ]
#     }},
#         {"$group": {
#             "_id": "",
#             "total": {"$sum": 1},
#             "data_subset": {"$push": "$radiation"}
#         }},
#         {"$unwind": "$data_subset"},
#         {"$group": {
#             "_id": {"radiation": "$data_subset", "total": "$total"},
#             "count": {"$sum": 1}}},
#         {"$project": {
#             "count": 1,
#             "percentage": {"$multiply": [{"$divide": [100, "$_id.total"]}, "$count"], }
#         }},
#         {"$sort": SON([("_id", 1)])}]))
#
#     return {
#         'labels': list(map(lambda x: x['_id']['radiation'], result)),
#         'datasets': [{
#             'data': list(map(lambda x: x['percentage'], result)),
#             'label': "Diagnosed",
#             'borderColor': '#48ccf5',
#             'fill': False
#         }]
#     }


# def survival_months_within_ages_30_40():
#     result = json.loads(aggregate([{"$match": {
#         "$or": [
#             {"age-recode-with-1-year-olds": "35-39 years"},
#             {"age-recode-with-1-year-olds": "30-34 years"}
#         ]
#     }},
#         {"$group": {
#             "_id": "$survival-months",
#             "count": {"$sum": 1}}},
#         {"$sort": SON([("_id", -1)])}]))
#
#     res = {'> 120 months': 0, '> 96 months': 0, '> 48 months': 0, '> 24 months': 0}
#     for i in result:
#         if isinstance(i['_id'], int) and i['_id'] > 120:
#             res['> 120 months'] += i['count']
#         elif isinstance(i['_id'], int) and i['_id'] > 96:
#             res['> 96 months'] += i['count']
#         elif isinstance(i['_id'], int) and i['_id'] > 48:
#             res['> 48 months'] += i['count']
#         elif isinstance(i['_id'], int) and i['_id'] > 24:
#             res['> 24 months'] += i['count']
#
#     return {
#         'labels': list(map(lambda x: x, res.keys())),
#         'datasets': [{
#             'data': list(map(lambda x: x, res.values())),
#             'label': "Diagnosed",
#             'borderColor': '#48ccf5',
#             'fill': False
#         }]
#     }


# def breast_cancer_by_size_age_30_40():
#     """
#     Custom func for cancer_by_size
#     :return:
#     """
#     j = aggregate([{"$match": {
#         "$or": [
#             {"age-recode-with-1-year-olds": "35-39 years"},
#             {"age-recode-with-1-year-olds": "30-34 years"}
#         ]
#     }},
#         {"$group": {
#             "_id": "$t-size-cm",
#             "count": {"$sum": 1}}},
#         {"$sort": SON([("_id", 1)])}])
#     l = json.loads(j)
#     res = {'< 1cm': 0}
#     for i in l:
#         if i['_id'] == '<1cm':
#             res['< 1cm'] += i['count']
#         elif i['_id'] == '<2cm':
#             res['< 2cm'] = i['count']
#         elif i['_id'] == '<3cm':
#             res['< 3cm'] = i['count']
#         elif i['_id'] == '>3cm':
#             res['> 3cm'] = i['count']
#         elif i['_id'] == '>5cm':
#             res['> 5cm'] = i['count']
#         elif i['_id'] == 'Micro':
#             res['< 1cm'] += i['count']
#
#     return {
#         'labels': list(map(lambda x: x, res.keys())),
#         'datasets': [{
#             'data': list(map(lambda x: x, res.values())),
#             'label': "Diagnosed",
#             'borderColor': '#48ccf5',
#             'fill': False
#         }]
#     }


# def woman_age_30_40_annualy_diagnosed():
#     result = json.loads(aggregate([{"$match": {
#         "$or": [
#             {"age-recode-with-1-year-olds": "35-39 years"},
#             {"age-recode-with-1-year-olds": "30-34 years"}
#         ]
#     }},
#         {"$group": {
#             "_id": "$year-of-diagnosis",
#             "count": {"$sum": 1}}},
#         {"$sort": SON([("_id", 1)])}]))
#
#     return {
#         'labels': list(map(lambda x: x['_id'], result)),
#         'datasets': [{
#             'data': list(map(lambda x: x['count'], result)),
#             'label': "Diagnosed",
#             'borderColor': '#48ccf5',
#             'fill': False
#         }]
#     }


# def distribution_of_stage_of_cancer_for_ages_30_40():
#     result = json.loads(aggregate([{"$match": {
#         "$or": [
#             {"age-recode-with-1-year-olds": "35-39 years"},
#             {"age-recode-with-1-year-olds": "30-34 years"}
#         ]
#     }},
#         {"$group": {
#             "_id": "$1998-stage",
#             "count": {"$sum": 1}}},
#         {"$sort": SON([("_id", 1)])}]))
#
#     return {
#         'labels': list(map(lambda x: x['_id'], result)),
#         'datasets': [{
#             'data': list(map(lambda x: x['count'], result)),
#             'label': "Diagnosed",
#             'borderColor': '#48ccf5',
#             'fill': False
#         }]
#     }
