from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView as BasePasswordChangeView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import ProfileForm


class HOUSKiPasswordChangeView(BasePasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('home:index')

    def form_valid(self, form):
        self.request.user.must_change_password = False
        self.request.user.save(update_fields=['must_change_password'])
        messages.success(self.request, 'Heslo bylo úspěšně změněno.')
        return super().form_valid(form)


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil byl aktualizován.')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})
