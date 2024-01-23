import json
import time
from abc import abstractmethod

from curl_cffi import requests, CurlHttpVersion

from config import capsolver_key, proxy
from log import logger


class ArkoseSolver(object):

    def __init__(self):
        self.session = requests.Session(
            impersonate="chrome99_android", proxies={"http": proxy, "https": proxy},
            http_version=CurlHttpVersion.V1_1,
            timeout=60
        )

    def get_arkose_token(self, payload):
        try:
            return self._get_arkose_token(payload)
        except Exception as e:
            logger.error(f"arkose get fail: {e}")
            raise e
        finally:
            self.session.close()

    @abstractmethod
    def _get_arkose_token(self, payload):
        pass


class Capsolver(ArkoseSolver):

    def _get_arkose_token(self, arkose_data_payload):
        logger.debug(f"start get arkose with arkose_data_payload: {arkose_data_payload}")

        url = "https://api.capsolver.com/createTask"
        payload = json.dumps({
            "clientKey": capsolver_key,
            "appId": "96BC17EB-3409-4ACA-AB4E-8643EA184A61",
            "task": {
                "type": "FunCaptchaTaskProxyLess",
                "websitePublicKey": "0655BC92-82E1-43D9-B32E-9DF9B01AF50C",
                "websiteURL": "https://chat.openai.com",
                "data": json.dumps({"blob": arkose_data_payload})
            }
        }
        )

        task_id = None

        for i in range(3):
            try:
                resp = self.session.post(url, data=payload, timeout=10)
                resp_json = resp.json()
                task_id = resp_json["taskId"]
                break
            except Exception as e:
                logger.warning(f"fail to create arkose task retry: {i}")

        if task_id:
            url = "https://api.capsolver.com/getTaskResult"
            status = ""
            while status == "" or status == "processing":
                time.sleep(1)

                logger.debug(f"{task_id} waiting for arkose token status: {status}")

                task = self.session.post(url, json={
                    "clientKey": "CAP-569BBC9FD5F22A478D466A01D3357C25",
                    "taskId": task_id
                })

                task_json = task.json()

                status = task_json["status"]

                if status == "ready":
                    return task_json["solution"]["token"]
                elif status == 'failed':
                    raise Exception(f"arkose get fail {task_json}")
        else:
            raise Exception("fail to get arkose token")
