import pandas as pd

class ConfirmationTool:
    def __init__(self, appointments_file="data/appointments.csv"):
        self.appointments_file = appointments_file

    def confirm(self, appointment_id):
        df = pd.read_csv(self.appointments_file)
        row = df[df["appointment_id"] == appointment_id]
        if row.empty:
            return {"status": "error", "message": "Appointment not found"}

        record = row.iloc[0].to_dict()
        msg = (
            f"Appointment confirmed!\n"
            f"Patient: {record['patient_name']}\n"
            f"Doctor Slot: {record['slot_id']}\n"
            f"Reason: {record['reason']}\n"
            f"Booked At: {record['booked_at']}"
        )
        return {"status": "confirmed", "message": msg}
