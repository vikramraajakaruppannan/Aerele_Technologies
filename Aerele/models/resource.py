from extensions import db

class Resource(db.Model):
    __tablename__ = "resources"

    resource_id = db.Column(db.Integer, primary_key=True)
    resource_name = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)

    allocations = db.relationship(
        "EventResourceAllocation",
        back_populates="resource",
        cascade="all, delete-orphan"
    )
