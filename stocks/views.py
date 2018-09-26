from django.shortcuts import render
from django.http import HttpResponse
import requests
import simplejson as json
from pandas.compat import reduce, numpy
from .models import AlgoProp
from .helpers import algo_result
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components


def stocks(request):
    return render(request, 'stocks/index.html')


def table_view(request):
    if request.method == 'POST':

        algo_name = request.POST['algo_name']
        if not algo_name:
            return HttpResponse('<h1>Please go back and enter a algo_name</h1>')

        signal = request.POST['signal']
        if not signal:
            return HttpResponse('<h1>Please go back and enter a stock signal</h1>')

        trade = request.POST['trade']
        if not trade:
            return HttpResponse('<h1>Please go back and enter a stock trade</h1>')

        ticker = request.POST['ticker']
        if not ticker:
            return HttpResponse('<h1>Please go back and enter a stock ticker</h1>')

        api_url = "https://api.iextrading.com/1.0/stock/{ticker}/chart/1y".format(ticker=ticker)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }

        response = requests.request('GET', api_url, headers=headers)

        if response.status_code == 200:
            json_response = json.loads(response.content)
        else:
            return render(request, 'stocks/errors.html', context={'error_string_exp': 'Some Errors Occurred!'})

        prices = [d['close'] for d in json_response if 'close' in d]

        positions, PnL = algo_result(signal, trade, prices)
        # Save the Algo name, the daily PnL and the positions.
        new_algo = AlgoProp(name=algo_name, daily_pnl=' '.join(map(str, PnL)), position=' '.join(map(str, positions)))
        new_algo.save()

        return_list = list()
        val = AlgoProp.objects.all()
        for v in val:
            l = list(map(float, v.daily_pnl.split(' ')))
            avg = reduce(lambda x, y: x + y, l) / len(l)
            return_list.append(dict({'daily_pnl': avg, 'name': v.name}))

    return render(request, 'stocks/table_view.html', {'d_val': return_list})


def graph(request, algo_name):

    form_dict = {}

    al = AlgoProp.objects.filter(name=algo_name).first()

    data = {'position': list(map(float, al.position.split(' '))), 'daily_pnl': list(map(float, al.daily_pnl.split(' ')))}
    data = pd.DataFrame(data, columns=['position', 'daily_pnl'])

    data['position'] = pd.to_numeric(list(map(float, al.position.split(' '))))
    data['daily_pnl'] = pd.to_numeric(list(map(float, al.daily_pnl.split(' '))))

    p = figure(x_axis_type="datetime", width=800, height=600)
    p.line(data['position'], al.daily_pnl.split(' '), legend='position', line_color='green')
    p.line(data['daily_pnl'], al.position.split(' '), legend='daily_pnl', line_color='blue')
    script, div = components(p)
    form_dict['script'] = script
    form_dict['div'] = div
    form_dict['algo_name'] = algo_name.upper()

    return render(request, 'stocks/graph.html', context=form_dict)

