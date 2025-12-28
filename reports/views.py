
from django.shortcuts import render
from django.db.models import Sum
from django.shortcuts import render
from timeTracker.models import TimeEntry, Sprint, Team, User,Task


from django.db.models.functions import TruncDate
from collections import defaultdict
import json
# Create your views here.

def team_dashboard(request):

    from collections import defaultdict
    from django.db.models import Sum



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





from decimal import Decimal
from django.contrib.auth.models import User
from django.db.models import Sum, F, Value, DecimalField
from django.db.models.functions import Coalesce, Greatest
from django.shortcuts import render



DECIMAL = DecimalField(max_digits=12, decimal_places=2)


def _clamp_decimal(x: Decimal, lo: Decimal, hi: Decimal) -> Decimal:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def users_task_dashboard(request):
    excluded_usernames = [
        "test",
        "test2",
        "milad_test",
        "milad",
    ]

    users = User.objects.exclude(username__in=excluded_usernames)

    rows = []

    for user in users:
        # -----------------------------------------
        # Base tasks: spent + remaining per task
        # -----------------------------------------
        base_tasks = Task.objects.filter(
            assigned_to=user,
            is_delete=False
        ).annotate(
            spent=Coalesce(Sum('timeentry__hours_spent'), Value(0), output_field=DECIMAL),
        ).annotate(
            remaining=Greatest(
                Coalesce(F('goal_time'), Value(0), output_field=DECIMAL) - F('spent'),
                Value(0),
                output_field=DECIMAL
            )
        )

        todo_tasks = base_tasks.filter(status='todo')
        doing_tasks = base_tasks.filter(status='doing')

        # اگر status='done' ندارید، این خط و بخش‌های مربوط به done را حذف کنید
        done_tasks = base_tasks.filter(status='done')

        # -----------------------------------------
        # Totals across ALL tasks (performance base)
        # -----------------------------------------
        all_tasks_agg = base_tasks.aggregate(
            total_goal=Coalesce(Sum('goal_time'), Value(0), output_field=DECIMAL),
            total_spent=Coalesce(Sum('spent'), Value(0), output_field=DECIMAL),
            total_remaining=Coalesce(Sum('remaining'), Value(0), output_field=DECIMAL),
        )
        total_goal_all = all_tasks_agg["total_goal"] or Decimal("0")
        total_spent_all_tasks = all_tasks_agg["total_spent"] or Decimal("0")
        total_remaining_all = all_tasks_agg["total_remaining"] or Decimal("0")

        # Also total spent across TimeEntry table (optional redundancy; keep if you want)
        total_spent_all = TimeEntry.objects.filter(user=user).aggregate(
            total=Coalesce(Sum('hours_spent'), Value(0), output_field=DECIMAL)
        )["total"] or Decimal("0")

        # -----------------------------------------
        # Progress (unclamped raw + clamped for UI)
        # -----------------------------------------
        if total_goal_all > 0:
            progress_raw = (total_spent_all_tasks / total_goal_all) * 100
        else:
            progress_raw = Decimal("0")

        # UI progress can be clamped to 0..100, but we also keep raw for "overrun" warning
        progress_ui = _clamp_decimal(progress_raw, Decimal("0"), Decimal("100"))
        progress_int = int(progress_ui.quantize(Decimal("1")))          # for progress bar width
        progress_display = progress_ui.quantize(Decimal("0.1"))         # shown percent

        # Overrun: spent > goal  => show warning + show raw percent (optional)
        is_overrun = (total_goal_all > 0 and total_spent_all_tasks > total_goal_all)
        overrun_percent = Decimal("0.0")
        if total_goal_all > 0:
            overrun_percent = progress_raw.quantize(Decimal("0.1"))

        # Over-commitment: goal is high but progress low
        # heuristic thresholds (tune as you like)
        # - if remaining is big AND progress is low => warning
        is_overcommit = (total_goal_all >= Decimal("20") and progress_ui < Decimal("40") and total_remaining_all >= Decimal("10"))

        # -----------------------------------------
        # UI status classes
        # -----------------------------------------
        if progress_ui >= Decimal("70"):
            status_text = "✅ عملکرد خوب"
            status_class = "pill-good"
            progress_class = "p-good"
        elif progress_ui >= Decimal("40"):
            status_text = "⚠️ عملکرد متوسط"
            status_class = "pill-mid"
            progress_class = "p-mid"
        else:
            status_text = "⛔ عملکرد ضعیف"
            status_class = "pill-low"
            progress_class = "p-low"

        # -----------------------------------------
        # Optional DONE totals
        # -----------------------------------------
        done_agg = done_tasks.aggregate(
            done_goal=Coalesce(Sum('goal_time'), Value(0), output_field=DECIMAL),
            done_spent=Coalesce(Sum('spent'), Value(0), output_field=DECIMAL),
            done_remaining=Coalesce(Sum('remaining'), Value(0), output_field=DECIMAL),
        )

        rows.append({
            "user": user,

            # totals
            "total_goal_all": total_goal_all,
            "total_spent_all_tasks": total_spent_all_tasks,
            "total_remaining_all": total_remaining_all,
            "total_spent_all": total_spent_all,  # from TimeEntry directly

            # progress / status
            "progress_int": progress_int,
            "progress_display": progress_display,
            "progress_raw_display": overrun_percent,  # only meaningful when overrun
            "status_text": status_text,
            "status_class": status_class,
            "progress_class": progress_class,

            # warnings
            "is_overrun": is_overrun,
            "is_overcommit": is_overcommit,

            # task lists
            "todo_tasks": todo_tasks,
            "doing_tasks": doing_tasks,
            "done_tasks": done_tasks,

            # done totals
            "done_total_goal": done_agg["done_goal"],
            "done_total_spent": done_agg["done_spent"],
            "done_total_remaining": done_agg["done_remaining"],
        })

    # -------------------------------------------------
    # Ranking: sort by progress (desc), then by spent (desc)
    # -------------------------------------------------
    rows_sorted = sorted(
        rows,
        key=lambda r: (Decimal(r["progress_display"]), Decimal(r["total_spent_all_tasks"])),
        reverse=True
    )

    # add rank & medal label
    for idx, r in enumerate(rows_sorted, start=1):
        r["rank"] = idx
        if idx == 1:
            r["rank_badge"] = "🥇"
        elif idx == 2:
            r["rank_badge"] = "🥈"
        elif idx == 3:
            r["rank_badge"] = "🥉"
        else:
            r["rank_badge"] = "⭐"

    # summary for top section
    summary = {
        "users_count": len(rows_sorted),
    }

    return render(
        request,
        "scrum_reports/sprint_hours.html",
        {"data": rows_sorted, "summary": summary}
    )
