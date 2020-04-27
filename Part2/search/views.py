from rest_framework.views import APIView
from rest_framework import status
from django.http import JsonResponse


#Local source tree imports
from .author_service import _author
from index.query_index import _query_service


class SearchView(APIView):
    def post(self, request):
        data = request.data
        result=[]
        num_of_results = data['K']
        for query in data['queries']:
            query_obj = _query_service.query_index(query,num_of_results) # Get the matching summaries
            if query_obj:
                for item in query_obj:
                    response = _author.api_call(method='POST',
                                                data='{"book_id":' + str(item['id']) + '}'
                                                )
                    item['query']=query
                    item['author'] = response.json()['author']
                result.append(query_obj)
        return JsonResponse(result,status=status.HTTP_200_OK, safe=False)