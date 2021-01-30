'''
POC to help interact with django dramatiq web app.

Copied and modified from https://medium.com/centrality/building-repls-for-fun-and-profit-597ae4fcdd85
'''
import click
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import base64
from requests_html import HTMLSession


class DeepThought:
    # TODO: Work to do.
    def __init__(self, host):
        super().__init__()
        self.host = host
    @property
    def answer(self):
        print(f"Connecting to {self.host}...")
        return 42


def get_crypto_key(key_name_path:str):
    '''Returns the specified key as a crypto object.
    Param
        key_name_path:  Expects a string of where the rsa key can be read
                        from the file system.
    Returns
        RSA crypto object.
    '''
    key = RSA.import_key(open(key_name_path).read())

    return key


@click.command()
@click.option("--host", default="localhost", help="Host URI")
def main(host):
    header = "Deep Thought initialised as `cpu`. " \
             "Type `help(cpu)` for assistance."
    footer = ""
    scope_vars = {"cpu": DeepThought(host)}
    try:
        import IPython
    except ImportError:
        from code import InteractiveConsole
        InteractiveConsole(locals=scope_vars).interact(header, footer)
    else:
        print(header)
        IPython.start_ipython(argv=[], user_ns=scope_vars)
        print(footer)


def get_cmd_sign(priv_key_obj, cleartext):
    '''
    Use this function to unit test rsa PKCS#1 v1.5 signing process.
    param: priv_key, rsa private key object
    param: cleartext, string of data that will be signed by the key and
           signature will be based on.

    returns byte encoded hex of signature.
    '''

    message = cleartext.encode('utf-8')
    key = priv_key_obj
    h = SHA256.new(message)
    signature = pkcs1_15.new(key).sign(h)
    
    return signature


def authenticate(username, password, key_path):
    RSA_KEY_PATH = key_path
    USERNAME = username
    PASSWORD = password

    session = HTMLSession()
    # Load auth form in order to get csrf token
    r = session.get('http://127.0.0.1:8000/accounts/login')
    csrfmiddlewaretoken = r.html.search('value="{csrftoken}"')['csrftoken']
    r2 = session.post("http://127.0.0.1:8000/accounts/login/", data={
            'username':USERNAME, 
            'password':PASSWORD,
            'csrfmiddlewaretoken':csrfmiddlewaretoken})

    # Load add job form to get csrf token
    r3 = session.get('http://127.0.0.1:8000/jobs_list/')
    csrfmiddlewaretoken = r3.html.search('value="{csrftoken}"')['csrftoken']


def run_os_cmd(os_cmd:str, username:str, password:str, pub_key_path):
    '''Caller executes an OS command on agent.
    Result of command cannot be determined as called web endpoint isn't a propert api.
    Must check web ui for result.

    Params
        os_cmd: Operating system os command. Command parameters must
                be appended with a commas. e.g. 'ls,-la'
    '''
    CMD = os_cmd
    RSA_KEY_PATH = pub_key_path
    USERNAME = username
    PASSWORD = password

    session = HTMLSession()
    # Load auth form in order to get csrf token
    r = session.get('http://127.0.0.1:8000/accounts/login')
    csrfmiddlewaretoken = r.html.search('value="{csrftoken}"')['csrftoken']
    r2 = session.post("http://127.0.0.1:8000/accounts/login/", data={
            'username':USERNAME, 
            'password':PASSWORD,
            'csrfmiddlewaretoken':csrfmiddlewaretoken})

    # Load add job form to get csrf token
    r3 = session.get('http://127.0.0.1:8000/jobs_list/')
    csrfmiddlewaretoken = r3.html.search('value="{csrftoken}"')['csrftoken']

    # Sign os command
    rsa_key = get_crypto_key(RSA_KEY_PATH)
    signature = get_cmd_sign(rsa_key, CMD)
    b64_signature = base64.b64encode(signature).decode('utf-8')
    
    # Create new job
    r4 = session.post("http://127.0.0.1:8000/add/", data={
            'cmd_list':CMD, 
            'signature':b64_signature,
            'csrfmiddlewaretoken':csrfmiddlewaretoken})


def run_api_os_cmd(os_cmd:str, rsa_key_path:str, auth_token:str):
    '''Caller executes an OS command on agent.
    Calls web api.

    Params
        os_cmd: Operating system os command. Command parameters must
                be appended with a commas. e.g. 'ls,-la'
    '''
    import requests

    session = HTMLSession()
    CMD = os_cmd
    AUTH_TOKEN = auth_token
    BASE_URL = 'http://127.0.0.1:8000/'
    RSA_KEY_PATH = rsa_key_path

    # Sign os command
    rsa_key = get_crypto_key(RSA_KEY_PATH)
    signature = get_cmd_sign(rsa_key, CMD)
    b64_signature = base64.b64encode(signature).decode('utf-8')
    
    req = requests.Request('POST', 
            f'{BASE_URL}jobs/', 
            {'Authorization':f'Token {AUTH_TOKEN}',}, 
            json= {
                    'cmd_list':CMD, 
                    'signature':b64_signature},)

    #session.prepare_request(req)
    prep_req = session.prepare_request(req)
    res = session.send(prep_req)
    
    return res
    

if __name__ == "__main__":
    main()