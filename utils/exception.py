from config import settings
from django.http import Http404
from rest_framework.exceptions import (
    NotFound, ValidationError, AuthenticationFailed, 
    NotAuthenticated, MethodNotAllowed, ParseError, 
    UnsupportedMediaType, Throttled, APIException
)
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.utils import IntegrityError, DataError, DatabaseError
from constants.response_messages import ResponseMessage
from constants.http_status_code import HttpStatusCode
from django.core.exceptions import ObjectDoesNotExist
from django.utils.deprecation import MiddlewareMixin
from rest_framework.views import exception_handler
from utils.api_response import JsonAPIResponse
from django.http import HttpResponseRedirect
from utils.api_response import APIResponse
from django.db import connections
from django.urls import reverse
from typing import Union


class MessageError(APIException):
    status_code = HttpStatusCode.BAD_REQUEST.value
    default_code = HttpStatusCode.BAD_REQUEST.name
    default_detail = ResponseMessage.BAD_REQUEST

    def __init__(self, detail: Union[ResponseMessage, str] = None):
        if isinstance(detail, ResponseMessage):
            self.detail = detail.value
        elif isinstance(detail, str) and detail:
            msg_key = detail.upper()
            if hasattr(ResponseMessage, msg_key):
                self.detail = getattr(ResponseMessage, msg_key)
            else:
                self.detail = detail


class ExceptionMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.path == "/admin":
            return HttpResponseRedirect(reverse("admin:index"))

        if HttpStatusCode.is_server_error(response.status_code):
            return JsonAPIResponse(status=HttpStatusCode.INTERNAL_SERVER_ERROR)

        if response.status_code == HttpStatusCode.NOT_FOUND.value:
            return JsonAPIResponse(status=HttpStatusCode.NOT_FOUND)

        return response

def ExceptionHandler(exc, context):
    """
    Xử lý toàn bộ exception trong dự án và trả về response có định dạng nhất quán.
    
    Args:
        exc: Exception cần xử lý
        context: Context của request
    
    Returns:
        APIResponse: Response với định dạng nhất quán
    """
    # Log exception để dễ debug
    request = context.get('request', None)
    
    def get_error_content(exc):
        """
        Phân tích nội dung lỗi từ exception.
        """
        if isinstance(exc, dict):
            if "non_field_errors" in exc:
                return get_error_content(exc["non_field_errors"])

            errors = {}
            for k, v in exc.items():
                errors[k] = get_error_content(v)
            return errors

        if isinstance(exc, list):
            if len(exc) > 0:
                return exc[0]
            return None

        if hasattr(exc, "detail"):
            return get_error_content(exc.detail)

        return str(exc)

    # Lấy DRF exception handler gốc
    exc_response = exception_handler(exc, context)
    
    # Xác định status code mặc định
    status_code = getattr(exc, "status_code", HttpStatusCode.BAD_REQUEST.value)
    status = HttpStatusCode(status_code)

    # Xử lý các loại exception cụ thể
    if isinstance(exc, (Http404, ObjectDoesNotExist, NotFound)):
        status = HttpStatusCode.NOT_FOUND
    elif isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        status = HttpStatusCode.UNAUTHORIZED
    elif isinstance(exc, PermissionDenied):
        status = HttpStatusCode.FORBIDDEN
    elif isinstance(exc, (ValidationError, DjangoValidationError)):
        status = HttpStatusCode.BAD_REQUEST
    elif isinstance(exc, MethodNotAllowed):
        status = HttpStatusCode.METHOD_NOT_ALLOWED
    elif isinstance(exc, Throttled):
        status = HttpStatusCode.TOO_MANY_REQUESTS
    elif isinstance(exc, UnsupportedMediaType):
        status = HttpStatusCode.UNSUPPORTED_MEDIA_TYPE
    elif isinstance(exc, ParseError):
        status = HttpStatusCode.BAD_REQUEST
    elif isinstance(exc, IntegrityError):
        status = HttpStatusCode.CONFLICT
    elif isinstance(exc, (DataError, DatabaseError)):
        status = HttpStatusCode.BAD_REQUEST
    elif exc_response is None:
        # Exception không phải từ DRF
        status = HttpStatusCode.INTERNAL_SERVER_ERROR

    # Rollback transaction nếu cần
    for db in connections.all():
        if db.settings_dict["ATOMIC_REQUESTS"] and db.in_atomic_block:
            db.set_rollback(True)

    # Lấy message dựa trên status
    status_name = status.name.upper()
    message = getattr(ResponseMessage, status_name, ResponseMessage.BAD_REQUEST).value

    # Chuẩn bị response
    response_kwargs = {
        "status": status,
        "message": message,
        "errors": {
            "code": status.value,
            "type": exc.__class__.__name__,
            "error": get_error_content(exc),
        }
    }

    # Xử lý đặc biệt cho một số loại exception
    if isinstance(exc, (MessageError, NotFound)):
        response_kwargs["message"] = exc.detail
        response_kwargs["errors"] = None
    
    # Xử lý cho các loại lỗi validation
    if isinstance(exc, ValidationError) and hasattr(exc, 'detail'):
        # Cung cấp thông tin chi tiết hơn cho lỗi validation
        error_details = {}
        if isinstance(exc.detail, dict):
            for field, errors in exc.detail.items():
                if isinstance(errors, list):
                    error_details[field] = errors[0] if errors else "Validation error"
                else:
                    error_details[field] = str(errors)
        else:
            error_details["detail"] = get_error_content(exc)
        
        response_kwargs["errors"]["fields"] = error_details

    # Thêm thông tin request để dễ debug (tùy chọn, có thể loại bỏ trong production)
    if settings.DEBUG:
        request_info = None
        if request:
            request_info = {
                "method": request.method,
                "path": request.path,
                "query_params": dict(request.query_params) if hasattr(request, 'query_params') else None,
                "data": request.data if hasattr(request, 'data') else None
            }
        
        if response_kwargs["errors"] is None:
            response_kwargs["errors"] = {}

        response_kwargs["errors"]["debug"] = {"request": request_info}

    return APIResponse(**response_kwargs)
