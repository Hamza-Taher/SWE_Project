class User:
    def __init__(self, username, first_name=None, last_name=None, passport_number=None, 
                 phone_number=None):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.passport_number = passport_number
        self.phone_number = phone_number

    def full_name(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username