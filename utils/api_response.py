from constants.response_messages import ResponseMessage
from constants.http_status_code import HttpStatusCode
from typing import Any, Union, List, Tuple, Dict
from rest_framework.response import Response
from django.http import JsonResponse


class BaseAPIResponse:

    def build_response(self, data: Any, message: str, success: bool,
                       status: Union[HttpStatusCode, int],
                       errors: Union[List, Tuple, Dict]) -> Dict:
        status = HttpStatusCode(status) if isinstance(status, int) else status
        success = success if success is not None else HttpStatusCode.is_success(status.value)
        message = message or getattr(ResponseMessage, status.name.upper(), "").value

        return {"status": status.value,
                "success": success,
                "status_text": status.name,
                "message": message,
                "errors": errors,
                "data": data}


class APIResponse(Response, BaseAPIResponse):
    def __init__(self, data: Any = None, message: str = None, success: bool = None,
                 http_status: Union[HttpStatusCode, int] = HttpStatusCode.OK,
                 status: Union[HttpStatusCode, int] = HttpStatusCode.OK,
                 errors: Union[List, Tuple, Dict] = None, **kwargs):
        response_data = self.build_response(data, message, success, status, errors)
        http_status = HttpStatusCode(http_status) if isinstance(http_status, int) else http_status
        super().__init__(data=response_data, status=http_status.value, **kwargs)


class JsonAPIResponse(JsonResponse, BaseAPIResponse):
    def __init__(self, data: Any = None, message: str = None, success: bool = None,
                 status: Union[HttpStatusCode, int] = HttpStatusCode.OK,
                 errors: Union[List, Tuple, Dict] = None, **kwargs):
        response_data = self.build_response(data, message, success, status, errors)
        super().__init__(data=response_data, **kwargs)
