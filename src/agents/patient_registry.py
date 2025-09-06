import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
PATIENTS_CSV = DATA_DIR / "patients.csv"

class PatientRegistry:
    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)
        if PATIENTS_CSV.exists():
            self.df = pd.read_csv(PATIENTS_CSV)
        else:
            self.df = pd.DataFrame(columns=[
                "patient_id", "full_name", "dob", "email", "phone", "preferred_doctor_id"
            ])

    def save(self):
        self.df.to_csv(PATIENTS_CSV, index=False)

    def lookup(self, patient_id=None, email=None):
        if patient_id:
            row = self.df[self.df["patient_id"] == patient_id]
        elif email:
            row = self.df[self.df["email"] == email]
        else:
            return None
        if not row.empty:
            return row.iloc[0].to_dict()
        return None

    def add_patient(self, patient: dict):
        self.df = pd.concat([self.df, pd.DataFrame([patient])], ignore_index=True)
        self.save()
        return patient
