# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import requests
from datetime import date,datetime, timedelta
import smtplib
import json
import http.client
import traceback

gmail_user = 'zomatorestaurantbot@gmail.com'
gmail_password = 'zomato123'

today = date.today()
timenow = datetime.now()
host = "https://cdn-api.co-vin.in/api/"
index = 1

def isnamepresent(hosp_name, regex):
    if hosp_name.lower().find(regex.lower()) != -1:
        return True
    else:
        return False

def makeRestCall(district_id,date_p):
    conn = http.client.HTTPSConnection("cdn-api.co-vin.in")
    payload = ''
    headers = {}
    conn.request("GET", "/api/v2/appointment/sessions/public/findByDistrict?district_id="+district_id+"&date="+date_p, payload,
                 headers)
    res = conn.getresponse()
    data = res.read()
    #print(data.decode("utf-8"))
    return json.loads(data.decode('utf-8'))['sessions']

def findVaccineByDistrict(district_id, date1=None, vaccine_type='COVAXIN', pincode=None, name_regex=None, buffer_days = 1,age_limit=45):
    url = host + "v2/appointment/sessions/public/findByDistrict?"
    today = date.today()
    timenow = datetime.now()
    for buf_days in range(0,buffer_days):
        if buf_days > 0:
            today = today + timedelta(days=1)
            date1 = today.strftime("%d-%m-%Y")
            print("Checking for next date", date1)
        elif buf_days==0:
            date1 = today.strftime("%d-%m-%Y")
            print("Checking for ", date1)

        params = {'district_id': district_id, "date": date1}
        try:
            #response = requests.get(url=url, params=params)
            #data = response.json()['sessions']
            data = makeRestCall(district_id,date1)
            #data = []
        except Exception as e1:
            print(data)
            raise e1
        filter_data = data
        if vaccine_type is not None:
            filter_data = list(filter(lambda hospital: hospital['vaccine'] == vaccine_type, filter_data))
        if pincode is not None:
            filter_data = list(filter(lambda hospital: hospital['pincode'] == pincode, filter_data))
        if name_regex is not None:
            filter_data = list(filter(lambda hospital: isnamepresent(hospital['name'], name_regex), filter_data))
        if age_limit is not None:
            filter_data = list(filter(lambda hospital: hospital['min_age_limit'] == age_limit, filter_data))

        if len(filter_data) > 0:
            print(timenow.strftime("%m/%d/%Y, %H:%M:%S"))
            print(filter_data)
            filter_data_new = []
            for i in filter_data:
                i['slots'] = ' ,'.join(i['slots'])
                filter_data_new.append(i)
            filter_data = filter_data_new
            df = pd.DataFrame(filter_data)
            html = df.to_html()
            email_body = json.dumps(filter_data)
            send_email(html)
            print("----"*10)
            for hosp in filter_data:
                print("Hospital name:",hosp['name'],"available_capacity:",hosp['available_capacity'],"pincode:",hosp['pincode'],"area:",hosp['block_name'])
            print("----" * 10)
        else:
            print("No hospital found")


def send_email(email_response, email_address=['varunvt119@gmail.com', 'bhargavivt1@gmail.com', 'vstapas@gmail.com']):
    part2 = MIMEText(email_response, 'html')
    msg = MIMEMultipart('alternative')
    global index
    timenow = datetime.now()
    msg['Subject'] = timenow.strftime("%m/%d/%Y, %H:%M:%S") + ': Vaccine Finder Results #' + str(index)

    index = index +1
    msg['From'] = gmail_user
    msg['To'] = ", ".join(email_address)
    msg.attach(part2)
    #print("sending email to", ", ".email_address)
    try:
        smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo()
        smtpserver.login(gmail_user, gmail_password)
        smtpserver.sendmail("vaccine finder vt", email_address, msg.as_string())
        smtpserver.close()
        print('Email sent!')
    except Exception as e:
        print('Something went wrong while sending email...')
        print(e)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # BBMP 294
    # vaccine_type = "COVISHIELD"
    # vaccine_type = "COVAXIN"
    # hospital name = "MANIPAL NORTHSIDE CANARA UNIO"
    import time
    while True:
        try:
            #findVaccineByDistrict('294', vaccine_type='COVAXIN')
            findVaccineByDistrict('294', vaccine_type='COVAXIN',buffer_days=2)
            time.sleep(30)
            print("sleeping")
            print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        except Exception as e:
            #import traceback as t
            #t.print_exc(e)
            traceback.print_exc()
            print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            print("Continuing....")
            time.sleep(360)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
