import pandas as pd

class PatientLookupTool:
    def __init__(self, patient_file="data/patients.csv"):
        self.df = pd.read_csv(patient_file)
        self.patient_file = patient_file

    def lookup(self, name=None, dob=None):
        df = self.df.copy()
        if name:
            df = df[df["full_name"].str.lower().str.contains(name.lower())]
        if dob:
            df = df[df["dob"] == dob]

        if df.empty:
            return {"status": "new_patient"}
        return {"status": "found", "patient": df.iloc[0].to_dict()}
