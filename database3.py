import streamlit as st
import smtplib
from datetime import datetime
import pandas as pd
from streamlit_option_menu import option_menu
import os


col1, col2, col3, col4 = st.columns([1, 1, 4, 1])
with col1:
    st.write("")
with col2:
    st.write("")
with col3:
    st.image("wingate.png", width=150, use_column_width=False, output_format='auto')
with col4:
    st.write("")

def primary():
    school_attendance_app("Primary School Attendance", "primary_students_database.xlsx", "primary_attendance_log.csv")

def secondary():
    school_attendance_app("Secondary School Attendance", "secondary_students_database.xlsx", "secondary_attendance_log.csv")

def school_attendance_app(title, database_file, attendance_log_file):
    # Read the existing database from Excel file or create an empty DataFrame if the file doesn't exist
    try:
        df = pd.read_excel(database_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Name", "PIN", "Parent Email"])

    # Convert columns to strings
    df = df.astype(str)

    # Initialize session state variables if not already initialized
    if 'children_database' not in st.session_state:
        st.session_state.children_database = df

    # Admin password
    admin_password = "admin123"

    def send_email(recipient_email, child_name, action):
        sender_email = "tuwa.1simon@gmail.com"  # Replace with your email
        sender_password = "rglz olty qhds ijcn"  # Replace with your password

        try:
            # Set up the SMTP server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            # Log in to your email account
            server.login(sender_email, sender_password)
            # Compose the email
            subject = f"Child {action.capitalize()} Confirmation"
            body = f"Your child, {child_name}, has been {action} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
            message = f"Subject: {subject}\n\n{body}"
            # Send the email
            server.sendmail(sender_email, recipient_email, message)
            st.success(f"Email sent successfully for {action}!")
        except Exception as e:
            st.error(f"An error occurred while sending email for {action}: Check Internet Connection")
        finally:
            # Close the connection to the SMTP server
            server.quit()

    def add_student(df, name, pin, parent_email):
        if not df[df["PIN"] == pin].empty:
            st.error("Student already exists.")
        else:
            new_student = pd.DataFrame({"Name": [name], "PIN": [pin], "Parent Email": [parent_email]})
            df = pd.concat([df, new_student], ignore_index=True)
            df.to_excel(database_file, index=False)
            st.session_state.children_database = df  # Update session state
            st.success("Student added successfully.")

    def remove_student(df, name):
        if not df[df["Name"] == name].empty:
            df = df[df["Name"] != name].reset_index(drop=True)
            df.to_excel(database_file, index=False)
            st.session_state.children_database = df  # Update session state
            st.success("Student removed successfully.")
        else:
            st.error("Student not found.")

    def edit_student(df, old_name, new_name, new_pin, new_email):
        if not df[df["Name"] == old_name].empty:
            df.loc[df["Name"] == old_name, ["Name", "PIN", "Parent Email"]] = new_name, new_pin, new_email
            df.to_excel(database_file, index=False)
            st.session_state.children_database = df  # Update session state
            st.success("Student information updated successfully.")
        else:
            st.error("Student not found.")

    def log_attendance(name, pin, action, attendance_log_file):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        attendance_log = pd.DataFrame({"Name": [name], "PIN": [pin], "Action": [action], "DateTime": [now]})
        attendance_log.to_csv(attendance_log_file, mode='a', header=not st.session_state.log_file_exists, index=False)
        st.session_state.log_file_exists = True

    # Initialize log_file_exists flag
    if 'log_file_exists' not in st.session_state:
        st.session_state.log_file_exists = False

    # Check if secondary attendance log file exists, if not, create it with headers
    if not os.path.isfile(attendance_log_file):
        with open(attendance_log_file, "w") as file:
            file.write("Name,PIN,Action,DateTime\n")

    # Streamlit UI
    st.title(title)

    # Sidebar
    with st.sidebar:
        selected = option_menu(menu_title='Main Menu',
                               options=['Attendance', 'View Report', 'Admin'],
                               icons=['calendar3', 'clipboard-data', 'person-check']
                               )

    # Attendance Functionality
    if selected == "Attendance":
        child_pin = st.text_input("Enter Child's PIN:")

        if st.button("Sign In"):
            # Check if PIN exists in the database
            if df["PIN"].isin([child_pin]).any():
                student_data = df[df["PIN"] == child_pin]
                child_name = student_data.iloc[0]["Name"]
                send_email(student_data.iloc[0]["Parent Email"], child_name, "sign in")
                st.success(
                    f"{child_name} signed in successfully! Email sent to {student_data.iloc[0]['Parent Email']}.")
                log_attendance(child_name, int(child_pin), "Sign In", attendance_log_file)
            else:
                st.error("Invalid PIN. Please enter a valid PIN.")

        if st.button("Sign Out"):
            # Check if PIN exists in the database
            if df["PIN"].isin([child_pin]).any():
                student_data = df[df["PIN"] == child_pin]
                child_name = student_data.iloc[0]["Name"]
                send_email(student_data.iloc[0]["Parent Email"], child_name, "sign out")
                st.success(
                    f"{child_name} signed out successfully! Email sent to {student_data.iloc[0]['Parent Email']}.")
                log_attendance(child_name, int(child_pin), "Sign Out", attendance_log_file)
            else:
                st.error("Invalid PIN. Please enter a valid PIN.")

    # View Report Functionality
    elif selected == "View Report":
        st.subheader("View Report")
        child_pin = st.text_input("Enter Child's PIN:")

        if st.button("Generate Report"):
            try:
                attendance_log = pd.read_csv(attendance_log_file)
                child_attendance = attendance_log[attendance_log["PIN"] == int(child_pin)]
                if not child_attendance.empty:
                    st.write(f"Attendance Report for Child with PIN {child_pin}:")
                    st.write(child_attendance)
                else:
                    st.write("No attendance records found for this child.")
            except FileNotFoundError:
                st.error("Attendance records not found.")

    # Admin Functionality
    elif selected == "Admin":
        # Password protection
        password = st.text_input("Enter Admin Password:", type="password")
        if password == admin_password:
            st.subheader("Admin Panel")
            action = st.selectbox("Select Action:", options=["Add Student", "Remove Student", "Edit Student", "View Report"])
            if action == "Add Student":
                new_name = st.text_input("Enter Student's Name:")
                new_pin = st.text_input("Enter Student's PIN:")
                new_email = st.text_input("Enter Parent's Email:")
                if st.button("Add Student"):
                    add_student(df, new_name, new_pin, new_email)
            elif action == "Remove Student":
                remove_name = st.selectbox("Select Student to Remove:",
                                           options=list(st.session_state.children_database["Name"]))
                if st.button("Remove Student"):
                    remove_student(df, remove_name)
            elif action == "Edit Student":
                st.subheader("Edit Student")
                if category == "Primary School":
                    try:
                        primary_students_df = pd.read_excel("primary_students_database.xlsx")
                    except FileNotFoundError:
                        primary_students_df = pd.DataFrame(columns=["Name", "PIN", "Parent Email"])
                    if not primary_students_df.empty:
                        edit_name = st.selectbox("Select Student to Edit:",
                                                 options=list(primary_students_df["Name"]))
                    else:
                        st.warning("No students available for editing in the primary school.")
                        return
                elif category == "Secondary School":
                    try:
                        secondary_students_df = pd.read_excel("secondary_students_database.xlsx")
                    except FileNotFoundError:
                        secondary_students_df = pd.DataFrame(columns=["Name", "PIN", "Parent Email"])
                    if not secondary_students_df.empty:
                        edit_name = st.selectbox("Select Student to Edit:",
                                                 options=list(secondary_students_df["Name"]))
                    else:
                        st.warning("No students available for editing in the secondary school.")
                        return
                if not edit_name:
                    st.warning("Please select a student to edit.")
                    return
                new_name = st.text_input("Enter New Name:",
                                         value=edit_name)
                new_pin = st.text_input("Enter New PIN:",
                                        value=primary_students_df.loc[primary_students_df["Name"] == edit_name, "PIN"].iloc[0] if category == "Primary School" else
                                              secondary_students_df.loc[secondary_students_df["Name"] == edit_name, "PIN"].iloc[0])
                new_email = st.text_input("Enter New Parent's Email:",
                                          value=primary_students_df.loc[primary_students_df["Name"] == edit_name, "Parent Email"].iloc[0] if category == "Primary School" else
                                                secondary_students_df.loc[secondary_students_df["Name"] == edit_name, "Parent Email"].iloc[0])
                if st.button("Save Changes"):
                    if category == "Primary School":
                        edit_student(primary_students_df, edit_name, new_name, new_pin, new_email)
                    elif category == "Secondary School":
                        edit_student(secondary_students_df, edit_name, new_name, new_pin, new_email)
            elif action == "View Report":
                st.subheader("View Report")
                try:
                    attendance_log = pd.read_csv(attendance_log_file)
                    st.write("Attendance Log:")
                    st.write(attendance_log)
                except FileNotFoundError:
                    st.error("Attendance records not found.")
        else:
            st.error("Invalid password. Please try again.")

# Run the app
if __name__ == "__main__":
    st.sidebar.title("Choose Category")
    category = st.sidebar.radio("Select Category:", ("Primary School", "Secondary School"))

    if category == "Primary School":
        primary()
    elif category == "Secondary School":
        secondary()
