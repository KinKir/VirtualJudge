from django.contrib import admin
from submission.models import Submission


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'remote_oj', 'remote_id', 'verdict', 'remote_run_id', 'verdict_code', 'hook')


admin.site.register(Submission, SubmissionAdmin)
