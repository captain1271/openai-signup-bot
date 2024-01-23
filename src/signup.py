import secrets
import string
import threading
import time
import uuid
from urllib.parse import urlparse, parse_qs

from curl_cffi import requests, CurlHttpVersion
from func_timeout import func_timeout

from arkose_solver import Capsolver
from config import proxy
from log import logger, log_context
from pool_manager import ThreadPoolManager

csrf_url = "https://chat.openai.com/api/auth/csrf"
prompt_login_url = "https://chat.openai.com/api/auth/signin/auth0?prompt=login&screen_hint=signup"
ContentType = "application/x-www-form-urlencoded"
UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
auth_url = "https://auth0.openai.com"

check_identifier_url = f"{auth_url}/u/signup/identifier?state="
check_password_url = f"{auth_url}/u/signup/password?state="


class Signup:
    def __init__(self):
        self.session = requests.Session(
            impersonate="chrome99_android", proxies={"http": proxy, "https": proxy},
            http_version=CurlHttpVersion.V1_1,
            timeout=60
        )

        self.arkose_solver = Capsolver()

    def _get_csrf(self):
        retry = 5
        for i in range(retry):
            response = self.session.get(
                csrf_url,
                headers={
                    "Content-Type": ContentType,
                    "User-Agent": UserAgent,
                    "Referer": "https://platform.openai.com/"
                },
                allow_redirects=False,
                timeout=30,
            )
            if response.status_code == 200:
                logger.debug(f"success to get csrf")
                return response.json()["csrfToken"]
            else:
                logger.warning(f"fail to get csrf current retry: {i}")
            time.sleep(5)
        raise Exception(f"fail to get csrf after {retry} attempts please check your network or ip")

    def _get_authorized_url(self, csrf):
        headers = {
            "Content-Type": ContentType,
            "User-Agent": UserAgent,
        }
        data = {"callbackUrl": "/", "csrfToken": csrf, "json": "true"}

        retry = 5
        for i in range(retry):
            response = self.session.post(
                prompt_login_url, data=data, headers=headers, allow_redirects=False
            )
            if response.status_code == 200:
                logger.debug(f"success to get authorized url")
                return response.json()["url"]
            else:
                logger.warning(f"fail to get authorized url current retry: {i}")
            time.sleep(5)

        raise Exception(f"fail to get authorized url after {retry} attempts please check your network or ip")

    def _get_state(self, authorized_url):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "User-Agent": UserAgent,
            "Referer": "https://platform.openai.com/"
        }

        retry = 5
        for i in range(retry):
            try:
                response = self.session.get(authorized_url, headers=headers, allow_redirects=False)
                if response.status_code == 302:
                    location = response.headers.get("Location", "")
                    parsed_url = urlparse(location)
                    query_params = parse_qs(parsed_url.query)
                    return query_params.get("state", [None])[0]
            except Exception as e:
                logger.warning(f"fail to get state current retry: {i}")

        raise Exception(f"fail to get state after {retry} attempts please check your network or ip")

    def _check_identifier(self, state, identifier):
        form_param = {
            "email": identifier,
            "action": "default",
            "state": state,
        }

        headers = {
            "Content-Type": ContentType,
            "User-Agent": UserAgent,
        }

        retry = 3
        for i in range(retry):
            try:
                response = self.session.post(check_identifier_url + state, data=form_param, headers=headers,
                                             allow_redirects=False)
                if response.status_code == 302:
                    location = response.headers.get("Location", "")
                    response = self.session.get(
                        auth_url + location,
                        headers={"User-Agent": UserAgent},
                        allow_redirects=False,
                    )
                    if response.status_code == 200:
                        logger.debug(f"success to check identifier {identifier}")
                        return True
            except Exception as e:
                logger.warning(f"fail to check identifier current retry: {i}")

            time.sleep(5)

        raise Exception(f"fail to check identifier after {retry} attempts please check your network or ip")

    def _gen_and_check_identifier_password(self, state):

        retry = 5

        for i in range(retry):
            try:
                identifier = ''.join(
                    [secrets.choice(string.ascii_letters + string.digits) for _ in range(12)]) + "@madoka.free.hr"
                password = ''.join(
                    [secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(15)])

                self._check_identifier(state, identifier)

                form_param = {
                    state: state,
                    "email": identifier,
                    "password": password,
                    "action": "default",
                    "strengthPolicy": "low",
                    "complexityOptions.minLength": "12",
                }

                headers = {
                    "Content-Type": ContentType,
                    "User-Agent": UserAgent,
                }

                response = self.session.post(check_password_url + state, data=form_param, headers=headers,
                                             allow_redirects=True)

                if response.status_code == 200:
                    logger.debug(f"success to gen and check identifier {identifier} password {password}")
                    return identifier, password
                else:
                    logger.warning(
                        f"fail to gen and check identifier {identifier} password {password} current retry: {i}")
            except Exception as e:
                logger.debug(f"fail to gen and check identifier password current retry: {i}")
            time.sleep(5)
        raise Exception(
            f"fail to gen and check identifier password after {retry} attempts please check your network 、 ip 、 domain")

    def _get_access_token(self):
        url = "https://auth0.openai.com/authorize"
        param = {
            "client_id": "DRivsnm2Mu42T3KOpqdtwB3NYviHYzwD",
            "audience": "https://api.openai.com/v1",
            "redirect_uri": "https://platform.openai.com/auth/callback",
            "scope": "openid profile email offline_access",
            "response_type": "code",
            "response_mode": "query",
            "state": "R3k1aU10eU1oS0V3NDFScW1XNkwyNEVzR3NEZTU1aTkyLmtTZm16SGZEaQ==",
            "nonce": "WmtJSTg4Ylh+RFlCYlIuRGFTcDBjak5odkNkM1NqeEdibzBhVXFiVHdZYg==",
            "code_challenge": "glzkKxDTe8479-eV0YP8yKoelv2qXwfpJWJEGraHDH8",
            "code_challenge_method": "S256",
            "auth0Client": "eyJuYW1lIjoiYXV0aDAtc3BhLWpzIiwidmVyc2lvbiI6IjEuMjEuMCJ9"
        }
        headers = {
            "Content-Type": ContentType,
            "User-Agent": UserAgent,
            "Referer": "https://platform.openai.com/"
        }

        retry = 5

        for i in range(retry):

            try:
                response = self.session.get(url, params=param, headers=headers, allow_redirects=False)

                if response.status_code == 302:
                    location = response.headers.get("Location", "")
                    parsed_url = urlparse(location)
                    query_params = parse_qs(parsed_url.query)
                    code = query_params.get("code", [None])[0]
                    json = {
                        "client_id": "DRivsnm2Mu42T3KOpqdtwB3NYviHYzwD",
                        "code_verifier": "EsASZu9OM3Bzik6nvcEdoaTn7oRuPjFUcer~j2msUGe",
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": "https://platform.openai.com/auth/callback"
                    }

                    token_url = "https://auth0.openai.com/oauth/token"
                    response = self.session.post(token_url, json=json, headers=headers, allow_redirects=False)

                    resp_json = response.json()
                    access_token = resp_json["access_token"]
                    refresh_token = resp_json["refresh_token"]

                    logger.debug(f"success to get access token")
                    return access_token, refresh_token
            except Exception as e:
                logger.warning(f"fail to get access token current retry: {i}")

            time.sleep(5)

        raise Exception(f"fail to get access token after {retry} attempts please check your network or ip")

    def _login(self, access_token):
        url = "https://api.openai.com/dashboard/onboarding/login"
        headers = {
            "User-Agent": UserAgent,
            "Authorization": f"Bearer {access_token}"
        }

        retry = 3

        for i in range(retry):
            response = self.session.post(url, headers=headers, allow_redirects=False)
            if response.status_code == 200:
                return response.json()
            time.sleep(5)

        raise Exception(f"fail to login after {retry} attempts please check your network or ip")

    def signup(self):
        csrf = self._get_csrf()

        authorized_url = self._get_authorized_url(csrf)

        state = self._get_state(authorized_url)

        identifier, password = self._gen_and_check_identifier_password(state)

        access_token, refresh_token = self._get_access_token()

        while True:
            account_status = self._login(access_token)
            if account_status and account_status["next"] == "register":
                break
            else:
                logger.debug(f"{identifier} waiting for email verify")
            time.sleep(10)

        arkose = None
        arkose_retry = 3
        for i in range(arkose_retry):
            try:
                account_status = self._login(access_token)
                arkose_data_payload = account_status["arkose_data_payload"]
                arkose = self.arkose_solver.get_arkose_token(arkose_data_payload)
                if arkose:
                    break
            except Exception as e:
                logger.warning(f"fail to get arkose token current retry: {i}")

        if not arkose:
            raise Exception(f"fail to get arkose token after {arkose_retry} attempts please check your network or ip")

        result = self._create_account(access_token, arkose)

        self._login(access_token)

        sess = result["session"]['sensitive_id']

        credit = self._get_credit_grants(sess)

        write_lock = threading.Lock()

        if credit and credit['total_granted'] > 0:
            logger.info(f"account: {identifier} has credit: {credit['total_granted']}")
            self.write_to_file(write_lock, "./data/credit.txt",
                               f"{identifier}----{password}----{sess}----{refresh_token}\n")
        else:
            self.write_to_file(write_lock, "./data/account.txt",
                               f"{identifier}----{password}----{sess}----{refresh_token}\n")
        self.session.close()

    def write_to_file(self, lock, file_name, text):
        with lock:
            with open(file_name, "a", encoding="utf-8") as f:
                f.write(text)

    def _create_account(self, access_token, arkose):
        url = "https://api.openai.com/dashboard/onboarding/create_account"
        json = {
            "app": "api",
            "name": "vvv",
            "picture": "https://s.gravatar.com/avatar/eb9cd315d89e3fb42733f8cbd94a1950?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fg2.png",
            "arkose_token": arkose,
            "birthdate": "2001-02-11",
        }

        headers = {
            "User-Agent": UserAgent,
            "Authorization": f"Bearer {access_token}"
        }

        retry = 3
        for i in range(retry):
            resp = self.session.post(url, json=json, headers=headers, allow_redirects=False)
            if resp.status_code == 200:
                resp_json = resp.json()
                logger.debug(f"account created resp {resp_json}")
                return resp_json
            time.sleep(5)

        raise Exception(f"fail to create account after {retry} attempts please check your network or ip")

    def _get_credit_grants(self, sess):
        url = "https://api.openai.com/dashboard/billing/credit_grants"
        headers = {
            "User-Agent": UserAgent,
            "Authorization": f"Bearer {sess}",
            "Content-Type": "application/json",
        }

        for i in range(3):
            resp = self.session.get(url, headers=headers, allow_redirects=False)
            if resp.status_code == 200:
                resp_json = resp.json()
                logger.debug(f"success to get credit grants {resp_json}")
                return resp_json
            time.sleep(5)


def main(sm):
    log_context.set(trace_id=str(uuid.uuid4()))
    s = Signup()
    try:
        func_timeout(5 * 60, s.signup)
        sm.increment_success()
    except BaseException as e:
        sm.increment_failure()
        s.session.close()
        logger.warning(f"sign up fail: {e}")


def run_sign_up(sm):
    main(sm)


if __name__ == '__main__':
    pm = ThreadPoolManager(2)
