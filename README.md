Financial Data Warehouse & AI Helper

This project is an end-to-end system that extracts financial data, stores it in a NoSQL database, and exposes it through an API and an AI powered chat interface (gui.py) or in the Visual Code terminal (Basic_AI.py).

Project Overview

Data ingestion & storage (data_ingestion.py): I wrote a Python script that pulls historical data for Microsoft (Alpha Vantage API) and Bitcoin (CoinGecko API). The data is stored in MongoDB.

Backend API (api.py): Built with FastAPI. It handles basic queries for assets, vendors, and time-series data. I also added endpoints for analytics that calculate things like min, max, average prices and basic short term trends.

AI Assistant: I built a simple web UI using Streamlit and Google's Gemini model. The LLM is integrated via tool calling. When you ask the bot a question, it doesn't just guess the answer; it actively calls the FastAPI endpoints, reads the JSON from database, and formulates an answer based strictly on that data.

Tech Stack
Python, MongoDB, FastAPI, Streamlit, Google GenAI.
