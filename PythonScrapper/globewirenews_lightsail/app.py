import sys
import requests
import time
import pandas as pd
import mysql.connector as mysqldb
from config import *
from langid import classify
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from apscheduler.schedulers.background import BackgroundScheduler


def db_conn():
    ''' DataBase Connection '''
    try:
        connection = mysqldb.connect(host="localhost", port=3306, database="scrapper", user="dbmasteruser", password="", autocommit=True)
    except Exception as err:
        connection = mysqldb.connect(host="", port=3306, database="scrapper", user="dbmasteruser", password="", autocommit=True)
        print(err)
    return connection

def datashow(conn,cur):
    df = pd.read_sql_query("select company_title,news,timestamp from dataset", conn)
    data = df.values.tolist()

    if len(data) > 0:
        for entry in data:
            API_ENDPOINT = "https://hooks.zapier.com/hooks/catch/ouqpzyd/"
            data = {"data":{"Data Company Title":entry[0],"Data News":entry[1],"Data Timestamp":entry[2]}}
            headers = {'content-type': 'application/json'}
            requests.post(url = API_ENDPOINT, json= data, headers=headers)

            cur.execute("""Delete from dataset where news = %s""",(entry[1],))
        
    return conn,cur


def index():
    conn = db_conn()
    cur = conn.cursor(buffered=True)

    conn,cur = datashow(conn,cur)
    
    API_KEY = keys.scrapper
    URL_TO_SCRAPE = 'https://www.globenewswire.com/'
    
    payload = {'api_key': API_KEY, 'url': URL_TO_SCRAPE}
    req = requests.get('http://api.scraperapi.com', params=payload, timeout=60)

    html = req.text.strip()
    soup = BeautifulSoup(html,features="lxml")

    company_title =[entry.text.lower() for entry in soup.find_all('p', {"class":'company-title'})]
    news = [entry.text.lower() for entry in soup.find_all('h1', {"class":'post-title16px'})]
    timestamp1 = [entry.text.lower().split("ago")[0] + "ago" for entry in soup.find_all('p', {"class":'post-metadata'})]

    timestamp = []
    for index in range(len(timestamp1)):
        try:
            if timestamp1[index] == 'less than a minute ago':
                cet = int(time.time())+3600
                data = time.strftime("%d.%m.%Y %H:%M - %Z", time.localtime(cet))
                timestamp.append(data.split("-")[0].strip())
            else:
                minutes = int(timestamp1[index].split(" ")[0])
                cet = int(time.time())+3600
                data = time.strftime("%d.%m.%Y %H:%M - %Z", time.localtime(cet-minutes*60))
                timestamp.append(data.split("-")[0].strip())
        except:
            timestamp.append(timestamp1[index])

    data = []
    new_data = []
    for i in range(len(company_title)):
        if classify(news[i])[0] == 'en':
            cur.execute("select * from datacheck where company_title = %s and news = %s",(company_title[i],news[i]))
            value = cur.fetchall()
            if len(value) == 0:
                new_data.append((company_title[i],news[i],timestamp[i]))
                data.append((company_title[i],news[i],timestamp[i]))
    
    if len(data) != 0:
        for x in data:
            cur.execute("""INSERT INTO datacheck(company_title,news,timestamp) VALUES (%s, %s, %s)""", x)
    
    if len(new_data)!= 0:
        for new in new_data:
            cur.execute("""INSERT INTO dataset(company_title,news,timestamp) VALUES (%s, %s, %s)""", new)

    
    cur.execute("select * from datacheck")
    cur.fetchall()
    x = cur.rowcount
    print(x)

    if int(x) > 100:
        data = pd.read_sql_query("SELECT id FROM datacheck ORDER BY id LIMIT "+str(x-100),conn)
        list1 = (i[0] for i in data.values.tolist())
        for entry in list1:
            cur.execute("DELETE FROM dataset WHERE id = %s", (entry,))
    cur.close()
    conn.close()
    print("time to break")
    

sched = BackgroundScheduler(daemon=True)
sched.add_job(index,'interval', seconds=5, max_instances=1)
sched.start()


application = Flask(__name__)
api = Api(application)

@application.route("/")
def show():
    conn = db_conn()
    cur = conn.cursor()
    
    df = pd.read_sql_query("select company_title,news,timestamp from dataset", conn)
    data = df.values.tolist()

    for entry in data:
        company_title = entry[0]
        news = entry[1]
        time = entry[2]

        API_ENDPOINT = "https://hooks.zapier.com/hooks/catch/5556991/ouqpzyd/"

        data = {"data":{"Data Company Title":entry[0],"Data News":entry[1],"Data Timestamp":entry[2]}}

        headers = {'content-type': 'application/json'}

        r = requests.post(url = API_ENDPOINT, json= data, headers=headers)

        print(r.text)

    
    news = [i[1] for i in data]

    for new in news:
        cur.execute("""Delete from dataset where news = %s""",(new,))

    cur.close()
    conn.close()
    return jsonify({"data":{"company_title":company_title,"news":news,"timestamp":time}})


if __name__ == "__main__":
    application.run(host='0.0.0.0', port='8000')


