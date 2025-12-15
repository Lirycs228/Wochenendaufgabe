from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .forms import AskForm
import requests
import mysql.connector
from dotenv import load_dotenv
import os

def db_execute(query):
    root = os.path.join(os.path.dirname(__file__))
    env_path = root + "/../../.env"
    load_dotenv(env_path)
    conn = mysql.connector.connect(
        host=f"{os.environ.get("DB_SERVER")}",
        port=os.environ.get("DB_PORT"),
        user=f"{os.environ.get("MYSQL_USER")}",
        password=f"{os.environ.get("MYSQL_PASSWORD")}",
        database=f"{os.environ.get("MYSQL_DATABASE")}"
    )

    curr = conn.cursor()
    curr.execute(query)
    results = curr.fetchall()
    curr.close()
    return results

# Create your views here.
def index(request):
    template = loader.get_template("chat/index.html")
    return HttpResponse(template.render({}, request))

def dash(request):
    template = loader.get_template("chat/dash.html")
    properties = db_execute("SELECT * FROM properties")
    clean_properties = []
    for row in properties:
        clean_properties.append({
            "straße": row[1], 
            "hausnummer": row[2],
            "plz": row[3],
            "ort": row[4],
            "land": row[5],
            "baujahr": row[6],
            "zustand": row[7],
            "zimmer": row[8],
            "wohnfläche": row[9],
            "art": row[10]})
    
    realtor = db_execute("SELECT * FROM realtor")
    clean_realtor = []
    for row in realtor:
        clean_realtor.append({
            "vorname": row[1], 
            "nachname": row[2]})
    
    owner = db_execute("SELECT * FROM owner")
    clean_owner = []
    for row in owner:
        clean_owner.append({
            "vorname": row[1], 
            "nachname": row[2],
            "geburtsdatum": row[3],
            "email": row[4],
            "telefonnummer": row[5]})
    
    buyer = db_execute("SELECT Vorname, Nachname, Budget, Art, Ort, ZimmerMin, ZimmerMax, WohnflächeMin, WohnflächeMax, Zustand FROM buyer LEFT JOIN criteria ON buyer.SuchkriterienId=criteria.id")
    clean_buyer = []
    for row in buyer:
        clean_buyer.append({
            "vorname": row[0], 
            "nachname": row[1],
            "budget": row[2],
            "art": row[3],
            "ort": row[4],
            "zimmerMin": row[5],
            "zimmerMax": row[6],
            "wohnflächeMin": row[7],
            "wohnflächeMax": row[8],
            "zustand": row[9]})

    return HttpResponse(template.render({
        "properties": clean_properties, 
        "realtor": clean_realtor,
        "buyer": clean_buyer,
        "owner": clean_owner
        }, request))

def event(request):
    template = loader.get_template("chat/event.html")

    events = db_execute("SELECT realtor.Vorname, realtor.Nachname, buyer.Vorname, buyer.Nachname, Straße, Hausnummer, Inhalt, DatumUhrzeit FROM event LEFT JOIN buyer ON event.buyerId = buyer.id LEFT JOIN realtor ON event.realtorId = realtor.id LEFT JOIN properties ON event.propertiesId = properties.id")
    clean_events = []
    for row in events:
        print(row[7])
        clean_row = {
            "realtor": row[0] + " " + row[1],
            "buyer": row[2] + " " + row[3],
            "content": row[6],
            "time": str(row[7])
        }

        if (row[4] != None and row[5] != None):
            clean_row["property"] = row[4] + " " + row[5]

        clean_events.append(clean_row)

    return HttpResponse(template.render({"events": clean_events}, request))

def note(request):
    template = loader.get_template("chat/note.html")

    notes = db_execute("SELECT Typ, Inhalt, Vorname, Nachname FROM note LEFT JOIN buyer ON note.buyerId=buyer.id")
    clean_notes = []
    for row in notes:
        clean_notes.append({
            "typ": row[0], 
            "inhalt": row[1],
            "vorname": row[2],
            "nachname": row[3]})
        
    return HttpResponse(template.render({"notes": clean_notes}, request))

def login(request):
    template = loader.get_template("chat/login.html")
    return HttpResponse(template.render({}, request))
