
import re
import os
import json
from urllib.request import urlopen, urlretrieve

handbook_urls = {
    'Economy': r"https://rbi.org.in/Scripts/AnnualPublications.aspx?head=Handbook%20of%20Statistics%20on%20Indian%20Economy",
    'States': r"https://www.rbi.org.in/Scripts/AnnualPublications.aspx?head=Handbook%20of%20Statistics%20on%20Indian%20States"
}


def extract_handbook_info(topic: str):
    """
        Extract info from
    """
    handbook_url = handbook_urls[topic]
    page = urlopen(handbook_url)
    html_str = page.read().decode("utf-8")
    table_title_url = []
    current_title = None
    for column_str in re.findall("<td.*?</td>",html_str, flags=re.DOTALL):
        if 'Table' in column_str:
            if current_title is not None:
                raise ValueError(fr'last found table {current_title} got no url')

            start_index = column_str.find('Table')
            end_index = column_str.find('</a>')
            current_title = column_str[start_index:end_index]

        for match_str in re.findall("href='.*\.XLSX'", column_str):
            if current_title is None:
                continue

            href_str = match_str[6:-1]
            table_title_url.append((current_title,href_str))
            current_title = None
    return table_title_url


def create_title_file(raw_data_dir: str, topic: str):
    import glob
    all_xlsx = set([full_path.rpartition('/')[2] for full_path in glob.glob(os.path.join(raw_data_dir, "*.XLSX"))])
    current_title = {}
    for _title, _url in extract_handbook_info(topic):
        xlsx_filename = _url.rpartition('/')[2]
        if xlsx_filename in all_xlsx:
            current_title[xlsx_filename] = _title

    print(all_xlsx)
    print(f"current_title: {current_title}")
    title_file_name = os.path.join(raw_data_dir, topic, 'title.json')
    with open(title_file_name, "w") as current_file_object:
        current_file_object.write(json.dumps(current_title))
    return current_title


def download_all_files(raw_data_dir: str, topic: str):
    # Read the title.json file
    title_file_name = os.path.join(raw_data_dir, topic,  'title.json')
    try:
        with open(title_file_name) as title_file:
            current_title = json.loads(title_file.read())
    except FileNotFoundError:
        current_title = create_title_file(raw_data_dir, topic)

    # Get info from website and download if does not exit
    source_title = {}
    for _title, _url in extract_handbook_info(topic):
        xlsx_filename = _url.rpartition('/')[2]
        source_title[xlsx_filename] = _title
        # Find out which all files are missing and download
        if xlsx_filename not in current_title:
            print(f"Downloading file {xlsx_filename}")
            urlretrieve(_url, os.path.join(raw_data_dir, topic, xlsx_filename))
        current_title[xlsx_filename] = _title
        print("Writing ")

    with open(title_file_name, "w") as current_file_object:
        current_file_object.write(json.dumps(current_title))


def test():
    topic = 'States'
    raw_data_dir = os.path.join('/home/vikas/personal_repository/rbi_state_finance/raw_data/')
    download_all_files(raw_data_dir, topic)


def print_file():
    topic = 'States'
    for index, (_title, _url) in enumerate(extract_handbook_info(topic)):
        print(f"Row {index} \'{_title}\')")
        print(f"    {_url}")


if __name__ == "__main__":
    #print_file()
    test()
    #create_title_file('/home/vikas/personal_repository/rbi_state_finance/raw_data/')




