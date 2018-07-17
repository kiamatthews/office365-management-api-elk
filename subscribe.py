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

#send subscription request
result = requests.post("https://manage.office.com/api/v1.0/{}/activity/feed/subscriptions/start?contentType=Audit.AzureActiveDirectory".format(tenant_id), headers=header)

print (result.json())
