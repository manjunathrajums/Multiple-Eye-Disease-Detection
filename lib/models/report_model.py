class PatientReportViewModel:
    def __init__(self, uuid, name, age, gender, email, phone, address, disease_detected,diagnosis_date):
        self.uuid = uuid
        self.name = name
        self.age = age
        self.gender = gender
        self.email = email
        self.phone = phone
        self.address = address
        self.disease_detected = disease_detected
        self.diagnosis_date = diagnosis_date

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "disease_detected": self.disease_detected,
            "diagnosis_date": self.diagnosis_date
        }