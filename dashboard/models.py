import time
import subprocess
import base64
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
    
    message = data.encode('utf-8')
    key = RSA.import_key(priv_key)
    h = SHA256.new(message)
    signature = pkcs1_15.new(key).sign(h)
    
    return signature


def verify_sign(pub_key, signature, data):
    '''
    Verifies with a public key from whom the data came that it was indeed
    signed by their private key
    param: public_key, string of rsa public key
    param: signature base64 encoded signature to be verified
    param: data, plain text data from which signature is derived from
    return: Boolean. True if the signature is valid; False otherwise.
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
    _output = models.TextField(default='', 
            help_text='Leave blank. This will dispay the result of the command.',
            blank=True,)

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

    def get_output(self):
        if self._output:
            try:
                output = base64.urlsafe_b64decode(self._output)
                return output.decode('utf-8','ignore')
            except Exception as e:
                return("Problem retrieving output\n{}".format(e))

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
