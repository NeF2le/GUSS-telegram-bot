class PersonAlreadyExists(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f"PersonAlreadyExists {self.message[0]}"
        else:
            return "PersonAlreadyExists has been raised"
