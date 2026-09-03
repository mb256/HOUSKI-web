from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Activity
from .forms import ActivityForm


def activity_list(request):
    today = timezone.localdate()
    upcoming = Activity.objects.select_related('author').filter(start_date__gte=today).order_by('start_date')
    past = Activity.objects.select_related('author').filter(start_date__lt=today).order_by('-start_date')
    return render(request, 'activities/list.html', {'upcoming': upcoming, 'past': past})


@login_required
def activity_create(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.author = request.user
            activity.save()
            messages.success(request, 'Aktivita byla přidána.')
            return redirect('activities:list')
    else:
        form = ActivityForm()
    return render(request, 'activities/form.html', {'form': form, 'action': 'Přidat aktivitu'})


@login_required
def activity_edit(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if activity.author != request.user and not request.user.is_staff:
        messages.error(request, 'Nemáte oprávnění upravit tuto aktivitu.')
        return redirect('activities:list')
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aktivita byla upravena.')
            return redirect('activities:list')
    else:
        form = ActivityForm(instance=activity)
    return render(request, 'activities/form.html', {'form': form, 'action': 'Upravit aktivitu', 'activity': activity})


@login_required
def activity_delete(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if activity.author != request.user and not request.user.is_staff:
        messages.error(request, 'Nemáte oprávnění smazat tuto aktivitu.')
        return redirect('activities:list')
    if request.method == 'POST':
        activity.delete()
        messages.success(request, 'Aktivita byla smazána.')
        return redirect('activities:list')
    return render(request, 'activities/confirm_delete.html', {'activity': activity})
