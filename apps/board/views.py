from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import BoardPost, BoardImage
from .forms import BoardPostForm, BoardImageFormSet

BOARD_PAGE_SIZE = 20


def board_list(request):
    posts = BoardPost.objects.select_related('author').prefetch_related('images')
    paginator = Paginator(posts, BOARD_PAGE_SIZE)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'board/list.html', {'page_obj': page})


@login_required
def board_create(request):
    if request.method == 'POST':
        form = BoardPostForm(request.POST)
        formset = BoardImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            images = formset.save(commit=False)
            for i, img in enumerate(images):
                img.post = post
                img.order = i
                img.save()
            messages.success(request, 'Příspěvek byl přidán.')
            return redirect('board:list')
    else:
        form = BoardPostForm()
        formset = BoardImageFormSet(queryset=BoardImage.objects.none())
    return render(request, 'board/form.html', {'form': form, 'formset': formset, 'action': 'Přidat příspěvek'})


@login_required
def board_edit(request, pk):
    post = get_object_or_404(BoardPost, pk=pk)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'Nemáte oprávnění upravit tento příspěvek.')
        return redirect('board:list')
    if request.method == 'POST':
        form = BoardPostForm(request.POST, instance=post)
        formset = BoardImageFormSet(request.POST, request.FILES, queryset=post.images.all())
        if form.is_valid() and formset.is_valid():
            form.save()
            images = formset.save(commit=False)
            for img in images:
                img.post = post
                img.save()
            for img in formset.deleted_objects:
                img.delete()
            messages.success(request, 'Příspěvek byl upraven.')
            return redirect('board:list')
    else:
        form = BoardPostForm(instance=post)
        formset = BoardImageFormSet(queryset=post.images.all())
    return render(request, 'board/form.html', {'form': form, 'formset': formset, 'action': 'Upravit příspěvek', 'post': post})


@login_required
def board_delete(request, pk):
    post = get_object_or_404(BoardPost, pk=pk)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'Nemáte oprávnění smazat tento příspěvek.')
        return redirect('board:list')
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Příspěvek byl smazán.')
        return redirect('board:list')
    return render(request, 'board/confirm_delete.html', {'post': post})
