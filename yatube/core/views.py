from django.shortcuts import render
from http import HTTPStatus

def page_not_found(request, exception):
    """
    Отображение страницы ошибки 404 NOT Found.
    """
    return render(request,
                  'core/404.html',
                  {'path': request.path},
                  status=HTTPStatus.NOT_FOUND)

def csrf_failure(request, reason=''):
    """
    Отображение страницы ошибки '403:
    ошибка проверки CSRF, запрос отклонён', если при отправке формы
    не был отправлен csrf-токен.
    """
    return render(request, 'core/403csrf.html')
