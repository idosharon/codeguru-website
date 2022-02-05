from django.shortcuts import redirect, render
from .models import RiddleSolution, War, Riddle, Survivor, warrior_storage
from itertools import chain
from codeguru.views import error
from codeguru.models import CgGroup
from django.contrib.auth.decorators import login_required
from .forms import SurvivorSubmissionForm, RiddleSubmissionForm
from django.http import FileResponse, HttpResponseNotFound
from os.path import join
import re
from django.utils.translation import gettext

def challenges(request):
    wars = War.objects.all()
    riddles = Riddle.objects.all()
    challenges = sorted(chain(wars, riddles), key=lambda x: x.end_date)

    return render(request, 'challenges/challenges.html', {'challenges': challenges})


@login_required
def riddle_page(request, id):
    form = RiddleSubmissionForm()
    try:
        group = request.user.profile.group
        riddle = Riddle.objects.get(id=id)
    except Riddle.DoesNotExist:
        return error(request, gettext('Riddle not found'))
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
    return render(request, 'challenges/riddles/riddle_page.html', {'challenge': riddle, 'form': form, 'current_solution': RiddleSolution.objects.filter(group=group).first()})


@login_required
def download(request, id, filename):
    if not re.compile(r"(bin|asm)_\d+").match(filename):
        return HttpResponseNotFound('Not Found: Bad filename')
    try:
        group = request.user.profile.group
        war = War.objects.get(id=id)
        path = join("wars", "submissions", str(war.id), group.center + "_" + group.name, filename)
        response = FileResponse(warrior_storage.open(
            path, 'rb'), content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except:
        return HttpResponseNotFound('Not Found')


@login_required
def war_page(request, id):
    try:
        war = War.objects.get(id=id)
        form = SurvivorSubmissionForm(war=war)
        group = request.user.profile.group
        prev_surv = Survivor.objects.filter(group=group, war=war)
        
        if request.method == 'POST':
            if not war.active:
                return error(request, gettext("Upload failed. This challenge is inactive."))
            form = SurvivorSubmissionForm(request.POST, request.FILES, war=war)
            if form.is_valid():
                for surv in prev_surv:
                    surv.delete()
                for i in range(1, war.amount_of_survivors + 1):
                    Survivor(
                        group=group, war=war, asm_file=form.files[f'asm_{i}'], bin_file=form.files[f'bin_{i}'], warrior_file_idx=i).save()

        return render(request, 'challenges/wars/war_page.html', {'challenge': war, 
            'form': form, 
            'prev_upload': prev_surv.first()})
    except War.DoesNotExist:
        return error(request, gettext('War not found'))
