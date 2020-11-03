import math
import os
from os import path
from os import listdir

# ----------------------------------------------------------------------------------
def create_directory(path):
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        print(path + ' folder already exists!')

# ----------------------------------------------------------------------------------
def find_suffix_filenames(path_to_dir, suffix=".csv"):
    filenames = listdir(path_to_dir)
    files = [ filename for filename in filenames if filename.endswith( suffix ) ]
    dict_return = {'path' : path_to_dir, 'filenames' : files}
    return dict_return

# ----------------------------------------------------------------------------------
def substract_list_from_list(x, y):
    """z = x - y"""
    z = [item for item in x if item not in y]
    return z
    
# ----------------------------------------------------------------------------------
def clean_directory(path_and_filenames, exclude = None):
    files = path_and_filenames['filenames']
    if exclude == None:
        pass
    else:
        files = substract_list_from_list(files, exclude)
        
    for file in files:
        os.remove("{}{}".format(path_and_filenames['path'],file))
        
    return listdir(path_and_filenames['path'])


# ----------------------------------------------------------------------------------
millnames = ['',' Thousand',' Million',' Billion',' Trillion']
def millify(n):
    "millify number so it is human readable"
    """
    millify number so it is human readable
    input --- n --- exp: 7794798729.0
    output --- '7.79 Billion'
    """
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

    return '{:.2f}{}'.format(n / 10**(3 * millidx), millnames[millidx])