from flask import Flask, render_template, request, redirect, flash
from config import Config
from extensions import db
from datetime import datetime


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        from models import Event, Resource, EventResourceAllocation
        db.create_all()

    # ---------------- DASHBOARD ----------------
    @app.route("/")
    def dashboard():
        from models import Event, Resource, EventResourceAllocation

        stats = {
            "events": Event.query.count(),
            "resources": Resource.query.count(),
            "allocations": EventResourceAllocation.query.count(),
            "upcoming": Event.query.filter(Event.start_time > datetime.now()).count()
        }
        return render_template("dashboard.html", stats=stats)

    # ---------------- EVENTS ----------------
    @app.route("/events")
    def view_events():
        from models import Event
        events = Event.query.all()
        return render_template("events.html", events=events)

    @app.route("/events/add", methods=["GET", "POST"])
    def add_event():
        from models import Event

        if request.method == "POST":
            event = Event(
                title=request.form["title"],
                start_time=datetime.fromisoformat(request.form["start_time"]),
                end_time=datetime.fromisoformat(request.form["end_time"]),
                description=request.form["description"]
            )
            db.session.add(event)
            db.session.commit()
            flash("Event created successfully", "success")
            return redirect("/events")

        return render_template("add_event.html")

    @app.route("/events/delete/<int:event_id>")
    def delete_event(event_id):
        from models import Event
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        flash("Event deleted successfully", "success")
        return redirect("/events")

    # ---------------- RESOURCES ----------------
    @app.route("/resources")
    def view_resources():
        from models import Resource
        resources = Resource.query.all()
        return render_template("resources.html", resources=resources)

    @app.route("/resources/add", methods=["GET", "POST"])
    def add_resource():
        from models import Resource

        if request.method == "POST":
            resource = Resource(
                resource_name=request.form["resource_name"],
                resource_type=request.form["resource_type"]
            )
            db.session.add(resource)
            db.session.commit()
            flash("Resource added successfully", "success")
            return redirect("/resources")

        return render_template("add_resource.html")

    @app.route("/resources/delete/<int:resource_id>")
    def delete_resource(resource_id):
        from models import Resource
        resource = Resource.query.get_or_404(resource_id)
        db.session.delete(resource)
        db.session.commit()
        flash("Resource deleted successfully", "success")
        return redirect("/resources")

    # ---------------- ALLOCATION ----------------
    @app.route("/allocate", methods=["GET", "POST"])
    def allocate_resource():
        from models import Event, Resource, EventResourceAllocation

        events = Event.query.all()
        resources = Resource.query.all()
        error = None

        if request.method == "POST":
            event_id = int(request.form["event_id"])
            resource_id = int(request.form["resource_id"])
            event = Event.query.get(event_id)

            existing_allocations = EventResourceAllocation.query.filter_by(
                resource_id=resource_id
            ).all()

            for alloc in existing_allocations:
                existing_event = alloc.event
                if event.start_time < existing_event.end_time and existing_event.start_time < event.end_time:
                    error = (
                        f"Resource '{alloc.resource.resource_name}' "
                        f"is already allocated to '{existing_event.title}' "
                        f"({existing_event.start_time} - {existing_event.end_time})"
                    )
                    break

            if not error:
                allocation = EventResourceAllocation(
                    event_id=event_id,
                    resource_id=resource_id
                )
                db.session.add(allocation)
                db.session.commit()
                flash("Resource allocated successfully", "success")
                return redirect("/allocations")

        return render_template(
            "allocate_resource.html",
            events=events,
            resources=resources,
            error=error
        )

    @app.route("/allocations")
    def view_allocations():
        from models import EventResourceAllocation
        allocations = EventResourceAllocation.query.all()
        return render_template("allocations.html", allocations=allocations)

    @app.route("/allocations/delete/<int:allocation_id>")
    def delete_allocation(allocation_id):
        from models import EventResourceAllocation
        allocation = EventResourceAllocation.query.get_or_404(allocation_id)
        db.session.delete(allocation)
        db.session.commit()
        flash("Allocation removed successfully", "success")
        return redirect("/allocations")

    # ---------------- REPORT ----------------
    @app.route("/report", methods=["GET", "POST"])
    def resource_report():
        from models import Resource

        report = []

        if request.method == "POST":
            start_date = datetime.fromisoformat(request.form["start_date"])
            end_date = datetime.fromisoformat(request.form["end_date"])

            for resource in Resource.query.all():
                total_hours = 0
                upcoming = []

                for alloc in resource.allocations:
                    event = alloc.event
                    if event.start_time < end_date and event.end_time > start_date:
                        overlap_start = max(event.start_time, start_date)
                        overlap_end = min(event.end_time, end_date)
                        total_hours += (overlap_end - overlap_start).total_seconds() / 3600
                        upcoming.append(f"{event.title} ({event.start_time} - {event.end_time})")

                report.append({
                    "resource": f"{resource.resource_name} ({resource.resource_type})",
                    "hours": round(total_hours, 2),
                    "upcoming": upcoming
                })

        return render_template("resource_report.html", report=report)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
