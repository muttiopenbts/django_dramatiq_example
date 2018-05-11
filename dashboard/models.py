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
                return output.decode('utf-8','ignore')
            except Exception as e:
                return("Problem retrieving output\n{}".format(e))

    def _process(self):
        output = subprocess.check_output(self.cmd_list.split(','))
        if output:
            self._output = base64.urlsafe_b64encode(output).decode("utf-8")

    def process(self):
        self._processPipes()

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
