from django.test import TestCase
import json
from Part2.index.create_index import CreateIndex
from Part2.index.query_index import QueryIndex

STOPWORD_FILE = 'index/stopwords.dat'
RAW_DATA_FILE = 'index/data.json'
TRANSFORMED_DATA_FILE = 'index/transformed_data.json'
INDEX_FILE = 'index/index.txt'

TEST_RAW_DATA_FILE = 'index/tests/test_data.json'
TEST_INDEX_FILE = 'index/tests/test_index.txt'
TEST_TRANSFORMED_DATA = 'index/tests/test_transformed_data.json'


class IndexTest(TestCase):
    """ Test module for index creation and querying module """

    def test_transformed_data(self):
        ci_obj = CreateIndex(STOPWORD_FILE, RAW_DATA_FILE, TRANSFORMED_DATA_FILE, INDEX_FILE)
        summary_dict = ci_obj._get_transformed_data()
        with open('index/data.json') as json_file:
            data = json.load(json_file)
            for key,value in data.items():
                if key=='summaries':
                    for item in data['summaries']:
                        self.assertEqual(item['summary'],summary_dict['summaries'][item['id']])

    def test_term_extraction(self):
        test_term = "The book in three sentences"
        ci_obj = CreateIndex(STOPWORD_FILE,RAW_DATA_FILE,TRANSFORMED_DATA_FILE,INDEX_FILE)
        self.assertEqual(['book','three','sentences'],ci_obj._get_terms(test_term))

    def test_total_summaries_in_index(self):
        num_summaries,summaries_count=0,0
        with open(INDEX_FILE, 'r') as index_file:
            num_summaries=int(index_file.readline().rstrip())

        ci_obj = CreateIndex(STOPWORD_FILE, RAW_DATA_FILE, TRANSFORMED_DATA_FILE, INDEX_FILE)
        summary_dict = ci_obj._get_transformed_data()

        for key in summary_dict['summaries']:
            summaries_count+=1

        self.assertEqual(num_summaries,summaries_count)


    def test_index_creation(self):
        '''
        Followed a simple strategy to manually calculate the counts, position , tf and idf of test input
        and checked the final index file with this manually pre-calculated values.
        '''
        index={}
        tf_dict={}
        idf_dict={}
        ci_obj = CreateIndex(STOPWORD_FILE, TEST_RAW_DATA_FILE, TRANSFORMED_DATA_FILE, TEST_INDEX_FILE)
        ci_obj.create_index()

        with open(TEST_INDEX_FILE, 'r') as index_file:
            num_summaries=int(index_file.readline().rstrip())
            for line in index_file:
                line=line.rstrip()
                term, position, tf, idf = line.split('|')
                position=position.split(';')
                position=[x.split(':') for x in position]
                position=[ [int(x[0]), list(map(int, x[1].split(',')))] for x in position ]
                index[term]=position
                tf=tf.split(',')
                tf_dict[term]=list(map(float, tf))
                idf_dict[term]=float(idf)

        #Validating summary_id and position(Values are pre-calcualted manually)
        self.assertEqual([[0,[0]],[1,[0]]],index['book'])
        self.assertEqual([[0, [1]], [1, [1]]], index['nawaz'])
        self.assertEqual([[1, [2]]], index['science'])
        self.assertEqual([[0, [2]]], index['literature'])

        # Validation TF(Values are pre-calcualted manually)
        self.assertEqual([0.5774,0.5774],tf_dict['book'])
        self.assertEqual([0.5774,0.5774], tf_dict['nawaz'])
        self.assertEqual([0.5774], tf_dict['science'])
        self.assertEqual([0.5774], tf_dict['literature'])

        # Validation IDF(Values are pre-calcualted manually)
        self.assertEqual(1.0,idf_dict['book'])
        self.assertEqual(1.0, idf_dict['nawaz'])
        self.assertEqual(2.0, idf_dict['science'])
        self.assertEqual(2.0, idf_dict['literature'])


    def test_query_index(self):

        #One word queries
        qi_obj = QueryIndex(STOPWORD_FILE, TEST_INDEX_FILE, TEST_TRANSFORMED_DATA)
        resp = qi_obj.query_index('science',1)

        self.assertEqual([{'id':1,'summary':'Book by nawaz on science'}],resp)

        resp = qi_obj.query_index('nawaz', 2)
        self.assertEqual([{'id': 1, 'summary': 'Book by nawaz on science'},
                          {'id': 0, 'summary': 'Book by nawaz on literature'}], resp)


        resp = qi_obj.query_index('book', 2)
        self.assertEqual([{'id': 1, 'summary': 'Book by nawaz on science'},
                          {'id': 0, 'summary': 'Book by nawaz on literature'}], resp)

        resp = qi_obj.query_index('by', 2)
        self.assertEqual(None, resp)


        #Free text queries
        resp = qi_obj.query_index('book on science', 2)
        self.assertEqual([{'id': 1, 'summary': 'Book by nawaz on science'},
                          {'id': 0, 'summary': 'Book by nawaz on literature'}], resp)

        resp = qi_obj.query_index('book on', 2)
        self.assertEqual([{'id': 1, 'summary': 'Book by nawaz on science'},
                          {'id': 0, 'summary': 'Book by nawaz on literature'}], resp)


        #Phrase queries

        resp = qi_obj.query_index('"nawaz on science"', 2)
        self.assertEqual([{'id': 1, 'summary': 'Book by nawaz on science'}], resp)

        resp = qi_obj.query_index('"book on science"', 2)
        self.assertEqual([], resp)
