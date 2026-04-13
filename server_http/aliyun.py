# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os
import json
import asyncio

from alibabacloud_dypnsapi20170525 import models as dypnsapi_20170525_models
from alibabacloud_dypnsapi20170525.client import Client as Dypnsapi20170525Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_credentials.models import Config as CredentialConfig
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models

class SMS:
    LOGIN_REGISTER = "100001"
    MODIFY_PHONE   = "100002"
    RESET_PASSWORD = "100003"
    BIND_PHONE     = "100004"
    VERIFY_PHONE   = "100005"

    def __init__(self):
        pass

    @staticmethod
    def create_client() -> Dypnsapi20170525Client:
        """
        使用凭据初始化账号Client
        @return: Client
        @throws Exception
        """
        credentialsConfig = CredentialConfig(
            type='access_key',
            # 必填参数，此处以从环境变量中获取AccessKey ID为例
            access_key_id=os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID'),
            # 必填参数，此处以从环境变量中获取AccessKey Secret为例
            access_key_secret=os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
        )
        credentialsClient = CredentialClient(credentialsConfig)

        # 若使用云产品 V2.0 SDK 时，使用alibabacloud_tea_openapi.models模块的Config类传递credential
        config = open_api_models.Config(
            credential=credentialsClient,
            endpoint=f'dypnsapi.aliyuncs.com'
        )
        return Dypnsapi20170525Client(config)

    @classmethod
    async def sendSmsVerifyCodeRequest(
        cls,
        phone_number:str,
        template_code:str=LOGIN_REGISTER
    ) -> bool:
        client = cls.create_client()
        send_sms_verify_code_request = dypnsapi_20170525_models.SendSmsVerifyCodeRequest(
            sign_name='速通互联验证码',
            template_code=template_code,
            phone_number=phone_number,
            template_param='{"code":"##code##","min":"5"}'
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = await client.send_sms_verify_code_with_options_async(send_sms_verify_code_request, runtime)
            return resp.body.success
        except Exception:
            return False

    @classmethod
    async def checkSmsVerifyCodeRequest(
        cls,
        phone_number:str,
        verify_code:str
    ) -> bool:
        client = cls.create_client()
        check_sms_verify_code_request = dypnsapi_20170525_models.CheckSmsVerifyCodeRequest(
            phone_number=phone_number,
            verify_code=verify_code
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = await client.check_sms_verify_code_with_options_async(check_sms_verify_code_request, runtime)
            return resp.body.success
        except Exception:
            return False

if __name__ == '__main__':
    phone_number = "18784108903"
    print(asyncio.run(SMS.sendSmsVerifyCodeRequest(phone_number)))
    verify_code = input("verify code: ")
    print(asyncio.run(SMS.checkSmsVerifyCodeRequest(phone_number, verify_code)))
