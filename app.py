import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration (Must be the very first Streamlit command)
st.set_page_config(
    page_title="Enterprise Analytics Portfolio",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Data Ingestion with Caching 
# This prevents the app from reloading the CSV every time you click a button
@st.cache_data
def load_data():
    df = pd.read_csv('customer_personas_final.csv')
    
    # Map the raw mathematical IDs to our corporate business names
    persona_mapping = {
        0: "Dormant/Struggling Accounts",
        1: "Everyday Transactors",
        2: "High-Risk Revolvers",
        3: "Premium Transactors"
    }
    df['PERSONA_NAME'] = df['PERSONA_ID'].map(persona_mapping)
    return df

df = load_data()

# 3. Sidebar Navigation
st.sidebar.title("Portfolio Navigation")
project_selection = st.sidebar.radio(
    "Select Analytics Module:",
    (
        "1. High-Net-Worth Segmentation",
        "2. Transaction Fraud Detection (Pending)",
        "3. Macro Credit Stress Index (Pending)"
    )
)

st.sidebar.markdown("---")
st.sidebar.info("Developed by a Senior Corporate Data Scientist")

# 4. Main Page Routing
if project_selection == "1. High-Net-Worth Segmentation":
    st.title("💳 Credit Card Customer Segmentation")
    st.markdown("Unsupervised Machine Learning (PCA + K-Means) to discover actionable product personas.")
    
    # Create the 3-tab layout
    tab1, tab2, tab3 = st.tabs([
        "📊 Executive Summary", 
        "🎯 Strategy & Profiling", 
        "🔍 Single Customer Lookup"
    ])
    
    with tab1:
        st.header("Executive Summary")
        st.markdown("High-level portfolio metrics and mathematical cluster validation.")
        
        # 1. Top-Level KPIs using Streamlit Columns
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Customers", f"{len(df):,}")
        col2.metric("Identified Personas", df['PERSONA_ID'].nunique())
        col3.metric("Avg Credit Limit", f"${df['CREDIT_LIMIT'].mean():,.0f}")
        col4.metric("Avg Purchases", f"${df['PURCHASES'].mean():,.0f}")
        
        st.markdown("---")
        
        # 2. 2D PCA Cluster Projection
        st.subheader("Customer Segments (2D PCA Projection)")
        st.write("This visualization compresses 17 financial behaviors into a 2D mathematical map. Distinct boundaries prove our unsupervised strategy successfully isolated unique customer behaviors.")
        
        # Interactive Plotly Scatter Plot
        fig = px.scatter(
            df, 
            x='PC1', 
            y='PC2', 
            color='PERSONA_NAME',
            hover_data={'CUST_ID': True, 'BALANCE': ':$,.2f', 'PURCHASES': ':$,.2f', 'PC1': False, 'PC2': False},
            color_discrete_sequence=px.colors.qualitative.Bold,
            title="Behavioral Boundaries"
        )
        
        # Clean up the chart UI
        fig.update_layout(legend_title_text='Customer Persona')
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        st.header("Persona Strategy & Behavioral Profiling")
        st.markdown("Compare individual cluster behaviors against the global portfolio average to design targeted product strategies.")
        
        # 1. Define the financial metrics we want to analyze
        metrics_to_plot = ['BALANCE', 'PURCHASES', 'CASH_ADVANCE', 'CREDIT_LIMIT', 'MINIMUM_PAYMENTS']
        
        # 2. Calculate global baseline averages
        global_avg = df[metrics_to_plot].mean()
        
        # 3. Interactive Dropdown for Persona Selection
        st.markdown("### Select Target Audience")
        selected_persona = st.selectbox("Choose a persona to profile:", df['PERSONA_NAME'].unique())
        
        # 4. Calculate averages for the selected persona
        persona_avg = df[df['PERSONA_NAME'] == selected_persona][metrics_to_plot].mean()
        
        # 5. Data Wrangling: Combine them into a single matrix for Plotly
        comparison_df = pd.DataFrame({
            'Financial Metric': metrics_to_plot,
            selected_persona: persona_avg.values,
            'Global Average': global_avg.values
        })
        
        # Melt the DataFrame to format it for grouped bar charts
        melted_df = comparison_df.melt(
            id_vars=['Financial Metric'], 
            var_name='Cohort', 
            value_name='Average Value ($)'
        )
        
        # 6. Build the Interactive Grouped Bar Chart
        fig_bar = px.bar(
            melted_df, 
            x='Financial Metric', 
            y='Average Value ($)', 
            color='Cohort',
            barmode='group',
            # Use a striking blue for the persona, and a muted grey for the baseline
            color_discrete_sequence=['#1f77b4', '#d3d3d3'], 
            title=f"Behavioral Fingerprint: {selected_persona} vs. Global Portfolio"
        )
        
        # Format the y-axis as currency
        fig_bar.update_layout(yaxis_tickformat="$,.0f")
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # 7. Automated Strategic Recommendations
        st.subheader("Recommended Product Strategy")
        
        if selected_persona == "Premium Transactors":
            st.success("**Target Action: Premium Card Upgrades & Travel Rewards.** \n\nThese users carry high limits and maximize purchases. They are highly profitable through interchange fees. Do not target with interest-rate promotions; instead, offer luxury partnerships and point multipliers.")
        
        elif selected_persona == "High-Risk Revolvers":
            st.error("**Target Action: Balance Transfer & Personal Loan Conversion.** \n\nHigh flight/default risk due to maxed-out cash advances. Intervene immediately with structured, fixed-rate repayment plans to convert high-interest debt into secure, manageable loans.")
        
        elif selected_persona == "Everyday Transactors":
            st.info("**Target Action: Retention & Engagement.** \n\nReliable convenience users who pay off their balances. Increase our share of their wallet by offering targeted grocery or gas cashback multipliers.")
        
        elif selected_persona == "Dormant/Struggling Accounts":
            st.warning("**Target Action: Reactivation Campaigns.** \n\nLow overall engagement. Trigger new spend behavior with micro-promotions like 'Spend $100 this month, get a $20 statement credit'.")
        
    with tab3:
        st.header("Customer Intelligence Engine")
        st.markdown("Query individual customer IDs to retrieve their behavioral classification and automated Next Best Action (NBA).")
        
        # 1. Search Bar for Customer ID
        search_id = st.text_input("Enter Customer ID (e.g., C10001, C10002):", "C10001").strip().upper()
        
        if search_id:
            # 2. Query the database
            customer_data = df[df['CUST_ID'] == search_id]
            
            if customer_data.empty:
                st.error(f"Customer ID '{search_id}' not found in the portfolio database.")
            else:
                st.success("Customer Record Located")
                
                # Extract the assigned persona
                customer_persona = customer_data['PERSONA_NAME'].values[0]
                
                st.markdown(f"### Persona Classification: **{customer_persona}**")
                
                # 3. Display their specific financial profile
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Current Balance", f"${customer_data['BALANCE'].values[0]:,.2f}")
                col2.metric("Total Purchases", f"${customer_data['PURCHASES'].values[0]:,.2f}")
                col3.metric("Cash Advance", f"${customer_data['CASH_ADVANCE'].values[0]:,.2f}")
                col4.metric("Credit Limit", f"${customer_data['CREDIT_LIMIT'].values[0]:,.2f}")
                
                st.markdown("---")
                
                # 4. The Decision Engine (Next Best Action)
                st.subheader("Decision Engine: Next Best Action (NBA)")
                
                if customer_persona == "Premium Transactors":
                    st.info("🎯 **Automated NBA:** Route to Premium Servicing. Pre-approve for Amex Platinum upgrade. Dispatch targeted email featuring luxury airline transfer partners.")
                
                elif customer_persona == "High-Risk Revolvers":
                    st.warning("⚠️ **Automated NBA:** Flag account for credit risk review. Suppress all credit line increase offers. Trigger 'Balance Transfer to Fixed Installment' campaign via mobile app.")
                
                elif customer_persona == "Everyday Transactors":
                    st.info("🎯 **Automated NBA:** Deploy dynamic spend multipliers. Trigger 3x points on grocery and transit categories for the next 30 days to drive primary-card behavior.")
                
                elif customer_persona == "Dormant/Struggling Accounts":
                    st.info("🎯 **Automated NBA:** Suppress cross-sell campaigns. Trigger a 'Zero-Fee Balance Transfer' offer to consolidate external debt, or a $50 statement credit for spending $250 this week.")
else:
    st.title("Module Under Construction")
    st.info("This section of the portfolio will be executed in Phase 2 and 3.")