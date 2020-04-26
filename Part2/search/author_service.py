# Standard Library Imports
import requests, json

# Third-party imports


# Local source tree imports

__all__=['_author',]


class AuthorService:
    def __init__(self):
        self.url = "http://ie4djxzt8j.execute-api.eu-west-1.amazonaws.com/coding/"

    def _create_api_headers(self):
        return  {
                'Content-Type': 'application/json',
                }

    def api_call(self,method,data, url=None):
        headers=self._create_api_headers()
        if method not in ["GET", "POST", "DELETE", "PUT", "PATCH"]:
            raise Exception("Unable to make a API call for {0} "
                            "method.".format(method))
        response = requests.request(url=self.url if url is None else url,
                                    method=method,
                                    headers=headers,
                                    data=data
                                    )

        if isinstance(response, requests.Response):
            response.raise_for_status()

        return response


_author = AuthorService()
