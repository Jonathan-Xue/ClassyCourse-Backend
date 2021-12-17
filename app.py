from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import xml.etree.ElementTree

from db import *

# Initialize
app = Flask(__name__)
CORS(app, support_credentials=True)

sqlObject = DB(reset=False)

# Routes
@app.route("/")
def default():
    return jsonify()

# Setup
@app.route("/reset", methods=['GET', 'POST'])
def reset():
    global sqlObject

    sqlObject.setup(reset=True)

    return jsonify()

@app.route("/import-records", methods=['GET', 'POST'])
def import_record():
    global sqlObject

    with open('data/uiuc-gpa-dataset.csv') as csv_file:
        data = list(csv.DictReader(csv_file, delimiter=','))

    # Clean Data
    for row in data:
        del row['YearTerm']

        # Necessary For Postgres: Replace ' With ''
        row['Course Title'] = row['Course Title'].replace("'", "''")
        row['Primary Instructor'] = row['Primary Instructor'].replace("'", "''")
    
    # Schedule Types
    for row in data:
        row['Sched Type'] = row['Sched Type'].upper()
        assert row['Sched Type'] in SCHEDULE_TYPES, row
    
    # Import
    for row in data:
        sqlObject.insert_record(row["Year"], row["Term"], row["Subject"], row["Number"], row["Course Title"], row["Primary Instructor"], row["Sched Type"], row["A+"], row["A"], row["A-"], row["B+"], row["B"], row["B-"], row["C+"], row["C"], row["C-"], row["D+"], row["D"], row["D-"], row["F"], row["W"])

    return jsonify()

# SQL Post
@app.route("/insert-record", methods=['GET', 'POST'])
def insert_record():
    global sqlObject

    year = request.get_json()['year']
    term = request.get_json()['term']
    subject = request.get_json()['subject'].replace("'", "''")
    number = request.get_json()['number']
    name = request.get_json()['name']
    instructor = request.get_json()['instructor'].replace("'", "''")
    sched_type = request.get_json()['sched_type']
    a_plus = request.get_json()['a+']
    a = request.get_json()['a']
    a_minus = request.get_json()['a-']
    b_plus = request.get_json()['b+']
    b = request.get_json()['b']
    b_minus = request.get_json()['b-']
    c_plus = request.get_json()['c+']
    c = request.get_json()['c']
    c_minus = request.get_json()['c-']
    d_plus = request.get_json()['d+']
    d = request.get_json()['d']
    d_minus = request.get_json()['d-']
    f = request.get_json()['f']
    w = request.get_json()['w']
    sqlObject.insert_record(year, term, subject, number, name, instructor, sched_type, a_plus, a, a_minus, b_plus, b, b_minus, c_plus, c, c_minus, d_plus, d, d_minus, f, w)
    
    return jsonify()

# SQL Database
@app.route("/course-statistics", methods=['GET'])
def course_statistics():
    subject = request.args['subject']
    number = request.args['number']
    name = request.args['name'].replace("'", "''")

    data = sqlObject.get_course_statistics(subject, number, name)
    
    return jsonify(data=data)

# REST CIS API
@app.route("/subjects", methods=['GET'])
def subjects():
    year = request.args['year']
    term = request.args['term']

    # API
    response = requests.get(f"https://courses.illinois.edu/cisapp/explorer/schedule/{year}/{term}.xml")
    responseXML = xml.etree.ElementTree.fromstring(response.text)
    subjectElements = responseXML.find('subjects').findall('subject')

    data = {}
    for elem in subjectElements:
        data[elem.attrib['id']] = elem.text
    
    return jsonify(data=data)

@app.route("/courses", methods=['GET'])
def courses():
    year = request.args['year']
    term = request.args['term']
    subject = request.args['subject']

    # API
    response = requests.get(f"https://courses.illinois.edu/cisapp/explorer/schedule/{year}/{term}/{subject}.xml")
    responseXML = xml.etree.ElementTree.fromstring(response.text)
    courseElements = responseXML.find('courses').findall('course')

    data = []
    for elem in courseElements:
        data.append({
            'subject': subject,
            'number': elem.attrib['id'],
            'name': elem.text.replace("'", "''"),
            'avg_gpa': sqlObject.get_course_avg(subject, elem.attrib['id'], elem.text)
        })
    
    return jsonify(data=data)

@app.route("/course-information", methods=['GET'])
def course_information():
    year = request.args['year']
    term = request.args['term']
    subject = request.args['subject']
    number = request.args['number']

    # API
    response = requests.get(f"https://courses.illinois.edu/cisapp/explorer/schedule/{year}/{term}/{subject}/{number}.xml")
    responseXML = xml.etree.ElementTree.fromstring(response.text)

    data = {}
    data['label'] = responseXML.find('label').text
    data['description'] = responseXML.find('description').text
    data['genEdCategories'] = []
    if responseXML.find('genEdCategories') != None:
        for elem in responseXML.find('genEdCategories').findall('category'):
            data['genEdCategories'].append(elem.find('description').text)

    data['sections'] = {}
    if responseXML.find('sections') != None:
        for elem in responseXML.find('sections').findall('section'):
            data['sections'][elem.attrib['id']] = elem.text

    return jsonify(data=data)

@app.route("/section-information", methods=['GET'])
def section_information():
    year = request.args['year']
    term = request.args['term']
    subject = request.args['subject']
    number = request.args['number']
    crn = request.args['crn']

    # API
    response = requests.get(f"https://courses.illinois.edu/cisapp/explorer/schedule/{year}/{term}/{subject}/{number}/{crn}.xml")
    responseXML = xml.etree.ElementTree.fromstring(response.text)

    data = {}
    data['enrollmentStatus'] = responseXML.find('enrollmentStatus').text
    data['meetings'] = []
    for elem in responseXML.find('meetings').findall('meeting'):
        data['meetings'].append({})

        # Instructor
        data['meetings'][-1]['instructor'] = []
        if elem.find('instructors') != None:
            for subElem in elem.find('instructors').findall('instructor'):
                data['meetings'][-1]['instructor'].append(subElem.text)

        # Type
        data['meetings'][-1]['type'] = elem.find('type').text if elem.find('type') != None else None
        
        # Time
        data['meetings'][-1]['start'] = elem.find('start').text if elem.find('start') != None else None
        data['meetings'][-1]['end'] = elem.find('end').text if elem.find('end') != None else None
        data['meetings'][-1]['daysOfTheWeek'] = elem.find('daysOfTheWeek').text.strip() if elem.find('daysOfTheWeek') != None else None

        # Room Number & Building
        data['meetings'][-1]['roomNumber'] = elem.find('roomNumber').text if elem.find('roomNumber') != None else None
        data['meetings'][-1]['buildingName'] = elem.find('buildingName').text if elem.find('buildingName') != None else None

    return jsonify(data=data)