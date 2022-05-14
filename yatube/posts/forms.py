from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {
            "text": "Текст",
            "group": "Группа",
        }
        help_texts = {
            "text": "Напишите текст поста",
            "group": "Выберите группу",
        }
# , "image" с этим полем из 6го спринта не проходят тесты
