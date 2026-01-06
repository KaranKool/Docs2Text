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

# --- Initialize Engine ---
# We initialize MarkItDown once. 
# Note: For URL processing in the future, request configuration would happen here.
md = MarkItDown()

def convert_to_markdown(file_path):
    """
    Helper function to convert file content using MarkItDown.
    Includes basic error handling logic.
    """
    try:
        # The primary engine call
        result = md.convert(file_path)
        return result.text_content
    except Exception as e:
        # Return None and the error message to handle it gracefully in the UI
        return None, str(e)

def main():
    st.title("📄 Universal Document Reader")
    st.markdown(
        """
        **Convert your documents to clean Markdown instantly.** *Supports: Word, Excel, PowerPoint, PDF, HTML, and ZIP archives.*
        """
    )

    # --- Upload Area ---
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
                # MarkItDown needs a file path to detect extensions correctly (especially for ZIPs/Excel).
                # We save the uploaded stream to a temporary file.
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        tmp_path = tmp_file.name
                    
                    # --- Conversion Engine ---
                    with st.spinner(f"Reading {uploaded_file.name}..."):
                        # We wrapped the conversion in a helper to catch errors
                        try:
                            result = md.convert(tmp_path)
                            text_content = result.text_content
                            
                            # Success Message
                            st.success(f"Successfully converted {uploaded_file.name}")
                            
                            # --- Instant Preview ---
                            st.subheader("Preview")
                            st.text_area("Content", value=text_content, height=300)
                            
                            # --- Download Options ---
                            # Generate safe filename base (removing original extension)
                            base_name = os.path.splitext(uploaded_file.name)[0]
                            
                            col1, col2 = st.columns(2)
                            
                            # Option 1: Download as Markdown
                            with col1:
                                st.download_button(
                                    label="Download .md file",
                                    data=text_content,
                                    file_name=f"{base_name}_converted.md",
                                    mime="text/markdown"
                                )
                                
                            # Option 2: Download as Text
                            with col2:
                                st.download_button(
                                    label="Download .txt file",
                                    data=text_content,
                                    file_name=f"{base_name}_converted.txt",
                                    mime="text/plain"
                                )

                        except Exception as e:
                            # --- Resilience: Error Handling ---
                            st.error(f"⚠️ Could not read {uploaded_file.name}. Please check the format.")
                            st.caption(f"Technical error: {str(e)}")

                finally:
                    # --- Cleanup ---
                    # Ensure the temp file is deleted even if errors occur
                    if 'tmp_path' in locals() and os.path.exists(tmp_path):
                        os.unlink(tmp_path)

if __name__ == "__main__":
    main()
