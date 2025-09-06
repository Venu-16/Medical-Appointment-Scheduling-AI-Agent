import pandas as pd

class InsuranceCollectionTool:
    def __init__(self, appointments_file="data/appointments.csv"):
        self.appointments_file = appointments_file

    def add_from_form(self, appointment_id, form_data: dict):
        df = pd.read_csv(self.appointments_file)
        idx = df.index[df["appointment_id"] == appointment_id].tolist()
        if not idx:
            return {"status": "error", "message": "Appointment not found"}

        for key, val in form_data.items():
            df.at[idx[0], key] = val
        df.to_csv(self.appointments_file, index=False)

        return {"status": "updated", "insurance": form_data}
