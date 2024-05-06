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
        print(f'======= {section} =========')
        for table_name, table_instance in section.table_files.items():
            print(f'    ===== {table_name}  ===')
            if not table_instance.readable:
                continue

            for table_suffix, table_data in table_instance.table_data_dict.items():
                print(f'        {table_instance.table_name} {"::" if table_suffix else ""} {table_suffix} ')
                all_table[(table_instance.table_name, table_suffix)] = table_data

    # Assuming only one section now
    while True:
        key_words = input('table name keywords:')
        if key_words == 'quit':
            break
        key_words = key_words.split(' ')
        key_words = [key.upper() for key in key_words]
        sorted_key = []
        for table_name, table_suffix in all_table.keys():
            if not [key_word for key_word in key_words if key_word not in table_name.upper()]:
                sorted_key.append((table_name, table_suffix))
        print('>>>> Selected names:')
        for key in sorted_key:
            print(f'    {key}')

        plot_or_not = input('Should we plot[y/n]:')
        if plot_or_not in ('Y', 'y','yes','Yes'):
            for table_name, table_suffix in sorted_key:
                print(f'plot for {table_name} {table_suffix}')
                table_data_instance = all_table[(table_name, table_suffix)]
                table_data_instance.plot()
        elif plot_or_not == 'quit':
            break


def main():
    year = options.handbook_year if options.handbook_year else '2023'
    meta_data = get_meta_data(year)
    if len(args)==1 and args[0]=='all':
        sections = meta_data.sections.keys()
    else:
        sections =  args

    base_path = os.path.join('/home/vikas/personal_repository/rbi_state_finance')

    section_d = {}
    for section_code in sections:
        section_instance = state_data.Section(section_code, meta_data, base_path)
        section_instance.load_tables()
        section_d[section_code] = section_instance
        #print(section_instance)
        #for table_code, table_file in section_instance.table_files.items():
        #    print(f'    KEY: {table_code}')
        #    print(f'    VALUE: {table_file}')
    #print('All states: ', set(all_states))
    interact(section_d)


if __name__=='__main__':
    main()
