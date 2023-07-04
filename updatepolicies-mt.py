''' This script is used to set Prisma Cloud CSPM policies using severity level and set policy status to enabled = true/false

Enabled = true sets policies to enabled
Enabled = false sets policies to disabled
For example: To disable all CSPM policies with severity level of 'informational', use 'python script.py informational true'
You can specify multiple severity levels separated by comma, for example: python script.py informational,low,medium true

The script usesconcurrent.futures librar for parallel processing.

Author: Binh Phan

'''

import requests
import json
import concurrent.futures
import argparse

access_key = 'Your_Access_Key'
secret_key = 'Your_Secret_Key'
url = 'https://Your_Tenant_URL'

login_url = f'{url}/login'
policies_url = f'{url}/policy'

def get_token():
    payload = {
        'username': access_key,
        'password': secret_key
    }
    response = requests.post(login_url, json=payload)
    response.raise_for_status()  # raise an exception if an HTTP error occurred
    token = response.json()['token']
    return token

def get_policies(token):
    headers = {
        'x-redlock-auth': token
    }
    response = requests.get(policies_url, headers=headers)
    response.raise_for_status()
    policies = response.json()
    return policies

def set_policy_status(token, policy, severities, status):
    headers = {
        'x-redlock-auth': token,
        'Content-Type': 'application/json'
    }
    if policy['severity'] in severities:
        policy['enabled'] = status
        response = requests.put(f"{policies_url}/{policy['policyId']}", headers=headers, json=policy)
        response.raise_for_status()

def main():
    parser = argparse.ArgumentParser(description='Modify policies based on given severities and status.')
    parser.add_argument('severities', type=lambda s: [item for item in s.split(',') if item in ['informational', 'low', 'medium', 'high', 'critical']],
                        help='Comma-separated list of severities of the policies to modify.')
    parser.add_argument('status', type=lambda x: str(x).lower() == 'true', help='The status to set for the policies. Use "true" to enable and "false" to disable.')
    args = parser.parse_args()

    token = get_token()
    policies = get_policies(token)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(set_policy_status, token, policy, args.severities, args.status) for policy in policies]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An exception occurred: {e}")

if __name__ == '__main__':
    main()

