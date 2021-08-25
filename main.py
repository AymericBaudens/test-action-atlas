import requests
import json
import os

# apitoken = os.environ["INPUT_TOKEN"]
# aiven_project = os.environ["INPUT_PROJECT"]
apitoken = ""
aiven_project = "fras-t-tst"
base_url = "https://api.aiven.io/v1"
euw1_service_name = "primary-region-db"
euw4_service_name = "recovery-region-db"
headers = {"Authorization": "aivenv1 " + apitoken}

# print("::set-output name=myres::coucou " + aiven_project)

req_url = base_url + "/project/" + aiven_project + "/service"

reseuw1 = requests.get(
    req_url + "/" + euw1_service_name,
    headers=headers,
)
reseuw4 = requests.get(
    req_url + "/" + euw4_service_name,
    headers=headers,
)

if reseuw1.status_code == 200 and reseuw4.status_code == 200:
    service_euw1 = json.loads(reseuw1.text)
    service_euw4 = json.loads(reseuw4.text)

    service_euw1_integ_id = "euw1ko"
    service_euw4_integ_id = "euw4ko"

    if "service_integrations" in service_euw1["service"]:
        for service_integration in service_euw1["service"]["service_integrations"]:
            if (
                service_integration["integration_type"] == "read_replica"
                and service_integration["active"]
            ):
                service_euw1_integ_id = service_integration["service_integration_id"]
    if "service_integrations" in service_euw4["service"]:
        for service_integration in service_euw4["service"]["service_integrations"]:
            if (
                service_integration["integration_type"] == "read_replica"
                and service_integration["active"]
            ):
                service_euw4_integ_id = service_integration["service_integration_id"]

    # + erreur si services n existent pas
    # + verifier sens de la replication
    # + ko si plusieurs replications

    if service_euw1_integ_id == service_euw4_integ_id:
        print("Integration to be deleted: " + service_euw1_integ_id)

        req_url = (
            base_url
            + "/project/"
            + aiven_project
            + "/integration/"
            + service_euw1_integ_id
        )

        res = requests.delete(
            req_url,
            headers=headers,
        )

        output = "failed to delete"
        if res.status_code == 200:
            deletion = json.loads(res.text)
            if deletion["message"] == "deleted":
                output = "youpi"
    else:
        output = "not ready to switch"

else:
    output = "services unavailable"

print(output)
