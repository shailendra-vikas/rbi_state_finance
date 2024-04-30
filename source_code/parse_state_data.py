import os
import state_hanbook.state_data as state_data
from optparse import OptionParser

parser = OptionParser()
parser.add_option( "--outfile", dest="output_filename", help="The name of the outputfile", default=None)
parser.add_option( "--year", dest="handbook_year", help="The year of the handbook", default=None)
(options, args) = parser.parse_args()

def get_meta_data(year: str):
    meta_data = __import__(f'setup_state_{year}')
    return meta_data

def interact(section_d):
    all_table = {}
    for section_name, section in section_d.items():
        print(f'======= {section_name} =========')
        for table_name, table_instance in section.section_d.items():
            print(f'    ===== {table_name}  ===')
            if not table_instance.read_it:
                continue

            for table_name_detail, data in table_instance.table_data.data_dict.items():
                print(f'        {table_name_detail} ')
                all_table[table_name_detail] = (data, table_instance)

    # Assuming only one section now
    while True:
        key_words = input('table name keywords:')
        if key_words == 'quit':
            break
        key_words = key_words.split(' ')
        key_words = [key.upper() for key in key_words]
        sorted_key = []
        for table_name in all_table.keys():
            if not [key_word for key_word in key_words if key_word not in table_name.upper()]:
                sorted_key.append(table_name)
        print('>>>> Selected names:')
        for key in sorted_key:
            print(f'    {key}')

        plot_or_not = input('Should we plot[y/n]:')
        if plot_or_not in ('Y', 'y','yes','Yes'):
            for table_name_detail in sorted_key:
                print(f'plot for {table_name_detail}')
        elif plot_or_not == 'quit':
            break


def main():
    year = options.handbook_year if options.handbook_year else '2023'
    meta_data = get_meta_data(year)
    if len(args)==1 and args[0]=='all':
        sections = meta_data.sections.keys()
    else:
        sections =  args

    raw_data_dir = os.path.join('/home/vikas/personal_repository/rbi_state_finance/raw_data/States')

    all_tables  = {}
    all_table_data = {}
    all_states = []
    section_d = {}
    for section_name in sections:
        section_name_part = section_name.split(':')
        section_name = section_name_part[0]
        section_instance = state_data.Section(raw_data_dir, meta_data, section_name)
        for table in section_instance.get_tables():
            if len(section_name_part) > 1:
                if not table.match(section_name_part[1]):
                    continue

            if table.read_it:
                table.read()
                #all_tables[(section_name, table.table_name)] = table
                #for table_data_name, value in table.table_data.data_dict.items():
                #    all_table_data[table_data_name] = value
                #    all_states.extend([ key[0] for key in value])
        section_d[section_name] = section_instance

    #print('All states: ', set(all_states))
    interact(section_d)


if __name__=='__main__':
    main()
