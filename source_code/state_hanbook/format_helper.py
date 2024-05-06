import os
import numpy as np
import pandas as pd


class NotCorrectFormat(Exception):
    pass


class Format1:
    """ TABLE xx, all nan
         [extra header only present if there are more than one 1 sheet but not ncessary, all nan]
         [unit, all, nan]
         [State/Union Territory, Year], all convertible to year (i.e 1990-91)
         ...
         [ALL INDIA],..
    """
    func1 = lambda x: int(x)
    func2 = lambda x: Format1.func1(x.split('-')[0])
    func3 = lambda x: Format1.func2(x.split('(')[1])
    text_to_year_funcs = [func1, func2, func3]

    def __init__(self, table_file):
        self.table_file = table_file
        self.tablename_in_file = None
        self.unit = None
        self.data_dict = {}

        self._table_name_map = {}
        self._year_map = {}

        sheet_data = self._read_data()
        self._update_meta_data(sheet_data)

        for _sheet_no, (top_part, header_part, body_part) in enumerate(sheet_data):
            for _index, row in enumerate(body_part):
                for state_name, column_index, value in self._process_row(row):
                    year, current_data_dict = self.get_current_dict(_sheet_no, column_index)
                    current_data_dict[(state_name,year)] = value

    def get_current_dict(self, sheet_no, column_index):
        full_table_name = self._table_name_map[sheet_no][column_index]
        current_dict = self.data_dict.setdefault(full_table_name, {})
        year = self._year_map[sheet_no][column_index]
        return year, current_dict

    def text_to_year(self, value):
        for func in self.text_to_year_funcs:
            try:
                return func(value)
            except ValueError:
                pass
        raise ValueError('Can not convert to year')

    def _trim_table_sheet_name(self, table_sheet_name):
        table_sheet_name = table_sheet_name.strip()
        if table_sheet_name[0] == '(':
            table_sheet_name = table_sheet_name[1:-1]
        table_sheet_name = table_sheet_name.split('(Per cent)')[0]
        return table_sheet_name.strip()

    def _update_meta_data(self, sheet_data):
        for _sheet_no, (top_part, header_part, body_part) in enumerate(sheet_data):
            if _sheet_no == 0:
                self.tablename_in_file = top_part[0][0].strip()
                if len(top_part) > 1:
                    self.unit = top_part[-1][0].strip()
            table_sheet_name = '' if len(top_part) <= 2  else self._trim_table_sheet_name(top_part[1][0].strip())

            column_tablename_map = self._table_name_map.setdefault(_sheet_no, {})
            year_tablename_map = self._year_map.setdefault(_sheet_no, {})
            last_year_value = None
            for i in range(len(header_part[0])):
                if i == 0:
                    continue

                value = header_part[0][i]
                if len(header_part) == 1:
                    column_tablename_map[i] = table_sheet_name
                    year_tablename_map[i] = self.text_to_year(value)
                else:
                    if not pd.isnull(value):
                        last_year_value = self.text_to_year(value)
                    year_tablename_map[i] = last_year_value
                    column_tablename_map[i] = table_sheet_name + self._trim_table_sheet_name(header_part[1][i].strip())

    def _read_data(self):
        sheet_data = []
        sheet_no = 0
        while True:
            try:
                data = pd.read_excel(self.table_file.full_file_name, sheet_name=sheet_no)
            except ValueError:
                return sheet_data
            data = data.drop(columns=data.columns[0])
            top_part = []
            header_part = []
            body_part = []
            done_top = False
            done_header = False
            for index, row in data.iterrows():
                if not done_top:
                    if self._only_first_column(row):
                        top_part.append(row)
                        continue
                    done_top = True

                if len(top_part) == 0:
                    raise NotCorrectFormat('Format1 is not correct format')

                if not done_header:
                    first_column = row[0]
                    if pd.isnull(first_column) or first_column.strip() in ('State/Union Territory','Year'):
                        header_part.append(row)
                        continue
                    done_header = True

                if len(header_part) == 0:
                    raise NotCorrectFormat('Format1 is not correct format')

                if row[0] == 'ALL INDIA' or row[0].strip().lower() == 'india':
                    row[0] = 'ALL INDIA'
                    body_part.append(row)
                    break

                body_part.append(row)

            if len(body_part) == 0:
                raise NotCorrectFormat('Format1 is not correct format')
            sheet_data.append((top_part, header_part, body_part))
            sheet_no += 1
        return sheet_data


    def _only_first_column(self, row):
        return  all(row.isna()[1:])


    def _process_row(self, row):
        for col_index,  _col in enumerate(row):
            if col_index == 0:
                state_name = self.table_file.meta_data.state_synonyms.get(_col, _col)
                continue
            try:
                value = float(_col)
            except ValueError:
                value = np.nan
            yield state_name, col_index, value

    def read_final_data(self):
        for table_suffix, data in self.data_dict.items():
            yield self.unit, table_suffix, data


