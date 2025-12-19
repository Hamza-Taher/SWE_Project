class Plane:
    def __init__(self, plane_id, model, capacity, seats_A, seats_B, seats_C):
        self.plane_id = plane_id
        self.model = model
        self.capacity = capacity
        self.seats_A = seats_A
        self.seats_B = seats_B
        self.seats_C = seats_C

    def __repr__(self):
        return f"<Plane {self.model} | Capacity {self.capacity}>"