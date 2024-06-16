from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from utils.azure_openai_manager import AzureOpenAIManager
from datetime import datetime
from django.http import HttpResponse


azure_openai_manager = AzureOpenAIManager(db_name='MapleBondDB', collection_name='ImmigrationCollection')


def index(request):
    now = datetime.now()
    html = f'''
    <html>
        <body>
            <h1>Hello from Vercel!</h1>
            <p>The current time is { now }.</p>
        </body>
    </html>
    '''
    return HttpResponse(html)


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
