import base64
import dramatiq

from django.test import TransactionTestCase, TestCase
from django.urls import reverse

from .models import Job
from .models import User
from .models import UserPublicKey

from .tasks import process_job
import base64
import time


class TestCaseJobs(TestCase):
    def setUp(self):
        super().setUp()
        self.TEST_USER_NAME = 'testuser'
        self.TEST_USER_PASSWORD = '1X<ISRUkw+tuK'
        # Create a user
        test_user1 = User.objects.create_user(username=self.TEST_USER_NAME, password=self.TEST_USER_PASSWORD, )
        test_user1.save()
        print(f'TEST USER {test_user1.username}')
        print(f'TEST USER {test_user1.id}')
        self.test_user = test_user1

        self.broker = dramatiq.get_broker()
        self.worker = dramatiq.Worker(self.broker, worker_timeout=100)
        self.worker.start()


    def tearDown(self):
        super().tearDown()
        self.worker.stop()


    def Test_public_key_create(self):
        # Generate new rsa key pair
        self.rsa_key = get_rsa_key()

        # Create user public key
        self.test_user.key.create(
                public_key=self.rsa_key.publickey().export_key().decode("utf-8"))
        print(f'user Key: {self.test_user.key.all()[0].public_key}')
        public_key = UserPublicKey.objects.get(id=self.test_user.key.all()[0].id)
        print(f'Key: {public_key.public_key}')
        self.assertEqual(self.test_user.key.all()[0].id, public_key.id)

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


    def test_login(self):
        login = self.client.login(username=self.TEST_USER_NAME, password=self.TEST_USER_PASSWORD)
        self.assertTrue(login)


    def test_job_create(self):
        # Client should have successfuly logged in
        response = self.client.get(reverse('dashboard:home'))
        # Expect test user to have public key saved in db
        self.Test_public_key_create()
        self.test_login()

        # Generate signature of os command
        CMD = 'uname'
        signature = get_cmd_sign(self.rsa_key.export_key().decode('utf-8'), CMD)
        b64_sig = base64.b64encode(signature).decode('utf-8')

        # Issue http post request
        response = self.client.post(reverse('dashboard:post_job_new'), {'signature':b64_sig, 'cmd_list':CMD,}, follow=True)

        # And wait for the queue and workers to complete
        self.broker.join(process_job.queue_name)
        self.worker.join()

        # Then I expect the job's status to be "done"
        job = Job.objects.get()

        print(f'job output: {job.output}\n{job.id}\n{job.cmd_list}\n{job.status}')

        self.assertEqual(job.signature, b64_sig)
        self.assertEqual(job.status, Job.STATUS_DONE)


class TestJobProcessing(TransactionTestCase):
    def setUp(self):
        super().setUp()

        self.broker = dramatiq.get_broker()
        self.worker = dramatiq.Worker(self.broker, worker_timeout=100)
        self.worker.start()

    def tearDown(self):
        super().tearDown()
        self.worker.stop()


def get_rsa_key():
    from Crypto.PublicKey import RSA

    key = RSA.generate(2048)
    return key

def get_cmd_sign(priv_key, cleartext):
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