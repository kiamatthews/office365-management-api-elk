import adal, json, requests

clientid = "YOUR-APPLICATION-ID"
tenant_id = "YOUR-TENANT-ID"
resource = "https://manage.office.com"
private_key = open("YOUR-PRIVATE-KEY-FILENAME.pem", "r").read()
public_key_thumbprint = "YOUR-PUBLIC-KEY-THUMBPRINT"

#request access token
context = adal.AuthenticationContext('https://login.microsoftonline.com/{}'.format(tenant_id))
token = context.acquire_token_with_client_certificate(
    resource,
    clientid,
    private_key,
    public_key_thumbprint)

#add access token to request header
header = {"Authorization": "Bearer {}".format(token['accessToken'])}

start_time = "2018-07-14T23:55"
end_time = "2018-07-14T23:56"

#poll to get available content
response = requests.get("https://manage.office.com/api/v1.0/{}/activity/feed/subscriptions/content?contentType=Audit.AzureActiveDirectory&startTime={}&endTime={}".format(tenant_id, start_time, end_time), headers=header)

print (response.status_code)
#if response.status_code == 200:

blobs = response.json()

print (blobs, file=open("blobs_test", "a"))

#iterate through list of available content blobs and pull URI
for blob in blobs:
    uri = blob['contentUri']
    print (uri, file=open("uri_test", "a"))
    #use URI to make request for events contained in blob
    event_blob = requests.get(uri + "?PublisherIdentifier={}".format(tenant_id), headers=header)
    events = event_blob.json()
    #print events to file
    print (event_blob.status_code, file=open("events", "a"))
    print (events, file=open("events", "a"))
