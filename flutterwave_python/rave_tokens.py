import requests, json, copy
# import urllib.parse as urlparse
# from urllib.parse import urlencode
from flutterwave_python.rave_base import RaveBase
from flutterwave_python.rave_misc import checkIfParametersAreComplete, generateTransactionReference, checkTransferParameters
from flutterwave_python.rave_exceptions import InitiateTransferError, ServerError, TransferFetchError, IncompletePaymentDetailsError


class Tokens(RaveBase):
    def __init__(self, publicKey, secretKey, encryptionKey, production, usingEnv):
        super(Tokens, self).__init__(publicKey, secretKey, encryptionKey, production, usingEnv)
    
    def _preliminaryResponseChecks(self, response, TypeOfErrorToRaise, reference):
        # Check if we can obtain a json
        try:
            responseJson = response.json()
        except:
            raise ServerError({"error": True, "reference": reference, "errMsg": response})

        # Check if the response contains data parameter
        if not responseJson.get("data", None):
            raise TypeOfErrorToRaise({"error": True, "reference": reference, "errMsg": responseJson.get("message", "Server is down")})
        
        # Check if it is returning a 200
        if not response.ok:
            errMsg = responseJson["data"].get("message", None)
            raise TypeOfErrorToRaise({"error": True, "errMsg": errMsg})

        return responseJson


    def _handleInitiateResponse(self, response, tokenDetails):
        responseJson = self._preliminaryResponseChecks(response, InitiateTransferError, tokenDetails["token"])
        
        if responseJson["status"] == "success":
            return {"error": False, "id": responseJson["data"].get("id", None), "data": responseJson["data"]}
        
        else:
            raise InitiateTransferError({"error": True, "data": responseJson["data"]})

    def _handleTokenStatusRequests(self, endpoint, method, data=None):
        # Request headers
        headers = {
            'content-type': 'application/json',
            'authorization' : 'Bearer ' + self._getSecretKey(),
        }

        #check if response is a post response
        if method == 'GET':
            if data == None:
                response = requests.get(endpoint, headers=headers)
            else:
                response = requests.get(endpoint, headers=headers, data=json.dumps(data))
        elif method == 'POST':
            response = requests.post(endpoint, headers=headers)
        elif method == 'PUT':
            response = requests.put(endpoint, headers=headers)
        elif method == 'PATCH':
            response = requests.patch(endpoint, headers=headers, data=json.dumps(data))
        else:
            response = requests.delete(endpoint, headers=headers, data=json.dumps(data))

        # Checks if it can be parsed to json
        try:
            responseJson = response.json()
        except:
            raise ServerError({"error": True, "errMsg": response.text })

        # Checks if it returns a 2xx code
        if response.ok:
            return {"error": False, "returnedData": responseJson}
        else:
            raise TransferFetchError({"error": True, "returnedData": responseJson })