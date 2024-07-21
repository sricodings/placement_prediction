
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np
from database import create_table, add_user, authenticate_user
import io

create_table()

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    
    if st.button("Login", key="login_button"):
        user = authenticate_user(username, password)
        if user:
            st.success("Logged in successfully!")
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
        else:
            st.error("Invalid username or password")


def register():
    st.title("Register")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type='password')

    if st.button("Register"):
        try:
            add_user(new_username, new_password)
            st.success("User registered successfully!")
        except Exception as e:
            st.error("Username already exists")



def overall_trends(data):
    overall_trend = data.groupby('year').agg({'num_placed': 'sum', 'lpa': 'mean'}).reset_index()

    fig_num_placed = px.line(overall_trend, x='year', y='num_placed', markers=True, title='Overall Placement Trend (Number of Students)')
    fig_num_placed.update_traces(line=dict(color='blue'))
    fig_num_placed.update_layout(xaxis_title='Year', yaxis_title='Number of Students Placed')

    fig_lpa = px.line(overall_trend, x='year', y='lpa', markers=True, title='Overall Placement Trend (Lakhs Per Annum)')
    fig_lpa.update_traces(line=dict(color='green'))
    fig_lpa.update_layout(xaxis_title='Year', yaxis_title='Lakhs Per Annum (LPA)')

    st.plotly_chart(fig_num_placed)
    st.plotly_chart(fig_lpa)

    X_num_placed = overall_trend['year'].values.reshape(-1, 1)
    y_num_placed = overall_trend['num_placed'].values

    X_lpa = overall_trend['year'].values.reshape(-1, 1)
    y_lpa = overall_trend['lpa'].values

    model_num_placed = LinearRegression()
    model_num_placed.fit(X_num_placed, y_num_placed)

    model_lpa = LinearRegression()
    model_lpa.fit(X_lpa, y_lpa)

    next_year = np.array([[overall_trend['year'].max() + 1]])

    predicted_placements = model_num_placed.predict(next_year)
    predicted_lpa = model_lpa.predict(next_year)

    st.write(f"Predicted placements for {next_year[0][0]} (Number of Students): {predicted_placements[0]:.0f}")
    st.write(f"Predicted LPA for {next_year[0][0]}: {predicted_lpa[0]:.2f}")


def company_trend(data, company_name):
    company_data = data[data['company'] == company_name]
    if company_data.empty:
        st.write(f"No data available for company: {company_name}")
        return

    company_trend = company_data.groupby('year').agg({'num_placed': 'sum', 'lpa': 'mean'}).reset_index()

    fig_num_placed = px.line(company_trend, x='year', y='num_placed', markers=True, title=f'Placement Trend for {company_name} (Number of Students)')
    fig_num_placed.update_traces(line=dict(color='blue'))
    fig_num_placed.update_layout(xaxis_title='Year', yaxis_title='Number of Students Placed')

    fig_lpa = px.line(company_trend, x='year', y='lpa', markers=True, title=f'Placement Trend for {company_name} (Lakhs Per Annum)')
    fig_lpa.update_traces(line=dict(color='green'))
    fig_lpa.update_layout(xaxis_title='Year', yaxis_title='Lakhs Per Annum (LPA)')

    st.plotly_chart(fig_num_placed)
    st.plotly_chart(fig_lpa)

    if len(company_trend) > 1:
        X_company_num_placed = company_trend['year'].values.reshape(-1, 1)
        y_company_num_placed = company_trend['num_placed'].values

        X_company_lpa = company_trend['year'].values.reshape(-1, 1)
        y_company_lpa = company_trend['lpa'].values

        model_company_num_placed = LinearRegression()
        model_company_num_placed.fit(X_company_num_placed, y_company_num_placed)

        model_company_lpa = LinearRegression()
        model_company_lpa.fit(X_company_lpa, y_company_lpa)

        next_year = np.array([[company_trend['year'].max() + 1]])

        predicted_company_placements = model_company_num_placed.predict(next_year)
        predicted_company_lpa = model_company_lpa.predict(next_year)

        st.write(f"Predicted placements for {company_name} in {next_year[0][0]} (Number of Students): {predicted_company_placements[0]:.0f}")
        st.write(f"Predicted LPA for {company_name} in {next_year[0][0]}: {predicted_company_lpa[0]:.2f}")
    else:
        st.write(f"Not enough data to predict placements for {company_name}")


def compare_companies(data, company1, company2):
    company1_data = data[data['company'] == company1]
    company2_data = data[data['company'] == company2]

    if company1_data.empty:
        st.write(f"No data available for company: {company1}")
        return

    if company2_data.empty:
        st.write(f"No data available for company: {company2}")
        return

    company1_trend = company1_data.groupby('year').agg({'num_placed': 'sum', 'lpa': 'mean'}).reset_index()
    company2_trend = company2_data.groupby('year').agg({'num_placed': 'sum', 'lpa': 'mean'}).reset_index()

    fig_num_placed = px.line(company1_trend, x='year', y='num_placed', markers=True, title='Number of Students Placed Comparison')
    fig_num_placed.add_scatter(x=company2_trend['year'], y=company2_trend['num_placed'], mode='lines+markers', name=company2)
    fig_num_placed.update_traces(line=dict(color='blue'))
    fig_num_placed.update_layout(xaxis_title='Year', yaxis_title='Number of Students Placed')

    fig_lpa = px.line(company1_trend, x='year', y='lpa', markers=True, title='LPA Comparison')
    fig_lpa.add_scatter(x=company2_trend['year'], y=company2_trend['lpa'], mode='lines+markers', name=company2)
    fig_lpa.update_traces(line=dict(color='green'))
    fig_lpa.update_layout(xaxis_title='Year', yaxis_title='Lakhs Per Annum (LPA)')

    st.plotly_chart(fig_num_placed)
    st.plotly_chart(fig_lpa)

    if len(company1_trend) > 1 and len(company2_trend) > 1:
        next_year = np.array([[max(company1_trend['year'].max(), company2_trend['year'].max()) + 1]])

        X_company1_num_placed = company1_trend['year'].values.reshape(-1, 1)
        y_company1_num_placed = company1_trend['num_placed'].values

        X_company1_lpa = company1_trend['year'].values.reshape(-1, 1)
        y_company1_lpa = company1_trend['lpa'].values

        model_company1_num_placed = LinearRegression()
        model_company1_num_placed.fit(X_company1_num_placed, y_company1_num_placed)

        model_company1_lpa = LinearRegression()
        model_company1_lpa.fit(X_company1_lpa, y_company1_lpa)

        predicted_company1_placements = model_company1_num_placed.predict(next_year)
        predicted_company1_lpa = model_company1_lpa.predict(next_year)

        st.write(f"Predicted placements for {company1} in {next_year[0][0]} (Number of Students): {predicted_company1_placements[0]:.0f}")
        st.write(f"Predicted LPA for {company1} in {next_year[0][0]}: {predicted_company1_lpa[0]:.2f}")

        X_company2_num_placed = company2_trend['year'].values.reshape(-1, 1)
        y_company2_num_placed = company2_trend['num_placed'].values

        X_company2_lpa = company2_trend['year'].values.reshape(-1, 1)
        y_company2_lpa = company2_trend['lpa'].values

        model_company2_num_placed = LinearRegression()
        model_company2_num_placed.fit(X_company2_num_placed, y_company2_num_placed)

        model_company2_lpa = LinearRegression()
        model_company2_lpa.fit(X_company2_lpa, y_company2_lpa)

        predicted_company2_placements = model_company2_num_placed.predict(next_year)
        predicted_company2_lpa = model_company2_lpa.predict(next_year)

        st.write(f"Predicted placements for {company2} in {next_year[0][0]} (Number of Students): {predicted_company2_placements[0]:.0f}")
        st.write(f"Predicted LPA for {company2} in {next_year[0][0]}: {predicted_company2_lpa[0]:.2f}")
    else:
        st.write(f"Not enough data to predict placements for {company1} or {company2}")


def user_analysis():
    st.write("\n--- User Analysis ---")
    current_year = st.number_input("Enter your current year of study (e.g., 2 for 2nd year)", min_value=1, max_value=5)
    cgpa = st.number_input("Enter your current CGPA", min_value=0.0, max_value=10.0, step=0.01)
    communication = st.slider("Rate your communication skills (1-10)", min_value=1, max_value=10)
    ats_score = st.number_input("Enter your ATS score of your resume (out of 100)", min_value=0, max_value=100)
    skills = st.text_input("List your current skills (comma-separated)").split(',')
    preferred_company = st.text_input("Enter your preferred company (or press Enter to skip)")

    advice = []

    if cgpa < 7.0:
        advice.append(f"Focus on improving your CGPA.")
    else:
        advice.append(f"**Good job maintaining a CGPA of {cgpa}.**")

    if communication < 7.0:
        advice.append("**Consider improving your communication skills.**")
    else:
        advice.append("**Your communication skills are good.**")

    if ats_score < 80:
        advice.append("**Work on improving your resume for better ATS scores.**")
    else:
        advice.append("**Your resume seems competitive for ATS.**")

    if preferred_company:
        company_data = data[data['company'] == preferred_company]
        if not company_data.empty:
            avg_interns = company_data['interns'].mean()
            skills_required = company_data['skills_required'].str.split(';').explode().value_counts().index.tolist()
            avg_lpa = company_data['lpa'].mean()

            advice.append(f"Based on previous data, {preferred_company} typically hires an average of {avg_interns:.1f} interns per year.")
            advice.append(f"Skills that are commonly required by {preferred_company} include: {', '.join(skills_required)}.")

            missing_skills = [skill for skill in skills_required if skill not in skills]
            if missing_skills:
                advice.append(f"**Consider developing the following skills to increase your chances with {preferred_company}: {', '.join(missing_skills)}.**")
            else:
                advice.append("**You have the necessary skills for your preferred company.**")

            company_trend = company_data.groupby('year').agg({'num_placed': 'sum', 'lpa': 'mean'}).reset_index()
            if len(company_trend) > 1:
                X_company_num_placed = company_trend['year'].values.reshape(-1, 1)
                y_company_num_placed = company_trend['num_placed'].values

                X_company_lpa = company_trend['year'].values.reshape(-1, 1)
                y_company_lpa = company_trend['lpa'].values

                model_company_num_placed = LinearRegression()
                model_company_num_placed.fit(X_company_num_placed, y_company_num_placed)

                model_company_lpa = LinearRegression()
                model_company_lpa.fit(X_company_lpa, y_company_lpa)

                next_year = np.array([[company_trend['year'].max() + 1]])

                predicted_company_placements = model_company_num_placed.predict(next_year)
                advice.append(f"Predicted placements for {preferred_company} in {next_year[0][0]} (Number of Students): {predicted_company_placements[0]:.0f}")

                predicted_company_lpa = model_company_lpa.predict(next_year)
                advice.append(f"Predicted LPA for {preferred_company} in {next_year[0][0]}: {predicted_company_lpa[0]:.2f}")
            else:
                advice.append(f"Not enough data to predict placements for {preferred_company}.")
        else:
            advice.append(f"No data available for your preferred company: {preferred_company}.")
    else:
        advice.append("Consider applying to companies with higher placement records.")
        if current_year <= 2:
            advice.append("**It's a good time to develop new skills and consider internships.**")
        if 'python' not in skills:
            advice.append("**Learning Python could be beneficial for your career.**")
        else:
            advice.append("**You are on the right track. Keep building your skills and consider internships.**")

    st.subheader("Career Advice after Analysis")
    st.markdown("<ul>", unsafe_allow_html=True)
    for line in advice:
        if "consider" in line.lower() or "focus" in line.lower() or "work on" in line.lower() or "develop" in line.lower():
            st.markdown(f"<li><span style='color:red;'>{line}</span></li>", unsafe_allow_html=True)
        else:
            st.markdown(f"<li>{line}</li>", unsafe_allow_html=True)
    st.markdown("</ul>", unsafe_allow_html=True)


def load_data_from_csv(uploaded_file):
    return pd.read_csv(uploaded_file)

def create_csv_download_link(df):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer.getvalue()

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

    if uploaded_file is None:
        st.sidebar.title("Upload Instructions")
        st.sidebar.write("Please ensure your CSV file has the following columns with the specified data types:")
        st.sidebar.write("""
        - **year**: int (e.g., 2021)
        - **company**: str (e.g., 'Company A')
        - **cgpa**: float (e.g., 8.5)
        - **interns**: int (e.g., 5)
        - **num_placed**: int (e.g., 50)
        - **ats_score**: int (e.g., 75)
        - **skills_required**: str (e.g., 'Python;Java;SQL')
        - **communication**: float (e.g., 7.0)
        - **lpa**: float (e.g., 5.0)
        """)
    else:
        data = load_data_from_csv(uploaded_file)

        if not st.session_state['logged_in']:
            page = st.sidebar.radio("Go to", ["Login", "Register"])
            if page == "Login":
                login()
            elif page == "Register":
                register()
        else:
            st.sidebar.title("Menu")
            menu_option = st.sidebar.selectbox("Choose an option", ["Overall Trends", "Company Trend", "Compare Companies", "User Analysis", "Add New Data"])

            if menu_option == "Overall Trends":
                overall_trends(data)
            elif menu_option == "Company Trend":
                company_name = st.sidebar.text_input("Enter Company Name")
                if company_name:
                    company_trend(data, company_name)
            elif menu_option == "Compare Companies":
                company1 = st.sidebar.text_input("Enter First Company Name")
                company2 = st.sidebar.text_input("Enter Second Company Name")
                if company1 and company2:
                    compare_companies(data, company1, company2)
            elif menu_option == "User Analysis":
                user = st.sidebar.text_input("Enter User Name")
                if user:
                    user_analysis() 
            elif menu_option == "Add New Data":
                st.subheader("Add New Data Row")

                new_data = {
                    'year': st.number_input("Year", min_value=2000, max_value=2100),
                    'company': st.text_input("Company Name"),
                    'cgpa': st.number_input("CGPA", min_value=0.0, max_value=10.0),
                    'interns': st.number_input("Number of Internships", min_value=0),
                    'num_placed': st.number_input("Number of Students Placed", min_value=0),
                    'ats_score': st.number_input("ATS Score", min_value=0),
                    'skills_required': st.text_input("Skills Required"),
                    'communication': st.number_input("Communication Skills", min_value=0.0, max_value=10.0),
                    'lpa': st.number_input("Lakhs Per Annum (LPA)", min_value=0.0),
                }

                if st.button("Add Data", key="add_data_button"):
                    new_data_df = pd.DataFrame([new_data])
                    data = pd.concat([data, new_data_df], ignore_index=True)

                    csv_data = create_csv_download_link(data)

                    st.download_button(
                        label="Download Updated CSV",
                        data=csv_data,
                        file_name="updated_data.csv",
                        mime="text/csv"
                    )

                    st.success("Data added successfully! Download the updated CSV file.")

    if uploaded_file is None:
        st.write("Please upload a dataset to proceed.")
    st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: #333; /* Dark background for contrast */
        color: #f1f1f1; /* Light text color */
        text-align: center;
        padding: 20px;
        font-size: 16px;
        border-top: 2px solid #444;
        box-shadow: 0px -2px 10px rgba(0, 0, 0, 0.2);
    }
    .footer a {
        color: #f1f1f1;
        text-decoration: none;
    }
    .footer a:hover {
        text-decoration: underline;
    }
    </style>
    <div class="footer">
        <p>&copy; 2024 Srikanth Sridhar. All rights reserved.</p>
    </div>
    """,
    unsafe_allow_html=True
)



if __name__ == '__main__':
    main()
