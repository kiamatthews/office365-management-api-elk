#!/usr/bin/env python3

import adal, json, logging, requests, socket, sys
import datetime

#Define logging
logging.basicConfig(
    filename="/var/log/o365_api/api_connector.log",
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s"
    )

# Remote Server to Receive Logs
TCP_IP = 'LOGSTASH-IP'
TCP_PORT = PORT

#Office 365 Authentication variables
clientid = "YOUR-APPLICATION-ID"
tenant_id = "YOUR-TENANT-ID"
resource = "https://manage.office.com"
private_key = open("YOUR-PRIVATE-KEY-FILENAME.pem", "r").read()
public_key_thumbprint = "YOUR-PUBLIC-KEY-THUMBPRINT"


#set time frame for query
timedelta = datetime.timedelta(minutes=10)
now = datetime.datetime.utcnow()
start = now - timedelta

start_time = start.strftime("%Y-%m-%dT%H:%M") #"2018-07-16T19:00"
end_time = now.strftime("%Y-%m-%dT%H:%M") #"2018-07-16T23:00"

def process():
    if response.status_code == 200:
        blobs = response.json()

        #iterate through list of available content blobs and pull URI
        for blob in blobs:
            uri = blob['contentUri']

            #use URI to make request for events contained in blob
            event_blob = requests.get(uri + "?PublisherIdentifier={}".format(tenant_id), headers=header)
            if event_blob.status_code == 200:
                events = json.loads(event_blob.content.decode('UTF-8'))

                #some blobs have more than one event - this will push each event individually via TCP
                for item in events:
                    event = item

                    # Open TCP connection to Logstash
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((TCP_IP, TCP_PORT))
                    # Send event over TCP connection
                    sock.send(str(json.dumps(event)).encode('utf-8'))
                    # Close Logstash TCP connection
                    sock.close()

            elif event_blob.status_code == 500:
                #print to stdout for use in Rundeck
                print ("URI query - Status code: " + str(event_blob.status_code))
                print (event_blob.json())
                #print to logfile
                logging.error("API status code: {} {} {} [content query]".format(event_blob.status_code, event_blob.json()['error']['code'], event_blob.json()['error']['message']))
                sys.exit() #comment this out to test if only some of the uri queries are returning errors

            else:
                #print to stdout for use in Rundeck
                print ("URI query - Status code: " + str(event_blob.status_code))
                print (event_blob.json())
                #print to logfile
                logging.error("API status code: {} {} [uri query]".format(event_blob.status_code, event_blob.json()['message']))
                sys.exit() #comment this out to test if only some of the uri queries are returning errors

    elif response.status_code == 500:
        #print to stdout for use in Rundeck
        print ("URI query - Status code: " + str(response.status_code))
        print (response.json())
        #print to logfile
        logging.error("API status code: {} {} {} [content query]".format(response.status_code, response.json()['error']['code'], response.json()['error']['message']))

    else:
        #print to stdout for use in Rundeck
        print ("Content query - Status code: " + str(response.status_code))
        print (response.json())
        #print to logfile
        logging.error("API status code: {} {} [content query]".format(response.status_code, response.json()['message']))

###### MAIN ######

#Request access token
context = adal.AuthenticationContext('https://login.microsoftonline.com/{}'.format(tenant_id))
token = context.acquire_token_with_client_certificate(
    resource,
    clientid,
    private_key,
    public_key_thumbprint)

#null access token check
if token['accessToken'] == None:
    logging.error("Null Access Token")
    #alert email@email.com

else:
    #add access token to header
    header = {"Authorization": "Bearer {}".format(token['accessToken'])}

    #poll to get available content
    response = requests.get("https://manage.office.com/api/v1.0/{}/activity/feed/subscriptions/content?contentType=Audit.AzureActiveDirectory&startTime={}&endTime={}".format(tenant_id, start_time, end_time), headers=header)

    while "NextPageUri" in response.headers:
        next_page = response.headers['NextPageUri']
        process()

        #use next page uri to get more blobs
        response = requests.get(next_page + "?PublisherIdentifier={}".format(tenant_id), headers=header)

    else:
        process()
