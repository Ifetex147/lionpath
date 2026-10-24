import heapq
from models import db, Node, Edge


def load_graph():
    """Build an adjacency list from the edges table with optional edge photos."""
    graph = {}
    for edge in Edge.query.all():
        edge_photo = getattr(edge, "photo_path", None)
        graph.setdefault(edge.source_node_id, []).append(
            (edge.destination_node_id, edge.distance_meters, edge.instruction, edge_photo)
        )
    return graph


def dijkstra(graph, start_id, end_id, return_distance=False):
    """
    Shortest path by distance using Dijkstra's algorithm.
    Returns path (or (path, total_distance) if return_distance=True).
    Path elements are (node_id, instruction, edge_photo, distance).
    """
    distances = {start_id: 0}
    previous = {}
    queue = [(0, start_id)]

    while queue:
        current_dist, current = heapq.heappop(queue)
        if current == end_id:
            break
        if current_dist > distances.get(current, float("inf")):
            continue
        for neighbor_entry in graph.get(current, []):
            if len(neighbor_entry) == 4:
                neighbor, weight, instruction, edge_photo = neighbor_entry
            else:
                neighbor, weight, instruction = neighbor_entry[:3]
                edge_photo = None

            new_dist = current_dist + weight
            if new_dist < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_dist
                previous[neighbor] = (current, instruction, edge_photo, weight)
                heapq.heappush(queue, (new_dist, neighbor))

    # Walk backwards from destination to reconstruct the path
    path = []
    node = end_id
    while node != start_id:
        if node not in previous:        # no route exists
            return (None, 0) if return_distance else None
        prev_node, instruction, edge_photo, weight = previous[node]
        path.append((node, instruction, edge_photo, weight))
        node = prev_node
    path.reverse()
    
    total_distance = distances.get(end_id, 0)
    return (path, total_distance) if return_distance else path


def get_directions(source_name, destination_name, return_route_data=False):
    """
    Finds nodes, calculates the shortest walking path via Dijkstra,
    and returns formatted directions with distance, walking time, and step photos.
    If return_route_data is True, returns:
      (text_result, route_node_ids, total_distance, est_mins, steps_data)
    """
    source = Node.query.filter_by(formal_name=source_name).first()
    destination = Node.query.filter_by(formal_name=destination_name).first()

    if not source:
        msg = f"I don't know a place called '{source_name}' yet."
        return (msg, [], 0, 0, []) if return_route_data else msg
    if not destination:
        msg = f"I don't know a place called '{destination_name}' yet."
        return (msg, [], 0, 0, []) if return_route_data else msg
    if source.node_id == destination.node_id:
        msg = f"You are already at **{destination.formal_name}**!"
        return (msg, [source.node_id], 0, 0, []) if return_route_data else msg

    graph = load_graph()
    path, total_distance = dijkstra(graph, source.node_id, destination.node_id, return_distance=True)

    if path is None:
        msg = f"I couldn't find a walking route from **{source_name}** to **{destination_name}**."
        return (msg, [], 0, 0, []) if return_route_data else msg

    # Average pedestrian walking pace: ~75 meters/minute
    est_mins = max(1, round(total_distance / 75))
    total_steps = len(path)
    route_node_ids = [source.node_id] + [item[0] for item in path]

    est_secs = round(total_distance / 1.25)
    lines = [
        f"🗺️ **Walking Route to {destination.formal_name}**",
        f"📍 **Starting Point**: {source.formal_name}",
        f"⏱️ **Estimated Distance & Time**: ~{total_distance} meters (~{est_mins} min{'s' if est_mins > 1 else ''} walk / {est_secs}s)\n"
    ]

    steps_data = []
    for step, item in enumerate(path, start=1):
        node_id = item[0]
        instruction = item[1]
        edge_photo = item[2] if len(item) > 2 else None
        weight = item[3] if len(item) > 3 else 0

        node = db.session.get(Node, node_id)
        is_dest = (step == total_steps)

        lines.append(f"**{step}.** {instruction}")
        if is_dest:
            lines.append(f"   🎯 *Arrive at: {node.formal_name}*")
        else:
            lines.append(f"   📍 *Pass through: {node.formal_name}*")

        # Step photo: edge photo preferred, fallback to node photo
        step_photo = edge_photo or (node.photo_path if node.photo_path else None)

        if step_photo:
            lines.append(f"[[PHOTO:{step_photo}:{node.formal_name}:{'dest' if is_dest else 'waypoint'}]]")

        steps_data.append({
            "step": step,
            "instruction": instruction,
            "node_id": node.node_id,
            "node_name": node.formal_name,
            "photo": step_photo,
            "distance": weight,
            "is_destination": is_dest
        })

    if destination.description:
        lines.append(f"\nℹ️ **Landmark Guide**: {destination.description}")

    # Intra-campus Keke Transit Advisory
    is_long_or_gate = (
        est_mins >= 8
        or total_distance >= 600
        or any(cat in (source.category, destination.category) for cat in ["gate"])
        or "medical" in source.formal_name.lower()
        or "medical" in destination.formal_name.lower()
    )
    if is_long_or_gate:
        lines.append(
            "\n💡 **Campus Transit Advice**: There are kekes that have been built by the school, "
            "specifically designed to transport students just within the school. And you can tell them where you want "
            "to go to and they can take you to your destination. If you need a quick movement, they arrive quickly."
        )

    text_result = "\n".join(lines)
    if return_route_data:
        return text_result, route_node_ids, total_distance, est_mins, steps_data
    return text_result
