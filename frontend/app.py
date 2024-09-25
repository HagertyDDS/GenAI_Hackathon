
import streamlit as st
import psycopg2
import time  # Used to simulate delay for testing
from streamlit_ace import st_ace


# Initialize session state variables for connection status, dialog visibility, and loading state
if 'db_status' not in st.session_state:
    st.session_state.db_status = 'not_tried'  # Other values: 'connected', 'failed'
if 'show_dialog' not in st.session_state:
    st.session_state.show_dialog = False
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False  # Tracks the connection loading state

def connect_to_postgres(host, port, dbname, user, password):
    try:
        # Simulate a connection delay (for demo purposes)
        time.sleep(2)
        connection = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        st.session_state.db_status = 'connected'
        st.success("Successfully connected to the PostgreSQL database!")
        # Force a rerun to immediately update the button text
        st.rerun()
        return connection
    except Exception as e:
        st.session_state.db_status = 'failed'
        st.error(f"Error connecting to database: {e}")
        # Force a rerun to immediately update the button text
        st.rerun()
        return None

@st.dialog("Connect to PostgreSQL")
def postgres_connection_dialog():
    # Collect connection details in the dialog
    host = st.text_input("Host", "localhost")
    port = st.number_input("Port", value=5432, min_value=1, max_value=65535)
    dbname = st.text_input("Database Name")
    user = st.text_input("User")
    password = st.text_input("Password", type="password")

    # Button to attempt the connection
    if st.button("Connect"):
        # Set loading state to True
        st.session_state.is_loading = True

        # Use spinner to show loading while connecting
        with st.spinner("Connecting to database..."):
            connect_to_postgres(host, port, dbname, user, password)
        
        # Set loading state to False after attempt
        st.session_state.is_loading = False

        # Close the dialog after the connection attempt
        if st.session_state.db_status != 'not_tried':
            st.session_state.show_dialog = False
    
    # Display the current connection status under the Connect button
    if st.session_state.db_status == 'not_tried':
        st.write("Database not connected.")
    elif st.session_state.db_status == 'connected':
        st.write("✅ Database connected successfully!")
    elif st.session_state.db_status == 'failed':
        st.write("❌ Database connection failed. Please check your credentials.")



def automl_settings_section():
    st.sidebar.header("AutoML Settings")
    
    # Placeholder inputs for the AutoML settings section
    st.sidebar.selectbox("Model Type", ["Random Forest", "XGBoost", "Neural Network"])
    st.sidebar.slider("Max Iterations", 1, 100, 10)
    st.sidebar.number_input("Learning Rate", min_value=0.001, max_value=1.0, value=0.01, step=0.001)
    st.sidebar.checkbox("Use Cross Validation", value=True)
    st.sidebar.selectbox("Optimization Metric", ["Accuracy", "Precision", "Recall"])
    st.sidebar.radio("Enable Feature Scaling", ["Yes", "No"])

    # Dummy button for training the model
    if st.sidebar.button("Train Model"):
        # Currently, this button does nothing
        pass



# Section 1: User Input
def user_input_section(id):
    st.subheader(f"User Input Section {id}")
    
    # Text input for Feature Title
    feature_title = st.text_input(f"Feature Title ({id}):", key=f"feature_title_{id}")
    
    # Text area for Feature Description
    feature_description = st.text_area(f"Feature Description ({id}):", key=f"feature_description_{id}")
    
    return feature_title, feature_description

# Section 2: Code Generation
def code_generation_section(feature_title, feature_description, id):
    st.subheader(f"Generated Code Section {id}")
    
    # Generate the Python function with title and description
    generated_code = f"""
def {feature_title}():
    \"\"\"{feature_description}\"\"\"
    # Placeholder function
    return 0
"""
    return generated_code

# Section 3: Code Editor
def code_editor_section(generated_code, id):
    st.subheader(f"Code Editor Section {id}")
    
    # Display editable code using Streamlit Ace
    edited_code = st_ace(value=generated_code, language='python', theme='monokai', height=200, key=f"editor_{id}")
    return edited_code

# Function to create multiple components dynamically
def create_input_code_pair(id):
    # Get the feature title and description from the user
    feature_title, feature_description = user_input_section(id)
    
    if feature_title and feature_description:
        # Generate the code based on the inputs
        generated_code = code_generation_section(feature_title, feature_description, id)
    
        # Display and edit code in a code editor
        edited_code = code_editor_section(generated_code, id)
    
        # Display the final edited code
        st.subheader(f"Final Code After Editing {id}:")
        st.code(edited_code, language='python')




def main():
    st.title("GenAI Hackathon - Streamlit Frontend")
    st.write("Frontend of our Generative AI project")

    num_sections = 5
    for i in range(1, num_sections + 1):
        create_input_code_pair(i)
        st.markdown("---")  # Divider between sections

    

    # Determine the button color and text based on the connection status
    if st.session_state.db_status == 'not_tried':
        button_text = "Database not connected"
        button_color = "orange"
    elif st.session_state.db_status == 'connected':
        button_text = "Database connected"
        button_color = "green"
    elif st.session_state.db_status == 'failed':
        button_text = "Database connection failed"
        button_color = "red"

    # Display the connection status button in the sidebar
    if st.sidebar.button(button_text, key="db_status_button", help="Check or change DB connection status"):
        # Open the dialog when the button is clicked
        st.session_state.show_dialog = True

    # Dialog for PostgreSQL connection details
    if st.session_state.show_dialog:
        postgres_connection_dialog()
        # Reset show_dialog after showing it once to avoid re-triggering
        st.session_state.show_dialog = False


    # AutoML settings section in the sidebar
    automl_settings_section()

if __name__ == "__main__":
    main()

