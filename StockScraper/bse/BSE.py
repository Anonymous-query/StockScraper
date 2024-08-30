from pathlib import Path
from StockScraper.base.BSEBase import BSEBase
from zipfile import ZipFile
from typing import Literal, Dict, List
from datetime import datetime
from requests.exceptions import ReadTimeout
from mthrottle import Throttle

throttle_config = {
    'lookup': {
        'rps': 15,
    },
    'default': {
        'rps': 8,
    }
}

th = Throttle(throttle_config, 15)


class BSE(BSEBase):
    def __init__(self, download_folder: str | Path):
        super().__init__()
        self.dir = BSE.__getPath(download_folder, isFolder=True)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.session.close()
        return False
    
    def exit(self):
        self.session.close()

    @staticmethod
    def __unzip(file: Path, folder: Path):
        with ZipFile(file) as zip:
            filepath = zip.extract(member=zip.namelist()[0], path=folder)

        file.unlink()

        return Path(filepath)
    
    def __download(self, url: str, folder: Path):
        fname = folder / url.split("/")[-1]

        th.check()

        try:
            with self.session.get(url, stream=True, timeout=10) as r:

                if r.status_code == 404:
                    raise RuntimeError(
                        'Report is unavailable or not yet updated.')

                with fname.open(mode='wb') as f:
                    for chunk in r.iter_content(chunk_size=1000000):
                        f.write(chunk)
        except ReadTimeout:
            raise TimeoutError('Request timed out')

        return fname
    
    @staticmethod
    def __getPath(path: str | Path, isFolder: bool = False):
        path = path if isinstance(path, Path) else Path(path)

        if isFolder:
            if path.is_file():
                raise ValueError(f'{path}: must be a folder')

            if not path.exists():
                path.mkdir(parents=True)

        return path
    
    def _segment_type(self, segment: Literal['equity', 'debt', 'mf_etf']):
        if segment == 'equity':
            return '0'
        return '1' if segment == 'debt' else '2'
    
    def _date_by(self, by_date: Literal['ex', 'record', 'bc_start']):
        if by_date == 'ex':
            return 'E'
        return 'R' if by_date == 'record' else 'B'
    
    def actions(self,
                segment: Literal['equity', 'debt', 'mf_etf'] = 'equity',
                from_date: datetime | None = None,
                to_date: datetime | None = None,
                by_date: Literal['ex', 'record', 'bc_start'] = 'ex',
                scripcode: str | None = None,
                sector: str = '',
                purpose_code: str | None = None) -> List[dict]:
        
        _type = self._segment_type(segment)
        by = self._date_by(by_date)

        params = {
            'ddlcategorys': by,
            'ddlindustrys': sector,
            'segment': _type,
            'strSearch': 'S',
        }

        if from_date and to_date:
            if from_date > to_date:
                raise ValueError(
                    "'from_date' cannot be greater than 'to_date'")
            
            fmt = '%Y%m%d'

            params.update({
                'Fdate': from_date.strftime(fmt),
                'TDate': to_date.strftime(fmt)
            })

        if purpose_code:
            params['Purposecode'] = purpose_code

        if scripcode:
            params['scripcode'] = scripcode

        return self.hit_and_get_data(f'{self.api_url}/DefaultData/w', params)
    
    def quote(self, scripcode) -> Dict[str, float]:
        url = f'{self.api_url}/getScripHeaderData/w'
        params = {
            'scripcode': scripcode,
        }

        th.check()
        response = self.hit_and_get_data(f'{url}/DefaultData/w', params)
        response = response['Header']
        fields = ('PrevClose', 'Open', 'High', 'Low', 'LTP')

        data = {}

        for k in fields:
            data[k] = float(response[k])

        return data
    
    def calculat_earning_dividend(self, 
                                ltp: str = '', 
                                dividend:str = '',
                                investment: int = 10000
                            ) -> tuple:
        try:
            ltp = float(ltp)
            dividend = float(dividend)

            # Number of shares bought
            shares = investment / ltp

            # Earnings from dividend
            earnings = shares * dividend
            return earnings
        except ValueError:
            raise ValueError("LTP and dividend should be valid numbers.")