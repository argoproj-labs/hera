from hera import Workflow, Task

from dyno.clients.middleware.dynet_iap import generate_dynet_iap_oauth_token
from hera import set_global_token, set_global_host

set_global_token(generate_dynet_iap_oauth_token().token)
set_global_host('https://argo.dynet.ai')

with Workflow('context') as w:
    Task('cowsay', image='docker/whalesay', command=['cowsay', 'foo'])

w.create()
