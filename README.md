# MapleBond Backend

Welcome to the backend repository of MapleBond, an AI assistant platform providing comprehensive services for Chinese immigrants or those planning to immigrate to North America. MapleBond offers immigration consultation, life advice, educational guidance, job search assistance, and more.

## Project Overview

This project serves as the backend for MapleBond, built using Django and Django REST Framework. The backend leverages Azure OpenAI for language model services and Azure MongoDB for vector storage and data management.

## Features

- **Immigration Consultation**: Provides guidance and advice on immigration processes and requirements.
- **Life Consultation**: Offers practical advice on integrating into North American life, including housing, transportation, and local services.
- **Education Consultation**: Assists with information on educational opportunities, schools, and academic pathways.
- **Job Search Assistance**: Helps users with job hunting, resume building, and interview preparation.

## Technology Stack

- **Django**: A high-level Python web framework that encourages rapid development and clean, pragmatic design.
- **Django REST Framework**: A powerful and flexible toolkit for building Web APIs in Django.
- **Azure OpenAI**: Provides language model services for natural language processing tasks.
- **Azure MongoDB**: Used for vector storage and efficient data management.

## Installation

To get started with the MapleBond backend, follow these steps:

1. **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/maplebond-backend.git
    cd maplebond-backend
    ```

2. **Create a virtual environment and activate it:**
    ```sh
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

    Create a `.env` file in the project root directory and add the following environment variables:

    ```dotenv
    OPENAI_API_KEY=your_openai_api_key
    OPENAI_AZURE_ENDPOINT=your_azure_openai_endpoint
    OPENAI_API_VERSION=your_openai_api_version
    EMBEDDINGS_DEPLOYMENT_NAME=your_embeddings_deployment_name
    COMPLETIONS_DEPLOYMENT_NAME=your_completions_deployment_name

    DB_USER=your_mongodb_user
    DB_PASSWORD=your_mongodb_password
    DB_SERVERNAME=your_mongodb_servername
    ```

5. **Run migrations:**
    ```sh
    python manage.py migrate
    ```

6. **Start the development server:**
    ```sh
    python manage.py runserver
    ```

## Usage

Once the server is running, you can access the API endpoints. Here are some example endpoints:

- **Get available routes:**
    ```sh
    GET /api/routes/
    ```

- **Chatbot interaction:**
    ```sh
    POST /api/chatbot/
    ```

    Example request body:
    ```json
    {
        "input": "Hello, how are you?"
    }
    ```

## Contributing

We welcome contributions to improve MapleBond! Please fork the repository and submit pull requests for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Thank you for your interest in MapleBond! If you have any questions or need further assistance, feel free to open an issue or contact us.
