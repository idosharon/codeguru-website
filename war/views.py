from django.shortcuts import redirect, render
from numpy import right_shift
from .models import RiddleSolution, War, Riddle
from itertools import chain
from codeguru.views import error
from codeguru.models import CgGroup
from django.contrib.auth.decorators import login_required
from .forms import SurvivorSubmissionForm, RiddleSubmissionForm


def challenges(request):
    wars = War.objects.all()
    riddles = Riddle.objects.all()
    challenges = sorted(chain(wars, riddles), key=lambda x: x.start_date)

    return render(request, 'challenges/challenges.html', {'challenges': challenges})


@login_required
def riddle_page(request, id):
    form = RiddleSubmissionForm()
    try:
        group = request.user.profile.group
        riddle = Riddle.objects.get(id=id)
    except Riddle.DoesNotExist:
        return error(request, 'Riddle not found')
    current_solution = None
    if RiddleSolution.objects.filter(group=group).exists():
        current_solution = RiddleSolution.objects.filter(group=group).first()
    if request.method == 'POST':
        form = RiddleSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            if current_solution:
                current_solution.delete()
            RiddleSolution(
                riddle_solution=request.FILES["riddle_solution"], riddle=riddle, group=group).save()
    return render(request, 'challenges/riddles/riddle_page.html', {'challenge': riddle, 'form': form, 'current_solution': current_solution})


@login_required
def war_page(request, id):
    try:
        war = War.objects.get(id=id)
        form = SurvivorSubmissionForm(war=war)
        return render(request, 'challenges/wars/war_page.html', {'challenge': war, 'form': form})
    except War.DoesNotExist:
        return error(request, 'War not found')
