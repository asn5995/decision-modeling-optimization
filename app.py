import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from datetime import datetime

st.set_page_config(
    page_title="Cash Matching Optimization",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Cash Matching Optimization")
st.markdown("""
Determine the **minimum-cost portfolio** of bonds that will meet all project cash flow requirements exactly.

- Bonds can be purchased fractionally
- Any interim excess cash can be reinvested at 4% annual (2% semiannual)
- The optimization uses linear programming to find the optimal solution
""")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    reinvestment_rate = st.number_input(
        "Reinvestment Rate (annual %)", 
        min_value=0.0, 
        max_value=20.0, 
        value=4.0, 
        step=0.1,
        help="Annual interest rate for reinvesting excess cash"
    )
    semiannual_rate = reinvestment_rate / 200  # Convert to semiannual decimal

# Main content area
tab1, tab2, tab3 = st.tabs(["📊 Cash Requirements", "📈 Bonds", "📋 Results"])

# Tab 1: Cash Requirements Input
with tab1:
    st.header("Cash Flow Requirements")
    st.markdown("Enter the dates and amounts for cash requirements.")
    
    # Initialize session state for cash requirements
    if 'cash_requirements' not in st.session_state:
        st.session_state.cash_requirements = pd.DataFrame({
            'Date': pd.to_datetime(['2024-01-01', '2024-07-01', '2025-01-01', '2025-07-01', 
                     '2026-01-01', '2026-07-01', '2027-01-01', '2027-07-01']),
            'Amount ($mm)': [7.50, 4.50, 1.00, 1.00, 1.00, 1.00, 1.00, 3.50]
        })
    
    # Editable dataframe for cash requirements
    edited_cash = st.data_editor(
        st.session_state.cash_requirements,
        num_rows="dynamic",
        column_config={
            "Date": st.column_config.DateColumn(
                "Date",
                format="YYYY-MM-DD",
                step=1,
            ),
            "Amount ($mm)": st.column_config.NumberColumn(
                "Amount ($mm)",
                min_value=0.0,
                step=0.01,
                format="$%.2f"
            )
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.session_state.cash_requirements = edited_cash

# Tab 2: Bonds Input
with tab2:
    st.header("Available Bonds")
    st.markdown("Enter bond information: maturity date, coupon rate (annual %), and current price.")
    
    # Initialize session state for bonds
    if 'bonds' not in st.session_state:
        st.session_state.bonds = pd.DataFrame({
            'Maturity': pd.to_datetime(['2024-01-01', '2024-07-01', '2025-01-01', '2025-07-01',
                        '2026-01-01', '2026-07-01', '2027-01-01', '2027-07-01']),
            'Coupon (%)': [7.00, 7.50, 6.75, 0.00, 10.00, 9.00, 10.25, 10.00],
            'Price': [1.00, 1.03, 1.02, 0.81, 1.16, 1.15, 1.23, 1.25]
        })
    
    # Editable dataframe for bonds
    edited_bonds = st.data_editor(
        st.session_state.bonds,
        num_rows="dynamic",
        column_config={
            "Maturity": st.column_config.DateColumn(
                "Maturity Date",
                format="YYYY-MM-DD",
                step=1,
            ),
            "Coupon (%)": st.column_config.NumberColumn(
                "Coupon Rate (annual %)",
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                format="%.2f%%"
            ),
            "Price": st.column_config.NumberColumn(
                "Current Price",
                min_value=0.0,
                step=0.01,
                format="$%.4f"
            )
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.session_state.bonds = edited_bonds

# Tab 3: Results
with tab3:
    st.header("Optimization Results")
    
    if st.button("🚀 Run Optimization", type="primary", use_container_width=True):
        try:
            # Validate inputs
            if len(st.session_state.cash_requirements) == 0:
                st.error("Please enter at least one cash requirement.")
                st.stop()
            
            if len(st.session_state.bonds) == 0:
                st.error("Please enter at least one bond.")
                st.stop()
            
            # Prepare data
            cash_req = st.session_state.cash_requirements.copy()
            bonds = st.session_state.bonds.copy()
            
            # Convert dates to strings for consistency
            # Handle both string and datetime/date objects from data_editor
            try:
                cash_req['Date'] = pd.to_datetime(cash_req['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
                bonds['Maturity'] = pd.to_datetime(bonds['Maturity'], errors='coerce').dt.strftime('%Y-%m-%d')
            except Exception as e:
                st.error(f"Error converting dates: {str(e)}")
                st.stop()
            
            # Drop any rows with invalid dates (NaT becomes 'NaT' string)
            cash_req = cash_req[cash_req['Date'] != 'NaT'].copy()
            bonds = bonds[bonds['Maturity'] != 'NaT'].copy()
            
            if len(cash_req) == 0:
                st.error("No valid cash requirements found. Please check date formats.")
                st.stop()
            
            if len(bonds) == 0:
                st.error("No valid bonds found. Please check date formats.")
                st.stop()
            
            # Sort by date
            cash_req = cash_req.sort_values('Date').reset_index(drop=True)
            bonds = bonds.sort_values('Maturity').reset_index(drop=True)
            
            # Get all unique dates (cash requirements + bond maturities)
            all_dates = sorted(set(cash_req['Date'].tolist() + bonds['Maturity'].tolist()))
            
            # Create needs array for all dates (0 for dates without cash requirements)
            needs_dict = dict(zip(cash_req['Date'], cash_req['Amount ($mm)']))
            needs = np.array([needs_dict.get(d, 0.0) for d in all_dates])
            
            dates = all_dates
            n_dates = len(dates)
            
            # Prepare bond data
            bond_data = bonds.copy()
            bond_data['Coupon'] = bond_data['Coupon (%)'] / 100
            bond_data['C_semi'] = bond_data['Coupon'] / 2
            
            n_bonds = len(bond_data)
            
            # Map maturities to timeline index (1-indexed for period number)
            maturity_to_idx = {d: i for i, d in enumerate(dates, start=1)}
            
            # Cash flow matrix
            CF = np.zeros((n_dates, n_bonds))
            for j in range(n_bonds):
                maturity_date = bond_data.loc[j, 'Maturity']
                if maturity_date in maturity_to_idx:
                    m = maturity_to_idx[maturity_date]  # m is 1-indexed
                    # Coupon payments up to and including maturity period
                    CF[:m, j] += bond_data.loc[j, 'C_semi']
                    # Principal at maturity (m-1 because CF is 0-indexed)
                    CF[m-1, j] += 1.0
                else:
                    # This shouldn't happen since we included all maturities in dates
                    st.warning(f"Bond {j} maturity {maturity_date} not found in timeline")
            
            # Build LP problem
            grow = 1 + semiannual_rate  # Growth factor per half-year
            
            n_vars = n_bonds + n_dates
            A_eq = np.zeros((n_dates, n_vars))
            b_eq = np.zeros(n_dates)
            
            # t = 1
            A_eq[0, :n_bonds] = CF[0, :]
            A_eq[0, n_bonds + 0] = -1.0  # -s_1
            b_eq[0] = needs[0]
            
            # t = 2..T
            for t in range(1, n_dates):
                A_eq[t, :n_bonds] = CF[t, :]
                A_eq[t, n_bonds + t] = -1.0  # -s_t
                A_eq[t, n_bonds + (t-1)] = grow  # +grow*s_{t-1}
                b_eq[t] = needs[t]
            
            # Bounds: x_j >= 0, s_t >= 0
            bounds = [(0, None)] * n_vars
            
            # Objective: minimize upfront cost
            c = np.zeros(n_vars)
            c[:n_bonds] = bond_data['Price'].to_numpy()
            
            # Solve LP
            with st.spinner("Solving optimization problem..."):
                res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
            
            if not res.success:
                st.error(f"❌ Optimization failed: {res.message}")
                st.stop()
            
            x = res.x[:n_bonds]
            s = res.x[n_bonds:]
            
            # Prepare results
            portfolio = bond_data[['Maturity', 'Coupon (%)', 'Price']].copy()
            portfolio['Face Value ($mm)'] = x
            portfolio['Cost ($mm)'] = portfolio['Price'] * portfolio['Face Value ($mm)']
            portfolio = portfolio[portfolio['Face Value ($mm)'] > 1e-6]  # Filter out near-zero holdings
            
            total_cost = portfolio['Cost ($mm)'].sum()
            
            # Reconstruct flows and check balances
            flows = CF @ x
            surplus = np.zeros(n_dates)
            surplus[0] = flows[0] - needs[0]
            for t in range(1, n_dates):
                surplus[t] = grow * surplus[t-1] + flows[t] - needs[t]
            
            summary_cf = pd.DataFrame({
                'Date': dates,
                'Bond Cash In ($mm)': np.round(flows, 6),
                'Required Outflow ($mm)': needs,
                'Surplus End ($mm)': np.round(surplus, 6)
            })
            
            # Display results
            st.success("✅ Optimization completed successfully!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Upfront Cost", f"${total_cost:,.4f} mm")
            with col2:
                st.metric("Number of Bonds Used", len(portfolio))
            
            st.subheader("📊 Optimal Portfolio")
            st.dataframe(
                portfolio.style.format({
                    'Coupon (%)': '{:.2f}%',
                    'Price': '${:.4f}',
                    'Face Value ($mm)': '{:.6f}',
                    'Cost ($mm)': '${:.4f}'
                }),
                use_container_width=True,
                hide_index=True
            )
            
            st.subheader("💵 Cash Flow & Surplus Analysis")
            st.dataframe(
                summary_cf.style.format({
                    'Bond Cash In ($mm)': '${:.6f}',
                    'Required Outflow ($mm)': '${:.2f}',
                    'Surplus End ($mm)': '${:.6f}'
                }),
                use_container_width=True,
                hide_index=True
            )
            
            # Validation
            if np.all(surplus >= -1e-6):
                st.success("✅ All constraints satisfied. No negative surplus detected.")
            else:
                st.warning("⚠️ Warning: Some negative surplus detected. Please review the inputs.")
            
            # Download results
            st.subheader("📥 Download Results")
            csv_portfolio = portfolio.to_csv(index=False)
            csv_cashflow = summary_cf.to_csv(index=False)
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download Portfolio",
                    data=csv_portfolio,
                    file_name="optimal_portfolio.csv",
                    mime="text/csv"
                )
            with col2:
                st.download_button(
                    label="Download Cash Flow",
                    data=csv_cashflow,
                    file_name="cash_flow_analysis.csv",
                    mime="text/csv"
                )
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    Cash Matching Optimization Tool | Built with Streamlit
</div>
""", unsafe_allow_html=True)

