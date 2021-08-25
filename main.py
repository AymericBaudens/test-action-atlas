import requests
import json

apitoken = ""
base_url = "https://api.aiven.io/v1"
aiven_project = "fras-t-tst"


print("::set-output name=myres::coucou")
headers = {"Authorization": "aivenv1 " + apitoken}
req_url = base_url + "/project/" + aiven_project + "/service"

res = requests.get(
    req_url,
    headers=headers,
)

if res.status_code == 200:
    json_data = json.loads(res.text)
    for service in json_data["services"]:
        for service_integration in service["service_integrations"]:
            if service_integration["integration_type"] == "read_replica":
                print(
                    "Integration to be deleted: "
                    + service_integration["service_integration_id"]
                )
                exit(0)
