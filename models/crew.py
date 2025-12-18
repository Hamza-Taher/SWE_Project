from .user import User

class Crew(User):
    def __init__(self, username, first_name=None, last_name=None,
                 passport_number=None, phone_number=None):
        super().__init__(username, first_name, last_name, passport_number, phone_number)