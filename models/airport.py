class Airport:
    def __init__(self, airport_id, name, country, city):
        self.airport_id = airport_id
        self.name = name
        self.country = country
        self.city = city

    def __repr__(self):
        return f"<Airport {self.name} - {self.city}, {self.country}>"