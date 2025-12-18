from extensions import db

class Event(db.Model):
    __tablename__ = "events"

    event_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)

    allocations = db.relationship(
        "EventResourceAllocation",
        back_populates="event",
        cascade="all, delete-orphan"
    )
