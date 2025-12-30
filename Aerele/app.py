from flask import Flask, render_template, request, redirect, flash
from datetime import datetime
from config import Config
from extensions import db
from models import Event,Resource,EventResourceAllocation

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ================= DASHBOARD =================
    @app.route("/")
    def dashboard():

        stats = {
            "events": Event.query.count(),
            "resources": Resource.query.count(),
            "allocations": EventResourceAllocation.query.filter_by(is_active=True).count(),
            "upcoming": Event.query.filter(Event.start_time > datetime.now()).count(),
            "completed": Event.query.filter(Event.end_time < datetime.now()).count(),
            "ongoing": Event.query.filter(Event.start_time <= datetime.now(), Event.end_time >= datetime.now()).count()
        }
        return render_template("dashboard.html", stats=stats)

    # ================= EVENTS =================
    @app.route("/events")
    def view_events():

        events = Event.query.order_by(Event.start_time).all()
        # events = Event.query.filter(Event.end_time > datetime.now()).all()
        
        # Add status dynamically
        for event in events:
            if event.end_time < datetime.now():
                event.status = "Completed"
            elif event.start_time > datetime.now():
                event.status = "Upcoming"
            else:
                event.status = "Ongoing"

        return render_template("events.html", events=events)


    @app.route("/events/add", methods=["GET", "POST"])
    def add_event():

        if request.method == "POST":
            try:
                event = Event(
                    title=request.form["title"],
                    start_time=datetime.fromisoformat(request.form["start_time"]),
                    end_time=datetime.fromisoformat(request.form["end_time"]),
                    description=request.form["description"]
                )
                start_time = datetime.fromisoformat(request.form["start_time"])
                end_time = datetime.fromisoformat(request.form["end_time"])

                if end_time <= start_time:
                    flash("End time must be greater than start time", "danger")
                    return redirect("/events/add")
                
                if start_time < datetime.now():
                    flash("Cannot create events in the past", "danger")
                    return redirect("/events/add")

                db.session.add(event)
                db.session.commit()
                flash("Event created successfully", "success")
            except Exception as e:
                db.session.rollback()
                flash("Failed to create event", "danger")

            return redirect("/events")

        return render_template("add_event.html")

    @app.route("/events/delete/<int:event_id>")
    def delete_event(event_id):

        event = Event.query.get_or_404(event_id)
        
        db.session.delete(event)
        db.session.commit()
        flash("Event deleted successfully", "success")
        return redirect("/events")
    
    @app.route("/events/edit/<int:event_id>", methods=["GET", "POST"])
    def edit_event(event_id):

        event = Event.query.get_or_404(event_id)

        if request.method == "POST":
            try:
                event.title = request.form["title"]
                event.start_time = datetime.fromisoformat(request.form["start_time"])
                event.end_time = datetime.fromisoformat(request.form["end_time"])
                event.description = request.form["description"]

                db.session.commit()
                flash("Event updated successfully", "success")
                return redirect("/events")

            except Exception as e:
                db.session.rollback()
                flash("Failed to update event", "danger")

        return render_template("edit_event.html", event=event)


    # ================= RESOURCES =================
    @app.route("/resources")
    def view_resources():
        return render_template("resources.html", resources=Resource.query.all())

    @app.route("/resources/add", methods=["GET", "POST"])
    def add_resource():

        if request.method == "POST":
            try:
                resource_name = request.form.get("resource_name")
                resource_type = request.form.get("resource_type")
                custom_type = request.form.get("custom_type")

                # Handle custom type safely
                if resource_type == "custom":
                    if not custom_type or custom_type.strip() == "":
                        flash("Please enter a custom resource type.", "danger")
                        return redirect("/resources/add")
                    resource_type = custom_type.strip()

                resource = Resource(
                    resource_name=resource_name,
                    resource_type=resource_type
                )

                db.session.add(resource)
                db.session.commit()

                flash("Resource added successfully", "success")
                return redirect("/resources")

            except Exception as e:
                db.session.rollback()
                flash("Failed to add resource. Please try again.", "danger")
                return redirect("/resources/add")

        return render_template("add_resource.html")


    @app.route("/resources/delete/<int:resource_id>")
    def delete_resource(resource_id):

        resource = Resource.query.get_or_404(resource_id)
        db.session.delete(resource)
        db.session.commit()
        flash("Resource deleted successfully", "success")
        return redirect("/resources")

    # ================= ALLOCATION =================
    @app.route("/allocate", methods=["GET", "POST"])
    def allocate_resource():

        events = Event.query.all()
        resources = Resource.query.all()
        error = None

        if request.method == "POST":
            event_id = int(request.form["event_id"])
            resource_id = int(request.form["resource_id"])

            event = Event.query.get(event_id)

            # ✅ CHECK 1: Event already has a resource
            existing_event_allocation = EventResourceAllocation.query.filter_by(
                event_id=event_id,
                is_active=True
            ).first()

            if existing_event_allocation:
                error = (
                    f"❌ Event '{event.title}' already has a resource assigned "
                    f"({existing_event_allocation.resource.resource_name})."
                )
                return render_template(
                    "allocate_resource.html",
                    events=events,
                    resources=resources,
                    error=error
                )

            # ✅ CHECK 2: Resource conflict (time overlap)
            allocations = EventResourceAllocation.query.filter_by(
                resource_id=resource_id,
                is_active=True
            ).all()

            for alloc in allocations:
                existing_event = alloc.event

                if (
                    event.start_time < existing_event.end_time and
                    existing_event.start_time < event.end_time
                ):
                    error = (
                        f"❌ Resource '{alloc.resource.resource_name}' is already booked "
                        f"for '{existing_event.title}' "
                        f"({existing_event.start_time} - {existing_event.end_time})"
                    )
                    break

            if error:
                return render_template(
                    "allocate_resource.html",
                    events=events,
                    resources=resources,
                    error=error
                )

            # ✅ SAFE TO ALLOCATE
            allocation = EventResourceAllocation(
                event_id=event_id,
                resource_id=resource_id,
                is_active=True
            )

            db.session.add(allocation)
            db.session.commit()

            flash("Resource allocated successfully", "success")
            return redirect("/allocations")

        return render_template(
            "allocate_resource.html",
            events=events,
            resources=resources,
            error=None
        )
        
    # Automatically deactivate expired allocations
    def cleanup_expired_allocations():
        now = datetime.now()
        expired = (
            EventResourceAllocation.query
            .join(Event)
            .filter(Event.end_time < now,
                    EventResourceAllocation.is_active == True)
            .all()
        )

        for alloc in expired:
            alloc.is_active = False

        db.session.commit()

    # ================= ALLOCATIONS =================
    @app.route("/allocations")
    def view_allocations():
        cleanup_expired_allocations()

        allocations = EventResourceAllocation.query.filter_by(is_active=True).all()
        return render_template("allocations.html", allocations=allocations)


    @app.route("/allocations/delete/<int:allocation_id>")
    def delete_allocation(allocation_id):

        allocation = EventResourceAllocation.query.get_or_404(allocation_id)
        
        db.session.delete(allocation)
        db.session.commit()
        flash("Allocation removed successfully", "success")
        return redirect("/allocations")

    # ================= REPORT =================
    @app.route("/report", methods=["GET", "POST"])
    def resource_report():

        report = []

        if request.method == "POST":
            start_date = datetime.fromisoformat(request.form["start_date"])
            end_date = datetime.fromisoformat(request.form["end_date"])

            for resource in Resource.query.all():
                total_hours = 0
                upcoming = []

                for alloc in resource.allocations:
                    e = alloc.event
                    if e.start_time < end_date and e.end_time > start_date:
                        overlap = min(e.end_time, end_date) - max(e.start_time, start_date)
                        total_hours += overlap.total_seconds() / 3600
                        upcoming.append(f"{e.title} ({e.start_time} - {e.end_time})")

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
