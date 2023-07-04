''' This script can be used to enable or disable Prisma Cloud CSPM policies based on policy severity level(s).

syntax: python3 updatepolicies-mt.py <severity> <true/false>
for example:  use 'python3 updatepolicies-mt.py high,critical true' to enable all CSPM high and critical policies globally

Enabled = true sets policies to enabled
Enabled = false sets policies to disabled
You can specify multiple severity levels separated by comma, for example: python updatepolicies-mt.pyinformational,low,medium true

The script usesconcurrent.futures librar for parallel processing.

Author: Binh Phan

'''

import requests
import json
import concurrent.futures
import argparse

# Replace these with your actual access key and secret key
access_key = 'Your_Access_Key'
secret_key = 'Your_Secret_Key'
# Replace this with your actual tenant URL
url = 'https://Your_Tenant_URL'

# Login URL
login_url = f'{url}/login'
# Policies URL
policies_url = f'{url}/policy'

# Function to get authentication token
def get_token():
    # Login payload
    payload = {
        'username': access_key,
        'password': secret_key
    }
    # Make POST request to login URL with the payload, raise an exception if an HTTP error occurred
    response = requests.post(login_url, json=payload)
    response.raise_for_status()
    # Return the token
    token = response.json()['token']
    return token

# Function to get all policies
def get_policies(token):
    headers = {
        'x-redlock-auth': token
    }
    # Make GET request to policies URL, raise an exception if an HTTP error occurred
    response = requests.get(policies_url, headers=headers)
    response.raise_for_status()
    # Return the policies
    policies = response.json()
    return policies

# Function to set the status of a policy
def set_policy_status(token, policy, severities, status):
    headers = {
        'x-redlock-auth': token,
        'Content-Type': 'application/json'
    }
    # If the severity of the policy is in the list of severities, set the status of the policy
    if policy['severity'] in severities:
        policy['enabled'] = status
        # Make PUT request to the policy URL, raise an exception if an HTTP error occurred
        response = requests.put(f"{policies_url}/{policy['policyId']}", headers=headers, json=policy)
        response.raise_for_status()

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Modify policies based on given severities and status.')
    parser.add_argument('severities', type=lambda s: [item for item in s.split(',') if item in ['informational', 'low', 'medium', 'high', 'critical']],
                        help='Comma-separated list of severities of the policies to modify.')
    parser.add_argument('status', type=lambda x: str(x).lower() == 'true', help='The status to set for the policies. Use "true" to enable and "false" to disable.')
    args = parser.parse_args()

    # Get token and policies
    token = get_token()
    policies = get_policies(token)

    # Create a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # For each policy, submit a new task to the executor
        futures = [executor.submit(set_policy_status, token, policy, args.severities, args.status) for policy in policies]
        # As the tasks complete, get their results (or exception if one occurred)
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                # Print any exceptions that occurred
                print(f"An exception occurred: {e}")

# If this script is being run directly, run the main function
if __name__ == '__main__':
    main()
