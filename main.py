import requests
import json
import os

apitoken = os.environ["INPUT_TOKEN"]
aiven_project = os.environ["INPUT_PROJECT"]
src_service_name = os.environ["INPUT_SRC_SERVICE"]
dst_service_name = os.environ["INPUT_DST_SERVICE"]
# apitoken = ""
# aiven_project = "fras-t-tst"
# src_service_name = "primary-region-db"
# dst_service_name = "recovery-region-db"
base_url = "https://api.aiven.io/v1"
headers = {"Authorization": "aivenv1 " + apitoken}


req_url = base_url + "/project/" + aiven_project + "/service"

ressrc = requests.get(
    req_url + "/" + src_service_name,
    headers=headers,
)
resdst = requests.get(
    req_url + "/" + dst_service_name,
    headers=headers,
)

if ressrc.status_code == 200 and resdst.status_code == 200:
    service_src = json.loads(ressrc.text)
    service_dst = json.loads(resdst.text)

    service_src_integ_id = "srcko"
    service_dst_integ_id = "dstko"

    if "service_integrations" in service_src["service"]:
        for service_integration in service_src["service"]["service_integrations"]:
            if (
                service_integration["integration_type"] == "read_replica"
                and service_integration["active"]
                and service_integration["dest_service"] == dst_service_name
            ):
                service_src_integ_id = service_integration["service_integration_id"]
    if "service_integrations" in service_dst["service"]:
        for service_integration in service_dst["service"]["service_integrations"]:
            if (
                service_integration["integration_type"] == "read_replica"
                and service_integration["active"]
                and service_integration["source_service"] == src_service_name
            ):
                service_dst_integ_id = service_integration["service_integration_id"]
    if service_src_integ_id == service_dst_integ_id:
        print("Integration to be deleted: " + service_src_integ_id)

        req_url = (
            base_url
            + "/project/"
            + aiven_project
            + "/integration/"
            + service_src_integ_id
        )

        res = requests.delete(
            req_url,
            headers=headers,
        )

        output = "failed to delete"
        if res.status_code == 200:
            deletion = json.loads(res.text)
            if deletion["message"] == "deleted":
                output = "dst DB promote master started. src DB will be shutted down"
                # update service powered = false
    else:
        output = "not ready to switch"

else:
    output = "services unavailable"

print("::set-output name=myres:: " + aiven_project + " - " + output)
