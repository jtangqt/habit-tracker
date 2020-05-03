
class JSONRecord():
    def __init__(self, data_model):
        self.data_model = data_model

    def to_json(self):
        return json.dumps(self.data_model, default=lambda o: o.__dict__)

    def unpack_json(self, record):
        try:
            self.data_model.update(record)
        except:
            print("Info: no measurements for this day")