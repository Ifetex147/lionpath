from app import app
from models import Node, Edge

with app.app_context():
    print("NODES:")
    for n in Node.query.all():
        print(f"  {n.node_id}: {n.formal_name} ({n.category})")
    print("\nEDGES:")
    for e in Edge.query.all():
        print(f"  {e.source_node_id} -> {e.destination_node_id}, {e.distance_meters}m")