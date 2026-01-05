import streamlit as st
import pandas as pd
import io
import time
from datetime import datetime
import os

# Set page configuration
st.set_page_config(
    page_title="Grocery Store Automation Suite",
    page_icon="🛒",
    layout="wide"
)

# Import your automation modules
# Note: You'll need to adapt these imports based on your actual script structure
try:
    # If your scripts are in a package
    from automation_scripts import (
        auto_fill_supplier_order,
        process_supplier_excel,
        convert_pdf_to_ecrs
    )
except ImportError:
    # Fallback: Define dummy functions for testing
    st.warning("⚠️ Automation scripts not found. Using demo mode.")
    
    def auto_fill_supplier_order(excel_file, supplier_name, store_id):
        """Dummy function for Task 1"""
        time.sleep(1)  # Simulate processing
        return f"Order for {supplier_name} (Store: {store_id}) processed successfully."
    
    def process_supplier_excel(input_file, output_format):
        """Dummy function for Task 2"""
        time.sleep(1)
        return pd.DataFrame({"Item": ["Demo1", "Demo2"], "Quantity": [10, 20]})
    
    def convert_pdf_to_ecrs(pdf_file, store_id, supplier_name):
        """Dummy function for Task 3"""
        time.sleep(1)
        return "INVOICE_DATA\nITEM1,10,100\nITEM2,5,200"

# Initialize session state for multi-step processes
if 'current_task' not in st.session_state:
    st.session_state.current_task = None
if 'processing_step' not in st.session_state:
    st.session_state.processing_step = 0
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}

# Sidebar - Store Selection and Navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3082/3082383.png", width=100)
    st.title("Store Dashboard")
    
    # Store selection
    stores = {
        "STORE001": "Main Store",
        "STORE002": "North Branch",
        "STORE003": "South Branch",
        "STORE004": "East Branch",
        "STORE005": "West Branch",
        "STORE006": "Central Branch"
    }
    
    selected_store = st.selectbox(
        "🏬 Select Store",
        options=list(stores.keys()),
        format_func=lambda x: f"{x} - {stores[x]}"
    )
    
    st.divider()
    
    # User info (in real app, this would be from login)
    st.write(f"👤 User: **Admin**")
    st.write(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    
    st.divider()
    
    # Quick stats
    st.subheader("Today's Activity")
    st.metric("Orders Processed", "12")
    st.metric("Invoices Converted", "8")
    
    st.divider()
    
    # Task shortcuts
    st.subheader("Quick Actions")
    if st.button("🔄 Process All Pending", use_container_width=True):
        st.session_state.current_task = "batch_process"
    
    if st.button("📊 View Reports", use_container_width=True):
        st.session_state.current_task = "reports"

# Main content area
st.title("🛒 Grocery Store Automation Suite")
st.markdown("---")

# Create tabs for different tasks
tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Auto-Fill Orders", 
    "🔄 Process Supplier Sheets", 
    "🧾 Convert Invoices", 
    "📈 Activity Log"
])

# TAB 1: Auto-Fill Supplier Orders
with tab1:
    st.header("Task 1: Auto-Fill Supplier Orders")
    st.markdown("Upload your order Excel and automatically fill supplier websites")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Supplier selection
        suppliers = {
            "supplier_a": "Supplier A - Fresh Produce",
            "supplier_b": "Supplier B - Dairy Products",
            "supplier_c": "Supplier C - Packaged Goods",
            "supplier_d": "Supplier D - Beverages"
        }
        
        selected_supplier = st.selectbox(
            "Select Supplier",
            options=list(suppliers.keys()),
            format_func=lambda x: suppliers[x]
        )
        
        # Excel file upload
        uploaded_file = st.file_uploader(
            "📤 Upload Order Excel File",
            type=["xlsx", "xls", "csv"],
            key="order_excel"
        )
        
        if uploaded_file:
            # Preview the Excel file
            try:
                df = pd.read_excel(uploaded_file)
                st.subheader("Order Preview")
                st.dataframe(df.head(), use_container_width=True)
                st.caption(f"Total Items: {len(df)} | File: {uploaded_file.name}")
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    with col2:
        st.subheader("Automation Settings")
        
        # Optional settings
        auto_submit = st.checkbox("Auto-submit order after filling", value=True)
        save_copy = st.checkbox("Save confirmation copy", value=True)
        email_notify = st.checkbox("Email confirmation", value=False)
        
        if email_notify:
            email_address = st.text_input("Notification Email")
        
        st.divider()
        
        # Process button
        if st.button("🚀 Start Auto-Fill Process", type="primary", use_container_width=True):
            if uploaded_file and selected_supplier:
                with st.spinner("Processing order..."):
                    # Call your automation function
                    try:
                        result = auto_fill_supplier_order(
                            excel_file=uploaded_file,
                            supplier_name=selected_supplier,
                            store_id=selected_store
                        )
                        
                        st.success("✅ Order processed successfully!")
                        
                        # Show results
                        st.subheader("Processing Results")
                        st.json({"supplier": selected_supplier, "store": selected_store, "status": "completed"})
                        
                        # Download confirmation
                        confirmation_text = f"Order confirmation for {selected_supplier}\nStore: {selected_store}\nTimestamp: {datetime.now()}"
                        st.download_button(
                            label="📥 Download Confirmation",
                            data=confirmation_text,
                            file_name=f"order_confirmation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                        
                        # Log activity
                        if 'activity_log' not in st.session_state:
                            st.session_state.activity_log = []
                        st.session_state.activity_log.append({
                            "timestamp": datetime.now(),
                            "task": "order_fill",
                            "supplier": selected_supplier,
                            "store": selected_store,
                            "file": uploaded_file.name
                        })
                        
                    except Exception as e:
                        st.error(f"❌ Processing failed: {str(e)}")
            else:
                st.warning("Please upload a file and select a supplier")

# TAB 2: Process Supplier Excel Sheets
with tab2:
    st.header("Task 2: Process Supplier Excel Sheets")
    st.markdown("Standardize supplier Excel sheets to your format")
    
    # File upload section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_excel = st.file_uploader(
            "📤 Upload Supplier Excel File",
            type=["xlsx", "xls", "csv"],
            help="Upload the Excel sheet received from supplier",
            key="supplier_excel"
        )
        
        if uploaded_excel:
            try:
                df = pd.read_excel(uploaded_excel)
                st.subheader("Original Supplier Format")
                st.dataframe(df, use_container_width=True)
                
                # Column mapping interface
                st.subheader("Column Mapping")
                if len(df.columns) > 0:
                    mapping = {}
                    for col in df.columns:
                        mapping[col] = st.selectbox(
                            f"Map '{col}' to:",
                            ["Item Name", "Quantity", "Price", "SKU", "Unit", "Ignore"],
                            key=f"map_{col}"
                        )
                    
                    st.session_state.column_mapping = mapping
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        st.subheader("Output Format")
        output_format = st.selectbox(
            "Select target format",
            ["Standard Order Sheet", "ECRS Import Format", "Inventory Update"]
        )
        
        st.divider()
        
        # Process button
        if st.button("🔄 Convert Format", type="primary", use_container_width=True):
            if uploaded_excel:
                with st.spinner("Converting format..."):
                    try:
                        # Call your processing function
                        processed_df = process_supplier_excel(
                            input_file=uploaded_excel,
                            output_format=output_format
                        )
                        
                        st.success("✅ Format converted successfully!")
                        
                        # Show processed data
                        st.subheader("Converted Format")
                        st.dataframe(processed_df, use_container_width=True)
                        
                        # Download button
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            processed_df.to_excel(writer, index=False, sheet_name='Processed')
                        
                        st.download_button(
                            label="📥 Download Converted File",
                            data=output.getvalue(),
                            file_name=f"converted_{uploaded_excel.name}",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                    except Exception as e:
                        st.error(f"Conversion failed: {e}")
            else:
                st.warning("Please upload a file first")

# TAB 3: Convert PDF Invoices to ECRS
with tab3:
    st.header("Task 3: Convert PDF Invoices to ECRS Format")
    st.markdown("Upload supplier PDF invoices and convert to ECRS-compatible TXT files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # PDF upload
        uploaded_pdf = st.file_uploader(
            "📤 Upload Invoice PDF",
            type=["pdf"],
            help="Upload supplier invoice in PDF format",
            key="invoice_pdf"
        )
        
        # Multiple file upload option
        multiple_files = st.file_uploader(
            "📚 Upload Multiple PDFs (Batch Processing)",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload multiple invoices at once"
        )
        
        # Supplier info
        invoice_supplier = st.selectbox(
            "Invoice From",
            ["Supplier A", "Supplier B", "Supplier C", "Supplier D", "Other"],
            key="invoice_supplier"
        )
        
        if invoice_supplier == "Other":
            custom_supplier = st.text_input("Enter supplier name")
    
    with col2:
        st.subheader("ECRS Settings")
        
        # ECRS format options
        ecrs_format = st.selectbox(
            "ECRS Import Format",
            ["Format A (Standard)", "Format B (With Tax)", "Format C (Itemized)"]
        )
        
        include_tax = st.checkbox("Include tax information", value=True)
        split_categories = st.checkbox("Split by category", value=False)
        
        st.divider()
        
        # Process button for single file
        if uploaded_pdf:
            if st.button("🧾 Convert Single Invoice", type="primary", use_container_width=True):
                with st.spinner("Extracting data from PDF..."):
                    try:
                        txt_content = convert_pdf_to_ecrs(
                            pdf_file=uploaded_pdf,
                            store_id=selected_store,
                            supplier_name=invoice_supplier
                        )
                        
                        st.success("✅ PDF converted successfully!")
                        
                        # Show preview
                        with st.expander("Preview Converted Data"):
                            st.text(txt_content[:500] + "..." if len(txt_content) > 500 else txt_content)
                        
                        # Download button
                        st.download_button(
                            label="📥 Download TXT for ECRS",
                            data=txt_content,
                            file_name=f"ecrs_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                        
                    except Exception as e:
                        st.error(f"Conversion failed: {e}")
        
        # Process button for multiple files
        if multiple_files and len(multiple_files) > 0:
            if st.button(f"🔄 Convert {len(multiple_files)} Invoices", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                results = []
                
                for i, pdf_file in enumerate(multiple_files):
                    try:
                        txt_content = convert_pdf_to_ecrs(
                            pdf_file=pdf_file,
                            store_id=selected_store,
                            supplier_name=invoice_supplier
                        )
                        results.append((pdf_file.name, txt_content))
                    except Exception as e:
                        results.append((pdf_file.name, f"ERROR: {str(e)}"))
                    
                    progress_bar.progress((i + 1) / len(multiple_files))
                
                st.success(f"✅ Processed {len(multiple_files)} invoices!")
                
                # Create zip file for multiple results
                import zipfile
                from io import BytesIO
                
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    for filename, content in results:
                        zip_file.writestr(f"{filename.replace('.pdf', '.txt')}", content)
                
                st.download_button(
                    label="📦 Download All as ZIP",
                    data=zip_buffer.getvalue(),
                    file_name=f"ecrs_batch_{datetime.now().strftime('%Y%m%d')}.zip",
                    mime="application/zip"
                )

# TAB 4: Activity Log
with tab4:
    st.header("📈 Activity Log & Reports")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Orders Today", "24", "+3")
    with col2:
        st.metric("Invoices Processed", "18", "+5")
    with col3:
        st.metric("Time Saved", "6.5 hours", "-1.2")
    with col4:
        st.metric("Success Rate", "98.2%", "+0.5")
    
    st.divider()
    
    # Sample activity log (in real app, this would be from database)
    st.subheader("Recent Activities")
    
    sample_activities = [
        {"time": "10:30 AM", "action": "Order processed", "supplier": "Supplier A", "user": "John", "status": "✅"},
        {"time": "11:15 AM", "action": "PDF converted", "supplier": "Supplier B", "user": "Sarah", "status": "✅"},
        {"time": "11:45 AM", "action": "Excel formatted", "supplier": "Supplier C", "user": "Mike", "status": "✅"},
        {"time": "12:30 PM", "action": "Order processed", "supplier": "Supplier D", "user": "John", "status": "⚠️"},
        {"time": "01:15 PM", "action": "PDF converted", "supplier": "Supplier A", "user": "Sarah", "status": "✅"},
    ]
    
    st.dataframe(
        pd.DataFrame(sample_activities),
        use_container_width=True,
        hide_index=True
    )
    
    # Export options
    st.download_button(
        label="📊 Export Activity Report",
        data=pd.DataFrame(sample_activities).to_csv(index=False).encode('utf-8'),
        file_name="activity_report.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.caption(f"© {datetime.now().year} Grocery Store Automation Suite | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Instructions for deployment
with st.expander("🚀 Deployment Instructions"):
    st.markdown("""
    ### How to Deploy This App:
    
    1. **Save this code as `app.py`**
    
    2. **Create `requirements.txt`** with dependencies listed above
    
    3. **Adapt your scripts** to work as modules:
       ```python
       # automation_scripts/order_filler.py
       import pandas as pd
       
       def auto_fill_supplier_order(excel_file, supplier_name, store_id):
           # Your existing automation code here
           pass
       ```
    
    4. **Test locally**:
       ```bash
       pip install -r requirements.txt
       streamlit run app.py
       ```
    
    5. **Deploy to Streamlit Cloud**:
       - Push to GitHub
       - Go to [share.streamlit.io](https://share.streamlit.io)
       - Connect your repo
       - Set main file to `app.py`
       - Deploy!
    """)

# Run instructions at the bottom
if __name__ == "__main__":
    # This is already a Streamlit app, no need for additional code
    pass