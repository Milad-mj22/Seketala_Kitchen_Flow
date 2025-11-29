from django.shortcuts import render

# Create your views here.
def is_any_team_admin(user):
    return hasattr(user, 'profile') and user.profile.admin_teams.exists()

def dashboard(request):
    return render(request, 'dashboard.html', {
        'user_data': request.user})



# timeTracker/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Sprint, Story, Task, Team, TimeEntry
from .forms import SprintForm, StoryForm, TaskForm, TeamForm, TimeEntryForm
from django.contrib.auth.decorators import login_required, user_passes_test

def is_superuser(user):
    return user.is_superuser  # or use any custom logic

@login_required
def team_list(request):
    teams = Team.objects.all()
    return render(request, 'teams/team_list.html', {'teams': teams})

@login_required
def team_create(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)  # Delay save
            team.save()                    # Save the instance first
            form.save_m2m()                # Now save M2M fields
            return redirect('team_list')
    else:
        form = TeamForm()
    return render(request, 'teams/team_form.html', {'form': form, 'title': 'Create Team'})

@login_required
def team_edit(request, pk):
    team = get_object_or_404(Team, pk=pk)
    form = TeamForm(request.POST or None, instance=team)
    if request.method == 'POST' and form.is_valid():
        team = form.save(commit=False)  # Delay save
        team.save()                    # Save the instance first
        form.save_m2m() 

                    # Explicitly sync admin_teams of each profile (optional)
        for profile in form.cleaned_data['admins']:
            profile.profile.admin_teams.add(team)


        return redirect('team_list')
    return render(request, 'teams/team_form.html', {'form': form, 'title': 'Edit Team'})




@login_required
# @user_passes_test(is_any_team_admin)
def sprint_list(request):
    sprints = Sprint.objects.all().order_by('-start_date')
    return render(request, 'sprints/sprint_list.html', {'sprints': sprints})


@login_required
def sprint_create(request):
    if request.method == 'POST':
        form = SprintForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sprint_list')
    else:
        form = SprintForm()

    return render(request, 'sprints/sprint_form.html', {
        'form': form,
        'title': 'Create Sprint'
    })


@login_required
def sprint_edit(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id)

    if request.method == 'POST':
        form = SprintForm(request.POST, instance=sprint)
        if form.is_valid():
            form.save()
            return redirect('sprint_list')  # Redirect back to the sprint list after saving
    else:
        form = SprintForm(instance=sprint)

    return render(request, 'sprints/sprint_edit.html', {'form': form, 'sprint': sprint})

@login_required
def task_create(request):
    profile = request.user.profile
    admin_teams = profile.admin_teams.all()

    # Filter stories to only those in admin's teams
    allowed_stories = Story.objects.filter(team__in=admin_teams)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        form.fields['story'].queryset = allowed_stories  # Ensure correct filtering on POST

        if form.is_valid():
            story = form.cleaned_data['story']
            if story.team in admin_teams:
                task = form.save()
                return redirect('task_list')  # Create this view later
            else:
                return render(request, '403.html')  # Not authorized for this story
    else:
        form = TaskForm()
        form.fields['story'].queryset = allowed_stories  # Only allow stories in admin’s teams

    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Create Task'})







@login_required
def story_list(request):
    profile = request.user.profile
    admin_teams = profile.admin_teams.all()

    team_id = request.GET.get('team')
    selected_team = None

    if team_id:
        selected_team = admin_teams.filter(id=team_id).first()
        if selected_team:
            stories = Story.objects.filter(team=selected_team).select_related('sprint', 'team')
        else:
            stories = Story.objects.none()
    else:
        stories = Story.objects.filter(team__in=admin_teams).select_related('sprint', 'team')

    return render(request, 'stories/story_list.html', {
        'stories': stories,
        'admin_teams': admin_teams,
        'selected_team': selected_team,
    })

@login_required
def story_create(request):
    profile = request.user.profile
    admin_teams = profile.admin_teams.all()

    if request.method == 'POST':
        form = StoryForm(request.POST)
        form.fields['team'].queryset = admin_teams
        if form.is_valid():
            story = form.save(commit=False)
            if story.team in admin_teams:
                story.save()
                return redirect('story_list')
            return render(request, '403.html')
    else:
        form = StoryForm()
        form.fields['team'].queryset = admin_teams

    return render(request, 'stories/story_form.html', {'form': form, 'title': 'Create Story'})

@login_required
def story_edit(request, pk):
    profile = request.user.profile
    story = get_object_or_404(Story, pk=pk)

    if story.team not in profile.admin_teams.all():
        return render(request, '403.html')

    form = StoryForm(request.POST or None, instance=story)
    form.fields['team'].queryset = profile.admin_teams.all()

    if request.method == 'POST' and form.is_valid():
        story = form.save(commit=False)
        story.save()
        return redirect('story_list')

    return render(request, 'stories/story_form.html', {'form': form, 'title': 'Edit Story'})

@login_required
def story_delete(request, pk):
    profile = request.user.profile
    story = get_object_or_404(Story, pk=pk)

    if story.team not in profile.admin_teams.all():
        return render(request, '403.html')

    if request.method == 'POST':
        story.delete()
        return redirect('story_list')

    return render(request, 'stories/story_confirm_delete.html', {'story': story})



@login_required
def task_list(request):
    from django.contrib.auth.models import User

    profile = request.user.profile
    teams = profile.teams.all()
    users = User.objects.filter(profile__teams__in=teams).distinct()
    sprints = Sprint.objects.filter(story__team__in=teams,is_active=True).distinct()

    selected_team_id = request.GET.get('team')
    selected_user_id = request.GET.get('user')
    selected_sprint_id = request.GET.get('sprint')
    selected_priority = request.GET.get('priority')

    # Filter tasks based on team, user, and sprint (if provided)
    tasks = Task.objects.filter(story__team__in=teams, story__sprint__is_active=True) \
        .select_related('story', 'assigned_to', 'story__team', 'story__sprint')
    

    if selected_team_id:
        tasks = tasks.filter(story__team_id=selected_team_id)
    if selected_user_id:
        tasks = tasks.filter(assigned_to_id=selected_user_id)
    if selected_sprint_id:
        tasks = tasks.filter(story__sprint_id=selected_sprint_id)
    if selected_priority:
        tasks = tasks.filter(priority=selected_priority)
        
    tasks = tasks.filter(is_delete = False)

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'teams': teams,
        'users': users,
        'sprints': sprints,
        'selected_team_id': selected_team_id,
        'selected_user_id': selected_user_id,
        'selected_sprint_id': selected_sprint_id,
        'title': 'Task Board'
    })


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


@login_required
def api_update_task_status(request, pk):
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)

    # Validate that user belongs to the team
    if request.user.profile not in task.story.team.members.all() :
        return JsonResponse({'error': 'Permission denied'}, status=403)

    new_status = request.POST.get('status')
    if new_status not in ['todo', 'doing', 'done']:
        return JsonResponse({'error': 'Invalid status'}, status=400)

    task.status = new_status
    task.save()

    return JsonResponse({'success': True, 'task_id': task.id, 'new_status': task.status})



@login_required
def task_detail_modal(request, pk):
    from django.template.loader import render_to_string
    task = get_object_or_404(Task, pk=pk)
    form = TimeEntryForm()

    if request.method == 'POST':

        if task.assigned_to != request.user:
            return JsonResponse({'error': 'You are not allowed to log time for this task.'}, status=403)


        form = TimeEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.task = task
            entry.user = request.user
            entry.save()
            form = TimeEntryForm()  # Clear form after save

    entries = TimeEntry.objects.filter(task=task).order_by('-datetime')

    html = render_to_string('tasks/partials/task_modal_content.html', {
        'task': task,
        'form': form,
        'entries': entries,
    }, request=request)

    return JsonResponse({'html': html})


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        task.is_delete = True
        task.user_delete = request.user
        task.save()
        return redirect('task_list')  # Or wherever you want to go after deletion

    # fallback for GET
    return redirect('task_list')


@login_required
def delete_time_entry(request, entry_id):
    entry = get_object_or_404(TimeEntry, id=entry_id)
    task = entry.task
    # Check if the logged-in user is assigned to the task
    if task.assigned_to != request.user:
        # messages.error(request, "You are not authorized to delete this time entry.")
        # return redirect('task_detail', task_id=task.id)
        return render('error_page.html',{'title':'دسترسی غیر مجاز','text':'شما مجاز به تغییر زمان وظیفه دیگران نیستید'})

    if request.method == 'POST':
        entry.delete()
        return redirect('task_list')

    # fallback for GET (optional)
    return redirect('task_list')


# views.py

from django.db.models import Sum
from django.shortcuts import render
from .models import TimeEntry, Sprint, Team, User

# def dashboard_view(request):
#     selected_sprint_id = request.GET.get("sprint_id")

#     # Filter by sprint if selected
#     if selected_sprint_id:
#         entries = TimeEntry.objects.filter(task__story__sprint_id=selected_sprint_id)
#     else:
#         entries = TimeEntry.objects.all()

#     # Total time by user
#     time_by_user = (
#         entries.values('user__username')
#         .annotate(total_hours=Sum('hours_spent'))
#         .order_by('-total_hours')
#     )

#     # Total time by team
#     time_by_team = (
#         entries.values('task__story__team__name')
#         .annotate(total_hours=Sum('hours_spent'))
#         .order_by('-total_hours')
#     )

#     # Goal vs Actual per task
#     task_progress = (
#         entries.values('task__title', 'task__goal_time')
#         .annotate(actual_time=Sum('hours_spent'))
#         .order_by('-actual_time')
#     )

#     return render(request, 'data_dashboard.html', {
#         'time_by_user': time_by_user,
#         'time_by_team': time_by_team,
#         'task_progress': task_progress,
#         'sprints': Sprint.objects.all(),
#         'selected_sprint_id': selected_sprint_id,
#     })





def team_dashboard(request):

    from collections import defaultdict
    from django.db.models import Sum
    from .models import TimeEntry


    team_task_data = defaultdict(list)

    entries = TimeEntry.objects.select_related('task__story__team').all()

    for entry in entries:
        team_name = entry.task.story.team.name
        task_title = entry.task.title
        team_task_data[team_name].append((task_title, float(entry.hours_spent)))

    # Aggregate data by task title for each team
    final_team_data = {}
    for team, task_entries in team_task_data.items():
        agg = {}
        for title, hours in task_entries:
            agg[title] = agg.get(title, 0) + hours
        final_team_data[team] = agg

    return render(request, 'data_dashboard.html', {
        'final_team_data': final_team_data,
    })




def selective_dashboard(request):

    from collections import defaultdict
    from django.db.models import Sum
    from .models import TimeEntry
    import json
    sprint_id = request.GET.get('sprint')
    sprints = Sprint.objects.all()
    selected_sprint = Sprint.objects.filter(id=sprint_id).first() if sprint_id else sprints.first()

    entries = TimeEntry.objects.select_related('task__story__team', 'user', 'task__story__sprint')
    if selected_sprint:
        entries = entries.filter(task__story__sprint=selected_sprint)

    # Structure: {team: {task: {user: hours}}}
    stacked_data = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    goal_data = defaultdict(lambda: {})

    for entry in entries:
        team = entry.task.story.team.name
        task = entry.task.title
        user = entry.user.username
        stacked_data[team][task][user] += float(entry.hours_spent)
        goal_data[team][task] = float(entry.task.goal_time)

    # Convert nested defaultdicts to normal dicts for safe use in template/JS
    stacked_data_json = json.dumps(stacked_data)
    goal_data_json = json.dumps(goal_data)

    return render(request, 'selective_dashboard.html', {
        'sprints': sprints,
        'selected_sprint': selected_sprint,
        'stacked_data_json': stacked_data_json,
        'goal_data_json': goal_data_json,
    })



def data_dashboard_view(request):
    from collections import defaultdict
    import json

    sprint_id = request.GET.get('sprint')
    sprints = Sprint.objects.all()
    selected_sprint = Sprint.objects.filter(id=sprint_id).first() if sprint_id else sprints.first()

    entries = TimeEntry.objects.select_related('task__story__team', 'user', 'task__story__sprint')
    if selected_sprint:
        entries = entries.filter(task__story__sprint=selected_sprint)

    # Structure: {team: {task: {user: hours}}}
    stacked_data = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    goal_data = defaultdict(dict)

    for entry in entries:
        team = entry.task.story.team.name
        task = entry.task.title
        user = entry.user.username
        stacked_data[team][task][user] += float(entry.hours_spent)
        goal_data[team][task] = float(entry.task.goal_time)

    # Total hours per team
    team_total_hours = (
        entries
        .values('task__story__team__name')
        .annotate(total_hours=Sum('hours_spent'))
        .order_by('-total_hours')
    )

    # Prepare for chart (labels and values)
    team_hours_chart = {
        "labels": [entry['task__story__team__name'] for entry in team_total_hours],
        "values": [float(entry['total_hours']) for entry in team_total_hours],
    }

    # Convert to normal dicts
    def convert(d):
        if isinstance(d, defaultdict):
            d = {k: convert(v) for k, v in d.items()}
        return d

    stacked_data_json = json.dumps(convert(stacked_data))
    goal_data_json = json.dumps(convert(goal_data))

    return render(request, 'data_dashboard.html', {
        'sprints': sprints,
        'selected_sprint': selected_sprint,
        'stacked_data_json': stacked_data_json,
        'goal_data_json': goal_data_json,
        'team_hours_chart': json.dumps(team_hours_chart),
    })





def team_overview_view(request):
    import json
    # Get all teams
    teams = Team.objects.all()

    # Prepare structure: {team_name: {users: [{name, time}], total: total_time}}
    overview_data = {}

    for team in teams:
        user_times = (
            TimeEntry.objects
            .filter(task__story__team=team,task__story__sprint__is_active=True)
            .values('user__username')
            .annotate(total=Sum('hours_spent'))
            .order_by('-total')
        )

        overview_data[team.name] = {
            'users': [
                {'name': u['user__username'], 'time': float(u['total'])}
                for u in user_times
            ],
            'total': sum(float(u['total']) for u in user_times)
        }

    return render(request, 'team_overview.html', {
        'overview_data': overview_data,
        'overview_json': json.dumps(overview_data),
    })




from django.db.models.functions import TruncDate
from .models import TimeEntry
from collections import defaultdict
import json

def team_timeline_view(request):
    entries = TimeEntry.objects.select_related('task__story__team', 'user').order_by('datetime')

    # Structure: {team: {date: hours}}
    timeline_data = defaultdict(lambda: defaultdict(float))
    all_dates = set()

    for entry in entries:
        team = entry.task.story.team.name
        day = entry.datetime.isoformat()
        timeline_data[team][day] += float(entry.hours_spent)
        all_dates.add(day)

    sorted_dates = sorted(all_dates)

    # Prepare chart format
    chart_data = {
        "labels": sorted_dates,
        "datasets": []
    }

    for i, (team, team_values) in enumerate(timeline_data.items()):
        chart_data["datasets"].append({
            "label": team,
            "data": [team_values.get(day, 0) for day in sorted_dates],
            "fill": False,
            "borderColor": f"hsl({i * 45 % 360}, 70%, 50%)",
            "tension": 0.3
        })

    return render(request, 'team_timeline.html', {
        'chart_json': json.dumps(chart_data)
    })