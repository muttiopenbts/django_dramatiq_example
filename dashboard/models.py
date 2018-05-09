import time
import subprocess
import base64
from django.db import models


class Job(models.Model):
    STATUS_PENDING = "pending"
    STATUS_DONE = "done"
    STATUSES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_DONE, "Done"),
    )

    _output = models.TextField(default='')
    cmd_list = models.TextField(default='',help_text='Command separated list of command and parameters.')
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
                return output.decode('utf-8')
            except:
                pass

    def process(self):
        output = subprocess.check_output(self.cmd_list.split(','))
        if output:
            self._output = base64.urlsafe_b64encode(output).decode("utf-8")
