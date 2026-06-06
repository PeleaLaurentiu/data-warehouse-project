# Financial Data Warehouse poject - Pelea Laurentiu

Final project for the Data Warehouse course. This project is a data platform built for a fictional company (Acme Ltd) to ingest, store, and analyze financial market data (stocks and crypto). It includes a backend REST API and an LLM assistant that can answer questions based on the stored data.

## Features
* **ETL Pipeline**: Fetches real-time and historical data from Alpha Vantage and CoinGecko.
* **Temporal Database**: Uses MongoDB to store data without overwriting, maintaining `validFrom` and `active` states to track data provenance.
* **REST API**: Built with FastAPI to serve data and handle analytics requests.
* **Data Analytics**: Apache Spark integration for computing statistics (min/max/mean) and basic price forecasting.
* **Agentic AI**: A Streamlit chat interface powered by Google Gemini, using tool calling (via MCP) to fetch data directly from the API based on user prompts.

## Tech Stack
* **Backend:** Python, FastAPI, Uvicorn
* **Database:** MongoDB
* **Analytics:** Apache Spark
* **Frontend/UI:** Streamlit
* **AI/LLM:** Google Gemini API

## Prerequisites
In order to run the project, the user has to have installed the following:
* Python 3.9+
* A running MongoDB instance
* API keys for Google Gemini and Alpha Vantage

## Installation

1. Get the repository
2. pip install -r requirements.txt
3. Make sure to place all the API keys where are needed

## How to run

1. Data Ingestion (ETL) (dbSetup.py and data_ingestion.py)
2. uvicorn api:main --reload (http://localhost:8000/docs)
3. run mcp_server.py
4. streamlit run gui.py in order to open de AI agent interface
