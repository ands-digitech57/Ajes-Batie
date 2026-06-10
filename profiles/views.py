from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ProfileForm
from .models import Profile


@login_required
def profile_list(request):
    query = request.GET.get('q', '').strip()
    profiles = Profile.objects.filter(is_public=True).select_related('user').prefetch_related('skills')

    if query:
        profiles = profiles.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(user__username__icontains=query)
            | Q(job_title__icontains=query)
            | Q(skills__name__icontains=query)
            | Q(education_level__icontains=query)
            | Q(location__icontains=query)
        ).distinct()

    return render(request, 'profiles/profile_list.html', {
        'profiles': profiles,
        'query': query,
    })


@login_required
def profile_detail(request, pk):
    profile = get_object_or_404(
        Profile.objects.select_related('user').prefetch_related('skills'),
        pk=pk,
        is_public=True,
    )
    return render(request, 'profiles/profile_detail.html', {'profile': profile})


@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={'email': request.user.email, 'is_public': True},
    )

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('accounts:dashboard')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profiles/profile_form.html', {'form': form, 'profile': profile})
