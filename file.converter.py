import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="File Converter", layout="wide")
st.title("File Converter & Cleaner")
st.write("Upload CSV or Excel files for conversion and cleaning")

files = st.file_uploader("Upload your CSV or Excel file", type=['csv', 'xlsx'], accept_multiple_files=True)

if files:
    for file in files:
        ext = file.name.split('.')[-1].lower()
              
        try:
            if ext == 'csv':
                df = pd.read_csv(file, encoding='utf-8', encoding_errors='ignore')
            else:
                try:
                    import openpyxl  # Ensure openpyxl is available
                    df = pd.read_excel(file, engine='openpyxl')
                except ImportError:
                    st.error("Error: `openpyxl` is required to read Excel files. Install it using `pip install openpyxl`.")
                    continue

            st.subheader(f"{file.name} - Preview")
            st.dataframe(df.head())

            if st.checkbox(f"Remove Duplicates - {file.name}"):
                df.drop_duplicates(inplace=True)
                st.success("Duplicates Removed")
                st.dataframe(df.head())

            if st.checkbox(f"Fill Missing Values - {file.name}"):
                num_cols = df.select_dtypes(include='number')
                if not num_cols.empty:
                    df.fillna(num_cols.mean(), inplace=True)
                    st.success("Missing values filled with column mean")
                else:
                    st.warning("No numerical columns found for filling missing values.")
                st.dataframe(df.head())

            selected_columns = st.multiselect(f"Select columns - {file.name}", df.columns, default=df.columns)
            df = df[selected_columns]
            st.dataframe(df.head())


            if st.checkbox(f"Show Chart - {file.name}"):
                num_cols = df.select_dtypes(include="number")
                if not num_cols.empty:
                    st.bar_chart(num_cols.iloc[:, :2])
                else:
                    st.warning("No numeric columns available for chart visualization.")

            format_choice = st.radio(f"Convert {file.name} to", ['csv', 'xlsx'])

            if st.button(f"Download {file.name} as {format_choice}"):
                output = BytesIO()
                new_name = file.name.rsplit('.', 1)[0] + f".{format_choice}"
                
                if format_choice == 'csv':
                    df.to_csv(output, index=False)
                    mime = 'text/csv'
                else:
                    try:
                        df.to_excel(output, index=False, engine='openpyxl')
                        mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    except ImportError:
                        st.error("Error: `openpyxl` is required to export Excel files. Install it using `pip install openpyxl`.")
                        continue

                output.seek(0)
                st.download_button(label=f"Download {new_name}", data=output, file_name=new_name, mime=mime)
                st.success(f"{file.name} has been converted to {format_choice}")

        except Exception as e:
            st.error(f"Error processing {file.name}: {e}")
