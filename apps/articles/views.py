from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Article, ArticleImage, Category
from .forms import ArticleForm, ArticleImageFormSet


def article_list(request):
    articles = Article.objects.select_related('author').prefetch_related('images', 'categories')
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
    article = get_object_or_404(Article.objects.prefetch_related('images', 'categories'), pk=pk)
    return render(request, 'articles/detail.html', {'article': article})


@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        formset = ArticleImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()
            images = formset.save(commit=False)
            for i, img in enumerate(images):
                img.article = article
                img.order = i
                img.save()
            messages.success(request, 'Článek byl přidán.')
            return redirect('articles:detail', pk=article.pk)
    else:
        form = ArticleForm()
        formset = ArticleImageFormSet(queryset=ArticleImage.objects.none())
    return render(request, 'articles/form.html', {'form': form, 'formset': formset, 'action': 'Přidat článek'})


@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.author != request.user and not request.user.is_staff:
        messages.error(request, 'Nemáte oprávnění upravit tento článek.')
        return redirect('articles:detail', pk=article.pk)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        formset = ArticleImageFormSet(request.POST, request.FILES, queryset=article.images.all())
        if form.is_valid() and formset.is_valid():
            form.save()
            images = formset.save(commit=False)
            for img in images:
                img.article = article
                img.save()
            for img in formset.deleted_objects:
                img.delete()
            messages.success(request, 'Článek byl upraven.')
            return redirect('articles:detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
        formset = ArticleImageFormSet(queryset=article.images.all())
    return render(request, 'articles/form.html', {'form': form, 'formset': formset, 'action': 'Upravit článek', 'article': article})


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
