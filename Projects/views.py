from django.shortcuts import render

# Create your views here.
# views.py
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Value , Q
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, render

from .models import Project
from timeTracker.models import Sprint, Story, Task, TimeEntry  # adjust import paths to your app
from django.db.models import Sum, Value, DecimalField
DECIMAL = DecimalField(max_digits=12, decimal_places=2)
@login_required
def project_time_report(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # ✅ sprints available for this project (through stories)
    sprints_qs = Sprint.objects.filter(
        story__project=project
    ).distinct().order_by("-start_date", "-id")

    last_sprint = sprints_qs.first()
    selected_sprint = request.GET.get("sprint")

    # default: last sprint (if exists)
    if not selected_sprint and last_sprint:
        selected_sprint = str(last_sprint.id)

    sprint_filter_id = None
    if selected_sprint and selected_sprint != "all":
        try:
            sprint_filter_id = int(selected_sprint)
        except (TypeError, ValueError):
            sprint_filter_id = None

    # ✅ base queryset for time entries in this project
    time_qs = TimeEntry.objects.filter(
        task__story__project=project
    )

    # ✅ apply sprint filter if not "all"
    if sprint_filter_id:
        time_qs = time_qs.filter(task__story__sprint_id=sprint_filter_id)

    # ----------------------------
    # Totals
    # ----------------------------
    total_spent = time_qs.aggregate(
        total=Coalesce(Sum("hours_spent"), Value(0), output_field=DECIMAL)
    )["total"] or 0

    # ----------------------------
    # Per-user totals
    # ----------------------------
    per_user = (
        time_qs.values("user_id", "user__username")
        .annotate(spent=Coalesce(Sum("hours_spent"), Value(0), output_field=DECIMAL))
        .order_by("-spent", "user__username")
    )

    # Optional: limit to project.persons users (if you want to hide others)
    # per_user = per_user.filter(user__in=project.persons.all())  # NOTE: requires join style change if needed

    # selected sprint obj for UI label
    selected_sprint_obj = None
    if sprint_filter_id:
        selected_sprint_obj = sprints_qs.filter(id=sprint_filter_id).first()

    return render(request, "projects/project_time_report.html", {
        "project": project,
        "sprints": sprints_qs,
        "selected_sprint": selected_sprint or "all",
        "selected_sprint_obj": selected_sprint_obj,
        "total_spent": total_spent,
        "per_user": per_user,
    })





# views.py
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import render

from .models import Project
from timeTracker.models import Sprint, TimeEntry  # adjust import path to your app

DECIMAL = DecimalField(max_digits=12, decimal_places=2)

@login_required
def projects_time_summary(request):
    # Sprint dropdown options
    sprints_qs = Sprint.objects.all().order_by("-start_date", "-id")

    last_sprint = sprints_qs.first()
    selected_sprint = request.GET.get("sprint")

    # default: last sprint (optional behavior; comment out if you want default=all)
    if not selected_sprint and last_sprint:
        selected_sprint = str(last_sprint.id)

    sprint_filter_id = None
    if selected_sprint and selected_sprint != "all":
        try:
            sprint_filter_id = int(selected_sprint)
        except (TypeError, ValueError):
            sprint_filter_id = None

    # selected sprint object for label
    selected_sprint_obj = None
    if sprint_filter_id:
        selected_sprint_obj = sprints_qs.filter(id=sprint_filter_id).first()

    # ---------------------------------------------------------
    # Projects queryset + conditional aggregation for spent time
    # ---------------------------------------------------------
    projects_qs = Project.objects.select_related("city").prefetch_related("persons")


    # If you want to limit projects by user access, uncomment:
    # projects_qs = projects_qs.filter(persons=request.user)

    if sprint_filter_id:
        # Only sum time entries that belong to stories in the selected sprint
        projects_qs = projects_qs.annotate(
            total_spent=Coalesce(
                Sum(
                    "story__task__timeentry__hours_spent",
                    filter=Q(story__sprint_id=sprint_filter_id),
                ),
                Value(Decimal("0.00")),
                output_field=DECIMAL,
            )
        )
    else:
        # "all" (or invalid) => sum across all sprints
        projects_qs = projects_qs.annotate(
            total_spent=Coalesce(
                Sum("story__task__timeentry__hours_spent"),
                Value(Decimal("0.00")),
                output_field=DECIMAL,
            )
        )

    rows = projects_qs.order_by("-total_spent", "name")

    # ---------------------------------------------------------
    # Grand total (optional)
    # ---------------------------------------------------------
    time_qs = TimeEntry.objects.filter(task__story__project__isnull=False)
    if sprint_filter_id:
        time_qs = time_qs.filter(task__story__sprint_id=sprint_filter_id)

    grand_total = time_qs.aggregate(
        total=Coalesce(Sum("hours_spent"), Value(Decimal("0.00")), output_field=DECIMAL)
    )["total"] or Decimal("0.00")

    return render(request, "projects/projects_time_summary.html", {
        "rows": rows,  # ✅ now Project objects with .image.url available
        "sprints": sprints_qs,
        "selected_sprint": selected_sprint or "all",
        "selected_sprint_obj": selected_sprint_obj,
        "grand_total": grand_total,
    })