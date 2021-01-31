import dramatiq

from .models import Job
from .models import Rpc


@dramatiq.actor
def process_job(job_id):
    job = Job.objects.get(pk=job_id)
    job.process()

    job.status = Job.STATUS_DONE
    job.save()


@dramatiq.actor
def process_rpc(rpc_id):
    rpc = Rpc.objects.get(pk=rpc_id)
    # Call the dispatcher that will eventually send the request to the specified rpc function.
    rpc.process()

    rpc.status = Job.STATUS_DONE
    rpc.save()