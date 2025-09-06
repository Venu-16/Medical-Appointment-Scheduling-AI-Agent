import pandas as pd
import os
from datetime import datetime, timedelta

class ReminderTool:
    def __init__(self, appointments_file="data/appointments.csv", reminder_file="data/reminders.csv"):
        self.appointments_file = appointments_file
        self.reminder_file = reminder_file

    def create_reminders(self, appointment_id, patient_email, patient_phone):
        if not os.path.exists(self.appointments_file):
            return {"status": "error", "message": "Appointments file not found"}

        df = pd.read_csv(self.appointments_file)
        appt = df[df["appointment_id"] == appointment_id]
        if appt.empty:
            return {"status": "error", "message": "Appointment not found"}

        reminders = []
        base_time = datetime.now()
        times = [
            base_time + timedelta(days=1),
            base_time + timedelta(hours=6),
            base_time + timedelta(hours=1)
        ]
        for i, t in enumerate(times, 1):
            reminders.append({
                "appointment_id": appointment_id,
                "reminder_number": i,
                "send_time": t.isoformat(),
                "email": patient_email,
                "phone": patient_phone,
                "status": "scheduled"
            })

        reminder_df = pd.DataFrame(reminders)
        if os.path.exists(self.reminder_file):
            reminder_df.to_csv(self.reminder_file, mode="a", header=False, index=False)
        else:
            reminder_df.to_csv(self.reminder_file, index=False)

        return {"status": "scheduled", "reminders": reminders}
