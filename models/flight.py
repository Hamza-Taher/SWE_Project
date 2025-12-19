class Flight:
    def __init__(self, flight_id, source_id, dest_id, pilot_id, plane_id,
                 departure_time, arrival_time, flight_date, distance_km):
        self.flight_id = flight_id
        self.source_id = source_id
        self.dest_id = dest_id
        self.pilot_id = pilot_id
        self.plane_id = plane_id
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.flight_date = flight_date
        self.distance_km = distance_km

    def __repr__(self):
        return f"<Flight {self.flight_id}: {self.source_id} → {self.dest_id}>"