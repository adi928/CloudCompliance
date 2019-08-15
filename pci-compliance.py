import requests
import json

with open('config-azure.json') as json_config:
    data = json.load(json_config)

with open('policies-required.json') as req_policies:
    requiredPolicies = json.load(req_policies)

SUBSCRIPTION_ID = data['subscription-id']
CLIENT_ID = data['client-id']
TENANT_ID = data['tenant-id']
CLIENT_SECRET = data['secret']

policyName = "pciControlSeceon"

def getAccessToken():
    body_post = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "resource": "https://management.azure.com"
    }
    url = "https://login.microsoftonline.com/"+TENANT_ID+"/oauth2/token"

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    resp = requests.post(url, data = body_post, headers = headers)
    resp = resp.json()
    return resp.get('access_token')


def getAllBuiltInPolicies(accessToken):
    listForPolicyDefSet = []
    header = {
        'Authorization' : 'Bearer '+accessToken,
        'Content-Type' : 'application/json'
    }
    for definitions in requiredPolicies.get('PolicyNames'):
        policyRec = {}
        url = "https://management.azure.com" + definitions + "?api-version=2019-01-01"
        policyDefs = requests.get(url, headers=header)
        policyDefs = policyDefs.json()
        policyRec['policyDefinitionId'] = definitions
        parameterRec = {}
        paramName = policyDefs['properties']['parameters']
        for param in paramName:
            paramValue = policyDefs['properties']['parameters'][param]['defaultValue']
            parameterRec[param] = {'value': paramValue}
        if len(parameterRec) != 0:
            policyRec['parameters'] = parameterRec
        listForPolicyDefSet.append(policyRec)
    return listForPolicyDefSet



def makePolicySetFromRequiredPolicies(accessToken):
    # Get All the policy definitions
    # Generate json from filtered policies
    listOfPolicyDefsAndParams = getAllBuiltInPolicies(accessToken)
    propertiesJSON = {
        "displayName" : "PCI Controls",
        "description" : "This is a set of policies for enforcing PCI compliance",
        "metadata" : {
            "category" : "PCI Compliance",
        }
    }

    propertiesJSON['policyDefinitions'] = listOfPolicyDefsAndParams
    '''
    For example:
    {
      "properties": {
        "displayName": "Cost Management",
        "description": "Policies to enforce low cost storage SKUs",
        "metadata": {
          "category": "Cost Management"
        },
        "policyDefinitions": [...]
    }
    '''
    return {"properties": propertiesJSON}

def createPolicySet(accessToken, policySetDefinition):
    url = "https://management.azure.com/subscriptions/"+SUBSCRIPTION_ID+"/providers/Microsoft.Authorization/policySetDefinitions/"+policyName+"?api-version=2019-01-01"
    header = {
        'Authorization': 'Bearer ' + accessToken,
        'Content-Type': 'application/json'
    }
    print("Making request with the following paramters:\n")
    print("Header: " + header.__str__())
    print("Requesting URL: " + url)
    print("Policy Set Definition: \n"+json.dumps(policySetDefinition))
    resp = requests.put(url, headers=header, data=json.dumps(policySetDefinition))
    print("Policy created with the following data:")
    print(resp.text)


def assignPolicies(accessToken, policyName):
    scope = "subscriptions/"+SUBSCRIPTION_ID
    url = "https://management.azure.com/"+scope+"/providers/Microsoft.Authorization/policyAssignments/"+policyName+"?api-version=2019-01-01"
    reqBody = {
      "location": "centralindia",
      "identity": {
        "tenantId": "9a91ec69-ffe6-4d00-867a-27cc570e6c24",
        "type": "SystemAssigned"
      },
      "properties": {
        "displayName": "PCI control implementations",
        "description": "PCI compliance assignment for seceon testing",
        "metadata": {
          "assignedBy": "Aditya Nath"
        },
        "policyDefinitionId": "/subscriptions/2a5934df-38ce-4bf7-bfef-946b13c388a5/providers/Microsoft.Authorization/policySetDefinitions/pciControlSeceon"
      }
    }
    header = {
        'Authorization': 'Bearer ' + accessToken,
        'Content-Type': 'application/json'
    }
    resp = requests.put(url, data=json.dumps(reqBody), headers=header)
    print("Policy assigned with the following data:")
    print(resp.text)


if __name__ == '__main__':
    accessToken = getAccessToken()
    policySetDefinition = makePolicySetFromRequiredPolicies(accessToken)
    createPolicySet(accessToken, policySetDefinition)
    assignPolicies(accessToken, policyName)
