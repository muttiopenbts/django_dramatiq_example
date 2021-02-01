import time
import subprocess
import base64
import json
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
# pip install pycryptodome
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

'''
Auto create auth tokens when user accounts are created.
'''
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def test_sign(priv_key, cleartext):
    '''
    Use this function to unit test rsa PKCS#1 v1.5 signing process.
    param: priv_key, string of rsa private key
    param: cleartext, string of data that will be signed by the key and
           signature will be based on.

    returns byte encoded hex of signature.
    '''
    from Crypto.Signature import pkcs1_15
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import RSA
    
    message = cleartext.encode('utf-8')
    key = RSA.import_key(priv_key)
    h = SHA256.new(message)
    signature = pkcs1_15.new(key).sign(h)
    
    return signature


def verify_sign(pub_key, signature, data):
    '''
    Verifies with a public key from whom the data came that it was indeed
    signed by their private key

    Params
        public_key: string of rsa public key
        signature:  base64 encoded signature to be verified
        data:       plain text data from which signature is derived from
    
    Return
        Boolean:    True if the signature is valid; False otherwise.
    '''
    rsakey = RSA.importKey(pub_key)
    signer = pkcs1_15.new(rsakey)
    digest = SHA256.new()
    # Assumes the data is base64 encoded to begin with
    digest.update(data.encode('utf-8'))

    try:
        signer.verify(digest, base64.b64decode(signature))
        return True
    except (ValueError, TypeError):
        return False

class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    STATUS_PENDING = "pending"
    STATUS_DONE = "done"
    STATUSES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_DONE, "Done"),
    )
    signature = models.TextField(default='', 
            help_text='Paste RSA PKCS#1 v1.5 signature of command. Ensure final input is base64 encoded.',
            blank=False,)

    cmd_list = models.TextField(
        help_text='Comma separated list of command and parameters. e.g. ls,-la',
        blank=False,
        null=False,
    )

    status = models.CharField(
        max_length=7,
        choices=STATUSES,
        default=STATUS_PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    _output = models.TextField(default='', 
            help_text='Leave blank. This will dispay the result of the command.',
            blank=True,)
    
    @property
    def output(self):
        if self._output:
            try:
                output = base64.urlsafe_b64decode(self._output)
                return output.decode('utf-8','ignore')
            except Exception as e:
                return("Problem retrieving output\n{}".format(e))

    @output.setter
    def output(self, value):
        self._output = value

    def _process(self):
        output = subprocess.check_output(self.cmd_list.split(','))
        if output:
            self._output = base64.urlsafe_b64encode(output).decode("utf-8")

    def process(self):
        self._processPipesSecure()

    def _processPipes(self):
        cmd = self.cmd_list
        cmd_out = ''
        for i in range(len(cmd.split('|'))):
            if i < 1:
                cmd_out = subprocess.Popen(cmd.split('|')[i].split(','), stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            else:
                cmd_out = subprocess.Popen(cmd.split('|')[i].split(','), stdin=cmd_out.stdout, stdout=subprocess.PIPE,stderr=subprocess.PIPE)

        output,error = cmd_out.communicate()

        if output:
            self._output =  base64.urlsafe_b64encode(output).decode("utf-8")
        elif error:
            self._output =  base64.urlsafe_b64encode(error).decode("utf-8")

    def _processPipesSecure(self):
        cmd = self.cmd_list
        cmd_out = ''
        rsa_signature = self.signature
        signature_verified = False
        output = None
        error = 'None'
        public_key = None

        # Verify cmd rsa signature using users public key
        if self.user.pk:
            try:
                public_key = UserPublicKey.objects.get(pk=self.user.pk).public_key
            except UserPublicKey.DoesNotExist:
                pass

        try:
            if not public_key:
                error = 'User has no public key'
            elif not verify_sign(public_key, rsa_signature, cmd):
                error = f'Unable to verify command signature\n{public_key}, {cmd}'
            else:
                signature_verified = True
        except:
            pass

        if signature_verified:
            for i in range(len(cmd.split('|'))):
                if i < 1:
                    cmd_out = subprocess.Popen(cmd.split('|')[i].split(','), stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                else:
                    cmd_out = subprocess.Popen(cmd.split('|')[i].split(','), stdin=cmd_out.stdout, stdout=subprocess.PIPE,stderr=subprocess.PIPE)

            output,error = cmd_out.communicate()

            if output:
                self._output =  base64.urlsafe_b64encode(output).decode("utf-8")
            elif error:
                self._output =  base64.urlsafe_b64encode(error).decode("utf-8")
        else:
            self._output =  base64.urlsafe_b64encode(error.encode('utf-8')).decode("utf-8")


class UserPublicKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=1, related_name='key')
    public_key = models.TextField(default='',help_text='Upload user public key')
    created_at = models.DateTimeField(
        auto_now_add=True,
    )


class Rpc(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    rpc = models.TextField(default='',help_text='Remote procedure call')
    # If rpc has no params, caller must at least specify empty dict {}.
    params = models.TextField(default='',
            help_text='Base64 encoded parameters in json format to be passed to the RPC function.')
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    timestamp = models.DateTimeField(default = "2020-01-01 00:00:00")

    STATUS_PENDING = "pending"
    STATUS_DONE = "done"
    STATUSES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_DONE, "Done"),
    )

    status = models.CharField(
        max_length=7,
        choices=STATUSES,
        default=STATUS_PENDING,
    )

    output = models.TextField(default='', 
            help_text='Leave blank. This will dispay the result of the rpc.',
            blank=True,)

    signature = models.TextField(default='', 
            help_text='Paste RSA PKCS#1 v1.5 signature of command. Ensure final input is base64 encoded.',
            blank=False,)

    def verify_signature(self):
        '''Verify provided signature for rpc.
        The signature provided by the caller has a very specific format.
        TODO: After a signature is verified as accurate, subsequent validation will take place to
        reduce likelihood of replay attacks (timestamps).
        '''
        public_key = None
        signaure_json_str = json.dumps({ 
            'rpc': self.rpc,
            'rpc_params': self.params,
            'timestamp' : self.timestamp.isoformat(),
        })
        signature_verified = False
        print(f'{repr(signaure_json_str)}')

        # Verify cmd rsa signature using users public key
        if self.user.pk:
            try:
                public_key = UserPublicKey.objects.get(pk=self.user.pk).public_key
            except UserPublicKey.DoesNotExist:
                pass

        try:
            if not public_key:
                print(f'User has no public key')
            elif not verify_sign(public_key, self.signature, signaure_json_str):
                print(f'Unable to verify command signature\n{public_key}\n{signaure_json_str}')
            else:
                signature_verified = True
        except:
            print(f'Verify signature failed: {public_key}, {signaure_json_str}')

        return signature_verified

    def process(self):
        '''Convert rpc string to method name and run.
        Can pass argument of dictionary to method as base64 encoded json.
        TODO: Try to implement method argument encoded as pickle.
        TODO: Implement public key signing function on rpc calls.

        Params
        self.rpc:       string representing method name to call.
        self.params:    base64 encoded json. e.g. {"arg1_int": 4, "arg2_str": "hello"}, then base64 
        '''
        print(f'Process: {self.rpc}')

        # Test if rpc is authorized by verifying callers signature.
        if self.verify_signature():
            # Dispatch rpc
            method_to_call = getattr(self, self.rpc)
            # Convert params field from base64 to json
            params_json = base64.b64decode(self.params)
            params_dic = None

            try:
                params_dic = json.loads(params_json)
            except ValueError: 
                raise Exception(f'Decoding rpc params as json has failed.')

            method_to_call(params_dic)

    def multiply(self, params_dict):
        '''Example of a user defined rpc.
        '''
        list_of_ints = params_dict['list']
        total = 1

        for x in list_of_ints:
            total *= x

        self.output = total

    def square(self, params_dict):
        '''Example of being able to accept a numeric python funtion parameter.
        '''
        value = params_dict['integer']
        self.output = value * value
