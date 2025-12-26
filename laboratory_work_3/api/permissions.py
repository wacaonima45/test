from rest_framework import permissions


class IsDeputyDirector(permissions.BasePermission):
    """Разрешение только для завуча"""

    def has_permission(self, request, view):
        # В реальном приложении здесь была бы проверка роли пользователя
        # Для примера разрешаем всем аутентифицированным пользователям
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)