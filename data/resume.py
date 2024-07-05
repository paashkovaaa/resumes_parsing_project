class Resume:
    def __init__(self, position, experience, skills, location, salary):
        self.position = position
        self.experience = experience
        self.skills = skills
        self.location = location
        self.salary = salary

    def __repr__(self):
        return (
            f"Position: {self.position}, "
            f"experience: {self.experience},  "
            f"skills: {self.skills}, "
            f"location: {self.location}, "
            f"salary expectation: {self.salary}, "
        )
