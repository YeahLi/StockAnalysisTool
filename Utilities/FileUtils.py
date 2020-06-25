import csv
import time
import pathlib
import os
import glob

from . import NumberUtils

STOCK_INFO_FILEDS = ['symbol', 'name', 'price', 'changesPercentage', 'change', 'dayLow', 'dayHigh', 'yearHigh', 'yearLow',
               'marketCap', 'priceAvg50', 'priceAvg200', 'volume', 'avgVolume', 'exchange', 'open', 'previousClose',
               'eps', 'pe', 'earningsAnnouncement', 'sharesOutstanding', 'timestamp', 'dcf']

SYMBOL_LIST_FILEDS = ['symbol', 'name', 'price', 'exchange']

# Python relative path is relative to current working directory os.getcwd()
CACHE_FILE_DIR = "./cache/"
SYMBOL_LIST_DIR = "./symbols/"

EXPIRE_INTERVAL = 300  # seconds

FILE_PREFIX_STOCK = "stocks"
FILE_PREFIX_SYMBOL = "symbols"


def writeDictListIntoCSV(file_path, fields, dict_list):
    with open(file_path, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fields, restval='', extrasaction='ignore')
        writer.writeheader()
        for item in dict_list:
            writer.writerow(item)

def readDictListFromCSV(file_path, fields, covert_type=True):
    result_list = []
    with open(file_path, newline='') as csv_file:
        reader = csv.DictReader(csv_file, fieldnames=fields)

        i = 0
        for row in reader:
            # convert string to related types
            if i > 0:  # Skip the header
                new_row = {}
                for key, value in row.items():
                    if covert_type:
                        if NumberUtils.is_integer(value):
                            new_row[key] = int(value)
                        elif NumberUtils.is_float(value):
                            new_row[key] = float(value)
                        else:
                            new_row[key] = value
                    else:
                        new_row[key] = value
                result_list.append(new_row)
            i += 1

    return result_list

def generateFileName(prefix):
    file_name = "%s_%d.csv" % (prefix, int(time.time()))
    pathlib.Path(CACHE_FILE_DIR).mkdir(parents=True, exist_ok=True)

    file_path = CACHE_FILE_DIR + file_name
    return file_path

# If cache file exists and is not expired, return file path. Otherwise, return None
def checkCacheFile(prefix, expire_interval = EXPIRE_INTERVAL):
    file_list = glob.glob(CACHE_FILE_DIR + prefix + "_*") # Only find out all related cache files
    if not file_list:
        return None

    for file_path in file_list:
        file_name = os.path.basename(file_path)
        time_str = file_name.split(".")[0].split("_")[-1]
        epoch_time = int(time_str)
        current_epoch_time = int(time.time())
        interval = current_epoch_time - epoch_time
        if interval <= expire_interval:
            return file_path
        else:
            pathlib.Path(file_path).unlink() # if cache file is expired, will remove it.

    return None
