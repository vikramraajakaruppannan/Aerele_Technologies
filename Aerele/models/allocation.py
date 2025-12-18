from extensions import db

class EventResourceAllocation(db.Model):
    __tablename__ = "event_resource_allocations"

    allocation_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.event_id"), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.resource_id"), nullable=False)

    event = db.relationship("Event", back_populates="allocations")
    resource = db.relationship("Resource", back_populates="allocations")
