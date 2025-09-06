import pandas as pd
import os

class BookSlotTool:
    def __init__(self, schedule_file="data/doctor_schedules.xlsx", appointments_file="data/appointments.csv"):
        self.schedule_file = schedule_file
        self.appointments_file = appointments_file

    def book(self, slot_id, patient_id, patient_name, reason="Consultation"):
        df = pd.read_excel(self.schedule_file, sheet_name="schedules")
        idx = df.index[df["slot_id"] == slot_id].tolist()
        if not idx:
            return {"status": "error", "message": "Slot not found"}
        if df.at[idx[0], "is_booked"]:
            return {"status": "error", "message": "Slot already booked"}

        # mark slot booked
        df.at[idx[0], "is_booked"] = True
        with pd.ExcelWriter(self.schedule_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df.to_excel(writer, sheet_name="schedules", index=False)

        # create appointment record
        appt = {
            "appointment_id": f"A_{slot_id}",
            "slot_id": slot_id,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "booked_at": pd.Timestamp.now().isoformat(),
            "reason": reason,
        }
        appt_df = pd.DataFrame([appt])
        if os.path.exists(self.appointments_file):
            appt_df.to_csv(self.appointments_file, mode="a", header=False, index=False)
        else:
            appt_df.to_csv(self.appointments_file, index=False)

        return {"status": "booked", "appointment": appt}
