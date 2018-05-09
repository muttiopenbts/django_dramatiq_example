from django.shortcuts import redirect, render

from .models import Job
from .tasks import process_job
import base64


def index(request):
    if request.method == "POST":
        job = Job.objects.create(type=request.POST["type"],cmd_list=request.POST["cmd_list"])
        process_job.send(job.pk)
        return redirect("index")
    return render(request, "dashboard/index.html", {
        "jobs": Job.objects.order_by("-created_at").all(),
    })
