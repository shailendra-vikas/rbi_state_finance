import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

import state_hanbook.format_helper as format_helper


class TableData:
    def __init__(self, table_file, unit, table_suffix, data_dict):
        # Formatter will create this instance
        self.table_file = table_file
        self.table_suffix = table_suffix
        self.unit = unit
        self.data_dict = data_dict

    def _extract_state_data(self, state):
        years = []
        values = []
        for (_state, _year), value in self.data_dict.items():
            if _state != state:
                continue
            years.append(_year)
            values.append(value)
        return years, values

    def state_plot(self, state):
        state_years , state_values  = self._extract_state_data(state)
        all_india_years, all_india_values = self._extract_state_data('ALL INDIA')

        fig, ax  = plt.subplots(1, 1, figsize=(14,7))
        ax.plot(state_years, state_values, marker='s', markersize=4, linestyle='-', linewidth=2, color='cyan', label=state)
        ax.plot(all_india_years, all_india_values, marker='s', markersize=4, linestyle='-', linewidth=2, color='black', label='Bharat')

        property_dict = self.table_file.meta_data.plotting_info.get((self.table_file.section.section_code, self.table_file.table_code, self.table_suffix), {})
        title = property_dict.get('TITLE', self.table_file.table_name)
        unit = property_dict.get('UNIT', self.unit)

        ax.set_ylabel(unit)
        ax.set_xlabel('year')
        ax.legend()
        fig.suptitle(title)
        plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))
        section = self.table_file.section
        file_location = os.path.join(section.base_dir, 'plots', 'States', section.section_code, self.table_file.table_code)
        if not os.path.exists(file_location):
            os.makedirs(file_location)

        file_name =  f"{state}_{self.table_file.table_name}_{self.table_suffix}.png"
        plt.savefig(os.path.join(file_location, file_name))
        plt.close()

    def plot(self):
        all_states = set([ state for (state, year) in self.data_dict.keys()])
        all_states.remove('ALL INDIA')
        for state in all_states:
            self.state_plot(state)


class TableFile:
    def __init__(self, section, table_code, readable):
        self.section = section
        self.table_code = table_code
        self.readable = readable
        self.meta_data = self.section.meta_data
        self.table_name = self.section.table_file_names[self.table_code]
        self.file_name = self.section.table_to_file[self.table_name]
        self.full_file_name = os.path.join(self.section.base_dir, 'raw_data', 'States', self.file_name)
        self.table_data_dict = {}

    def load_tabledata(self):
        if not self.readable:
            return

        formatter_iter = iter(self.section.formatter_list)
        formatter = next(formatter_iter)
        process_next = True
        while process_next:
            try:
                for unit, table_suffix, data_dict in formatter(self).read_final_data():
                    table_data_instance = TableData(self, unit, table_suffix, data_dict)
                    self.table_data_dict[table_suffix] = table_data_instance
                process_next = False
            except format_helper.NotCorrectFormat:
                print('Formatting not correct')
                formatter = next(formatter_iter)

    def __str__(self):
        return os.linesep.join([f"{self.table_code} :: {self.table_name}", f"    {'' if self.readable else 'NOT'} READABLE" , f"    Excel = {self.file_name}"])


class Section:
    section_code_formats = {
            'section1' : ['Format1',],
            }

    def __init__(self, section_code, meta_data, base_dir):
        """ base_dir: where title.json is expected
            meta_data : configs and other manual inputs
            section_code: the code for the section
        """
        self.base_dir = base_dir
        self.meta_data = meta_data
        self.section_code = section_code
        self.section_title = self.meta_data.sections[self.section_code]
        self.table_file_names = self.meta_data.group_names[self.section_code]
        self.formatter_list = [getattr(format_helper, format_name) for format_name in self.section_code_formats.get(self.section_code, ['Format1',])]

        self.table_files = {}

        with open(os.path.join(self.base_dir, 'raw_data', 'States', 'title.json')) as title_file:
            self.file_to_table = json.loads(title_file.read())
        self.table_to_file = {_title: _file for _file, _title in self.file_to_table.items()}

    def load_tables(self):
        do_not_read_list = self.meta_data.do_not_read[self.section_code]
        for table_code, table_file_name in self.table_file_names.items():
            table_file_instance = TableFile(self, table_code, table_code not in do_not_read_list)
            #print(table_file_instance)
            table_file_instance.load_tabledata()
            self.table_files[table_code] = table_file_instance

    def __str__(self):
        return f"{self.section_code} :: {self.section_title}"

