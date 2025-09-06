import os
import shutil

class FormDistributionTool:
    def __init__(self, forms_dir="data/forms", sent_dir="data/forms_sent"):
        self.forms_dir = forms_dir
        self.sent_dir = sent_dir
        os.makedirs(sent_dir, exist_ok=True)

    def send_form(self, patient_email, appointment_id):
        src = os.path.join(self.forms_dir, "intake_form.pdf")
        dest = os.path.join(self.sent_dir, f"{appointment_id}_intake_form.pdf")
        shutil.copy(src, dest)
        return {
            "status": "sent",
            "message": f"Intake form sent to {patient_email}",
            "file_path": dest
        }
