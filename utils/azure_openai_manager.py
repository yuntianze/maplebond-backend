
import os
import json
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv
from openai import AzureOpenAI
from utils.azure_mongodb_manager import AzureMongoDBManager
from .logger import logger, timeit

class AzureOpenAIManager:
    def __init__(self, db_name: str, collection_name: str):
        """
        Initialize the Azure OpenAI Manager with credentials and client setup.
        :param env_file: The environment file containing all necessary API configuration.
        """
        load_dotenv()  # Load the environment variables

        # Retrieve API credentials and endpoint from environment variables
        api_key = os.getenv('OPENAI_API_KEY')
        azure_endpoint = os.getenv('OPENAI_AZURE_ENDPOINT')
        api_version = os.getenv('OPENAI_API_VERSION')
        self.embeddings_model = os.getenv('EMBEDDINGS_DEPLOYMENT_NAME')
        self.completions_model = os.getenv('COMPLETIONS_DEPLOYMENT_NAME')

        # Setup Azure OpenAI client
        self.client = AzureOpenAI(azure_endpoint=azure_endpoint, api_key=api_key, api_version=api_version)

        # Initialize MongoDB Manager
        self.mongo_manager = AzureMongoDBManager(db_name, collection_name)
        
    def quick_reply(self, question: str, max_tokens: int = 4096):
        """
        Generate a quick reply response to a question using the configured Azure OpenAI API completions model.
        :param question: The question to generate a response to.
        :param max_tokens: The maximum number of tokens to generate in the response.
        :return: The generated response to the question.
        """
        system_prompt = '''
        You are MapleBondBak, A North American native life specialist, designed to assist with immigration, studying, job hunting, and housing in North America.
            - Respond to user queries based on the provided data, focusing on practical advice for integrating into North American life.
            - Provide answers in a clear, concise list format, with two lines of whitespace between each answer.
            - If the query is unclear or beyond the scope of available information, respond with "I'm not sure" and suggest that the user might want to explore further on their own.
        '''
        formatted_prompt = system_prompt + "System-generated context based on user query:\n\n"        
        messages = [
            {"role": "system", "content": formatted_prompt},
            {"role": "user", "content": question}
        ]

        completion = self.client.chat.completions.create(messages=messages, model=self.completions_model)
        return completion.choices[0].message.content
        
    def generate_embeddings(self, text: str):
        """
        Generate embeddings from a string of text using the configured Azure OpenAI API embeddings model.
        :param text: The text from which to generate embeddings.
        :return: A list of floats representing the embedding vector.
        """
        response = self.client.embeddings.create(input=text, model=self.embeddings_model)
        embeddings = response.data[0].embedding
        return embeddings

    def add_collection_content_vector_field(self, field: str):
        collection = self.mongo_manager.collection
        bulk_operations = []
        count = 0
        batch_size = 50
        with self.mongo_manager.client.start_session() as session:
            cursor = collection.find(no_cursor_timeout=True, session=session).batch_size(batch_size)
            try:
                for doc in cursor:
                    content = json.dumps(doc.get(field, ""), default=str)
                    content_vector = self.generate_embeddings(content)

                    bulk_operations.append(UpdateOne(
                        {"_id": doc["_id"]},
                        {"$set": {"contentVector": content_vector}},
                        upsert=True
                    ))
                    count += 1

                    if len(bulk_operations) >= batch_size:
                        collection.bulk_write(bulk_operations)
                        bulk_operations = []
                        logger.info(f"Bulk update completed for {count} documents.")

                if bulk_operations:
                    collection.bulk_write(bulk_operations)
                    logger.info(f"Final bulk update completed for {count} documents.")

            except BulkWriteError as bwe:
                logger.error(f"Bulk write error occurred: {bwe.details}")
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
            finally:
                cursor.close()

    def create_vector_index(self):
        """
        Creates a vector index on the 'contentVector' field in the MongoDB collection.
        """
        index_command = {
            'createIndexes': self.mongo_manager.collection_name,
            'indexes': [
                {
                    'name': 'VectorSearchIndex',
                    'key': {"contentVector": "cosmosSearch"},
                    'cosmosSearchOptions': {
                        'kind': 'vector-ivf',
                        'numLists': 1,  # Adjust based on your expected dataset size
                        'similarity': 'COS',
                        'dimensions': 1536  # Ensure this matches the dimensions of your embeddings
                    }
                }
            ]
        }
        try:
            result = self.mongo_manager.db.command(index_command)
            logger.info("Index creation result:", result)
        except Exception as e:
            logger.error("An error occurred while creating the vector index:", str(e))

    def delete_vector_index(self):
        """
        Deletes the vector index on the 'contentVector' field in the MongoDB collection.
        """
        index_name = 'VectorSearchIndex'

        try:
            result = self.mongo_manager.collection.drop_index(index_name)
            logger.info("Index deletion result:", result)
        except Exception as e:
            logger.error("An error occurred while deleting the vector index:", str(e))

    def vector_search(self, query_text, num_results=3):
        """
        Perform a vector search to find the most similar documents based on the query.
        :param query_text: The text query to search against document vectors.
        :param num_results: The number of top similar documents to return.
        :return: A list of documents sorted by similarity.
        """
        collection = self.mongo_manager.collection
        query_embedding = self.generate_embeddings(query_text)
        pipeline = [
            {
                '$search': {
                    "cosmosSearch": {
                        "vector": query_embedding,
                        "path": "contentVector",
                        "k": num_results
                    },
                    "returnStoredSource": True}},
            {'$project': {'similarityScore': {'$meta': 'searchScore'}, 'document': '$$ROOT'}}
        ]
        results = collection.aggregate(pipeline)
        return list(results)

    @timeit
    def rag_with_vector_search(self, question, num_results=1):
        """
        Generate a response using RAG technique based on vector search results from the incoming question.
        :param question: The user's query question.
        :param num_results: Number of search results to utilize for generating the response.
        :return: The generated text response from Azure OpenAI.
        """
        system_prompt = '''
        You are MapleBond, A North American native life specialist, designed to assist with immigration, studying, job hunting, and housing in North America.
            - Respond to user queries based on the provided data, focusing on practical advice for integrating into North American life.
            - Provide answers in a clear, concise list format, with two lines of whitespace between each answer.
            - If the query is unclear or beyond the scope of available information, respond with "I'm not sure" and suggest that the user might want to explore further on their own.
        '''

        results = self.vector_search(question, num_results)
        for result in results:
            logger.info(f"Similarity Score: {result['similarityScore']}")
            logger.info(f"Title: {result['document']['title']}")
            logger.info(f"Content: {result['document']['desc']}\n")

        # Extract and use only relevant parts of the documents to stay within token limits
        result_list = "\n".join(json.dumps(
            {
                "title": result['document'].get('title', ''),
                "desc": result['document'].get('desc', '')
            }, indent=4, default=str) for result in results)

        # Format the prompt for the LLM
        formatted_prompt = system_prompt + "System-generated context based on user query:\n" + result_list

        # Split prompt if it is too long
        max_tokens = 4096
        prompt_tokens = len(formatted_prompt.split())
        if prompt_tokens > max_tokens:
            formatted_prompt = formatted_prompt[:max_tokens]
            
         # Ensure formatted_prompt is a valid string
        formatted_prompt = formatted_prompt.strip()

        # prepare the LLM request
        messages = [
            {"role": "system", "content": formatted_prompt},
            {"role": "user", "content": question}
        ]
        
        logger.info(f"Sending request to Azure OpenAI for RAG completion with vector search: {messages}")

        response = self.client.chat.completions.create(messages=messages, model=self.completions_model, timeout=30)
        return response.choices[0].message.content