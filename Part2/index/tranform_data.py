import json


class DataTransformation:
    '''
    Accepts an input file and transform summaries to key:value pair.
    Converts list of summaries to summary object with book_id as key and summary as value
    so that the summary can be fetched in O(1) time without parsing the summary list.
    '''
    def __init__(self,data_file,target_data_file):
        self.summary_dict={}
        self.data_file=data_file
        self.target_data_file=target_data_file

    def transform_data(self):
        self._parse_raw_data_file()
        self._write_to_file()

    def _write_to_file(self):
        with open(self.target_data_file,'w') as outfile:
            outfile.write(json.dumps(self.summary_dict))

    def _parse_raw_data_file(self):
        self.summary_dict['summaries']={}
        self.summary_dict['authors'] = {}

        with open(self.data_file) as json_file:
            data = json.load(json_file)
            self.summary_dict['titles'] = data['titles']
            self.summary_dict['queries'] = data['queries']
            for key,value in data.items():
                if key == 'summaries':
                    for item in data['summaries']:
                        self.summary_dict['summaries'][item['id']] = item['summary']
                elif key == 'authors':
                    for item in data['authors']:
                        self.summary_dict['authors'][item['book_id']] = item['author']