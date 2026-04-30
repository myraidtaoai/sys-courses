import csv
import os
from local_database_ops import LocalDatabaseManager


def create_test_dataset():
    # Create a connection to the local database by using LocalDatabaseManager

    output_dir = "database"
    os.makedirs(output_dir, exist_ok=True)
    # db_path = os.path.join(output_dir, "health_informative.db")
    db_path = "health_informative.db"
    
    # Remove existing db if it exists to start fresh
    if os.path.exists(db_path):
        os.remove(db_path)

    db_manager = LocalDatabaseManager(db_name=db_path)

    # 1. table: patient_info
    patient_headers = [
        "patient_id", "FName", "MName", "LName", "Age", "BloodGroup", "Gender", "height", "weight", 
        "race", "MobileNumber", "EmailId", "Address", "Location", "City", "Province", 
        "PostalCode", "Latitude", "Longitude", "HCardNumber", "PassportNumber", "PRNumber", 
        "DLNumber", "uuid",  "verification", "date_of_birth"
    ]
    
    patient_schema = {
        "patient_id": "TEXT PRIMARY KEY",
        "FName": "TEXT",
        "MName": "TEXT",
        "LName": "TEXT",
        "Age": "INTEGER",
        "BloodGroup": "TEXT",
        "Gender": "TEXT",
        "height": "REAL",
        "weight": "REAL",
        "race": "TEXT",
        "MobileNumber": "INTEGER",
        "EmailId": "TEXT",
        "Address": "TEXT",
        "Location": "TEXT",
        "City": "TEXT",
        "Province": "TEXT",
        "PostalCode": "TEXT",
        "Latitude": "REAL",
        "Longitude": "REAL",
        "HCardNumber": "TEXT",
        "PassportNumber": "TEXT",
        "PRNumber": "TEXT",
        "DLNumber": "TEXT",
        "uuid": "TEXT",
        "verification": "INTEGER",
        "date_of_birth": "TEXT"
    }
    db_manager.create_table("patient_info", patient_schema)

    patients = [
        ["p_1001", "John", "A", "Doe", 35, "O+", "Male", 180, 80, "White", 6131230001, "john.doe@test.com", "123 Main St", "Apt 1", "Ottawa", "Ontario", "K1A 0B1", 45.4215, -75.6972, "HC001", "PASS001", "PR001", "DL001", "PAT-001", 1, "1989-01-01"],
        ["p_1002", "Jane", "B", "Smith", 28, "A-", "Female", 165, 60, "Asian", 6131230002, "jane.smith@test.com", "456 Oak Ave", "Unit 2", "Ottawa", "Ontario", "K1A 0B2", 45.4216, -75.6973, "HC002", "PASS002", "PR002", "DL002", "PAT-002" , 1, "1995-05-15"],
        ["p_1003", "Bob", "C", "Jones", 45, "B+", "Male", 175, 85, "Black", 6131230003, "bob.jones@test.com", "789 Pine Rd", "", "Ottawa", "Ontario", "K1A 0B3", 45.4217, -75.6974, "HC003", "PASS003", "PR003", "DL003", "PAT-003", 1, "1979-11-20"],
        ["p_1004", "Alice", "D", "Brown", 52, "AB-", "Female", 170, 70, "White", 6131230004, "alice.brown@test.com", "321 Elm St", "Bsmt", "Ottawa", "Ontario", "K1A 0B4", 45.4218, -75.6975, "HC004", "PASS004", "PR004", "DL004", "PAT-004", 1, "1972-03-10"],
        ["p_1005", "Charlie", "E", "Snow", 30, "O-", "Male", 178, 75, "Asian", 6131230005, "charlie.snow@test.com", "654 Cedar Ln", "Apt 3", "Ottawa", "Ontario", "K1A 0B5", 45.4219, -75.6976, "HC005", "PASS005", "PR005", "DL005", "PAT-005", 1, "1993-07-05"]
    ]

    for patient in patients:
        data = dict(zip(patient_headers, patient))
        db_manager.insert_record("patient_info", data)
    print(f"Inserted {len(patients)} records into patient_info")

    # 2. table : doctor_info
    doctors_headers = ["doctor_id", "FName", "MName", "LName", "Specialization", "phone", "email", "office_address"]
    
    doctor_schema = {
        "doctor_id": "TEXT PRIMARY KEY",
        "FName": "TEXT",
        "MName": "TEXT",
        "LName": "TEXT",
        "Specialization": "TEXT",
        "phone": "INTEGER",
        "email": "TEXT",
        "office_address": "TEXT"
    }
    db_manager.create_table("doctor_info", doctor_schema)

    doctors = [
        ["d_101", "Dr. Alice", "M", "Wonder", "General Practitioner", 6135559999, "alice.wonder@test.com", "101 Clinic Way"],
        ["d_102", "Dr. Bob", "N", "Builder", "Cardiologist", 6135558888, "bob.builder@test.com", "202 Hospital Blvd"],
        ["d_103", "Dr. Charlie", "O", "Chaplin", "Dermatologist", 6135557777, "charlie.chaplin@test.com", "303 Health St"]
    ]

    for doctor in doctors:
        data = dict(zip(doctors_headers, doctor))
        db_manager.insert_record("doctor_info", data)
    print(f"Inserted {len(doctors)} records into doctor_info")

    # 3. table: patient_treatment
    treatment_headers = ["id", "patient_id", "doctor_id", "treatment", "dose","RecordDate", "disease_type", "disease_id"]
    
    treatment_schema = {
        "id": "INTEGER PRIMARY KEY",
        "patient_id": "TEXT",
        "doctor_id": "TEXT",
        "treatment": "TEXT",
        "dose": "TEXT",
        "RecordDate": "TEXT",
        "disease_type": "TEXT",
        "disease_id": "INTEGER"
    }
    db_manager.create_table("patient_treatment", treatment_schema)
    
    treatments = [
        [1, "p_1001", "d_101", "Ibuprofen", "10mg","2024-01-15", "Pain", 1],
        [2, "p_1001", "d_101", "Physiotherapy", "", "2024-01-20", "Back Pain", 2],
        [3, "p_1002", "d_102", "Amoxicillin", "10mg", "2024-02-10", "Infection", 3],
        [4, "p_1003", "d_103", "Insulin", "1units", "2024-03-05", "Diabetes", 4],
        [5, "p_1003", "d_103", "Metformin", "10mg", "2024-03-05", "Diabetes", 4],
        [6, "p_1004", "d_101", "Aspirin","10mg", "2024-04-12", "Heart Disease", 5],
        [7, "p_1005", "d_102", "Lisinopril", "5mg", "2024-05-01", "Hypertension", 6],
        [8, "p_1001", "d_101", "Ibuprofen", "5mg", "2024-06-15", "Pain", 1],
        [9, "p_1002", "d_102", "Amoxicillin", "10mg", "2024-02-10", "Infection", 3],
        [10, "p_1003", "d_103", "Insulin", "1units", "2024-03-05", "Diabetes", 4],
        [11, "p_1004", "d_101", "Aspirin","10mg", "2024-04-12", "Heart Disease", 5],
        [12, "p_1005", "d_102", "Lisinopril","5mg", "2024-05-01", "Hypertension", 6],
        [13, "p_1001", "d_101", "Ibuprofen","5mg", "2024-06-15", "General", 7]
    ]

    for treatment in treatments:
        data = dict(zip(treatment_headers, treatment))
        db_manager.insert_record("patient_treatment", data)
    print(f"Inserted {len(treatments)} records into patient_treatment")

    # 4. table: patient_prescription
    prescription_headers = [
        "id", "patient_id", "doctor_id", "prescription_description", "prescription_creation_time", 
        "medicine_id", "dose", "dose_unit", "frequency", "duration", "route", "quantity", 
        "quantity_unit", "refill", "diagnosis_id", "pharmacist_permission"
    ]
    
    prescription_schema = {
        "id": "INTEGER PRIMARY KEY",
        "patient_id": "TEXT",
        "doctor_id": "TEXT",
        "prescription_description": "TEXT",
        "prescription_creation_time": "TEXT",
        "medicine_id": "INTEGER",
        "dose": "REAL",
        "dose_unit": "TEXT",
        "frequency": "TEXT",
        "duration": "TEXT",
        "route": "TEXT",
        "quantity": "INTEGER",
        "quantity_unit": "TEXT",
        "refill": "INTEGER",
        "diagnosis_id": "INTEGER",
        "pharmacist_permission": "INTEGER"
    }
    db_manager.create_table("patient_prescription", prescription_schema)

    prescriptions = [
        [1, "p_1001", "d_101", "Pain relief", "2024-01-15", 10, 400, "mg", "Twice daily", "7 days", "Oral", 14, "Pills", 0, 1, 1],
        [2, "p_1002", "d_102", "Antibiotic", "2024-02-10", 20, 500, "mg", "Three times daily", "10 days", "Oral", 30, "Capsules", 0, 3, 1],
        [3, "p_1003", "d_103", "Diabetes management", "2024-03-05", 30, 10, "units", "Once daily", "30 days", "Injection", 30, "Vials", 3, 4, 1],
        [4, "p_1004", "d_101", "Heart health", "2024-04-12", 40, 81, "mg", "Once daily", "90 days", "Oral", 90, "Tablets", 1, 5, 1],
        [5, "p_1005", "d_102", "Blood pressure control", "2024-05-01", 50, 10, "mg", "Once daily", "30 days", "Oral", 30, "Tablets", 0, 6, 1]
    ]
    
    for prescription in prescriptions:
        data = dict(zip(prescription_headers, prescription))
        db_manager.insert_record("patient_prescription", data)
    print(f"Inserted {len(prescriptions)} records into patient_prescription")

    # 5. table: checkup_info
    checkup_headers = ["checkup_id", "patient_id", "doctor_id", "checkup_date", "weight", "height", "blood_pressure", "heart_rate", "temperature"]
    
    checkup_schema = {
        "checkup_id": "INTEGER PRIMARY KEY",
        "patient_id": "TEXT",
        "doctor_id": "TEXT",
        "checkup_date": "TEXT",
        "weight": "REAL",
        "height": "REAL",
        "blood_pressure": "TEXT",
        "heart_rate": "INTEGER",
        "temperature": "REAL"
    }
    db_manager.create_table("checkup_info", checkup_schema)

    checkups = [
        [1, "p_1001", "d_101", "2024-01-15", 80, 180, "120/80", 72, 36.5],
        [2, "p_1002", "d_102", "2024-02-10", 75, 175, "110/70", 68, 36.2],
        [3, "p_1003", "d_103", "2024-03-05", 90, 178, "130/85", 75, 36.8],
        [4, "p_1004", "d_101", "2024-04-12", 85, 176, "125/80", 70, 36.4],
        [5, "p_1005", "d_102", "2024-05-01", 78, 172, "128/82", 69, 36.6]
    ]

    for checkup in checkups:
        data = dict(zip(checkup_headers, checkup))
        db_manager.insert_record("checkup_info", data)
    print(f"Inserted {len(checkups)} records into checkup_info")

    # 6. table: patient_pathology_reports
    pathology_headers = ["report_id", "patient_id", "report_date", "report_type", "findings", "doctor_id"]
    pathology_schema = {
        "report_id": "INTEGER PRIMARY KEY",
        "patient_id": "TEXT",
        "report_date": "TEXT",
        "report_type": "TEXT",
        "findings": "TEXT",
        "doctor_id": "TEXT"
    }
    db_manager.create_table("patient_pathology_reports", pathology_schema)
    pathology_reports = [
        [1, "p_1001", "2024-01-16", "Blood Test", "Normal", "d_101"],
        [2, "p_1002", "2024-02-11", "X-Ray", "Minor fracture", "d_102"],
        [3, "p_1003", "2024-03-06", "MRI", "No abnormalities", "d_103"],
        [4, "p_1004", "2024-04-13", "CT Scan", "Mild inflammation", "d_101"],
        [5, "p_1005", "2024-05-02", "Ultrasound", "Normal", "d_102"]
    ]
    for report in pathology_reports:
        data = dict(zip(pathology_headers, report))
        db_manager.insert_record("patient_pathology_reports", data)
    print(f"Inserted {len(pathology_reports)} records into patient_pathology_reports")


if __name__ == "__main__":
    create_test_dataset()
