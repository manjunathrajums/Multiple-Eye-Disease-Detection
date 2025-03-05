class Prediction:
    def __init__(self,uuid,predicted_class,recorded_time):
        self.uuid = uuid
        self.predicted_class = predicted_class
        self.recorded_time = recorded_time
    
    def to_dict(self):
        return {
            "uuid" : self.uuid,
            "predicted_class" : self.predicted_class,
            "timestamp" : self.recorded_time
        }