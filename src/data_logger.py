import settings

from utils import leading_zero
from time import now


class CSVDataLogger:
    filename = None
    delimiter = ';'
    headers = None

    def __init__(self, headers):
        log_path = settings.SD_CARD_PATH if settings.DATA_LOGGER['use_sd'] else ''
        log_dir = settings.DATA_LOGGER['dir']

        if log_dir not in uos.listdir(log_path):
            uos.mkdir(log_path + '/' + log_dir)

        _now = now()

        self.filename = log_path + '/' + log_dir + '/log_{year}-{month}-{day}_{hour}-{minute}-{second}.csv'.format(
            year=_now[0],
            month=leading_zero(_now[1]),
            day=leading_zero(_now[2]),
            hour=leading_zero(_now[4]),
            minute=leading_zero(_now[5]),
            second=leading_zero(_now[6]))

        self.headers = headers
        self._write_line(self.delimiter.join(self.headers))

    def _write_line(self, line):
        with open(self.filename, 'a') as file:
            file.write(line)
            file.write('\n')

    def log_data(self, data):
        line_elements = [data.get(header, '') for header in self.headers]
        self._write_line(self.delimiter.join(line_elements))
