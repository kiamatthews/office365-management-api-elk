import adal, json, requests, socket

# Remote Server to Receive Logs
TCP_IP = 'LOGSTASH-IP'
TCP_PORT = PORT

#Office 365 Authentication variables
clientid = "YOUR-APPLICATION-ID"
tenant_id = "YOUR-TENANT-ID"
resource = "https://manage.office.com"
private_key = open("YOUR-PRIVATE-KEY-FILENAME.pem", "r").read()
public_key_thumbprint = "YOUR-PUBLIC-KEY-THUMBPRINT"

#Request access token
context = adal.AuthenticationContext('https://login.microsoftonline.com/{}'.format(tenant_id))
token = context.acquire_token_with_client_certificate(
    resource,
    clientid,
    private_key,
    public_key_thumbprint)

#add access token to header
header = {"Authorization": "Bearer {}".format(token['accessToken'])}

#set time frame for query
start_time = "2018-07-15T11:55"
end_time = "2018-07-15T11:56"

#poll to get available content
response = requests.get("https://manage.office.com/api/v1.0/{}/activity/feed/subscriptions/content?contentType=Audit.AzureActiveDirectory&startTime={}&endTime={}".format(tenant_id, start_time, end_time), headers=header)

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

        else:
            print (response.json())
else:
    print (response.json())
