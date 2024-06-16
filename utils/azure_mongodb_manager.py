import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus
import pymongo

class AzureMongoDBManager:
    def __init__(self, db_name: str, collection_name: str):
        """
        Initialize MongoDB connection.
        :param env_file: Name of the environment file containing database connection info.
        :param db_name: The name of the database to use.
        :param collection_name: The name of the collection to use.
        """
        # Load the environment variables file
        load_dotenv()

        # Retrieve database connection information from environment variables
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        servername = os.getenv('DB_SERVERNAME')

        # Escape user and password to be URL safe
        user = quote_plus(user)
        password = quote_plus(password)

        # Construct the connection string including the database name
        uri = (
            f"mongodb+srv://{user}:{password}@{servername}/{db_name}"
            "?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
        )

        # Create a MongoClient using the connection string and specifying the CA file
        self.client = MongoClient(uri, tlsCAFile=certifi.where())
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.collection_name = collection_name

        # Check if the collection exists and create it if it does not
        if collection_name not in self.db.list_collection_names():
            self.db.create_collection(collection_name)
            print(f"Created collection '{collection_name}'.\n")
        else:
            print(f"Using collection: '{collection_name}'.\n")

    def insert_document(self, document: dict):
        """
        Insert a single document into the collection.
        :param document: A dictionary representing the document to insert.
        :return: The inserted document ID or None if insertion fails.
        """
        try:
            return self.collection.insert_one(document).inserted_id
        except pymongo.errors.PyMongoError as e:
            print(f"Insert failed: {e}")
            return None

    def insert_documents(self, documents: list):
        """
        Insert multiple documents into the collection.
        :param documents: A list of dictionaries representing the documents to insert.
        :return: List of inserted document IDs.
        """
        try:
            return self.collection.insert_many(documents).inserted_ids
        except pymongo.errors.PyMongoError as e:
            print(f"Insert failed: {e}")
            return None

    def update_document(self, query: dict, new_values: dict, multiple: bool = False):
        """
        Update documents in the collection based on a query.
        :param query: A dictionary specifying the query conditions.
        :param new_values: A dictionary specifying the fields to update.
        :param multiple: A boolean to determine if multiple documents should be updated.
        :return: The count of documents updated.
        """
        try:
            if multiple:
                return self.collection.update_many(query, {'$set': new_values}).modified_count
            else:
                return self.collection.update_one(query, {'$set': new_values}).modified_count
        except pymongo.errors.PyMongoError as e:
            print(f"Update failed: {e}")
            return 0

    def query_documents(self, query: dict):
        """
        Query documents from the collection.
        :param query: A dictionary specifying the query conditions.
        :return: A list of documents that match the query.
        """
        try:
            return list(self.collection.find(query))
        except pymongo.errors.PyMongoError as e:
            print(f"Query failed: {e}")
            return []

    def delete_document(self, query: dict, multiple: bool = False):
        """
        Delete documents based on a query.
        :param query: A dictionary specifying the query conditions.
        :param multiple: A boolean to determine if multiple documents should be deleted.
        :return: The count of documents deleted.
        """
        try:
            if multiple:
                return self.collection.delete_many(query).deleted_count
            else:
                return self.collection.delete_one(query).deleted_count
        except pymongo.errors.PyMongoError as e:
            print(f"Delete failed: {e}")
            return 0

    def close_connection(self):
        """
        Close the database connection.
        """
        self.client.close()
