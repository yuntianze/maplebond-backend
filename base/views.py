from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from utils.azure_openai_manager import AzureOpenAIManager

azure_openai_manager = AzureOpenAIManager(db_name='MapleBondDB', collection_name='ImmigrationCollection')

@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/chat/',
        '/api/topics/',
    ]
    return Response(routes)


@api_view(['POST'])
def startChat(request):
    user_input = request.data.get('input')
    if not user_input:
        return Response({'error': 'No input provided'}, status=400)

    try:
        openai_response = azure_openai_manager.rag_with_vector_search(question=user_input)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

    return Response(openai_response, status=200)
