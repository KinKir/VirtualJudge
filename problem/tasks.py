from VirtualJudgeSpider.config import Problem
from celery import shared_task

from problem import models
from problem.dispatcher import ProblemDispatcher


@shared_task
def get_problem_task(problem_id):
    problem = models.Problem.objects.get(id=problem_id)
    if problem.request_status in [Problem.Status.STATUS_PENDING.value,
                                  Problem.Status.STATUS_SUBMIT_FAILED.value,
                                  Problem.Status.STATUS_PROBLEM_NOT_EXIST.value,
                                  Problem.Status.STATUS_NO_ACCOUNT.value]:
        problem.request_status = Problem.Status.STATUS_RUNNING.value
        problem.save()
    ProblemDispatcher(problem_id).submit()
