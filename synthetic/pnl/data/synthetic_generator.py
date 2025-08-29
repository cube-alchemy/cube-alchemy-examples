import pandas as pd
import numpy as np
import random
import os
import datetime

def generate_calendar(start_date, end_date):
    """Generate a calendar dimension table with date hierarchies"""
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    calendar_df = pd.DataFrame({
        'date': dates,
        'day': dates.day,
        'month': dates.month,
        'month_name': dates.strftime('%B'),
        'quarter': dates.quarter,
        'year': dates.year,
        'month_year': dates.strftime('%Y-%m'),  # Added month_year for consistency with budget
        'day_of_week': dates.dayofweek,
        'day_name': dates.strftime('%A'),
        'week_of_year': dates.isocalendar().week,
        'is_weekend': dates.dayofweek.isin([5, 6]),
        'is_month_end': dates.is_month_end,
        'is_quarter_end': dates.is_quarter_end,
        'is_year_end': dates.is_year_end
    })
    
    return calendar_df

def generate_synthetic_data(start_date, end_date):
    """Generate synthetic P&L data with the specified date range"""
    
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load dimension tables
    accounts_df = pd.read_csv(os.path.join(script_dir, 'accounts.csv'))
    location_df = pd.read_csv(os.path.join(script_dir, 'location_dim.csv'))
    business_unit_df = pd.read_csv(os.path.join(script_dir, 'business_unit_dim.csv'))
    cost_center_df = pd.read_csv(os.path.join(script_dir, 'cost_center_dim.csv'))
    vendor_df = pd.read_csv(os.path.join(script_dir, 'vendor_dim.csv'))
    project_df = pd.read_csv(os.path.join(script_dir, 'project_dim.csv'))
    
    # Generate calendar
    calendar_df = generate_calendar(start_date, end_date)
    calendar_df.to_csv(os.path.join(script_dir, 'calendar_dim.csv'), index=False)
    
    # Define the dimensions
    dates = calendar_df['date'].tolist()
    location_ids = location_df['location_id'].tolist()
    business_unit_ids = business_unit_df['bu_id'].tolist()
    cost_center_ids = cost_center_df['cost_center_id'].tolist()
    vendor_ids = vendor_df['vendor_id'].tolist()
    project_ids = project_df['project_id'].tolist()
    segments = ['Corporate', 'Retail', 'Government']
    
    # Get the list of account numbers
    account_numbers = accounts_df['account_number'].tolist()
    account_mapping = dict(zip(accounts_df['account_number'], accounts_df['pnl_account_name']))
    
    # Create base data for actuals
    actuals_data = []

    # Generate individual transactions for actuals
    np.random.seed(42)
    
    # Create a range of mean values for each account type
    account_mean_values = {
        'Gross Revenue': (1000, 5000),
        'Sales Returns': (-300, -50),
        'Net Revenue': (700, 4700),
        'Direct Materials': (-1000, -200),
        'Direct Labor': (-800, -100),
        'Manufacturing Overhead': (-400, -50),
        'Marketing': (-500, -100),
        'Salaries': (-8000, -2000),
        'Sales Commissions': (-600, -100),
        'Travel & Entertainment': (-300, -50),
        'Rent': (-2000, -500),
        'Utilities': (-500, -100),
        'Office Supplies': (-200, -50),
        'R&D': (-5000, -1000),
        'Depreciation': (-200, -50),
        'Amortization': (-100, -20),
        'Interest': (-50, -10),
        'Taxes': (-500, -100)
    }
    
    # For each day, location, business unit, etc., generate individual transactions
    for date in dates:
        # Convert to datetime if it's not already
        date_dt = pd.to_datetime(date)
        # Skip weekends for some transaction types
        if date_dt.dayofweek >= 5 and np.random.random() < 0.7:
            continue
            
        # Each account might have different frequencies
        for account_num in account_numbers:
            pnl_account_name = account_mapping[account_num]
            
            # Some accounts might not have daily transactions
            if np.random.random() > 0.3:
                continue
                
            # For each transaction, randomly select from the other dimensions
            location_id = np.random.choice(location_ids)
            location_info = location_df[location_df['location_id'] == location_id].iloc[0]
            country = location_info['country']
            region = location_info['region']
            subregion = location_info['subregion']
            
            # Randomly select business unit
            bu_id = np.random.choice(business_unit_ids)
            bu_info = business_unit_df[business_unit_df['bu_id'] == bu_id].iloc[0]
            business_unit = bu_info['business_unit']
            division = bu_info['division']
            
            # Select segment based on division
            if division == 'Retail':
                segment = 'Retail'
            elif division in ['Banking', 'Medical']:
                segment = 'Corporate'
            else:
                segment = np.random.choice(segments)
                
            # Add cost centers, vendors, and projects for expenses only
            cost_center_id = None
            vendor_id = None
            project_id = None
            
            if 'Revenue' not in pnl_account_name:
                cost_center_id = np.random.choice(cost_center_ids)
                cost_center_info = cost_center_df[cost_center_df['cost_center_id'] == cost_center_id].iloc[0]
                
                # Add vendor for certain expense types
                if pnl_account_name in ['Direct Materials', 'Office Supplies', 'Utilities', 'Marketing']:
                    vendor_id = np.random.choice(vendor_ids)
                
                # Add project for certain strategic expenses
                if pnl_account_name in ['Marketing', 'R&D', 'Travel & Entertainment'] and np.random.random() > 0.5:
                    project_id = np.random.choice(project_ids)
            
            # Filter out combinations that don't make sense
            if pnl_account_name in ['Depreciation', 'Amortization', 'R&D'] and segment != 'Corporate':
                continue
                
            if pnl_account_name in ['Direct Materials', 'Direct Labor', 'Manufacturing Overhead'] and segment == 'Government':
                continue
            
            # Generate amount based on the account type
            min_val, max_val = account_mean_values[pnl_account_name]
            amount = np.random.uniform(min_val, max_val)
            
            # Add some randomness based on day of week, month, etc.
            day_of_week = date_dt.dayofweek
            month = date_dt.month
            
            # Month-end effects
            if date_dt.is_month_end:
                if pnl_account_name in ['Gross Revenue', 'Sales Commissions']:
                    amount *= 1.2  # Month-end boost
                elif pnl_account_name in ['Depreciation', 'Amortization']:
                    amount *= 1.0  # Consistent monthly
            
            # Quarter-end effects
            if date_dt.is_quarter_end:
                if pnl_account_name in ['Marketing', 'Sales Commissions']:
                    amount *= 1.3  # Quarter-end boost
            
            # Create the transaction record with account_number (for actuals)
            # Only include the foreign keys, not the denormalized attributes
            # Keep pnl_account_name temporarily for later filtering
            transaction = {
                'date': date,
                'account_number': account_num,
                'pnl_account_name': pnl_account_name,  # Needed for filtering, will remove later
                'location_id': location_id,
                'bu_id': bu_id,
                'segment': segment,
                'amount': amount
            }
            
            # Add optional dimension foreign keys if applicable
            if cost_center_id:
                transaction['cost_center_id'] = cost_center_id
            
            if vendor_id:
                transaction['vendor_id'] = vendor_id
            
            if project_id:
                transaction['project_id'] = project_id
            
            actuals_data.append(transaction)
    
    # Create the actuals dataframe
    actuals_df = pd.DataFrame(actuals_data)
    
    # Calculate Net Revenue transactions as a reconciliation of Gross Revenue and Sales Returns
    # First identify account numbers for each category
    gross_rev_account_nums = [acc_num for acc_num, acc_name in account_mapping.items() if acc_name == 'Gross Revenue']
    sales_returns_account_nums = [acc_num for acc_num, acc_name in account_mapping.items() if acc_name == 'Sales Returns']
    net_rev_account_nums = [acc_num for acc_num, acc_name in account_mapping.items() if acc_name == 'Net Revenue']
    
    # Filter based on account numbers
    gross_rev = actuals_df[actuals_df['account_number'].isin(gross_rev_account_nums)].copy()
    sales_returns = actuals_df[actuals_df['account_number'].isin(sales_returns_account_nums)].copy()
    
    # Group by the common dimensions
    groupby_cols = ['date', 'bu_id', 'location_id', 'segment']
    
    # Group and sum the amounts
    gross_rev_grouped = gross_rev.groupby(groupby_cols)['amount'].sum().reset_index()
    sales_returns_grouped = sales_returns.groupby(groupby_cols)['amount'].sum().reset_index()
    
    # Join the two dataframes
    net_revenue_df = pd.merge(gross_rev_grouped, sales_returns_grouped, on=groupby_cols, how='outer', suffixes=('_gross', '_returns'))
    net_revenue_df.fillna(0, inplace=True)
    
    # Calculate net revenue
    net_revenue_df['amount'] = net_revenue_df['amount_gross'] + net_revenue_df['amount_returns']
    
    # Add the necessary columns for net revenue transactions
    net_revenue_df = net_revenue_df[groupby_cols + ['amount']].copy()
    
    # Add the required columns to match the actuals_df
    for idx, row in net_revenue_df.iterrows():
        # Create a new transaction for Net Revenue with only the necessary keys
        net_rev_transaction = {
            'date': row['date'],
            'account_number': np.random.choice(net_rev_account_nums),
            'location_id': row['location_id'],
            'bu_id': row['bu_id'],
            'segment': row['segment'],
            'amount': row['amount']
        }
        
        # Find a matching gross revenue row to copy optional dimensions
        matching_gross = gross_rev[
            (gross_rev['date'] == row['date']) & 
            (gross_rev['bu_id'] == row['bu_id']) &
            (gross_rev['location_id'] == row['location_id']) &
            (gross_rev['segment'] == row['segment'])
        ]
        
        if not matching_gross.empty:
            # Copy optional dimension keys if they exist
            for key in ['cost_center_id', 'vendor_id', 'project_id']:
                if key in matching_gross.iloc[0] and pd.notna(matching_gross.iloc[0][key]):
                    net_rev_transaction[key] = matching_gross.iloc[0][key]
            
            # Append to actuals data
            actuals_data.append(net_rev_transaction)
    
    # Recreate actuals dataframe with net revenue transactions
    actuals_df = pd.DataFrame(actuals_data)
    
    # Remove the temporary pnl_account_name column from actuals
    if 'pnl_account_name' in actuals_df.columns:
        actuals_df = actuals_df.drop(columns=['pnl_account_name'])
    
    # Save the actuals data
    actuals_df.to_csv(os.path.join(script_dir, 'actuals.csv'), index=False)
    
    # Create budget data (at business unit and month level)
    # Note: budget uses pnl_account_name instead of account_number
    
    # Extract month-year from date
    actuals_df['month_year'] = pd.to_datetime(actuals_df['date']).dt.strftime('%Y-%m')
    
    # Get the account mapping for budget (which uses pnl_account_name)
    account_to_name = dict(zip(accounts_df['account_number'], accounts_df['pnl_account_name']))
    
    # Create a temporary df with the pnl_account_name for grouping
    budget_prep_df = actuals_df.copy()
    budget_prep_df['pnl_account_name'] = budget_prep_df['account_number'].map(account_to_name)
    
    # Group actuals by month-year and business unit
    # Budget is at a higher level of granularity - only month_year, bu_id, pnl_account_name
    budget_groupby_cols = ['month_year', 'bu_id', 'pnl_account_name']
    budget_df = budget_prep_df.groupby(budget_groupby_cols)['amount'].sum().reset_index()
    
    # Adjust budget amounts to be slightly different from actuals
    budget_df['amount'] = budget_df['amount'] * np.random.uniform(0.9, 1.1, len(budget_df))
    
    # Select only needed columns - normalized approach
    budget_df = budget_df[['month_year', 'bu_id', 'pnl_account_name', 'amount']]
    
    # Save the budget data - using pnl_account_name instead of account_number
    # and month_year instead of separate month and year fields
    budget_df.to_csv(os.path.join(script_dir, 'budget.csv'), index=False)
    
    print(f"Synthetic data generated successfully for period {start_date} to {end_date}")
    print(f"- Generated {len(actuals_df):,} actual transactions")
    print(f"- Generated {len(budget_df):,} budget entries")
    print(f"- Calendar dimension created with {len(calendar_df):,} date records")
    
# If this script is run directly, allow dynamic selection of date range
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate synthetic P&L data for a specific date range')
    parser.add_argument('--start_date', type=str, default='2023-01-01', help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end_date', type=str, default='2023-12-31', help='End date in YYYY-MM-DD format')
    
    args = parser.parse_args()
    
    # Validate dates
    try:
        pd.to_datetime(args.start_date)
        pd.to_datetime(args.end_date)
    except ValueError:
        print("Error: Invalid date format. Please use YYYY-MM-DD format.")
        exit(1)
    
    print(f"Generating synthetic P&L data from {args.start_date} to {args.end_date}")
    generate_synthetic_data(args.start_date, args.end_date)
