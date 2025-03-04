from enum import Enum


class ResponseMessage(Enum):

    OK = "Thành công"
    CREATED = "Tạo mới thành công"
    BAD_REQUEST = "Yêu cầu không hợp lệ"
    UNAUTHORIZED = "Vui lòng đăng nhập để thực hiện thao tác này"
    FORBIDDEN = "Bạn không có quyền thực hiện thao tác này"
    NOT_FOUND = "Yêu cầu không thể thực hiện"
    INTERNAL_SERVER_ERROR = "Hệ thống gặp sự cố, vui lòng thử lại sau"
    BAD_GATEWAY = "Hệ thống đang bận kết nối, vui lòng chờ và thử lại sau"

    VALUE_INVALID = "Dữ liệu không hợp lệ"
    GET_ERROR = "Lấy dữ liệu không thành công"
    DELETED_ERROR = "Xoá dữ liệu không thành công"
    CREATED_ERROR = "Tạo mới dữ liệu không thành công"
    UPDATED_ERROR = "Cập nhật dữ liệu không thành công"
    GET_DETAIL_ERROR = "Lấy chi tiết dữ liệu không thành công"

    INVALID_USERNAME = "Tài khoản không chính xác"
    INVALID_PASSWORD = "Mật khẩu không chính xác"
    USER_BANNED = "Tài khoản đang bị khoá"

    def __str__(self):
        return str(self.value)
