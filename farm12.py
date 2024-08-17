import streamlit as st
import pandas as pd
import random
import pyodbc
from twilio.rest import Client

# Twilio configuration
account_sid = 'AC2c5d74e8b6e15f0a25efc95ec5f9d252'
auth_token = 'b6940fb67241d24b3f37677d5b8c11a4'
twilio_phone_number = '+13344686964'

client = Client(account_sid, auth_token)

# MSSQL connection configuration
conn_str = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=DESKTOP-CEIB8QQ\NIRAJ;'
    r'DATABASE=ContractFarming;'
    r'Trusted_Connection=yes;'
)

# Function to get database connection
def get_connection():
    return pyodbc.connect(conn_str)

# Function to send OTP via SMS
def send_otp(phone_number):
    if not phone_number.startswith("+"):
        phone_number = "+91" + phone_number[-10:]  # Assuming Indian numbers
    
    otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
    client.messages.create(
        body=f"Your OTP is {otp}",
        from_=twilio_phone_number,
        to=phone_number
    )
    return otp

# Function to insert a farmer
def insert_farmer(name, email, phone, location):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Farmers (Name, Email, Phone, Location) VALUES (?, ?, ?, ?)",
            (name, email, phone, location)
        )
        conn.commit()
        st.success("Farmer inserted successfully.")
    except Exception as e:
        st.error(f"Error inserting farmer: {e}")
    finally:
        conn.close()

# Function to insert Buyer data
def insert_buyer(name, email, phone, company):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Buyers (Name, Email, Phone, Company) VALUES (?, ?, ?, ?)",
            (name, email, phone, company)
        )
        conn.commit()
    except Exception as e:
        st.error(f"Error inserting buyer: {e}")
    finally:
        conn.close()

# Function to create a new Contract
def create_contract(buyer_id, crop, quantity, price, delivery_date):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Contracts (BuyerID, Crop, Quantity, Price, DeliveryDate) VALUES (?, ?, ?, ?, ?)",
            (buyer_id, crop, quantity, price, delivery_date)
        )
        conn.commit()
        st.success("Contract created successfully.")
    except Exception as e:
        st.error(f"Error creating contract: {e}")
    finally:
        conn.close()

# Function to insert Contract data
def insert_contract(buyer_id, crop, quantity, price, delivery_date):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Contracts (BuyerID, Crop, Quantity, Price, DeliveryDate) VALUES (?, ?, ?, ?, ?)",
            (buyer_id, crop, quantity, price, delivery_date)
        )
        conn.commit()
    except Exception as e:
        st.error(f"Error inserting contract: {e}")
    finally:
        conn.close()

# Function to insert a payment
def insert_payment(contract_id, amount, payment_date, status):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Payments (ContractID, Amount, PaymentDate, Status) VALUES (?, ?, ?, ?)",
            (contract_id, amount, payment_date, status)
        )
        conn.commit()
        st.success("Payment inserted successfully.")
    except Exception as e:
        st.error(f"Error inserting payment: {e}")
    finally:
        conn.close()

# Function to authenticate users
def authenticate_user(username, password, user_type):
    if user_type == "Farmer" and username == "farmer1" and password == "password":
        return True
    elif user_type == "Buyer" and username == "buyer1" and password == "password":
        return True
    return False

# Function to send notifications (for demo purposes)
def send_notification(user, message):
    st.info(f"Notification sent to {user}: {message}")

# Function to get real-time price updates (for demo purposes)
def get_real_time_price_update(crop):
    return {"Wheat": 16.0, "Corn": 19.5}.get(crop, "Price not available")

def execute_query(query, params):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
    except Exception as e:
        st.error(f"Database error: {e}")
    finally:
        conn.close()

# Streamlit UI
st.title("Assured Contract Farming Platform")

# Top Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Home"):
        st.session_state.page = "Home"

with col2:
    if st.button("Farmer"):
        st.session_state.page = "Farmer"

with col3:
    if st.button("Buyer"):
        st.session_state.page = "Buyer"
st.markdown("---")

# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Home Page
if st.session_state.page == "Home":
    st.header("Welcome to the Assured Contract Farming Platform")

    # User Authentication
    st.subheader("User Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    user_type = st.selectbox("User Type", ["Farmer", "Buyer"])

    if st.button("Login"):
        if authenticate_user(username, password, user_type):
            st.success(f"Welcome, {username}!")
        else:
            st.error("Invalid credentials")

# Farmer Page
elif st.session_state.page == "Farmer":
    st.header("Farmer Dashboard")

    # Farmer Registration with OTP Verification
    st.subheader("Register as a Farmer")
    with st.form("farmer_form"):
        farmer_name = st.text_input("Name")
        farmer_email = st.text_input("Email")
        farmer_phone = st.text_input("Phone")
        farmer_location = st.text_input("Location")
        
        if st.form_submit_button("Send OTP"):
            otp = send_otp(farmer_phone)
            st.session_state['otp'] = otp
            st.session_state['phone'] = farmer_phone
            st.session_state['name'] = farmer_name
            st.session_state['email'] = farmer_email
            st.session_state['location'] = farmer_location
            st.success(f"OTP sent to {farmer_phone}")

    if 'otp' in st.session_state:
        st.subheader("Verify OTP")
        user_otp = st.text_input("Enter OTP")
        
        if st.button("Verify OTP"):
            if int(user_otp) == st.session_state['otp']:
                insert_farmer(
                    st.session_state['name'],
                    st.session_state['email'],
                    st.session_state['phone'],
                    st.session_state['location']
                )
                st.success("OTP verified! Farmer registered successfully.")
                send_notification(st.session_state['name'], "Welcome to the platform!")
                del st.session_state['otp']
                del st.session_state['phone']
                del st.session_state['name']
                del st.session_state['email']
                del st.session_state['location']
            else:
                st.error("Invalid OTP. Please try again.")

    # Create Contract
    st.subheader("Create Contract")
    with st.form("contract_form"):
        # Sample data for demo purposes
        buyers_sample_data = pd.DataFrame({"Name": ["Buyer A", "Buyer B"]})
        buyer_id = st.selectbox("Select Buyer", buyers_sample_data["Name"].tolist())
        crop = st.text_input("Crop")
        quantity = st.number_input("Quantity (kg)", min_value=0.0, step=0.1)
        price = st.number_input("Price (per kg)", min_value=0.0, step=0.1)
        delivery_date = st.date_input("Delivery Date")
        real_time_price = get_real_time_price_update(crop)
        st.write(f"Real-time price for {crop}: {real_time_price}")
        if st.form_submit_button("Create Contract"):
            st.success(f"Contract for {crop} created successfully.")
            send_notification(farmer_name, f"New contract created for {crop}.")

    # View Contracts
    st.subheader("View Your Contracts")
    # Sample data for demo purposes
    contracts_sample_data = pd.DataFrame({"Farmer": ["John Doe"], "Crop": ["Wheat"], "Quantity": [100], "Price": [16.0]})
    st.dataframe(contracts_sample_data[contracts_sample_data["Farmer"] == "John Doe"])

# Buyer Page
elif st.session_state.page == "Buyer":
    st.header("Buyer Dashboard")

    # Buyer Registration with OTP Verification
    st.subheader("Register as a Buyer")
    with st.form("buyer_form"):
        buyer_name = st.text_input("Name")
        buyer_email = st.text_input("Email")
        buyer_phone = st.text_input("Phone")
        buyer_company = st.text_input("Company")
        
        if st.form_submit_button("Send OTP"):
            otp = send_otp(buyer_phone)
            st.session_state['otp'] = otp
            st.session_state['phone'] = buyer_phone
            st.session_state['name'] = buyer_name
            st.session_state['email'] = buyer_email
            st.session_state['company'] = buyer_company
            st.success(f"OTP sent to {buyer_phone}")

    if 'otp' in st.session_state:
        st.subheader("Verify OTP")
        user_otp = st.text_input("Enter OTP")
        
        if st.button("Verify OTP"):
            if int(user_otp) == st.session_state['otp']:
                insert_buyer(
                    st.session_state['name'],
                    st.session_state['email'],
                    st.session_state['phone'],
                    st.session_state['company']
                )
                st.success("OTP verified! Buyer registered successfully.")
                send_notification(st.session_state['name'], "Welcome to the platform!")
                del st.session_state['otp']
                del st.session_state['phone']
                del st.session_state['name']
                del st.session_state['email']
                del st.session_state['company']
            else:
                st.error("Invalid OTP. Please try again.")

    # Create Payment
    st.subheader("Record Payment")
    with st.form("payment_form"):
        # Sample data for demo purposes
        contracts_sample_data = pd.DataFrame({"ID": [1, 2], "Contract": ["Contract A", "Contract B"]})
        contract_id = st.selectbox("Select Contract", contracts_sample_data["Contract"].tolist())
        amount = st.number_input("Amount", min_value=0.0, step=0.1)
        payment_date = st.date_input("Payment Date")
        payment_status = st.selectbox("Payment Status", ["Pending", "Completed"])
        if st.form_submit_button("Record Payment"):
            insert_payment(contract_id, amount, payment_date, payment_status)
            send_notification(buyer_name, f"Payment for Contract {contract_id} recorded successfully.")

    # View Payments
    st.subheader("View Your Payments")
    # Sample data for demo purposes
    payments_sample_data = pd.DataFrame({"Buyer": ["Buyer A"], "Amount": [1000], "Status": ["Completed"]})
    st.dataframe(payments_sample_data[payments_sample_data["Buyer"] == "Buyer A"])
