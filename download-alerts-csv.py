import argparse
import requests
import time
import json

BASE_URL = "https://api.prismacloud.io" #Replace BASE_URL with the URL for your Prisma Cloud stack api1, api2, etc
API_ACCESS_KEY = "<API_ACCESS_KEY>" #Replace value with your API access key
API_SECRET_KEY = "<API_SECRET_KEY>" #Replace value with API secret key

""" Prisma Cloud API Documentation

1. Submit Alert CSV Generation Job
https://pan.dev/prisma-cloud/api/cspm/submit-an-alert-csv-download-job/

2. Get Alert CSV Job Status
https://pan.dev/prisma-cloud/api/cspm/get-alert-csv-job-status/

3. Download Alert CSV
https://pan.dev/prisma-cloud/api/cspm/download-alert-csv/

"""

def get_token(api_access_key, api_secret_key):
    url = f"{BASE_URL}/login"
    auth_data = {
        "username": api_access_key,
        "password": api_secret_key
    }
    response = requests.post(url, json=auth_data)
    response.raise_for_status()
    return response.json()["token"]

def parse_arguments():
    parser = argparse.ArgumentParser(description="Download Prisma Cloud alerts as CSV")
    parser.add_argument("-c", "--compliance", type=str, default=None,
                        help="Compliance standard name (optional)")
    parser.add_argument("-s", "--status", type=str, default=None,
                        help="Alert status (Open, Dismissed, Resolved) (optional)")
    parser.add_argument("-a", "--accounts", type=str, nargs="*", default=None,
                        help="Cloud accounts (separate multiple accounts with spaces) (optional)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose mode for debugging (optional)")
    return parser.parse_args()

args = parse_arguments()
compliance_standard_name = args.compliance
alert_status = args.status
cloud_accounts = args.accounts
verbose = args.verbose

token = get_token(API_ACCESS_KEY, API_SECRET_KEY)

headers = {
    "x-redlock-auth": token,
    "Content-Type": "application/json"
}

# Submit alert CSV generation job
submit_job_url = f"{BASE_URL}/alert/csv"
submit_job_data = {
    "detailed": True,
    "filters": []
}

if compliance_standard_name:
    submit_job_data["filters"].append({"complianceStandard": {"operator": "=", "value": compliance_standard_name}})

if alert_status:
    submit_job_data["filters"].append({"alertStatus": {"operator": "=", "value": alert_status}})

if cloud_accounts:
    submit_job_data["filters"].append({"cloud.account": {"operator": "IN", "value": cloud_accounts}})

if verbose:
    print("Submitting CSV generation job with the following data:")
    print(json.dumps(submit_job_data, indent=2))

response = requests.post(submit_job_url, headers=headers, data=json.dumps(submit_job_data))
response.raise_for_status()
job = response.json()

job_id = job["id"]
print(f"Job ID: {job_id}")

# Get status of CSV generation job
status_url = f"{BASE_URL}/alert/csv/{job_id}/status"

while True:
    response = requests.get(status_url, headers=headers)
    response.raise_for_status()
    job_status = response.json()

    if verbose:
        print("Job status:")
        print(json.dumps(job_status, indent=2))

    if job_status["status"] in ["COMPLETED", "READY_TO_DOWNLOAD"]:
        print("CSV generation job completed")
        break
    elif job_status["status"] == "FAILED":
        print("CSV generation job failed")
        break
    else:
        print("CSV generation job in progress")
        time.sleep(10)

# Download the alert CSV
download_url = f"{BASE_URL}/alert/csv/{job_id}/download"
response = requests.get(download_url, headers=headers)
response.raise_for_status()

csv_filename = f"alert_list.csv"
with open(csv_filename, "wb") as f:
    f.write(response.content)

print(f"Alert CSV downloaded as '{csv_filename}'")
```

Replace `<API_ACCESS_KEY>` and `<API_SECRET_KEY>` with your actual API
