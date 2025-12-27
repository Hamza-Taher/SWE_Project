class Seat:
    def __init__(self, seat_id, plane_id, seat_class, is_available=True):
        self.seat_id = seat_id
        self.plane_id = plane_id
        self.seat_class = seat_class  # A, B, or C
        self.is_available = is_available

    def __repr__(self):
        return f"<Seat {self.seat_id} | Plane {self.plane_id} | Class {self.seat_class} | Available {self.is_available}>"