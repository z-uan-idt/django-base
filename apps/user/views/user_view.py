from rest_framework.permissions import IsAuthenticated
from utils.views import APIGenericView


class APIUser(APIGenericView):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        return "OK"