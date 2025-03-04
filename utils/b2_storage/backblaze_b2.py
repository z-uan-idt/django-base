import requests
import hashlib
import base64


class BackBlazeB2(object):

    def __init__(self, app_key=None, account_id=None, bucket_name=None, bucket_id=None):
        self.bucket_id = bucket_id
        self.account_id = account_id
        self.app_key = app_key
        self.bucket_name = bucket_name
        self.base_url = ''
        self.authorization_token = ''
        self.download_url = ''
        self.authorize()

    def authorize(self):
        try:
            auth_string = f"{self.account_id}:{self.app_key}"
            encoded_auth_string = base64.b64encode(
                auth_string.encode('utf-8')
            ).decode('utf-8')

            basic_auth_header = f"Basic {encoded_auth_string}"
            headers = {'Authorization': basic_auth_header}

            response = requests.get('https://api.backblaze.com/b2api/v2/b2_authorize_account',
                                    headers=headers)

            response.raise_for_status()

            if response.status_code == 200:
                resp = response.json()
                self.base_url = resp['apiUrl']
                self.download_url = resp['downloadUrl']
                self.authorization_token = resp['authorizationToken']

                return True
            else:
                return False

        except requests.RequestException as e:
            print(f"Request error: {e}")
            return False

    def get_upload_url(self):
        params = {'bucketId': self.bucket_id}
        url = self._build_url('/b2api/v1/b2_get_upload_url')
        headers = {'Authorization': self.authorization_token}
        return requests.get(url,
                            headers=headers,
                            params=params).json()

    def _build_url(self, endpoint=None, authorization=True):
        return "%s%s" % (self.base_url, endpoint)

    def upload_file(self, name, content):
        response = self.get_upload_url()
        if 'uploadUrl' not in response:
            self.authorize()
            response = self.get_upload_url()
            if 'uploadUrl' not in response:
                return False

        url = response['uploadUrl']
        content.seek(0)

        headers = {
            'Authorization': response['authorizationToken'],
            'X-Bz-File-Name': name,
            'Content-Type': "b2/x-auto",
            'X-Bz-Content-Sha1': 'do_not_verify',
            'X-Bz-Info-src_last_modified_millis': '',
        }

        download_response = requests.post(url,
                                          headers=headers,
                                          data=content.read())

        if download_response.status_code == 503:
            attempts = 0
            while attempts <= 3 and download_response.status_code == 503:
                download_response = requests.post(
                    url, headers=headers, data=content.read())
                attempts += 1
        if download_response.status_code != 200:
            download_response.raise_for_status()

        return download_response.json()

    def get_file_info(self, name):
        headers = {'Authorization': self.authorization_token}
        return requests.get("%s/file/%s/%s" % (self.download_url, self.bucket_name, name), headers=headers)

    def download_file(self, name):
        headers = {'Authorization': self.authorization_token}
        return requests.get("%s/file/%s/%s" % (self.download_url, self.bucket_name, name), headers=headers).content

    def get_file_url(self, name):
        return "%s/file/%s/%s" % (self.download_url, self.bucket_name, name)

    def get_bucket_id_by_name(self):
        headers = {'Authorization': self.authorization_token}
        params = {'accountId': self.account_id}
        resp = requests.get(self._build_url(
            "/b2api/v1/b2_list_buckets"), headers=headers, params=params).json()
        if 'buckets' in resp:
            buckets = resp['buckets']
            for bucket in buckets:
                if bucket['bucketName'] == self.bucket_name:
                    self.bucket_id = bucket['bucketId']
                    return True

        else:
            return False
