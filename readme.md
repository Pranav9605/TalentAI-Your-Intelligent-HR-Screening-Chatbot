# TalentAI - Your Intelligent HR Screening Chatbot

**TalentAI: Your AI-Powered HR Screening Assistant** is a state-of-the-art chatbot designed to revolutionize recruitment screening. With TalentAI, HR professionals can upload a Job Description (JD) file and instantly receive tailored, context-aware responses to HR-related queries—be it about candidate experience, qualifications, or specific job requirements.

## Key Features

- **Job Description Upload:**  
  Easily upload a JD file (TXT format) to provide rich context for HR queries.

- **Intelligent HR Query Handling:**  
  Uses advanced NLP powered by spaCy to detect HR-related keywords and generate responses by incorporating the uploaded JD via the Gemini API.

- **Interactive Chat Interface:**  
  Engage in seamless, real-time conversations with a user-friendly Streamlit interface and view complete chat histories.

- **Modular & Extensible Architecture:**  
  Built using FastAPI and Streamlit for easy customization, scalability, and integration of future HR modules.

## Technologies Used

Python, FastAPI, Streamlit, spaCy, Google Generative AI (Gemini API), pydantic, uvicorn, dotenv

## Setup & Installation

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/YourUsername/TalentAI-Your-Intelligent-HR-Screening-Chatbot.git
    cd TalentAI-Your-Intelligent-HR-Screening-Chatbot
    ```

2. **Set Up Environment Variables:**  
   Create a `.env` file in the project root and add your API key:
    ```dotenv
    GOOGLE_API_KEY=your_google_api_key_here
    ```

3. **Install and Run the Backend:**
    ```bash
    cd backend
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    uvicorn main:app --reload
    ```
    The backend will run at [http://localhost:8000](http://localhost:8000).

4. **Install and Run the Frontend:**
    Open a new terminal window/tab:
    ```bash
    cd frontend
    pip install -r requirements.txt
    streamlit run streamlit_app.py
    ```
    Your browser should open the interface (typically at [http://localhost:8501](http://localhost:8501)).

## Contributing

Contributions are welcome! Please open issues or submit pull requests on the [GitHub repository](https://github.com/YourUsername/TalentAI-Your-Intelligent-HR-Screening-Chatbot/issues) to suggest improvements or report bugs.

## License

This project is licensed under the MIT License.
