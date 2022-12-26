from django.shortcuts import render
from .models import RiddleSolution, War, Challenge, Riddle, Survivor, warrior_storage, format_path
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

def check_requirements(group, challenge, solution_model, field="required_riddles"):
    required = [(req_riddle, solution_model.objects.filter(group=group, riddle=req_riddle).exists()) 
                    for req_riddle in getattr(challenge, field).all()]
    is_solved_requirements = all(x[1] for x in required)
    return required, is_solved_requirements

@login_required
def riddle_page(request, id):
    form = RiddleSubmissionForm()
    try:
        group = request.user.profile.group
        riddle = Riddle.objects.get(id=id)
    except Riddle.DoesNotExist:
        return error(request, gettext('Riddle not found'))

    current_solution = None
    if RiddleSolution.objects.filter(group=group, riddle=riddle).exists():
        current_solution = RiddleSolution.objects.filter(group=group, riddle=riddle).first()

    required, is_solved_requirements = check_requirements(group, riddle, RiddleSolution)

    if request.method == 'POST':
        form = RiddleSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            if current_solution:
                current_solution.delete()
            RiddleSolution(
                riddle_solution=request.FILES["riddle_solution"], riddle=riddle, group=group).save()

    return render(request, 'challenges/riddles/riddle_page.html', 
                        {
                         'challenge': riddle, 
                         'solved_requirements': is_solved_requirements,
                         'form': form, 
                         'current_solution': current_solution,
                         'required': required
                         })


@login_required
def download_war(request, id, fieldname):
    try:
        profile = request.user.profile
        group = profile.group
        war = War.objects.get(id=id)

        bin = fieldname.split('_')[0] == 'bin'
        idx = fieldname.split('_')[-1]
        
        # folder_name = f"{group.center}_{group.name}"
        file_name = format_path(request.user.profile, idx, bin)

        path = join("wars", "submissions", str(id), "joined_submissions", file_name)

        response = FileResponse(warrior_storage.open(
            path, 'rb'), content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
    except Exception:
        return HttpResponseNotFound('Not Found')

@login_required
def download_riddle(request, id):
    try:
        group = request.user.profile.group
        riddle = Riddle.objects.get(id=id)
        solution = RiddleSolution.objects.get(group=group, riddle=riddle)
        file_name = re.sub(r'[^a-zA-Z0-9_.]', '', solution.riddle_solution.name)
        response = FileResponse(solution.riddle_solution, content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
    except Exception:
        return HttpResponseNotFound('Not Found')

@login_required
def war_page(request, id):
    try:
        war = War.objects.get(id=id)
        form = SurvivorSubmissionForm(war=war)
        group = request.user.profile.group
        prev_surv = Survivor.objects.filter(group=group, war=war)

        required_riddles, is_solved_riddles = check_requirements(group, war, RiddleSolution)
        required_wars = [(req_war, Survivor.objects.filter(group=group, war=req_war).exists()) 
                                for req_war in war.required_wars.all()] 
        is_solved_wars = all(x[1] for x in required_wars)

        is_solved_requirements = is_solved_riddles and is_solved_wars
        required = required_riddles + required_wars

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

        return render(request, 'challenges/wars/war_page.html', {
            'challenge': war, 
            'solved_requirements': is_solved_requirements,
            'required': required,
            'form': form, 
            'prev_upload': prev_surv.first()})
    except War.DoesNotExist:
        return error(request, gettext('War not found'))
