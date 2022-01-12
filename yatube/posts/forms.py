from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    """
    Класс для создания формы, предназначенной для создания нового поста.
    """
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': 'Текст поста',
            'group': 'Выбрать группу',
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
