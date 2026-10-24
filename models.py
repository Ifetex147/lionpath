from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Node(db.Model):
    __tablename__ = "nodes"

    node_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    formal_name = db.Column(db.String(100), nullable=False)
    informal_names = db.Column(db.String(255))          # comma-separated slang names
    category = db.Column(db.String(50), nullable=False) # building, hostel, junction, theatre, library, gate, cafeteria, etc.
    description = db.Column(db.Text)                    # what it looks like
    photo_path = db.Column(db.String(255))              # landmark photo


class Edge(db.Model):
    __tablename__ = "edges"

    edge_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_node_id = db.Column(db.Integer, db.ForeignKey("nodes.node_id"), nullable=False)
    destination_node_id = db.Column(db.Integer, db.ForeignKey("nodes.node_id"), nullable=False)
    instruction = db.Column(db.Text, nullable=False)    # "walk past the Physics block..."
    distance_meters = db.Column(db.Integer, nullable=False)
    foot_accessible = db.Column(db.Boolean, default=True)
    photo_path = db.Column(db.String(255), nullable=True) # photo of the walkway or turn


class OrientationKB(db.Model):
    __tablename__ = "orientation_kb"

    kb_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(50), nullable=False) # fees, registration, id_card, hostel, academics, facilities, etc.
    question_pattern = db.Column(db.Text, nullable=False)   # example questions this entry answers
    answer = db.Column(db.Text, nullable=False)             # the step-by-step answer

class Timetable(db.Model):
    __tablename__ = "timetable"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department = db.Column(db.String(50), default="General") # e.g. "Computer Science", "Mathematics", "Geology"
    course_code = db.Column(db.String(20), nullable=False)
    course_title = db.Column(db.String(100), default="") # e.g. "Elementary Mathematics I"
    day = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    venue = db.Column(db.String(100), nullable=False)

class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    date_time = db.Column(db.String(100), nullable=False)
    venue = db.Column(db.String(100), nullable=False)
