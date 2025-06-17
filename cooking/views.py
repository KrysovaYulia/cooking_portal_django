from django.shortcuts import render, redirect
from .models import Category, Post, Comment

from django.db.models import F, Q

from .forms import PostAddForm, LoginForm, RegistrationForm, CommentForm
from django.contrib.auth import login, logout

from django.contrib import messages

from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView

from django.urls import reverse_lazy


from django.contrib.auth.models import User 
# Create your views here.


# def index(request):
#     """Для главной страницы"""
#     posts = Post.objects.all()
  
#     context = {'title' : 'Главная страница', 
#                'posts' : posts,
              
#                }
    
#     return render(request, template_name='cooking/index.html', context=context)

class Index(ListView):
    """Для главной страницы"""
    model = Post
    context_object_name = 'posts'
    template_name = 'cooking/index.html'
    extra_context = {'title' : 'Главная страница'}


# def category_list(request, pk):
#     """Реакция на нажатие кнопки категории"""
#     posts = Post.objects.filter(category_id=pk)
 

#     context = {'title' : posts[0].category, 
#                'posts' : posts,
              
#                }
    
#     return render(request, template_name='cooking/index.html', context=context)

class ArticaleByCategory(Index):
    """Реакция на нажатие кнопки категории"""
    def get_queryset(self):
        """Здесь можно переделать фильтрации"""
        return Post.objects.filter(category_id=self.kwargs['pk'], is_published=True)
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        category = Category.objects.get(pk=self.kwargs['pk'])
        context['title'] = category.title
        return context
        
# def post_detail(request, pk):
#     """страничка статьи"""

#     article = Post.objects.get(pk=pk)
#     Post.objects.filter(pk=pk).update(watched=F('watched') + 1)
#     ext_post = Post.objects.all().exclude(pk=pk).order_by('-watched')[:5]
#     context = {
        
#         'title' : article.title,
#         'post' : article,
#         'ext_post' : ext_post,
        
#         }
#     return render(request, template_name='cooking/artical_detail.html', context=context)
class PostDetail(DeleteView):
    """Страничка статьи"""
    
    template_name = 'cooking/artical_detail.html'

    def get_queryset(self):

        return Post.objects.filter(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        
        """Для динамических данных"""
        Post.objects.filter(pk=self.kwargs['pk']).update(watched=F('watched') + 1)
        context = super().get_context_data()
        post = Post.objects.get(pk=self.kwargs['pk'])
        posts = Post.objects.all().exclude(pk=self.kwargs['pk']).order_by('-watched')[:5]
        context['title'] = post.title
        context['ext_post'] = posts
        context['comments'] = Comment.objects.filter(post=post)
        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm
        return context 
        


        


# def add_post(request):
#     """добавление статьи от пользователя, без админки"""

#     if request.method == 'POST':
#         form = PostAddForm(request.POST, request.FILES)
#         if form.is_valid():
#             post = Post.objects.create(**form.cleaned_data)
#             post.save()
#             return redirect('post_detail', post.pk)

#     else:
#         form = PostAddForm()


#     context = {

#         'title' : 'Добавить статью',
#         'form' : form
#     }

#     return render(request, template_name='cooking/artical_add_form.html', context=context)

class AddPost(CreateView):
    """Добавление статьи от пользоваетля, без админки"""
    form_class = PostAddForm
    template_name = 'cooking/artical_add_form.html'
    extra_context = {'title' : 'Добавьте статью'}

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    


class  PostUpdate(UpdateView):
    """Изменение статьи по кнопке"""

    model = Post

    form_class = PostAddForm

    template_name = 'cooking/artical_add_form.html'


class PostDelete(DeleteView):
    """Удаление поста"""
    model = Post
    success_url = reverse_lazy('index')
    context_object_name = 'post'
    
    extra_content = {'title' : 'Изменить статью'}


class SearchResult(Index):


    def get_queryset(self):
        word = self.request.GET.get('q')

        posts = Post.objects.filter(


            Q(title__icontains=word) | Q(content__icontains=word)
        )

        return posts
    
def add_comment(request, post_id):
    """добавление комментариев к статьям"""

    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)

        comment.user = request.user

        comment.post = Post.objects.get(pk=post_id)

        comment.save()
        messages.success(request, 'Ваш комментарий успешно добавлен')

    return redirect('post_detail', post_id)


def user_login(request):

    '''Аутентификация пользователя'''

    if request.method == 'POST':

        form = LoginForm(data=request.POST)

        if form.is_valid():
            
            user = form.get_user()

            login(request, user)
            messages.success(request, message='Вы успешно вошли в аккаунт!')
            return redirect('index')
    else:

        form = LoginForm()

    context = {

        'title' : 'Авторизация пользователя',
        'form' : form
    }


    return render(request, template_name='cooking/login_form.html', context=context)
    


def user_logout(request):

    """Выход пользователя"""


    logout(request)

    return redirect('index')


def register(request):
    """регистрация"""

    if request.method == 'POST':

        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:

        form = RegistrationForm()

    context = {

        'title' : 'Регистрация пользователя',
        'form' : form
    }


    return render(request, template_name='cooking/register.html', context=context)



def profile(request, user_id):

    user = User.objects.get(pk=user_id)

    posts = Post.objects.filter(author=user)
    context = {

        'user' : user,
        'posts' : posts
    }

    return render(request, template_name='cooking/profile.html', context=context)