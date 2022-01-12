from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    """
    Класс для создания формы, предназначенной для регистрации
    нового пользователя на сайте.
    """
    class Meta(UserCreationForm.Meta):
        """
        Переопределенный класс Meta, необходимый для вывода
        полей, обязательных для заполнения в форме регистрации.
        """
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class PasswordResetForm(PasswordResetForm):
    """
    Класс для отправки письма со ссылкой на смену пароля.
    """
    model = User
    fields = ('email')
