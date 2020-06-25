import os

from . import NetworkUtils
from . import FileUtils

API_KEY = "b161855253f849704ec985cb63f498ea"
DCF_URL = "https://financialmodelingprep.com/api/v3/discounted-cash-flow/"
QUOTE_URL = "https://financialmodelingprep.com/api/v3/quote/"
SYMBOL_LIST_URL = "https://financialmodelingprep.com/api/v3/stock/list"

# return a list of stock's DCF with dict type
def getDCF(symbol_list_str):
    url = DCF_URL + symbol_list_str
    payload = {"apikey": API_KEY}
    result = NetworkUtils.sendGetRequest(url, payload)
    if result:
        print(f'Get DCF for symbols successfully.')
        return result
    else:
        print(f'Failed to get DCF for symbols')
        return None

# return a list of stock's quote information with dict type
def getQuote(symbol_list_str):
    url = QUOTE_URL + symbol_list_str
    payload = {"apikey": API_KEY}
    result = NetworkUtils.sendGetRequest(url, payload)
    if result:
        print(f'Get quote for symbols successfully.')
        return result
    else:
        print(f'Failed to get quote for symbols')
        return None

# return a list of stock information with dict type
def getStockInfoBySymbolList(symbol_list):
    separator = ','
    symbol_list_str = separator.join(symbol_list)
    dcf_res = getDCF(symbol_list_str)
    quote_res = getQuote(symbol_list_str)

    stock_info_list = []
    for i in range(len(symbol_list)):
        try:
            stock_info = {}
            if quote_res:
                stock_info = quote_res[i]
                if dcf_res:
                    stock_info['dcf'] = dcf_res[i]['dcf']
            else:
                if dcf_res:
                    stock_info['symbol'] = dcf_res[i]['symbol']
                    stock_info['price'] = dcf_res[i]['Stock Price']
                    stock_info['dcf'] = dcf_res[i]['dcf']

            stock_info_list.append(stock_info)
        except IndexError:
            print(f'Error: get information for symbol list {symbol_list} failed. '
                  f'Please check if every symbols in the list {symbol_list} is a normal US stock and not futures')

    return stock_info_list

# Return boolean
def isValidSymbol(symbol):
    # 1. Get symbols list
    symbol_list = getSymbolList()
    # 2. Check if symbol is valid
    if symbol_list:
        for item in symbol_list:
            if symbol.lower() == item['symbol'].lower():
                print(f"find matched symbol from {len(symbol_list)}")
                return True
        return False
    else:
        print(f"Error: Get symbol list failed. Will consider symbol {symbol} is valid.")
        return True

# Return a list of {symbol, company}
def getSymbolList():
    print("Start getting symbol list ...")
    result = []
    # 1. Check if there's available cache files
    file_prefix = FileUtils.FILE_PREFIX_SYMBOL + "_"
    file_path = FileUtils.checkCacheFile(file_prefix, 60*60*16)
    # 2. If yes, use cache files
    if file_path:
        if os.path.exists(file_path):
            result = FileUtils.readDictListFromCSV(file_path, FileUtils.SYMBOL_LIST_FILEDS, False)
            print(f"Load symbols list from cache {file_path} successfully.")
        else:
            result = []
            print(f"Error: Somehow {file_path} does not exist!")
    # 3. If no, send request to API and save result as a csv.
    else:
        url = SYMBOL_LIST_URL
        payload = {"apikey": API_KEY}
        result = NetworkUtils.sendGetRequest(url, payload)
        if result:
            file_path = FileUtils.generateFileName(file_prefix)
            FileUtils.writeDictListIntoCSV(file_path, FileUtils.SYMBOL_LIST_FILEDS, result)
            print(f'Get symbol list from Internet successfully and will save cache at {file_path}.')
        else:
            print(f'Failed to get symbol list from Internet.')
            result = []

    # 4. Return result
    return result

