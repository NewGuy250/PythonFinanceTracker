import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

def save_categories():
    with open(category_file, "w") as f:
        json.dump(st.session_state.categories, f)

def categorize_transaction(df):
    df["Category"] = "Uncategorized"  # default

    for category, keywords in st.session_state.categories.items():
        if category == "Uncategorized" or not keywords:
            continue
        lowered_keywords = [kw.lower().strip() for kw in keywords]
        for idx, row in df.iterrows():
            vendor = str(row["Vendor"]).lower().strip()
            # check if any keyword is inside details text
            if any(kw in vendor for kw in lowered_keywords):
                df.at[idx, "Category"] = category
    return df

def load_transactions(file):
    try:
        # Read CSV with headers
        df = pd.read_csv(file)

        # Drop unused "Blank" column if it exists
        if "Blank" in df.columns:
            df = df.drop(columns=["Blank"])

        # Convert Date (your file is MM/DD/YYYY)
        df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y", errors="coerce")

        # Convert Amount from string -> float
        df["Amount"] = (
            df["Amount"]
            .astype(str)
            .str.replace(",", "")   # remove thousands separator
            .str.replace('"', "")   # remove quotes if present
            .astype(float)
        )

        # Categorize
        df = categorize_transaction(df)
        return df

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def add_keyword_to_category(category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories.get(category, []):
        st.session_state.categories[category].append(keyword)
        save_categories()
        return True
    return False

def main():
    st.title("💰 Simple Finance Dashboard")

    uploaded_file = st.file_uploader("Upload your transactions CSV file", type=["csv"])

    if uploaded_file is not None:
        df = load_transactions(uploaded_file)

        if df is not None:
            # Split into debits (negative) and credits (positive)
            debits_df = df[df["Amount"] < 0].copy()
            credits_df = df[df["Amount"] > 0].copy()

            # Store debits for editing
            st.session_state.debits_df = debits_df.copy()

            tab1, tab2 = st.tabs(["Expenses (Debits)", "Payments (Credits)"])

            with tab1:
                # Add new category
                new_category = st.text_input("New Category Name")
                add_button = st.button("Add Category")

                if add_button and new_category:
                    if new_category not in st.session_state.categories:
                        st.session_state.categories[new_category] = []
                        save_categories()
                        st.success(f"Category '{new_category}' added successfully!")
                        st.rerun()

                # Editable expenses
                st.subheader("Your Expenses")
                edited_df = st.data_editor(
                    st.session_state.debits_df[["Date", "Vendor", "Amount", "Category"]],
                    column_config={
                        "Date": st.column_config.DateColumn("Date", format="MM/DD/YYYY"),
                        "Amount": st.column_config.NumberColumn("Amount", format="%.2f"),
                        "Category": st.column_config.SelectboxColumn(
                            "Category",
                            options=list(st.session_state.categories.keys())
                        )
                    },
                    hide_index=True,
                    use_container_width=True,
                    key="category_editor"
                )

                # Apply category changes
                save_button = st.button("Apply Changes", type="primary")
                if save_button:
                    for idx, row in edited_df.iterrows():
                        new_category = row["Category"]
                        if new_category == st.session_state.debits_df.at[idx, "Category"]:
                            continue
                        vendor = row["Vendor"]
                        st.session_state.debits_df.at[idx, "Category"] = new_category
                        add_keyword_to_category(new_category, vendor)

                # Summary table
                st.subheader("Expense Summary")

                # Convert expenses to positive values
                expenses_df = st.session_state.debits_df.copy()
                expenses_df["Amount"] = expenses_df["Amount"].abs()

                category_totals = (
                    expenses_df.groupby("Category")["Amount"]
                    .sum()
                    .reset_index()
                )
                category_totals = category_totals.sort_values(by="Amount", ascending=False)

                category_totals = category_totals.sort_values(by="Amount", ascending=False)



                st.dataframe(
                    category_totals,
                    column_config={
                        "Amount": st.column_config.NumberColumn("Total Amount", format="%.2f USD")
                    },
                    use_container_width=True,
                    hide_index=True
                )

                # Pie chart
                fig = px.pie(category_totals, names="Category", values="Amount", title="Expenses by Category")
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.subheader("Payments Summary")
                total_payments = credits_df["Amount"].sum()
                st.metric("Total Payments", f"${total_payments:,.2f}")
                st.write(credits_df)

if __name__ == "__main__":
    st.set_page_config(page_title="Simple Finance App", page_icon="💰", layout="wide")

    category_file = "categories.json"

    # Initialize session state for categories if not already set
    if "categories" not in st.session_state:
        st.session_state.categories = {
            "Uncategorized": []
        }

    # Load categories from JSON file if it exists
    if os.path.exists(category_file):
        with open(category_file, "r") as f:
            st.session_state.categories = json.load(f)
    main()
