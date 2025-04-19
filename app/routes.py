from flask import Blueprint, render_template, request, send_file, session, url_for
from .utils import fetch_and_save_stock_data, load_stock_data_from_json, generate_chart, filter_date_range
import pandas as pd
import io
import os
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    chart_path = None
    table_data = None
    stock_data = None

    if request.method == 'POST':
        symbol = request.form['symbol'].upper()
        chart_type = request.form['chart_type']
        time_series = request.form['time_series']
        interval = request.form.get('interval')
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        display = request.form.get("display", "chart").lower()

        try:
           
            filename = os.path.join("data", f"{symbol}_{time_series}.json")
            if not os.path.exists(filename):
               
                fetch_and_save_stock_data(symbol, time_series)

          
            stock_data = load_stock_data_from_json(symbol, time_series)

           
            filtered_data = filter_date_range(stock_data, start_date, end_date)

            if filtered_data is not None and not filtered_data.empty:
              
                if display in ['Table', 'Both']:
                    table_data = filtered_data.head(3)

                
                if display in ['chart', 'both']:
                    chart_filename = generate_chart(filtered_data, chart_type, symbol)
                    chart_path = url_for('static', filename=f'charts/{chart_filename}')
                else:
                    chart_path = None

                session['symbol'] = symbol
                if table_data is not None:
                    session['table_data'] = table_data.to_dict()

            else:
                chart_path = None  

        except ValueError as e:
            chart_path = None

    return render_template(
        "index.html",
        chart_path=chart_path,
        table_data=table_data
    )


@main.route('/download', methods=['GET'])
def download_csv():
    symbol = session.get('symbol', 'stock')
    table_data_dict = session.get('table_data', {})

    if not table_data_dict:
        return "No data available for download."

    
    df = pd.DataFrame.from_dict(table_data_dict)
    df.index.name = 'Date'
    df.reset_index(inplace=True)

   
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return send_file(io.BytesIO(buf.getvalue().encode()),
                     mimetype='text/csv',
                     download_name=f'{symbol}_data.csv',
                     as_attachment=True)
