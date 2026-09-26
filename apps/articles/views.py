from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Article, Category
from .forms import ArticleForm


def article_list(request):
    articles = Article.objects.select_related('author').prefetch_related('categories')
    category_slug = request.GET.get('category')
    if category_slug:
        articles = articles.filter(categories__slug=category_slug)
    paginator = Paginator(articles, 12)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'articles/list.html', {
        'page_obj': page,
        'categories': Category.objects.all(),
        'active_category': category_slug,
    })


def article_detail(request, pk):
    article = get_object_or_404(Article.objects.prefetch_related('categories'), pk=pk)
    return render(request, 'articles/detail.html', {'article': article})


@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()
            messages.success(request, 'Článek byl přidán.')
            return redirect('articles:detail', pk=article.pk)
    else:
        form = ArticleForm()
    return render(request, 'articles/form.html', {'form': form, 'action': 'Přidat článek'})


@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.author != request.user and not request.user.is_staff:
        messages.error(request, 'Nemáte oprávnění upravit tento článek.')
        return redirect('articles:detail', pk=article.pk)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Článek byl upraven.')
            return redirect('articles:detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'articles/form.html', {'form': form, 'action': 'Upravit článek', 'article': article})


@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.author != request.user and not request.user.is_staff:
        messages.error(request, 'Nemáte oprávnění smazat tento článek.')
        return redirect('articles:detail', pk=article.pk)
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Článek byl smazán.')
        return redirect('articles:list')
    return render(request, 'articles/confirm_delete.html', {'article': article})
