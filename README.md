# Django Base Project

## Overview
Đây là một project Django giúp khởi tạo nhanh một ứng dụng Django Rest Framework (DRF) với các tính năng sẵn có.

## Installation
### 1. Clone project
```bash
git clone <repo-url>
cd django-base
```
### 2. Tạo và kích hoạt virtual environment
> Yêu cầu python nhỏ hơn hoặc bằng 3.9.x

```bash
python -m venv venv
source venv/bin/activate  # Trên macOS/Linux
venv\Scripts\activate  # Trên Windows
```
### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt  # Hoặc production.txt nếu chạy môi trường production
```
### 4. Cấu hình môi trường
Sao chép file `.env.local` thành `.env` và chỉnh sửa giá trị nếu cần.
```bash
cp .env.local .env
```
### 5. Chạy migration database
```bash
python manage.py migrate
```
### 6. Chạy server
```bash
python manage.py runserver
```
Server sẽ chạy tại `http://127.0.0.1:8000/`.

## Project Structure
```
django-boilderpalte/
│
├── apps/
│   ├── __init__.py
│   ├── users/
│   │   ├── docs/
│   │   │   ├── auth_swagger.py
│   │   │   ├── user_swagger.py
│   │   │   └── ...
│   │   ├── migrations/
│   │   │   └── ...
│   │   ├── models/
│   │   │   ├── utils/
│   │   │   │   ├── choices.py
│   │   │   │   ├── manager.py
│   │   │   │   └── ...
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   └── ...
│   │   ├── serializers/
│   │   │   ├── request_serializer.py
│   │   │   ├── response_serializer.py
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── user_service.py
│   │   │   └──  ...
│   │   ├── views/
│   │   │   ├── auth_view.py
│   │   │   ├── user_view.py
│   │   │   └── ...
│   │   ├── __init__.py
│   │   └── admin.py
│   │   ├── apps.py
│   │   └── urls.py
│   └── ...
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── constants/
│   ├── __init__.py
│   ├── http_status_code.py
│   └── response_message.py
│
├── helpers/
│   ├── __init__.py
│   ├── datetime_helper.py
│   ├── query_helper.py
│   └── token_helper.py
│
├── utils/
│   ├── decorators/
│   │   ├── __init__.py
│   │   ├── api_method.py
│   │   └── singleton.py
│   ├── mixins/
│   │   ├── __init__.py
│   │   ├── base_api_view_mixin.py
│   │   └── serializer_mixin.py
│   ├── __init__.py
│   ├── api_response.py
│   ├── authentication.py
│   ├── base_models.py
│   ├── exception.py
│   ├── paginator.py
│   └── views.py
│
├── ...
│
├── .env.local
│
├── manage.py
│
├── requirements.txt
│
└── ...
```

## Project Tools
- Sử dụng lệnh:
```bash
python make.py --name product --vi_name = 'Sản phẩm' --init_model Product
```
-------------------

| name         | vi_name                     | init_model           |
|--------------|-----------------------------|----------------------|
| Tên ứng dụng | Tên tiếng việt của ứng dụng | Model chính ứng dụng |
-------------------

- Thêm vào INSTALLED_APPS trong `config/settings.py`:
```python
INSTALLED_APPS = [
    ...
    'apps.product'
]
```
- Thêm vào urls trong `config/urls.py`:
```python
....
from apps.product.urls import product_urlpatterns

...
urlpatterns += product_urlpatterns
```

## API Documentation
Sử dụng Swagger để xem API docs:
```bash
python manage.py runserver
```
Truy cập `http://127.0.0.1:8000/swagger/` để xem chi tiết API.


## Khởi tạo API
```bash
cd ./apps
django-admin startapp users
```

#### - Tổ chức và cấu trúc lại như sau:
```
├── ...
│   │
│   ├── users/
│   │   ├── docs/
│   │   │   ├── user_swagger.py
│   │   │   └── ...
│   │   ├── migrations/
│   │   │   └── ...
│   │   ├── models/
│   │   │   └── ...
│   │   ├── serializers/
│   │   │   └── ...
│   │   ├── services/
│   │   │   └──  ...
│   │   ├── views/
│   │   │   └── ...
│   │   ├── __init__.py
│   │   └── admin.py
│   │   ├── apps.py
│   │   └── urls.py
│   └── ...
└── ...
```

#### - Cập nhật `apps.py`

Trong file `apps.py` của mỗi ứng dụng, cập nhật lại như sau:

```python
class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Tài khoản'  # Đặt tên hiển thị cho ứng dụng
    name = 'apps.user'  # Thêm tiền tố "apps."
```

### Giải thích
- **Thêm `apps.` vào `name`** để thống nhất cấu trúc thư mục.
- **Bổ sung `verbose_name`** để mô tả rõ chức năng của ứng dụng.

Ví dụ:

```python
# Trước đây:
name = 'users'

# Sau khi chỉnh sửa:
name = 'apps.user'
verbose_name = 'Tài khoản'
```

#### - Thêm vào`INSTALLED_APPS`. 🚀
```python
INSTALLED_APPS += ["apps.user"]
```

#### - Tạo API
``` python
from constants.response_messages import ResponseMessage
from constants.http_status_code import HttpStatusCode
from utils.views import APIGenericView
from utils.views import APIView

from utils.decorators import api

class APIFirst(APIGenericView):
    ...

    action_serializers = {
        "list_request": {{serializer}},
        "list_response": {{serializer}},
        ...
    }
    
    def list(self, request)
        => self.get_response_serializer(...) from action_serializers["list_response"]
        => self.get_request_serializer(...) from action_serializers["list_request"]
        Ngoài ra còn có:
            + self.api_response(
                data: Any = None,
                message: str = None,
                success: bool = None,
                http_status: Union[HttpStatusCode, int] = HttpStatusCode.OK,
                status: Union[HttpStatusCode, int] = HttpStatusCode.OK,
                errors: Union[List, Tuple, Dict] = None,
                **kwargs
            )
            + self.paginator(
                object_list: Union[List, QuerySet],
                per_page: int = None, # Không truyền mặc đinh sẽ lấy trong request với key = 'limit'
                page: int = None, # Không truyền mặc đinh sẽ lấy trong request với key = 'page'
                **kwargs
            )
        pass

    def update(self, request, pk)
        pass

    def create(self, request)
        pass

    def destroy(self, request, pk)
        pass

    def retrieve(self, request, pk)
        pass

    def partial_update(self, request, pk)
        pass
    
    @api.post() # Method POST
    @api.swagger(...) # swagger_auto_schema
    def custom_route(self, request, pk)
        pass

    ...


class APISecond(APIView):

    ...

    def post(self, request):
        ...

    ...
```

``` python
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from ... import APIFirst, APISecond


api_router = DefaultRouter(trailing_slash=False)
api_router.register(prefix="first", viewset=APIFirst, basename="first")

users_urlpatterns = [
    path("api/v1/", include(api_router.urls)),
    path("api/v1/second", APISecond.as_view(), name="second")
]
```

# => Tạm thời thế đã ... 🚀 🚀 🚀 🚀

🚀 ...
