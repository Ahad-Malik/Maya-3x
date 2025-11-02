from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class WorkflowMetadata(db.Model):
    __tablename__ = "workflow_metadata"

    id = db.Column(db.String, primary_key=True)
    status = db.Column(db.String, nullable=False, default="in_progress")
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    output = db.Column(db.Text, nullable=True)
    history = db.Column(db.JSON, nullable=True)


