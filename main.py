import streamlit as st
from ui_module import patient_form
from data_module import save_record, load_records

def main():
    st.title("Physiotherapy Post-Op Assistant")

    menu = st.sidebar.selectbox("Menu", ["New Patient Entry", "View Saved Records"])

    if menu == "New Patient Entry":
        record = patient_form()
        if record:
            save_record(record)
            st.success("Patient record saved successfully!")

    elif menu == "View Saved Records":
        records = load_records()
        st.write("### Saved Records")
        st.dataframe(records)

if __name__ == "__main__":
    main()
