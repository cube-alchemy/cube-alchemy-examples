"""
P&L Data Generator
Creates realistic synthetic budget and actuals data for a profit and loss dashboard.

Key Parameters:
- TARGET_ANNUAL_REVENUE: 20M USD
- TARGET_NET_MARGIN: 19%
- Seasonality patterns included
- Realistic variance between actuals and budget
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION PARAMETERS - Easy to tweak
# ============================================================================

# Financial Targets (calculated backwards from 19% net margin with 25% tax rate)
TARGET_ANNUAL_REVENUE = 80_000_000  # $80M per year
TARGET_NET_MARGIN = 0.19           # 19% net margin
# Working backwards: Net margin 19% with 25% tax rate means pre-tax margin of 25.3%
# So total costs before tax should be 74.7% of revenue
TARGET_COGS_RATIO = 0.69           # 69% of revenue (MAJOR cost increase needed!)
TARGET_OPEX_RATIO = 0.04           # 4% of revenue
TARGET_DEPRECIATION_RATIO = 0.005  # 0.5% of revenue
TARGET_INTEREST_RATIO = 0.002      # 0.2% of revenue
TARGET_TAX_RATIO = 0.005           # 0.5% of revenue (will calculate actual tax at 25%)

# Seasonality (monthly multipliers - higher = more revenue that month)
SEASONALITY = {
    1: 0.85,   # January - slower start
    2: 0.90,   # February 
    3: 1.05,   # March - Q1 end push
    4: 0.95,   # April
    5: 1.00,   # May
    6: 1.10,   # June - Q2 end push
    7: 0.90,   # July - summer slowdown
    8: 0.85,   # August - vacation time
    9: 1.05,   # September - back to work
    10: 1.10,  # October
    11: 1.15,  # November - holiday season
    12: 1.20   # December - year-end push
}

# Variance parameters
BUDGET_VS_ACTUAL_VARIANCE = 0.15   # ±15% variance between budget and actuals
MONTHLY_VARIANCE = 0.10            # ±10% monthly variance within actuals
DAILY_VARIANCE = 0.05              # ±5% daily variance

# Data generation parameters
START_DATE = '2024-01-01'
END_DATE = '2025-09-30'
TRANSACTION_FREQUENCY = {
    'Revenue': 100,         # More frequent revenue transactions
    'COGS': 80,            # Regular COGS transactions
    'Operating Expenses': 60,  # Regular operating expenses
    'Depreciation & Amortization': 12,  # Monthly depreciation
    'Interest': 12          # Monthly interest
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_dimensions():
    """Load all dimension tables."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    dims_path = script_dir / 'dimensions'
    
    accounts = pd.read_csv(dims_path / 'accounts.csv')
    business_units = pd.read_csv(dims_path / 'business_unit_dim.csv')
    locations = pd.read_csv(dims_path / 'location_dim.csv')
    cost_centers = pd.read_csv(dims_path / 'cost_center_dim.csv')
    projects = pd.read_csv(dims_path / 'project_dim.csv')
    vendors = pd.read_csv(dims_path / 'vendor_dim.csv')
    pnl_mapping = pd.read_csv(dims_path / 'pnl_report_mapping.csv')
    
    return {
        'accounts': accounts,
        'business_units': business_units,
        'locations': locations,
        'cost_centers': cost_centers,
        'projects': projects,
        'vendors': vendors,
        'pnl_mapping': pnl_mapping
    }

def get_monthly_target(month, category, annual_target):
    """Calculate monthly target with seasonality."""
    base_monthly = annual_target / 12
    seasonal_multiplier = SEASONALITY.get(month, 1.0)
    return base_monthly * seasonal_multiplier

def apply_variance(amount, variance_pct):
    """Apply random variance to an amount."""
    variance = random.uniform(-variance_pct, variance_pct)
    return amount * (1 + variance)

def apply_monthly_category_variance(amount, category, month):
    """Apply category-specific monthly variance to make expenses more realistic (reduced variance)."""
    # Different expense categories have different volatility patterns (reduced from previous)
    variance_patterns = {
        'COGS': 0.03,                    # COGS is fairly stable (reduced from 0.08)
        'Operating Expenses': 0.05,      # OpEx can vary slightly (reduced from 0.12)
        'Depreciation & Amortization': 0.01,  # Depreciation is very stable (reduced from 0.03)
        'Interest': 0.02,                # Interest is fairly stable (reduced from 0.05)
        'Revenue': 0.04,                 # Revenue has moderate variance (reduced from 0.10)
        'Taxes': 0.02                    # Taxes are fairly stable
    }
    
    # Add seasonal effects for some categories (reduced impact)
    seasonal_effects = {
        'Operating Expenses': {
            12: 1.08,  # December bonuses (reduced from 1.15)
            1: 0.98,   # January cost cutting (reduced impact)
            7: 0.96,   # July summer slowdown (reduced impact)
            8: 0.96    # August vacation period (reduced impact)
        },
        'COGS': {
            11: 1.04,  # November inventory build-up (reduced from 1.10)
            12: 1.02,  # December holiday production (reduced from 1.05)
            1: 0.98    # January slowdown (reduced impact)
        }
    }
    
    base_variance = variance_patterns.get(category, 0.03)
    seasonal_multiplier = seasonal_effects.get(category, {}).get(month, 1.0)
    
    # Apply both random variance and seasonal effects
    varied_amount = apply_variance(amount, base_variance)
    return varied_amount * seasonal_multiplier

def get_business_unit_weights():
    """Define relative size/revenue contribution of each business unit."""
    return {
        1: 0.25,  # Consumer Products - 25%
        2: 0.20,  # Industrial Solutions - 20%
        3: 0.15,  # Healthcare Services - 15%
        4: 0.15,  # Financial Services - 15%
        5: 0.10,  # Technology Software - 10%
        6: 0.08,  # Technology Hardware - 8%
        7: 0.04,  # Energy Renewable - 4%
        8: 0.03   # Energy Traditional - 3%
    }

def get_bu_cost_structure_multipliers():
    """Define cost structure variations by business unit type (subtle but realistic adjustments)."""
    return {
        1: {'cogs': 1.02, 'opex': 0.98, 'depreciation': 0.95, 'interest': 1.00, 'taxes': 1.00},   # Consumer Products
        2: {'cogs': 1.04, 'opex': 0.96, 'depreciation': 1.05, 'interest': 1.01, 'taxes': 1.00},   # Industrial
        3: {'cogs': 0.96, 'opex': 1.04, 'depreciation': 0.98, 'interest': 0.98, 'taxes': 1.00},   # Healthcare
        4: {'cogs': 0.92, 'opex': 1.06, 'depreciation': 0.94, 'interest': 0.96, 'taxes': 1.00},   # Financial
        5: {'cogs': 0.94, 'opex': 1.05, 'depreciation': 0.96, 'interest': 0.94, 'taxes': 1.00},   # Tech Software
        6: {'cogs': 1.01, 'opex': 1.00, 'depreciation': 1.02, 'interest': 1.00, 'taxes': 1.00},   # Tech Hardware
        7: {'cogs': 0.98, 'opex': 1.01, 'depreciation': 1.08, 'interest': 1.04, 'taxes': 1.00},   # Energy Renewable
        8: {'cogs': 1.00, 'opex': 0.99, 'depreciation': 1.06, 'interest': 1.02, 'taxes': 1.00}    # Energy Traditional
    }

def get_account_weights_by_category():
    """Define how much each account contributes within its category."""
    return {
        'Revenue': {
            'Gross Revenue': 1.0,
            'Sales Returns': -0.03  # 3% returns (negative impact on revenue)
        },
        'COGS': {
            'Direct Materials': 0.55,  # Slightly varied from 0.60
            'Direct Labor': 0.30,     # Slightly varied from 0.25
            'Manufacturing Overhead': 0.15
        },
        'Operating Expenses': {
            'Marketing': 0.2,      # Reduced from 0.30
            'Sales': 0.17,          # Reduced from 0.25
            'Administrative': 0.1,  # Reduced from 0.20
            'R&D': 0.2,            # Increased from 0.15
            'IT': 0.13,             # Reduced from 0.10
            'Salaries': 0.2        # Added explicit salaries component
        }
    }

def get_account_detail_weights():
    """Define how amounts should be distributed across account details within each pnl_account_name."""
    return {
        # Weights for account distribution within each pnl_account_name
        'Gross Revenue': {
            1001: 0.45,  # Online Product Sales (45% of Gross Revenue)
            1002: 0.35,  # Retail Product Sales (35% of Gross Revenue)
            1003: 0.10,  # Wholesale Product Sales (10% of Gross Revenue)
            1201: 0.04,  # Bulk Sales (4% of Gross Revenue)
            1202: 0.04,  # Service Fees - Recurring (4% of Gross Revenue)
            1203: 0.02,  # Licensing Income (2% of Gross Revenue)
        },
        'Sales Returns': {
            1301: 0.60,  # E-commerce Sales (60% of Sales Returns)
            1302: 0.40,  # Direct Sales (40% of Sales Returns)
        },
        'Direct Materials': {
            2001: 0.50,  # Raw Materials Cost (50% of Direct Materials)
            2002: 0.30,  # Packaging Materials (30% of Direct Materials)
            2003: 0.20,  # Component Costs (20% of Direct Materials)
        },
        'Direct Labor': {
            2101: 0.40,  # Production Labor (40% of Direct Labor)
            2102: 0.25,  # Assembly Labor (25% of Direct Labor)
            2103: 0.15,  # Quality Control Labor (15% of Direct Labor)
            2104: 0.20,  # Manufacturing Labor (20% of Direct Labor)
        },
        'Manufacturing Overhead': {
            2201: 0.60,  # Factory Overhead (60% of Manufacturing Overhead)
            2202: 0.40,  # Production Overhead (40% of Manufacturing Overhead)
        },
        'Marketing': {
            3001: 0.40,  # Advertising Expenses (40% of Marketing)
            3002: 0.30,  # Promotional Costs (30% of Marketing)
            3003: 0.30,  # Marketing Campaigns (30% of Marketing)
        },
        'Salaries': {
            3101: 0.30,  # Executive Salaries (30% of Salaries)
            3102: 0.50,  # Staff Salaries (50% of Salaries)
            3103: 0.20,  # Manager Salaries (20% of Salaries)
        },
        'Sales Commissions': {
            3201: 0.70,  # Sales Team Commissions (70% of Sales Commissions)
            3202: 0.30,  # Agent Commissions (30% of Sales Commissions)
        },
        'Travel & Entertainment': {
            3301: 0.40,  # Business Travel (40% of Travel & Entertainment)
            3302: 0.30,  # Client Entertainment (30% of Travel & Entertainment)
            3303: 0.30,  # Employee Travel (30% of Travel & Entertainment)
        },
        'Rent': {
            3401: 0.60,  # Office Rent (60% of Rent)
            3402: 0.40,  # Warehouse Rent (40% of Rent)
        },
        'Utilities': {
            3501: 0.80,  # Electricity (80% of Utilities)
            3502: 0.20,  # Water and Sewage (20% of Utilities)
        },
        'Office Supplies': {
            3601: 0.30,  # Stationery (30% of Office Supplies)
            3602: 0.40,  # Office Equipment (40% of Office Supplies)
            3603: 0.30,  # IT Supplies (30% of Office Supplies)
        },
        'R&D': {
            3701: 0.55,  # Research Expenses (55% of R&D)
            3702: 0.45,  # Development Costs (45% of R&D)
        },
        'Depreciation': {
            4001: 0.50,  # Equipment Depreciation (50% of Depreciation)
            4002: 0.30,  # Building Depreciation (30% of Depreciation)
            4003: 0.20,  # Vehicle Depreciation (20% of Depreciation)
        },
        'Amortization': {
            4101: 0.65,  # Intangible Amortization (65% of Amortization)
            4102: 0.35,  # Patent Amortization (35% of Amortization)
        },
        'Interest': {
            5001: 0.65,  # Loan Interest (65% of Interest)
            5002: 0.25,  # Credit Interest (25% of Interest)
            5003: 0.10,  # Investment Interest (10% of Interest)
        },
        'Taxes': {
            5101: 0.75,  # Income Tax (75% of Taxes)
            5102: 0.15,  # Property Tax (15% of Taxes)
            5103: 0.10,  # Sales Tax (10% of Taxes)
        }
    }

def get_account_sign(category):
    """Return the sign multiplier for different P&L categories."""
    signs = {
        'Revenue': 1,                        # Positive
        'COGS': -1,                         # Negative (cost)
        'Operating Expenses': -1,            # Negative (cost)
        'Depreciation & Amortization': -1,   # Negative (cost)
        'Interest': -1,                     # Negative (cost)
        'Taxes': -1                         # Negative (cost)
    }
    return signs.get(category, 1)

def calculate_tax_amount(revenue, cogs, opex, depreciation, interest, tax_rate=0.25):
    """Calculate tax amount based on pre-tax income with realistic corporate tax rate."""
    pre_tax_income = revenue - abs(cogs) - abs(opex) - abs(depreciation) - abs(interest)
    if pre_tax_income > 0:
        return pre_tax_income * tax_rate
    else:
        return 0  # No taxes on losses

# ============================================================================
# CALENDAR DIMENSION
# ============================================================================

def create_calendar_dim():
    """Create calendar dimension table."""
    start = datetime.strptime(START_DATE, '%Y-%m-%d')
    end = datetime.strptime(END_DATE, '%Y-%m-%d')
    
    dates = []
    current = start
    while current <= end:
        dates.append({
            'date': current.strftime('%Y-%m-%d'),
            'year': current.year,
            'month': current.month,
            'day': current.day,
            'quarter': f"Q{((current.month - 1) // 3) + 1}",
            'month_name': current.strftime('%B'),
            'day_name': current.strftime('%A'),
            'is_weekend': current.weekday() >= 5,
            'week_of_year': current.isocalendar()[1],
            'month_year': current.strftime('%Y-%m')
        })
        current += timedelta(days=1)
    
    return pd.DataFrame(dates)

# ============================================================================
# BUDGET GENERATION
# ============================================================================

def generate_budget_data(dims):
    """Generate monthly budget data by business unit and P&L account."""
    budget_data = []
    bu_weights = get_business_unit_weights()
    account_weights = get_account_weights_by_category()
    
    # Get unique P&L categories and their accounts
    accounts_by_category = dims['accounts'].groupby('pnl_category')['pnl_account_name'].unique().to_dict()
    
    # Generate budget for all years in the date range
    start_date = datetime.strptime(START_DATE, '%Y-%m-%d')
    end_date = datetime.strptime(END_DATE, '%Y-%m-%d')
    
    current_year = start_date.year
    while current_year <= end_date.year:
        # Determine which months to include for this year
        if current_year == start_date.year:
            start_month = start_date.month
        else:
            start_month = 1
            
        if current_year == end_date.year:
            end_month = end_date.month
        else:
            end_month = 12
        
        for month in range(start_month, end_month + 1):
            month_year = f"{current_year}-{month:02d}"
            
            for bu_id, bu_weight in bu_weights.items():
                
                # Revenue
                if 'Revenue' in accounts_by_category:
                    monthly_revenue = get_monthly_target(month, 'Revenue', TARGET_ANNUAL_REVENUE * bu_weight)
                    
                    for account_name in accounts_by_category['Revenue']:
                        if account_name in account_weights['Revenue']:
                            account_amount = monthly_revenue * account_weights['Revenue'][account_name]
                            # Apply enhanced variance with revenue-specific patterns
                            varied_amount = apply_monthly_category_variance(account_amount, 'Revenue', month)
                            # Apply correct sign (Revenue is positive)
                            signed_amount = varied_amount * get_account_sign('Revenue')
                            budget_data.append({
                                'month_year': month_year,
                                'bu_id': bu_id,
                                'pnl_account_name': account_name,
                                'amount': round(signed_amount / 100) * 100  # Round to nearest hundred
                            })
                
                # COGS
                if 'COGS' in accounts_by_category:
                    bu_multipliers = get_bu_cost_structure_multipliers()
                    cogs_multiplier = bu_multipliers[bu_id]['cogs']
                    base_monthly_cogs = get_monthly_target(month, 'COGS', TARGET_ANNUAL_REVENUE * TARGET_COGS_RATIO * bu_weight)
                    monthly_cogs = base_monthly_cogs * cogs_multiplier
                    
                    for account_name in accounts_by_category['COGS']:
                        # Map account names to weights
                        if 'Materials' in account_name:
                            weight = account_weights['COGS']['Direct Materials']
                        elif 'Labor' in account_name:
                            weight = account_weights['COGS']['Direct Labor']
                        elif 'Overhead' in account_name:
                            weight = account_weights['COGS']['Manufacturing Overhead']
                        else:
                            weight = 1.0 / len(accounts_by_category['COGS'])
                        
                        account_amount = monthly_cogs * weight
                        # Apply enhanced variance with category-specific patterns
                        varied_amount = apply_monthly_category_variance(account_amount, 'COGS', month)
                        # Apply correct sign (COGS is negative)
                        signed_amount = varied_amount * get_account_sign('COGS')
                        budget_data.append({
                            'month_year': month_year,
                            'bu_id': bu_id,
                            'pnl_account_name': account_name,
                            'amount': round(signed_amount / 100) * 100  # Round to nearest hundred
                        })
                
                # Operating Expenses
                if 'Operating Expenses' in accounts_by_category:
                    bu_multipliers = get_bu_cost_structure_multipliers()
                    opex_multiplier = bu_multipliers[bu_id]['opex']
                    base_monthly_opex = get_monthly_target(month, 'Operating Expenses', TARGET_ANNUAL_REVENUE * TARGET_OPEX_RATIO * bu_weight)
                    monthly_opex = base_monthly_opex * opex_multiplier
                    
                    for account_name in accounts_by_category['Operating Expenses']:
                        # More realistic distribution based on account name
                        if 'Marketing' in account_name:
                            weight = account_weights['Operating Expenses']['Marketing']
                        elif 'Sales' in account_name or 'Commission' in account_name:
                            weight = account_weights['Operating Expenses']['Sales']
                        elif 'Administrative' in account_name or 'Office' in account_name or 'Rent' in account_name or 'Utilities' in account_name:
                            weight = account_weights['Operating Expenses']['Administrative']
                        elif 'R&D' in account_name:
                            weight = account_weights['Operating Expenses']['R&D']
                        elif 'IT' in account_name:
                            weight = account_weights['Operating Expenses']['IT']
                        elif 'Salaries' in account_name:
                            weight = account_weights['Operating Expenses']['Salaries']
                        else:
                            weight = 1.0 / len(accounts_by_category['Operating Expenses'])
                        
                        account_amount = monthly_opex * weight
                        # Apply enhanced variance with category-specific patterns
                        varied_amount = apply_monthly_category_variance(account_amount, 'Operating Expenses', month)
                        # Apply correct sign (Operating Expenses are negative)
                        signed_amount = varied_amount * get_account_sign('Operating Expenses')
                        budget_data.append({
                            'month_year': month_year,
                            'bu_id': bu_id,
                            'pnl_account_name': account_name,
                            'amount': round(signed_amount / 100) * 100  # Round to nearest hundred
                        })
                
                # Depreciation & Amortization
                if 'Depreciation & Amortization' in accounts_by_category:
                    bu_multipliers = get_bu_cost_structure_multipliers()
                    depreciation_multiplier = bu_multipliers[bu_id]['depreciation']
                    base_monthly_depreciation = get_monthly_target(month, 'Depreciation', TARGET_ANNUAL_REVENUE * TARGET_DEPRECIATION_RATIO * bu_weight)
                    monthly_depreciation = base_monthly_depreciation * depreciation_multiplier
                    
                    for account_name in accounts_by_category['Depreciation & Amortization']:
                        # Apply enhanced variance (depreciation is usually stable)
                        varied_amount = apply_monthly_category_variance(monthly_depreciation, 'Depreciation & Amortization', month)
                        # Apply correct sign (Depreciation is negative)
                        signed_amount = varied_amount * get_account_sign('Depreciation & Amortization')
                        budget_data.append({
                            'month_year': month_year,
                            'bu_id': bu_id,
                            'pnl_account_name': account_name,
                            'amount': round(signed_amount / 100) * 100  # Round to nearest hundred
                        })
                
                # Interest
                if 'Interest' in accounts_by_category:
                    bu_multipliers = get_bu_cost_structure_multipliers()
                    interest_multiplier = bu_multipliers[bu_id]['interest']
                    base_monthly_interest = get_monthly_target(month, 'Interest', TARGET_ANNUAL_REVENUE * TARGET_INTEREST_RATIO * bu_weight)
                    monthly_interest = base_monthly_interest * interest_multiplier
                    
                    for account_name in accounts_by_category['Interest']:
                        # Apply enhanced variance
                        varied_amount = apply_monthly_category_variance(monthly_interest, 'Interest', month)
                        # Apply correct sign (Interest is negative)
                        signed_amount = varied_amount * get_account_sign('Interest')
                        budget_data.append({
                            'month_year': month_year,
                            'bu_id': bu_id,
                            'pnl_account_name': account_name,
                            'amount': round(signed_amount / 100) * 100  # Round to nearest hundred
                        })
                
                # Taxes (calculated based on pre-tax income)
                if 'Taxes' in accounts_by_category:
                    bu_multipliers = get_bu_cost_structure_multipliers()
                    tax_multiplier = bu_multipliers[bu_id]['taxes']
                    
                    # Calculate pre-tax income components for this BU and month
                    monthly_revenue = get_monthly_target(month, 'Revenue', TARGET_ANNUAL_REVENUE * bu_weight)
                    monthly_cogs = get_monthly_target(month, 'COGS', TARGET_ANNUAL_REVENUE * TARGET_COGS_RATIO * bu_weight) * bu_multipliers[bu_id]['cogs']
                    monthly_opex = get_monthly_target(month, 'Operating Expenses', TARGET_ANNUAL_REVENUE * TARGET_OPEX_RATIO * bu_weight) * bu_multipliers[bu_id]['opex']
                    monthly_depreciation = get_monthly_target(month, 'Depreciation', TARGET_ANNUAL_REVENUE * TARGET_DEPRECIATION_RATIO * bu_weight) * bu_multipliers[bu_id]['depreciation']
                    monthly_interest = get_monthly_target(month, 'Interest', TARGET_ANNUAL_REVENUE * TARGET_INTEREST_RATIO * bu_weight) * bu_multipliers[bu_id]['interest']
                    
                    # Calculate tax based on pre-tax income
                    monthly_tax = calculate_tax_amount(monthly_revenue, monthly_cogs, monthly_opex, monthly_depreciation, monthly_interest) * tax_multiplier
                    
                    for account_name in accounts_by_category['Taxes']:
                        # Apply enhanced variance
                        varied_amount = apply_monthly_category_variance(monthly_tax, 'Taxes', month)
                        # Apply correct sign (Taxes are negative)
                        signed_amount = varied_amount * get_account_sign('Taxes')
                        budget_data.append({
                            'month_year': month_year,
                            'bu_id': bu_id,
                            'pnl_account_name': account_name,
                            'amount': round(signed_amount / 100) * 100  # Round to nearest hundred
                        })
        
        current_year += 1  # Move to next year
    
    return pd.DataFrame(budget_data)

# ============================================================================
# ACTUALS GENERATION
# ============================================================================

def generate_actuals_data(dims, budget_df):
    """Generate daily actuals data based on budget with realistic variance."""
    actuals_data = []
    calendar = create_calendar_dim()
    
    # Get account detail weights for distribution
    account_detail_weights = get_account_detail_weights()
    
    # Create mappings
    # Map from pnl_account_name to all associated account_numbers
    account_number_by_pnl_name = {}
    for _, row in dims['accounts'].iterrows():
        if row['pnl_account_name'] not in account_number_by_pnl_name:
            account_number_by_pnl_name[row['pnl_account_name']] = []
        account_number_by_pnl_name[row['pnl_account_name']].append(row['account_number'])
    
    # Map from account_number to pnl_account_detail
    account_detail_mapping = dims['accounts'].set_index('account_number')['pnl_account_detail'].to_dict()
    # Map from account_number to pnl_category
    category_by_account = dims['accounts'].set_index('account_number')['pnl_category'].to_dict()
    # Map from account_number to pnl_account_name
    account_name_by_number = dims['accounts'].set_index('account_number')['pnl_account_name'].to_dict()
    
    for _, budget_row in budget_df.iterrows():
        month_year = budget_row['month_year']
        year, month = map(int, month_year.split('-'))
        bu_id = budget_row['bu_id']
        pnl_account_name = budget_row['pnl_account_name']
        monthly_budget = budget_row['amount']
        
        # Apply budget vs actual variance
        monthly_actual = apply_variance(monthly_budget, BUDGET_VS_ACTUAL_VARIANCE)
        
        # Get account numbers for this pnl_account_name
        account_numbers = account_number_by_pnl_name.get(pnl_account_name, [])
        if not account_numbers:
            # If no account numbers found, use a default
            account_numbers = [9999]
            print(f"Warning: No account numbers found for {pnl_account_name}")
            continue
        
        # Get days in this month
        month_days = calendar[
            (calendar['year'] == year) & 
            (calendar['month'] == month)
        ].copy()
        
        # Get the category based on the first account number (they should all have the same category)
        category = category_by_account.get(account_numbers[0], 'Unknown')
        
        # Determine transaction frequency for this account category
        freq = TRANSACTION_FREQUENCY.get(category, 30)
        
        # Get weights for distributing amount across account details
        if pnl_account_name in account_detail_weights:
            weights = account_detail_weights[pnl_account_name]
            # Filter weights to only include account numbers we have
            weights = {num: weight for num, weight in weights.items() if num in account_numbers}
            # Normalize weights to sum to 1
            weight_sum = sum(weights.values())
            if weight_sum > 0:
                weights = {num: weight/weight_sum for num, weight in weights.items()}
            else:
                # Equal distribution if no weights or sum is 0
                weights = {num: 1.0 / len(account_numbers) for num in account_numbers}
        else:
            # If no weights defined, distribute equally
            weights = {num: 1.0 / len(account_numbers) for num in account_numbers}
        
        # Distribute the monthly amount across account details according to weights
        for account_number, weight in weights.items():
            account_amount = monthly_actual * weight
            
            # Generate transactions for this account and month
            num_transactions = max(1, min(freq // len(weights), len(month_days)))
            selected_days = random.sample(list(month_days['date']), num_transactions)
            
            # Distribute this account's amount across its transactions
            for date in selected_days:
                # Base amount (equal distribution with some variance)
                base_amount = account_amount / num_transactions
                transaction_amount = apply_variance(base_amount, DAILY_VARIANCE)
                
                # Select random dimensions
                location_id = random.choice(dims['locations']['location_id'].tolist())
                cost_center_id = random.choice(dims['cost_centers']['cost_center_id'].tolist())
                vendor_id = random.choice(dims['vendors']['vendor_id'].tolist())
                project_id = random.choice(dims['projects']['project_id'].tolist())
                
                # Generate segment (simple business categorization)
                segments = ['B2B', 'B2C', 'Government', 'Enterprise']
                segment = random.choice(segments)
                
                actuals_data.append({
                    'date': date,
                    'account_number': account_number,
                    'location_id': location_id,
                    'bu_id': bu_id,
                    'segment': segment,
                    'amount': round(transaction_amount, 2),
                    'cost_center_id': cost_center_id,
                    'vendor_id': vendor_id,
                    'project_id': project_id
                })
    
    return pd.DataFrame(actuals_data)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function to generate all P&L data."""
    print("Starting P&L Data Generation...")
    print(f"Target Annual Revenue: ${TARGET_ANNUAL_REVENUE:,.0f}")
    print(f"Target Net Margin: {TARGET_NET_MARGIN:.1%}")
    
    # Load dimensions
    print("\nLoading dimensions...")
    dims = load_dimensions()
    
    # Create output directory using proper path handling
    script_dir = Path(__file__).parent
    output_dir = script_dir / 'generated'
    output_dir.mkdir(exist_ok=True)
    
    # Generate calendar dimension
    print("Generating calendar dimension...")
    calendar_df = create_calendar_dim()
    calendar_df.to_csv(output_dir / 'calendar_dim.csv', index=False)
    print(f"Created calendar_dim.csv with {len(calendar_df)} records")
    
    # Generate budget data
    print("\nGenerating budget data...")
    budget_df = generate_budget_data(dims)
    budget_df.to_csv(output_dir / 'budget.csv', index=False)
    print(f"Created budget.csv with {len(budget_df)} records")
    
    # Generate actuals data
    print("\nGenerating actuals data...")
    actuals_df = generate_actuals_data(dims, budget_df)
    actuals_df.to_csv(output_dir / 'actuals.csv', index=False)
    print(f"Created actuals.csv with {len(actuals_df)} records")
    
    # Summary statistics
    print("\n" + "="*50)
    print("GENERATION SUMMARY")
    print("="*50)
    
    total_budget = budget_df['amount'].sum()
    total_actuals = actuals_df['amount'].sum()
    
    print(f"Total Budget Amount: ${total_budget:,.0f}")
    print(f"Total Actuals Amount: ${total_actuals:,.0f}")
    print(f"Variance: {((total_actuals - total_budget) / total_budget * 100):+.1f}%")
    
    # Revenue analysis
    revenue_budget = budget_df[budget_df['pnl_account_name'].str.contains('Revenue', na=False)]['amount'].sum()
    print(f"\nRevenue Budget: ${revenue_budget:,.0f}")
    
    # Account detail distribution analysis
    print("\nAccount Detail Distribution Summary:")
    account_detail_summary = actuals_df.groupby('account_number')['amount'].sum().reset_index()
    account_detail_summary = account_detail_summary.merge(
        dims['accounts'][['account_number', 'pnl_account_name', 'pnl_account_detail']],
        on='account_number'
    )
    # Group by pnl_account_name to show distribution
    account_name_totals = account_detail_summary.groupby('pnl_account_name')['amount'].sum().to_dict()
    
    # Sample of the distribution (show a few examples)
    print("\nSample Account Detail Distribution:")
    sample_accounts = ['Gross Revenue', 'Direct Materials', 'Salaries']
    for account_name in sample_accounts:
        print(f"\n{account_name} Distribution:")
        account_details = account_detail_summary[account_detail_summary['pnl_account_name'] == account_name]
        if not account_details.empty:
            total = account_name_totals.get(account_name, 1)  # Avoid division by zero
            for _, row in account_details.iterrows():
                pct = (row['amount'] / total * 100) if total != 0 else 0
                print(f"  - {row['pnl_account_detail']} (#{row['account_number']}): ${row['amount']:,.0f} ({pct:.1f}%)")
    
    print(f"\nFiles created in '{output_dir}' directory:")
    print("- calendar_dim.csv")
    print("- budget.csv") 
    print("- actuals.csv")
    print("\nP&L Data Generation Complete!")

if __name__ == "__main__":
    main()