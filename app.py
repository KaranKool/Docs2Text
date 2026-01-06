import streamlit as st
import os
import tempfile
from markitdown import MarkItDown

# --- Page Configuration ---
st.set_page_config(
    page_title="Universal Doc Reader",
    page_icon="📄",
    layout="centered"
)

# --- Utility: File Size Formatter ---
def format_file_size(size_in_bytes):
    """Converts bytes to readable KB or MB."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} bytes"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.2f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"

# --- Initialize Engine ---
md = MarkItDown()

def main():
    st.title("📄 Universal Document Reader")
    st.markdown(
        """
        **Convert your documents to clean Markdown instantly.** *Supports: Word, Excel, PowerPoint, PDF, HTML, and ZIP archives.*
        """
    )

    # --- Upload Area ---
    # Added 'zip' explicitly to the allowed types
    uploaded_files = st.file_uploader(
        "Drag and drop files here", 
        accept_multiple_files=True,
        type=['docx', 'xlsx', 'pptx', 'pdf', 'html', 'zip', 'csv', 'txt']
    )

    if uploaded_files:
        st.write("---")
        
        for uploaded_file in uploaded_files:
            # Create a collapsible section for each file
            with st.expander(f"Processing: {uploaded_file.name}", expanded=True):
                
                # --- File Handling (Temp Storage) ---
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        tmp_path = tmp_file.name
                    
                    # --- Conversion Engine ---
                    with st.spinner(f"Reading {uploaded_file.name}..."):
                        try:
                            # Run conversion
                            result = md.convert(tmp_path)
                            text_content = result.text_content
                            
                            # --- Calculate Metrics ---
                            original_size = uploaded_file.size
                            # Calculate size of the resulting text string in bytes
                            converted_size = len(text_content.encode('utf-8'))
                            
                            # Avoid division by zero
                            if original_size > 0:
                                reduction_percent = ((original_size - converted_size) / original_size) * 100
                            else:
                                reduction_percent = 0

                            # Success Message
                            st.success(f"Successfully converted {uploaded_file.name}")
                            
                            # --- TABS INTERFACE ---
                            tab_preview, tab_stats = st.tabs(["👁️ Preview & Download", "📊 File Size Comparison"])
                            
                            # TAB 1: Preview and Download
                            with tab_preview:
                                st.text_area("Content", value=text_content, height=300)
                                
                                # Download Options
                                base_name = os.path.splitext(uploaded_file.name)[0]
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.download_button(
                                        label="Download .md file",
                                        data=text_content,
                                        file_name=f"{base_name}_converted.md",
                                        mime="text/markdown"
                                    )
                                with col2:
                                    st.download_button(
                                        label="Download .txt file",
                                        data=text_content,
                                        file_name=f"{base_name}_converted.txt",
                                        mime="text/plain"
                                    )

                            # TAB 2: File Size Comparison
                            with tab_stats:
                                # Data for the table
                                data = [
                                    {"Metric": "Original File Size", "Value": format_file_size(original_size)},
                                    {"Metric": "Converted .txt Size", "Value": format_file_size(converted_size)}
                                ]
                                
                                # Display Table
                                st.table(data)
                                
                                # Display Percentage Badge
                                if reduction_percent > 0:
                                    st.metric(
                                        label="Efficiency", 
                                        value=f"{reduction_percent:.1f}% Smaller",
                                        delta="Compression achieved",
                                        delta_color="normal"
                                    )
                                else:
                                    st.info("The text version is larger than the original file.")

                        except Exception as e:
                            # Error Handling
                            st.error(f"⚠️ Could not read {uploaded_file.name}. Please check the format.")
                            st.caption(f"Technical error: {str(e)}")

                finally:
                    # Cleanup
                    if 'tmp_path' in locals() and os.path.exists(tmp_path):
                        os.unlink(tmp_path)

if __name__ == "__main__":
    main()
