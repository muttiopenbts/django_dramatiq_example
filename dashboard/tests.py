import dramatiq

from django.test import TransactionTestCase, TestCase
from django.urls import reverse

from .models import Job
from .models import User
from .models import UserPublicKey
from .tasks import process_job


class TestCaseAnonymous(TestCase):
    def setUp(self):
        super().setUp()
        self.TEST_USER_NAME = 'testuser'
        self.TEST_USER_PASSWORD = '1X<ISRUkw+tuK'
        # Create a user
        test_user1 = User.objects.create_user(username=self.TEST_USER_NAME, password=self.TEST_USER_PASSWORD)
        test_user1.save()
        print(f'TEST USER {test_user1.username}')
        print(f'TEST USER {test_user1.id}')
        self.test_user = test_user1

    def test_public_key_create(self):
        # Create user public key
        self.test_user.key.create(public_key='key1')
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

        response = self.client.get(reverse('dashboard:home'))
        response = self.client.post(reverse('dashboard:post_job_new'), {'signature':'sig', 'cmd_list':'eeeee',}, follow=True)

        #print(f'Reponse: {response.content} {response.redirect_chain}')

        job = Job.objects.get()
        print(f'jobs: {job}')

        self.assertEqual(job.signature, 'sig')


class TestJobProcessing(TransactionTestCase):
    def setUp(self):
        super().setUp()

        self.broker = dramatiq.get_broker()
        self.worker = dramatiq.Worker(self.broker, worker_timeout=100)
        self.worker.start()

    def tearDown(self):
        super().tearDown()
        self.worker.stop()

    def test_can_process_jobs(self):
        # Given a web client
        # When I submit a job
        #response = self.client.post("/", {"type": Job.TYPE_FAST})
        response = self.client.post("/")
        #self.assertEqual(response.status_code, 302)

        # And wait for the queue and workers to complete
        self.broker.join(process_job.queue_name)
        self.worker.join()

        # Then I expect the job's status to be "done"
        #job = Job.objects.get()
        #self.assertEqual(job.status, Job.STATUS_DONE)
