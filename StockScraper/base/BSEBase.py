from datetime import datetime

import pandas as pd
from .customRequest import CustomSession

class BSEBase(CustomSession):
    base_url = 'https://www.bseindia.com/'
    api_url = 'https://api.bseindia.com/BseIndiaAPI/api'

    valid_groups = ('A', 'B', 'E', 'F', 'FC', 'GC', 'I', 'IF', 'IP', 'M', 'MS',
                    'MT', 'P', 'R', 'T', 'TS', 'W', 'X', 'XD', 'XT', 'Y', 'Z',
                    'ZP', 'ZY')

    def __init__(self):
        super().__init__(headers={
            'authority': 'api.bseindia.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'referer': self.base_url,
            'Origin': self.base_url,
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54',
        })
        
        # self.hit_and_get_data(self.base_url)

    