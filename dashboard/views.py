from django.shortcuts import redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django_tables2 import SingleTableView
import django_tables2 as tables

from .models import Job
from .tasks import process_job


class JobTable(tables.Table):
    signature = tables.Column(attrs={'td': {'style': 'width: 100px; overflow: auto'}})
    get_output = tables.TemplateColumn('{{ record.get_output|linebreaks }}')
    class Meta:
        model = Job
        attrs = {'class': 'table table-hover table-bordered'}
        fields = ('id','cmd_list','user','get_output','signature',)


class IndexView(LoginRequiredMixin, SingleTableView):
    model = Job
    template_name = 'dashboard/index.html'

    context_object_name = 'jobs'  # Default: object_list

    paginate_by = 5

    queryset = Job.objects.filter(
    ).order_by('-created_at')

    table_class = JobTable



class JobCreate(LoginRequiredMixin, CreateView):
    model = Job
    template_name = 'dashboard/index.html'

    fields = [
        'cmd_list',
        'signature',
    ]

    success_url = reverse_lazy('dashboard:index')

    def form_valid(self, form):
        user = self.request.user
        # Save the form and values to db
        form.instance.user = user
        self.object = form.save()
        # Process job will reference job pk
        process_job.send(self.object.pk)

        return HttpResponseRedirect(self.get_success_url())
