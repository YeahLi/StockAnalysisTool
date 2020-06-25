import itertools
import os
import json

from flask import Flask, make_response, jsonify
from flask import render_template
from Utilities import StockUtils
from Utilities import FileUtils

# EB looks for an 'application' callable by default.
application = Flask(__name__)

STOCK_DISPLAY_FIELDS_DICT = {"symbol": "Symbol", "name": "Company Name", "price": "Price",
                             "changesPercentage": "Percentage", "change": "Change", 'pe': "PE",
                             'dcf': "Discounted Cash Flow"}

HENRY_SYMBOLS = ["AMZN", "FB", "TWTR", "AAPL", "NFLX", "GOOG", "SHOP", "BABA", "MSFT", "NVDA", "AMD", "INTC",
                 "GOOS", "TSLA", "WORK", "PYPL", "CRM", "UBER", "DIS", "RY", "COST", "JPM", "ZM", "DOCU"]

BLACK_ROCK_SYMBOLS = ["MSFT", "AAPL", "BABA", "GOOG", "AMZN", "CRM", "PYPL", "ADBE", "TWLO"]

# print a nice greeting.
@application.route('/hello')
def say_hello():
    return "Hello Money ~"

@application.route('/')
@application.route('/index')
def main_page():
    #return "Welcome!"
    return render_template('stock_info.html', dataURL="/stock_info/henry")

@application.route('/stock_info/<list_name>', methods=['GET'])
def stock_info(list_name):
    print(f"Start getting stock info for {list_name} ...")
    symbol_list = []
    # 1. Get symbol list by list_name
    if list_name == "henry":
        symbol_list = HENRY_SYMBOLS
    elif list_name == "black_rock":
        symbol_list = BLACK_ROCK_SYMBOLS

    # 2. Check if cache is available
    file_prefix = FileUtils.FILE_PREFIX_STOCK + "_" + list_name
    file_path = FileUtils.checkCacheFile(file_prefix)

    # 3. if cache is available, read result from cache
    if file_path:
        if os.path.exists(file_path):
            print(f"Load stock info from cache {file_path}.")
            stock_info_list = FileUtils.readDictListFromCSV(file_path, FileUtils.STOCK_INFO_FILEDS)
            print(f"Finish: Get stock info for {list_name} from Internet successfully.")
        else:
            stock_info_list = []
            print(f"Error: Somehow {file_path} does not exist!")
    # 4. if cache is unavailable, get it from Internet and save into cache
    else:
        print("Get stock info from Internet.")
        stock_info_list = StockUtils.getStockInfoBySymbolList(symbol_list)
        file_path = FileUtils.generateFileName(file_prefix)
        FileUtils.writeDictListIntoCSV(file_path, FileUtils.STOCK_INFO_FILEDS, stock_info_list)
        print(f"Finish: Get stock info for {list_name} from Internet successfully and saved cache file at {file_path}.")
    # 5. Return result
    result = {"data": refine_stock_list(stock_info_list)}
    return json.dumps(result, indent=4)  # return a string

def refine_stock_list(stock_info_list):
    result_list = []
    for item in stock_info_list:
        result_item = {}
        for key in STOCK_DISPLAY_FIELDS_DICT:
            value = item[key]
            if isinstance(item[key], float):
                value = round(item[key], 2)
            result_item[key] = value
        result_list.append(result_item)

    return result_list

@application.route('/stock_columns', methods=['GET'])
def stock_columns():
    result = {"columns": STOCK_DISPLAY_FIELDS_DICT}
    return json.dumps(result, indent=4)

@application.route('/search')
def search():
    return render_template('search.html')

@application.route('/search/<stock_symbols>', methods=['GET'])
def search_stocks(stock_symbols):
    print(f'Start searching stocks: {stock_symbols} ...')

    # 1. Verify inputs
    if stock_symbols == "empty":
        return json.dumps({"data": []})
    stock_symbol_list = stock_symbols.split(",")
    for symbol in stock_symbol_list:
        if not StockUtils.isValidSymbol(symbol):
            error_msg = "Symbol %s is invalid." % symbol
            return make_response(jsonify({'error': error_msg}), 401)

    # 2. Get stock info from Internet
    stock_info_list = StockUtils.getStockInfoBySymbolList(stock_symbol_list)
    print(f'Finish searching stocks: {stock_symbols}.')
    result = {"data": refine_stock_list(stock_info_list)}
    return json.dumps(result, indent=4)  # return a string

@application.route('/getHints/<search_word>', methods=['GET'])
def getHints(search_word):
    # 1. Split search_word by "," to get multiple sub_words
    sub_words = search_word.split(",")
    # 2. Get symbol list
    symbol_list = StockUtils.getSymbolList()
    if not symbol_list:
        return json.dumps({"hints": sub_words}, indent=4)
    # 3. Get hints for each word
    hints_dict = {}
    for word in sub_words:
        hint_list = []
        i = 0
        for item in symbol_list:
            if i >= 5: # Only get 5 hints for each sub_word
                break
            if word.lower() in item['symbol'].lower() or word.lower() in item['name'].lower():
                hint_list.append(item['symbol'])
                i += 1
        hints_dict[word] = hint_list
    # 4. Cartesian product. Get 10 at most
    all_hints = itertools.product(*list(hints_dict.values()))  # This is a generator, each item is a tuple
    hints = []
    i = 0
    for hint in all_hints:
        if i >= 10:
            break
        hints.append(",".join(hint))
        i += 1
    # 5. Return result
    return json.dumps({"hints": hints}, indent=4)


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()