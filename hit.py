import requests

url = "http://msilstaging/Webservice/REST/Summit_RESTWCF.svc/RESTService/CommonWS_JsonObjCall"

payload = {
    "ServiceName": "SR_GetServiceRequestList",
    "objCommonParameters": {
        "_ProxyDetails": {
            "AuthType": "APIKEY",
            "APIKey": "sWkL0CqC1bikNDIJvI66eNxPVBMgNTtlSX31d5kZ4OM=",
            "TokenID": "",
            "OrgID": "1",
            "ReturnType": "JSON",
            "ProxyID": 0
        },
        "objSR_SearchFilterParam": {
            "Executive": 1,
            "WorkgroupName": "",
            "CurrentPageIndex": 0,
            "PageSize": 5,
            "OrgID": "1",
            "Instance": "Info",
            "Status": "Open",
            "strUpdatedFromDate": "",
            "strUpdatedToDate": "",
            "IsWebServiceRequest": True
        }
    }
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(
    url,
    json=payload,
    headers=headers,
    timeout=30
)

print("Status:", response.status_code)
print(response.text)