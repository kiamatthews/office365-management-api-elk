import adal, json

clientid = "YOUR-APPLICATION-ID"
tenant_id = "YOUR-TENANT-ID"
resource = "https://manage.office.com"
private_key = open("YOUR-PRIVATE-KEY-FILENAME.pem", "r").read()
public_key_thumbprint = "YOUR-PUBLIC-KEY-THUMBPRINT"
context = adal.AuthenticationContext('https://login.microsoftonline.com/{}'.format(tenant_id))
token = context.acquire_token_with_client_certificate(
    resource,
    clientid,
    private_key,
    public_key_thumbprint)

print('Here is the token:')
print(json.dumps(token, indent=2))
