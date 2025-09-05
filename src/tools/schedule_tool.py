import pandas as pd

class ScheduleLookupTool:
    def __init__(self, schedule_file="data/doctor_schedules.xlsx"):
        self.schedule_file = schedule_file

    def get_slots(self, doctor_id, date=None):
        df = pd.read_excel(self.schedule_file, sheet_name="schedules")
        df = df[(df["doctor_id"] == doctor_id) & (df["is_booked"] == False)]
        if date:
            df = df[df["date"] == date]
        return df.to_dict(orient="records")
