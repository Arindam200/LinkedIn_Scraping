import requests
import streamlit as st


# Function to make a request to the FastAPI endpoint
def call_fastapi_endpoint(title, location, data_name):
    url = "http://127.0.0.1:6000/scrape" 
    
    payload = {
        "title": title,
        "location": location,
        "data_name": str(data_name)
    }
    response = requests.post(url, json=payload)
    return response.json()

def main():
    st.title("LinkedIn Jobs Crawler")

    # User input fields
    title = st.text_input("Enter Job Title: ")
    location = st.text_input("Enter Job Location: ")
    data_name = st.text_input("Enter Data Name")

   

    if st.button("Start Processing"):
        with st.spinner("Crawling in progress..."):
            r = call_fastapi_endpoint(title, location, data_name) 
        if r['status_code'] == 200:
            st.success("Processing complete!")
        else:
            st.success("Error")

    else:
        st.error("Please fill in all fields.")

if __name__ == "__main__":
    main()