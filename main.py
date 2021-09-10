import requests
from requests.auth import HTTPDigestAuth
import os

atlas_token_public = os.environ["INPUT_TOKEN_PUBLIC"]
atlas_token_private = os.environ["INPUT_TOKEN_PRIVATE"]
atlas_project = os.environ["INPUT_PROJECT"]
service_name = os.environ["INPUT_SERVICE"]
src_region = os.environ["INPUT_SRC_REGION"]
dst_region = os.environ["INPUT_DST_REGION"]
arb_region = os.environ["INPUT_ARB_REGION"]

# atlas_token_public = ""
# atlas_token_private = ""
# atlas_project = "fras-t-tst"
# service_name = "Cluster0"
# src_region = "WESTERN_EUROPE"
# dst_region = "EUROPE_WEST_4"
# arb_region = "EUROPE_NORTH_1"

# warning IP whitelist du token utilisé

atlas_project_id = "0"

base_url = "https://cloud.mongodb.com/api/atlas/v1.0"
auth = HTTPDigestAuth(atlas_token_public, atlas_token_private)
headers = {"Content-type": "application/json", "Accept": "application/json"}

response = requests.get(
    base_url + "/groups/byName/" + atlas_project,
    auth=auth,
    headers=headers,
)
res_json = response.json()
if "id" in res_json:
    atlas_project_id = res_json["id"]

response = requests.get(
    base_url + "/groups/" + atlas_project_id + "/clusters/" + service_name,
    auth=auth,
    headers=headers,
)
res_json = response.json()
if (
    response.status_code == 403
    and res_json["errorCode"] == "IP_ADDRESS_NOT_ON_ACCESS_LIST"
):
    output = "IP whitelist KO"
elif response.status_code != 200:
    output = "Service or project unavailable"

else:
    print(res_json["replicationSpec"])
    if (
        src_region in res_json["replicationSpec"]
        and dst_region in res_json["replicationSpec"]
        and arb_region in res_json["replicationSpec"]
    ):
        if (
            res_json["replicationSpec"][src_region]["priority"]
            > res_json["replicationSpec"][dst_region]["priority"]
            and res_json["replicationSpec"][dst_region]["priority"]
            > res_json["replicationSpec"][arb_region]["priority"]
        ):
            print("ready to switch")
            # tjs array a une seule entree???? a verifier
            specs = res_json["replicationSpecs"][0]
            p_high = specs["regionsConfig"][src_region]["priority"]
            p_mid = specs["regionsConfig"][dst_region]["priority"]
            specs["regionsConfig"][src_region]["priority"] = p_mid
            specs["regionsConfig"][dst_region]["priority"] = p_high
            data = {"replicationSpecs": [specs]}
            print(data)
            response = requests.patch(
                base_url + "/groups/" + atlas_project_id + "/clusters/" + service_name,
                auth=auth,
                json=data,
                headers=headers,
            )
            if response.status_code == 200:
                output = "region switch in progress"
            else:
                output = "failed to switch"
        else:
            output = "wrong replication way"
    else:
        output = "wrong regions"

print("::set-output name=myres:: " + atlas_project + " - " + output)
