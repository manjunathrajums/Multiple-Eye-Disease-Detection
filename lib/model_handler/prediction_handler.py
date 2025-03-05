from lib.extensions import mongo
from datetime import datetime

from lib.models.prediction import Prediction
class PredictionHandler:
    def __init__(self,uuid,reported_disease):
        self.uuid = uuid
        self.reported_disease = reported_disease
    
    def save_prediction(self):
        timestamp = datetime.now()
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        data = Prediction(self.uuid,self.reported_disease,timestamp).to_dict()
        mongo.db.prediction.insert_one(data)
        return 

        
