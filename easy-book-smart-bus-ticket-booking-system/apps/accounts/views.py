from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import SignupForm


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                messages.success(request, 'Account created successfully!')

                if user.user_type == 'bus_owner':
                    return redirect('bus_owner_dashboard')
                else:
                    return redirect('customer_dashboard')

            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
                return render(request, 'accounts/signup.html', {'form': form})
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{field}: {error}")
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


def customer_dashboard(request):
    return render(request, 'customer/dashboard.html')


def bus_owner_dashboard(request):
    return render(request, 'bus_owner/dashboard.html')