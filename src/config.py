import json

with open('config/config.json', 'r') as file:
    config = json.load(file)

domain = config['domain']
proxy = config['proxy']
signup_worker_num = config['signupWorkerNum']
email_worker_num = config['emailWorkerNum']

email_addr = config['emailAddr']
email_password = config['emailPassword']
email_imap_server = config['emailImapServer']
email_imap_port = config['emailImapPort']

yes_client_key = config['yesClientKey']
cf_solver_proxy = config['cfSolverProxy']

capsolver_key = config['capsolverKey']

max_success_accounts = config['maxSuccessAccounts']
max_failure_accounts = config['maxFailureAccounts']

if not max_success_accounts:
    max_success_accounts = -1
else:
    max_success_accounts = int(max_success_accounts)

if not max_failure_accounts:
    max_failure_accounts = -1
else:
    max_failure_accounts = int(max_failure_accounts)

if not yes_client_key:
    raise Exception("yes client key is required")

if not cf_solver_proxy:
    raise Exception("cf solver proxy is required")

if not capsolver_key:
    raise Exception("capsolver key is required")
