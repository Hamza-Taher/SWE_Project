from .user import User

class Passenger(User):
    def __init__(self, username, first_name=None, last_name=None,
                 email=None, passport_number=None, phone_number=None, flight_number=None):
        super().__init__(username, first_name, last_name, passport_number, phone_number)
        self.email = email
        self.flight_number = flight_number