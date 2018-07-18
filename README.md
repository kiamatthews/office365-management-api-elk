# Office 365 Management API Connector for the Elastic Stack (ELK)

This simple API connector queries the Office 365 Management API and pushes audit logs the Elastic Stack via Logstash. *This script was tested with Python 3.5 and 3.6.*

## Required modules
[Microsoft Azure Active Directory Authentication Library (ADAL) for Python](https://github.com/AzureAD/azure-activedirectory-library-for-python)
```
pip3 install adal
```
**IMPORTANT**: Before utilizing this script, you will need to create an Azure app to grant this script access to the API endpoints. [I've written a post about this (and my process while scripting this connector).](https://medium.com/@kiamatthews/office-365-management-api-connector-for-elk-b94fe4ed4a53)

Please note that I am a novice at both Python and working with APIs, so this script will likely be refined over time. Please let me know if you have any suggestions to improve the script!
