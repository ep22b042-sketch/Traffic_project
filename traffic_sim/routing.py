import heapq


def shortest_path_road_ids(junctions, roads, start_junction_id, end_junction_id):
    graph = {jid: [] for jid in junctions}
    for road in roads.values():
        graph[road.start_junction].append((road.end_junction, road.length, road.road_id))

    dist = {jid: float("inf") for jid in junctions}
    prev = {jid: None for jid in junctions}
    prev_road = {jid: None for jid in junctions}
    dist[start_junction_id] = 0

    pq = [(0, start_junction_id)]

    while pq:
        cur_dist, node = heapq.heappop(pq)
        if cur_dist > dist[node]:
            continue
        if node == end_junction_id:
            break

        for nbr, weight, road_id in graph[node]:
            nd = cur_dist + weight
            if nd < dist[nbr]:
                dist[nbr] = nd
                prev[nbr] = node
                prev_road[nbr] = road_id
                heapq.heappush(pq, (nd, nbr))

    if dist[end_junction_id] == float("inf"):
        return []

    road_path = []
    cur = end_junction_id
    while cur != start_junction_id:
        road_path.append(prev_road[cur])
        cur = prev[cur]
    road_path.reverse()
    return road_path