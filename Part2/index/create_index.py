import sys
import re
from collections import defaultdict
from array import array
import math
from .tranform_data import *


class CreateIndex:

    def __init__(self, stopword_file, raw_data_file, target_data_file, index_file):
        self.index=defaultdict(list)    #the inverted index
        self.tf=defaultdict(list)       #term frequencies of terms in each summary
        self.df=defaultdict(int)        #frequencies of terms in the complete data
        self.num_summaries=0            #Stores total number of summaries
        self.stopwords = self._get_stopwords(stopword_file) #Stores all the stopwords defined in stopword file
        self.raw_data_file = raw_data_file #This is the raw data file got by web scraping
        self.target_data_file = target_data_file
        self.index_file = index_file # This is the final index file that is created

    def _get_stopwords(self,stopword_file):
        '''
        Gets stopwords from the stopwords file
        '''
        with open(stopword_file, 'r') as stopword_file:
            sw=[line.rstrip() for line in stopword_file]
            stopwords=dict.fromkeys(sw)
        return stopwords

    def _get_terms(self, line):
        '''
        Given a stream of text, get the terms from the text
        '''
        line=line.lower()
        line=re.sub(r'[^a-z0-9 ]',' ',line) #put spaces instead of non-alphanumeric characters
        line=line.split()
        line=[x for x in line if x not in self.stopwords]  #eliminate the stopwords
        return line

    def _get_transformed_data(self):
        '''
        Gets the transformed data which will be used to create indexes
        '''
        tranform_data_obj = DataTransformation(self.raw_data_file, self.target_data_file)
        tranform_data_obj.transform_data()
        return tranform_data_obj.summary_dict


    def _write_to_file(self):
        '''
        Write the index to the file
        Format: keyword|summary_id:position|tf|idf
        '''
        with open(self.index_file, 'w') as index_file:
            index_file.write(str(self.num_summaries))
            index_file.write('\n')
            self.num_summaries=float(self.num_summaries)
            for term in self.index.keys():
                postinglist=[]
                for p in self.index[term]:
                    docID=p[0]
                    positions=p[1]
                    postinglist.append(':'.join([str(docID) ,','.join(map(str,positions))]))
                postingData=';'.join(postinglist)
                tfData=','.join(map(str,self.tf[term]))
                idfData='%.4f' % (self.num_summaries/self.df[term])
                index_file.write('|'.join((term, postingData, tfData, idfData)))
                index_file.write('\n')

    def create_index(self):
        '''
        Creates the index on summaries and saves it into a file.
        Also calculates the term frequencies and inverse document frequency.
        '''
        summary_dict = self._get_transformed_data()
        for key,summary in  summary_dict['summaries'].items():
            terms=self._get_terms(summary)
            self.num_summaries+=1

            #build the index for the current page
            term_dict={}
            for position, term in enumerate(terms):
                try:
                    term_dict[term][1].append(position)
                except:
                    term_dict[term]=[key, array('I',[position])]

            #normalizing the data
            norm=0
            for term, posting in term_dict.items():
                norm+=len(posting[1])**2
            norm=math.sqrt(norm)

            #calculate the tf and df weights
            for term, posting in term_dict.items():
                self.tf[term].append('%.4f' % (len(posting[1])/norm))
                self.df[term]+=1

            #merge the current index with the main index
            for term, position in term_dict.items():
                self.index[term].append(position)
        self._write_to_file()
        
    
if __name__=="__main__":
    STOPWORD_FILE = 'stopwords.dat'
    RAW_DATA_FILE = 'data.json'
    TRANSFORMED_DATA_FILE = 'transformed_data.json'
    INDEX_FILE = 'index.txt'
    c=CreateIndex(STOPWORD_FILE, RAW_DATA_FILE, TRANSFORMED_DATA_FILE, INDEX_FILE)
    c.create_index()