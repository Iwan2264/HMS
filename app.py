import streamlit as st
import json
import pandas as pd
import os
import csv
from datetime import datetime

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'directory'
if 'selected_doctor' not in st.session_state:
    st.session_state.selected_doctor = None
if 'booking' not in st.session_state:
    st.session_state.booking = False
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# Load doctors data
with open('doctors.json', 'r', encoding='utf-8') as f:
    doctors = json.load(f)

# Save appointment
def save_appointment(patient_name, age, contact, date, time, symptoms, doctor_name):
    symptoms = symptoms.replace(',', ';')
    data = {
        'Patient_Name': [patient_name],
        'Age': [age],
        'Contact': [contact],
        'Date': [date],
        'Time': [time],
        'Symptoms': [symptoms],
        'Doctor': [doctor_name]
    }
    df = pd.DataFrame(data)
    if os.path.exists('appointments.csv'):
        df.to_csv('appointments.csv', mode='a', header=False, index=False, quoting=csv.QUOTE_MINIMAL)
    else:
        df.to_csv('appointments.csv', mode='w', header=True, index=False, quoting=csv.QUOTE_MINIMAL)

# Top Navigation
def top_nav():
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Doctor Directory"):
            st.session_state.page = 'directory'
            st.rerun()
    with col2:
        if st.button("Admin Panel"):
            st.session_state.page = 'admin'
            st.rerun()

# Doctor Directory Page
def show_directory():
    st.title("Doctor Directory")
    for doctor in doctors:
        with st.container():
            st.markdown(f"""
                <div style='border:1px solid #ddd; padding:15px; border-radius:10px;'>
                    <h4>{doctor['name']}</h4>
                    <p><b>Specialization:</b> {doctor['specialization']}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("View Details", key=f"view_{doctor['id']}"):
                st.session_state.selected_doctor = doctor
                st.session_state.page = 'profile'
                st.rerun()

# Doctor Profile Page
def show_profile():
    doctor = st.session_state.selected_doctor
    st.title(f"Dr. {doctor['name']}'s Profile")
    st.markdown(f"**Specialization:** {doctor['specialization']}")
    st.markdown(f"**Qualifications:** {doctor['qualifications']}")
    st.markdown(f"**Experience:** {doctor['experience']} years")
    st.markdown(f"**Availability:** {doctor['availability']}")
    st.markdown(f"**Bio:** {doctor['bio']}")

    if st.button("Book Appointment"):
        st.session_state.booking = True
        st.session_state.page = 'booking'
        st.rerun()
    if st.button("Back to Directory"):
        st.session_state.page = 'directory'
        st.session_state.selected_doctor = None
        st.rerun()

# Booking Page
def show_booking():
    doctor = st.session_state.selected_doctor
    st.title(f"Book Appointment with Dr. {doctor['name']}")

    with st.form("appointment_form"):
        patient_name = st.text_input("Patient Name")
        age = st.number_input("Age", min_value=0, max_value=120)
        contact = st.text_input("Contact Info (Phone/Email)")
        date = st.date_input("Preferred Date")
        time = st.time_input("Preferred Time")
        symptoms = st.text_area("Symptoms / Reason for Visit")
        submitted = st.form_submit_button("Submit Appointment")

        if submitted:
            if patient_name and age and contact and symptoms:
                save_appointment(patient_name, age, contact, date, time, symptoms, doctor['name'])
                st.success("Appointment booked successfully!")
                st.session_state.page = 'directory'
                st.session_state.booking = False
                st.session_state.selected_doctor = None
                st.rerun()
            else:
                st.error("Please fill in all fields.")

    if st.button("Back to Profile"):
        st.session_state.page = 'profile'
        st.session_state.booking = False
        st.rerun()

# Admin Login and Panel
def admin_panel():
    if not st.session_state.admin_logged_in:
        st.title("Admin Login")
        user = st.text_input("User ID")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "admin" and pwd == "admin123":
                st.session_state.admin_logged_in = True
                st.success("Login successful!")
                st.session_state.page = 'admin'
                st.rerun()
            else:
                st.error("Invalid credentials")
    else:
        st.title("Admin Panel")
        if os.path.exists("appointments.csv"):
            try:
                df = pd.read_csv("appointments.csv", quoting=csv.QUOTE_MINIMAL)
                st.subheader("All Appointments")
                st.dataframe(df)
            except Exception as e:
                st.error(f"Error reading appointments.csv: {e}")
        else:
            st.info("No appointments found.")

        if st.button("Go to Discharge Summary"):
            st.markdown("[Open Discharge Summary Generator](https://discharge-summary-generator.streamlit.app/)", unsafe_allow_html=True)

        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.session_state.page = 'directory'  # Redirect back to directory after logout
            st.rerun()

# Main App Logic
def main():
    top_nav()

    if st.session_state.page == 'directory':
        show_directory()
    elif st.session_state.page == 'profile':
        show_profile()
    elif st.session_state.page == 'booking':
        show_booking()
    elif st.session_state.page == 'admin':
        admin_panel()

if __name__ == "__main__":
    main()
