from rest_framework.decorators import action
from rest_framework.response import Response

from component.drf.viewsets import GenericViewSet


class UserViewSets(GenericViewSet):
    @action(methods=['GET'], detail=False)
    def info(self, request, *args, **kwargs):
        return Response({
            "username": request.user.username,
            "role": "admin" if request.user.is_superuser else "other"
        })

    @action(methods=['POST'], detail=False)
    def change_password(self, request, *args, **kwargs):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
             return Response({"code": 400, "result": False, "message": "密码不能为空"})
        
        user = request.user
        if not user.check_password(old_password):
             return Response({"code": 400, "result": False, "message": "旧密码错误"})
        
        user.set_password(new_password)
        user.save()
        return Response({"code": 200, "result": True, "message": "密码修改成功，请重新登录"})
