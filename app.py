from flask import Flask, render_template, request
import numpy as np
#import matplotlib.pyplot as plt
import pandas
import Quandl
import csv
from datetime import datetime
from bokeh.plotting import figure
from bokeh.embed import file_html, components

app = Flask(__name__)

app.vars={}
database = 'WIKI'

# Create function to handle month change
def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)

# Create function to return a formatted Quandl code, with error checking
def get_quandl(symbol):
    test_code = database + '/' + symbol.upper()
    with open('WIKI_tickers.csv', 'rU') as f:
        # f = open(filename, 'rU')
        reader = csv.reader(f)
        for line in reader:
            # Compare with first column in file return the Quandl code if found,
            # return 'NA' if not found
            if test_code == line[0]: return [line[0], line[1]]
    return ['NA']

#@app.route('/index_ms', methods=['GET','POST'])
@app.route('/', methods=['GET','POST'])
def index():
    # The 'GET' is called the first time.
    if request.method == 'GET':
        return render_template('landing.html')
    else:
        # Here is where I put stuff when the user submits things in the fields
        # Clear the check boxes everytime I hit submit
        app.vars['close_px'] = 0
        app.vars['open_px'] = 0
        app.vars['high_px'] = 0
        app.vars['low_px'] = 0
            
        # Move variables into the app.vars dictionary
        app.vars['symbol'] = request.form['stock_sym']
        
        # Do a simple error checking to see if stock symbol exists
        quandl_code = get_quandl(app.vars['symbol'])
        if quandl_code == ['NA']: return render_template('error.html', sym=app.vars['symbol'])
        
        if 'option1' in request.form:
            app.vars['close_px'] = request.form['option1']
        if 'option2' in request.form:
            app.vars['open_px'] = request.form['option2']
        if 'option3' in request.form:
            app.vars['high_px'] = request.form['option3']
        if 'option4' in request.form:
            app.vars['low_px'] = request.form['option4']
            
        # Get the current date and the date one month ago
        # Put those dates in the Quandl format
        current_date = datetime.today()
        previous_date = monthdelta(current_date,-1)
        current_date = ("%s-%s-%s" % (current_date.year, current_date.month, current_date.day))
        previous_date = ("%s-%s-%s" % (previous_date.year, previous_date.month, previous_date.day))
        
        # Get the quandl data
        mydata = Quandl.get(quandl_code[0], returns='pandas',\
            trim_start=previous_date, trim_end=current_date)

        # Example of how to get one closing price
        # close = mydata.ix['2015-12-11', 'Close']
        
        # Generate Bokeh HTML elements
        # Create a 'figure' object that will hold everything
        p = figure(title='Stock prices for {}, {}'.format(app.vars['symbol'],\
            quandl_code[1]), plot_width=500, plot_height=500, x_axis_type='datetime')
        # x axis will always be the same
        x = mydata.index
        
        # y axis will depend on which check boxes were selected
        y1 = mydata['Close']
        y2 = mydata['Open']
        y3 = mydata['High']
        y4 = mydata['Low']
        
        x = mydata.index  # All x axis is the same
        if 'option1' in request.form:
            y = y1
            p.line(x,y, color='crimson', line_width=2, legend='Closing Price')
        if 'option2' in request.form:
            y = y2
            p.line(x,y, color='black', line_width=2, legend='Opening Price')
        if 'option3' in request.form:
            y = y3
            p.line(x,y, color='blue', line_width=2, legend="Day's High Price")
        if 'option4' in request.form:
            y = y4
            p.line(x,y, color='darkgreen', line_width=2, legend="Day's Low Price")
        
        # create the HTML elements
        figJS, figDiv = components(p)
       
        # return 'Current date is: {}; Closing price: {}'.format(current_date, close)
        return render_template('figure.html',figJS=figJS, figDiv=figDiv)

if __name__ == "__main__":
  app.run()
