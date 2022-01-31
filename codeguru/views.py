from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import NewUserForm, NewGroupForm
from .models import Profile, Invite, CgGroup
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.utils import translation
from django.http import HttpResponse
from django.utils.translation import gettext
from django.conf import settings

def error(request, msg):
    return render(request, "error.html", {"error_message": msg})


@login_required
def profile(request):
    return render(request, 'profile.html')


@login_required
def delete_profile(request):
    request.user.delete()
    return redirect("/")


@login_required
def group(request):
    if request.method == "POST":
        form = NewGroupForm(request.POST)
        if form.is_valid():
            if CgGroup.objects.filter(name=form.cleaned_data["name"]).exists():
                return error(request, gettext("Group already exists. try choosing another name."))
            new_group = CgGroup(
                name=form.cleaned_data["name"], owner=request.user, center=form.cleaned_data["center"])
            new_group.save()
            request.user.profile.group = new_group
            request.user.profile.save()
            return redirect("group")
    link_expired = False
    try:
        link_expired = request.user.profile.group.invite.expired
    except:
        link_expired = False

    return render(request, 'group.html', {"form": NewGroupForm(), "is_expired": link_expired, "members": Profile.objects.all().filter(group=request.user.profile.group)})


def register(request):
    if request.user.is_authenticated:
        return redirect('profile/')
    if request.method == "POST":
        form = NewUserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
    form = NewUserForm()
    return render(request, "registration/registration_form.html", {"form": form})


@login_required
def invite(request, code):
    if request.user.profile.group:
        return error(request, gettext("You must leave your group first."))
    try:
        invite = Invite.objects.get(code=code)
        if invite.expired:
            return error(request, gettext("Invite expired."))
        if request.user.profile.group != invite.group:
            leave_group(request)
        request.user.profile.group = invite.group
        request.user.profile.save()
        return redirect("/group/")
    except Invite.DoesNotExist:
        return error(request, gettext("Invalid Invite link."))


@login_required
def create_invite(request):
    if not request.user.profile.group:
        return error(request, gettext("You do not have a group."))
    if request.user != request.user.profile.group.owner:
        return error(request, gettext("Only an owner can create a group invite."))

    try:
        invite = Invite.objects.get(group=request.user.profile.group)
        invite.code = get_random_string(64)
        invite.save()
    except Invite.DoesNotExist:
        invite = Invite(group=request.user.profile.group,
                        code=get_random_string(64))
        invite.save()
    return redirect("/group/")


@login_required
def leave_group(request):
    if request.user.profile.group:
        group = request.user.profile.group
        members = Profile.objects.all().filter(group=group)
        if members.count() == 1:
            group.delete()
        else:
            request.user.profile.group = None
            request.user.profile.save()
            if request.user == group.owner:
                group.owner = Profile.objects.all().filter(group=group).first().user
            group.save()
    return redirect("/group/")


def set_lang(request):
    print(request.method)
    if request.method == "POST":
        language = request.POST.get('language', 'en')
        if language not in ("en", "he"):
            return HttpResponse("Bad request", status=400)
        translation.activate(language)
        response = redirect(request.POST["next"])
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
        return response
    return HttpResponse("Method Not Allowed", status=405)


def index(request):
    return render(request, 'index.html', {"groups": CgGroup.objects.all()})
