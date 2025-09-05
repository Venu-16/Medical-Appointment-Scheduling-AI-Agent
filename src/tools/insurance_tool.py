import pandas as pd

class InsuranceCollectionTool:
    def __init__(self, appointments_file="data/appointments.csv"):
        self.appointments_file = appointments_file

    def add_insurance(self, appointment_id, carrier, member_id, group_number):
        df = pd.read_csv(self.appointments_file)
        idx = df.index[df["appointment_id"] == appointment_id].tolist()
        if not idx:
            return {"status": "error", "message": "Appointment not found"}

        df.at[idx[0], "insurance_carrier"] = carrier
        df.at[idx[0], "insurance_member_id"] = member_id
        df.at[idx[0], "insurance_group"] = group_number
        df.to_csv(self.appointments_file, index=False)

        return {"status": "updated", "appointment": df.iloc[idx[0]].to_dict()}
