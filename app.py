import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Add a secret key

# Ensure the transactions file exists
TRANSACTIONS_FILE = 'transactions.csv'
if not os.path.exists(TRANSACTIONS_FILE):
    pd.DataFrame(columns=['date', 'category', 'amount', 'description']).to_csv(TRANSACTIONS_FILE, index=False)

def load_transactions():
    """Load transactions from CSV file."""
    try:
        df = pd.read_csv(TRANSACTIONS_FILE)
        # Explicitly convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        print(f"Error loading transactions: {e}")
        return pd.DataFrame(columns=['date', 'category', 'amount', 'description'])

def save_transactions(df):
    """Save transactions to CSV file."""
    try:
        # Ensure date is in string format for saving
        df_to_save = df.copy()
        df_to_save['date'] = df_to_save['date'].dt.strftime('%Y-%m-%d')
        df_to_save.to_csv(TRANSACTIONS_FILE, index=False)
    except Exception as e:
        print(f"Error saving transactions: {e}")

@app.route('/')
def index():
    """Display the main dashboard with recent transactions and insights."""
    try:
        df = load_transactions()
        
        # Recent transactions
        recent_transactions = df.sort_values('date', ascending=False).head(10)
        
        # Total spending by category
        category_spending = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        # Monthly total spending
        df['month'] = df['date'].dt.to_period('M')
        monthly_spending = df.groupby('month')['amount'].sum()
        
        return render_template('index.html', 
                               recent_transactions=recent_transactions.to_dict('records'),
                               category_spending=category_spending.to_dict(),
                               monthly_spending=monthly_spending.to_dict())
    except Exception as e:
        print(f"Error in index route: {e}")
        return f"An error occurred: {e}", 500

@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    """Add a new transaction."""
    if request.method == 'POST':
        try:
            # Get form data
            date = request.form['date']
            category = request.form['category']
            amount = float(request.form['amount'])
            description = request.form['description']
            
            # Load existing transactions
            df = load_transactions()
            
            # Add new transaction
            new_transaction = pd.DataFrame({
                'date': [pd.to_datetime(date)],
                'category': [category],
                'amount': [amount],
                'description': [description]
            })
            
            # Combine and save
            df = pd.concat([df, new_transaction], ignore_index=True)
            save_transactions(df)
            
            return redirect(url_for('index'))
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return f"An error occurred: {e}", 500
    
    return render_template('add_transaction.html')

@app.route('/insights')
def insights():
    """Generate financial insights."""
    try:
        df = load_transactions()
        
        # Spending insights
        insights_data = {
            'total_spending': df['amount'].sum(),
            'average_monthly_spending': df.groupby(df['date'].dt.to_period('M'))['amount'].sum().mean(),
            'top_categories': df.groupby('category')['amount'].sum().nlargest(3)
        }
        
        return render_template('insights.html', insights=insights_data)
    except Exception as e:
        print(f"Error in insights route: {e}")
        return f"An error occurred: {e}", 500

if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000)
    print("Flask application started.")