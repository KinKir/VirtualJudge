from VirtualJudgeSpider import control
from django.db import DatabaseError
from rest_framework import status
from rest_framework.views import APIView, Response

from support.models import Language, Account, Support
from support.serializers import AccountSerializer
from support.serializers import LanguagesSerializer
from support.tasks import update_language_task
from utils.response import res_format, Message


class SupportAPI(APIView):

    def get(self, request, *args, **kwargs):
        try:
            support = list({item.oj_name for item in Support.objects.filter(oj_enable=True)})
            support.sort()
            return Response(res_format(support), status=status.HTTP_200_OK)
        except DatabaseError:
            return Response(res_format('System error', status=Message.ERROR),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AccountAPI(APIView):
    def post(self, request, *args, **kwargs):
        if request.user is None or request.user.is_authenticated is False or request.user.is_admin is False:
            return Response(res_format('Permission Denied', status=Message.ERROR), status=status.HTTP_200_OK)
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.save():
                return Response(res_format('operation success', status=Message.SUCCESS), status=status.HTTP_200_OK)
            else:
                return Response(res_format('operation failed', status=Message.ERROR),
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response(res_format(serializer.errors, status=Message.ERROR), status=status.HTTP_400_BAD_REQUEST)


class LanguagesAPI(APIView):

    def get(self, request, raw_oj_name, *args, **kwargs):
        remote_oj = control.Controller.get_real_remote_oj(raw_oj_name)
        if control.Controller.is_support(remote_oj):
            try:
                languages = Language.objects.filter(oj_name=remote_oj)
                return Response(res_format(LanguagesSerializer(languages, many=True).data), status=status.HTTP_200_OK)
            except DatabaseError:
                return Response(res_format('System error', status=Message.ERROR),
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(res_format('we do not support it', status=Message.ERROR), status=status.HTTP_400_BAD_REQUEST)


class FreshLanguageAPI(APIView):

    def post(self, request, *args, **kwargs):
        if request.user is None or request.user.is_authenticated is False or request.user.is_admin is False:
            return Response(res_format('Login required', status=Message.ERROR), status=status.HTTP_200_OK)
        try:
            accounts = Account.objects.all()
            for remote_oj in {account.oj_name for account in accounts}:
                update_language_task.delay(remote_oj)
            return Response(res_format('Refreshed successfully'), status=status.HTTP_200_OK)
        except DatabaseError:
            return Response(res_format('Refreshed error', status=Message.ERROR),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
