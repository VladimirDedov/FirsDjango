from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q

from .models import *
from .utils import *


# Начальная страница через class представления ListView
class AptekaHome(DataMixin, ListView):  # автоматически формирует коллекцию статей object_list
    paginate_by = 5  # Пагинатор опрделяет сколько элементов отображать на странице.
    model = Apteka  # model ссылается на модель Apteka. Выбирает все записи из таблицы и пытается отобразить в виде списка
    template_name = 'pharmacy/index.html'  # Указываем классу шаблон по умолчанию
    context_object_name = 'posts'  # указываем имя списка постов с помощью специального отрибута

    # Специальный метод get_context_data
    def get_context_data(self, *, object_list=None, **kwargs):  # формирует динамический и статический контекст,
        # который передается в шаблон index.html
        context = super().get_context_data(**kwargs)  # Получаем уже сформированный контекст для index.html
        c_def = self.get_user_context(title="Главная страница")  # get_user_context из utils. Возвращаем список данных.
        context = dict(
            list(context.items()) + list(c_def.items()))  # Обединение словарей context и c_def, чтобы передать
        # нормально в шаблон

        return context

    # Специальный метод класса get_queryset возвращает что должно быть прочитано из модели
    def get_queryset(self):  # Метод возвращает только опубликованные статьи АВТОМАТИЧЕСКИ
        return Apteka.objects.filter(is_published=True).select_related(
            'cat')  # select_related('cat') - совместно с данными
        # из таблицы Apteka загружает данные из таблицы категории. cat -внешний ключ

# отображение поста (конкретной страницы) через class
class ShowPost(DataMixin, DetailView):
    model = Apteka
    template_name = 'pharmacy/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'  # post используется в шаблоне post.html

    def get_queryset(self):
        return Apteka.objects.filter(slug=self.kwargs['post_slug'])

    def get_context_data(self, *, object=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=context['post'])
        context = dict(list(context.items()) + list(c_def.items()))
        return context


class AptekaCategory(DataMixin, ListView):  # Класс отображения категорий по аналогии
    model = Apteka
    template_name = 'pharmacy/index.html'
    context_object_name = 'posts'
    allow_empty = False  # атрибут формирования страницы 404 если posts пустой список

    def get_queryset(self):  # Прописываем фильтр, какие данные выбирать из модели Apteka
        return Apteka.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True).select_related('cat')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c = Category.objects.get(slug=self.kwargs['cat_slug'])
        c_def = self.get_user_context(title="Категория - " + str(c.name),
                                      cat_selected=c.pk)  # Mixin функция из файла utils.py
        context = dict(list(context.items()) + list(c_def.items()))
        return context


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


def search(request):
    search_query = request.GET.get('query', '')
    if search_query:
        posts = Apteka.objects.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
        if len(posts) == 0:
            posts = Apteka.objects.filter(slug='nobody')
            print(posts)
        cat_selected=1000
    else:
        posts = Apteka.objects.all()
        cat_selected = 0
    cats = Category.objects.all()

    return render(request, 'pharmacy/index.html', {'cat_selected': cat_selected, 'cats': cats, 'posts': posts})
