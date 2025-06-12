import streamlit as st
import requests
import json
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="Cold Call Agent Demo",
    page_icon="📞",
    layout="centered"
)

# Backend API URL
API_BASE_URL = "http://localhost:8000"

def main():
    st.title("📞 Cold Call Agent Demo")
    st.markdown("---")
    
    # Create form for user input
    with st.form("call_form"):
        st.subheader("Initiate Outbound Call")
        
        # User inputs
        user_name = st.text_input(
            "Customer Name",
            placeholder="Enter customer name (e.g., Jayden)",
            help="Name of the customer to call"
        )
        
        phone_number = st.text_input(
            "Phone Number",
            placeholder="Enter phone number (e.g., +1234567890)",
            help="Customer's phone number with country code"
        )
        
        # Submit button
        submitted = st.form_submit_button(
            "🚀 Make Call",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not user_name or not phone_number:
                st.error("❌ Please fill in both customer name and phone number")
            else:
                initiate_call(user_name, phone_number)

def initiate_call(user_name: str, phone_number: str):
    """
    Send request to backend to initiate the call
    """
    with st.spinner("🔄 Initiating call..."):
        try:
            # Prepare request payload
            payload = {
                "user_name": user_name,
                "phone_number": phone_number
            }
            
            # Make API request
            response = requests.post(
                f"{API_BASE_URL}/initiate_call",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                st.success("✅ Call initiated successfully!")
                
                # # Display call details
                # st.subheader("Call Details")
                # call_details = result["call_details"]
                
                # col1, col2 = st.columns(2)
                
                # with col1:
                #     st.metric("Customer Name", call_details["user_name"])
                #     st.metric("Phone Number", call_details["phone_number"])
                #     st.metric("Status", call_details["status"].title())
                
                # with col2:
                #     st.metric("Room Name", call_details["room_name"])
                #     st.metric("Dispatch ID", call_details["dispatch_id"][:12] + "...")
                #     st.metric("Timestamp", datetime.fromisoformat(call_details["timestamp"].replace('Z', '+00:00')).strftime("%H:%M:%S"))
                
                # # Show raw response in expandable section
                # with st.expander("📋 Raw Response"):
                #     st.json(result)
                    
                st.info("💡 The agent will now dial the provided number and attempt to confirm the appointment.")
                
            else:
                error_detail = response.json().get("detail", "Unknown error")
                st.error(f"❌ Failed to initiate call: {error_detail}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Make sure the FastAPI server is running on port 8000.")
        except requests.exceptions.Timeout:
            st.error("❌ Request timed out. Please try again.")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This demo showcases an AI-powered outbound calling agent that:
    
    - 📞 Calls customers automatically
    - 🗣️ Uses natural voice conversation
    - 📅 Confirms appointment details
    - 🤖 Handles common scenarios
    
    """)
    
    st.header("🛠️ Backend Status")
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            st.success("✅ Backend is running")
        else:
            st.error("❌ Backend error")
    except:
        st.error("❌ Backend not accessible")

if __name__ == "__main__":
    main()