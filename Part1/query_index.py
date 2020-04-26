import re
from collections import defaultdict
import copy
import json
import functools

STOPWORD_FILE = 'stopwords.dat'
RAW_DATA_FILE = 'data.json'
TRANSFORMED_DATA_FILE = 'transformed_data.json'
INDEX_FILE = 'index.txt'


class QueryIndex:

    def __init__(self, stopword_file, index_file, transformed_data_file):
        self.index={}
        self.tf={}      #term frequencies
        self.idf={}    #inverse document frequencies
        self.stopwords = self._get_stopwords(stopword_file) #Stores all the stopwords defined in stopword file
        self.index_file = index_file # Stores the index file which is generated after parsing our data
        self.transformed_data_file = transformed_data_file # Transformed file to improve performance

    def _intersect_lists(self,lists):
        if len(lists)==0:
            return []
        #start intersecting from the smaller list
        lists.sort(key=len)
        return list(functools.reduce(lambda x,y: set(x)&set(y),lists))

    def _get_stopwords(self,stopword_file):
        '''
        Gets stopwords from the stopwords file
        '''
        with open(stopword_file, 'r') as swf:
            sw=[line.rstrip() for line in swf]
            stopwords=dict.fromkeys(sw)
        return stopwords

    def _get_terms(self, line):
        line=line.lower()
        line=re.sub(r'[^a-z0-9 ]',' ',line) #put spaces instead of non-alphanumeric characters
        line=line.split()
        line=[x for x in line if x not in self.stopwords]
        return line


    def get_positions(self, terms):
        #all terms in the list are guaranteed to be in the index
        return [ self.index[term] for term in terms ]


    def get_summaries_from_positions(self, positions):
        #no empty list in positions
        return [ [x[0] for x in p] for p in positions ]

    def read_index(self):
        with open(self.index_file, 'r') as index_file:
            # first read the number of documents
            self.num_summaries=int(index_file.readline().rstrip())
            for line in index_file:
                line=line.rstrip()
                term, position, tf, idf = line.split('|')
                position=position.split(';')
                position=[x.split(':') for x in position]
                position=[ [int(x[0]), list(map(int, x[1].split(',')))] for x in position ]
                self.index[term]=position
                #read term frequencies
                tf=tf.split(',')
                self.tf[term]=list(map(float, tf))
                #read inverse document frequency
                self.idf[term]=float(idf)


    def dotProduct(self, vec1, vec2):
        if len(vec1)!=len(vec2):
            return 0
        return sum([ x*y for x,y in zip(vec1,vec2) ])


    def rankDocuments(self, terms, match_indexes,k):
        #term at a time evaluation
        docVectors=defaultdict(lambda: [0]*len(terms))
        queryVector=[0]*len(terms)
        for termIndex, term in enumerate(terms):
            if term not in self.index:
                continue

            queryVector[termIndex]=self.idf[term]

            for i, (summary_id, postings) in enumerate(self.index[term]):
                if summary_id in match_indexes:
                    docVectors[summary_id][termIndex]=self.tf[term][i]

        #calculate the score of each summary
        docScores=[ [self.dotProduct(curDocVec, queryVector), doc] for doc, curDocVec in docVectors.items() ]
        docScores.sort(reverse=True)
        result=[x[1] for x in docScores][:k]

        #Print the final response
        return self._serialize(result)

    def _serialize(self,result):
        response=[]
        with open(self.transformed_data_file,'r') as tdf:
            json_file = json.load(tdf)

        for x in result:
            response.append({"id": x,
                             "summary":json_file['summaries'][str(x)]})
        return response



    def one_word_query(self,query,k):
        query=self._get_terms(query)
        if len(query)==0:
            print('')
            return

        q = query[0]
        if q not in self.index:
            print("No results found for {}".format(query))
            return
        else:
            matches=self.index[q]
            match_index =[x[0] for x in matches]
            return self.rankDocuments(query, match_index,k)


    def free_text_query(self,query,k):
        query=self._get_terms(query)
        if len(query)==0:
            print('')
            return

        li=set()
        for term in query:
            try:
                positions=self.index[term]
                docs=[x[0] for x in positions]
                li=li|set(docs)
            except:
                #term not in index
                pass

        li=list(li)
        return self.rankDocuments(query, li,k)


    def phrase_query(self,query,k):
        originalQuery=query
        query=self._get_terms(query)
        if len(query)==0:
            print('')
            return
        elif len(query)==1:
            self.one_word_query(originalQuery)
            return

        phraseDocs=self.phrase_query_summaries(query)
        return self.rankDocuments(query, phraseDocs,k)


    def phrase_query_summaries(self, terms):
        '''
        Takes in all the terms user has searched for and checks in summaries
        '''
        phraseDocs=[]
        length=len(terms)
        #first find matching summaries
        for term in terms:
            if term not in self.index:
                #if a term doesn't appear in the index
                #there can't be any document maching it
                return []

        positions=self.get_positions(terms)    #all the terms in q are in the index
        summary_ids=self.get_summaries_from_positions(positions)
        #Filter only those summaries which contain all the terms of the query
        summary_ids=self._intersect_lists(summary_ids)
        #postings are the postings list of the terms in the documents docs only
        for i in range(len(positions)):
            positions[i]=[x for x in positions[i] if x[0] in summary_ids]

        #check whether the term ordering in the summary is like in the phrase query

        #subtract i from the ith terms location in the summary
        positions=copy.deepcopy(positions)

        for i in range(len(positions)):
            for j in range(len(positions[i])):
                positions[i][j][1]=[x-i for x in positions[i][j][1]]

        #intersect the locations
        result=[]
        for i in range(len(positions[0])):
            li=self._intersect_lists( [x[i][1] for x in positions] )
            if li==[]:
                continue
            else:
                result.append(positions[0][i][0])    #append the summary_id to the result

        return result

    def query_index(self,query,k):
        '''

        :param query: Accepts the keyword/phrase that needs to be searched
        :param k: The number of matching results
        There can be 3 types of queries which are searched by the search engine.
        It it contains quotation marks, it is a phrase query.Exact match will be checked for this search.
        If the length of query is 1, it's considered as a single word query.
        Otherwise, it's a free text query.Not all words need to match in this case
        The relevance is calculated by the (term frequency * inverse document frequency).
        '''
        self.read_index()

        if '"' in query:
            return self.phrase_query(query,k)
        elif len(query.split()) > 1:
            return self.free_text_query(query,k)
        else:
            return self.one_word_query(query,k)

_query_service = QueryIndex(STOPWORD_FILE,INDEX_FILE,TRANSFORMED_DATA_FILE)

if __name__=='__main__':
    stopword_file = STOPWORD_FILE
    index_file = INDEX_FILE
    transformed_data_file = TRANSFORMED_DATA_FILE
    q=QueryIndex(stopword_file, index_file, transformed_data_file)
    print(q.query_index('book',1))


