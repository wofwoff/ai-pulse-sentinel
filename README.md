# AI-Pulse Sentinel

AI-Pulse Sentinel is a real-time AI-powered financial monitoring and sentiment analysis dashboard. It combines live stock data tracking with asynchronous AI text analysis to provide actionable insights into market vibes.

## Project Structure

The project is structured as a monorepo containing both the frontend and backend applications:

*   **`ai-pulse-frontend/`**: The Next.js React application providing the user interface.
*   **`ai-pulse-backend/`**: The FastAPI application handling API requests, WebSocket connections, and background task processing.

## Technologies Used

### Frontend
*   **Next.js 16** (React 19)
*   **TypeScript**
*   **Tailwind CSS** (v4) for styling
*   **Zustand** for state management
*   **Recharts** for data visualization
*   **Framer Motion** for animations
*   **Lucide React** for icons

### Backend
*   **FastAPI** for high-performance REST and WebSocket APIs
*   **Celery** for asynchronous background task processing
*   **Redis** for message brokering and Pub/Sub (real-time updates)
*   **yfinance** for fetching historical stock data
*   **Google Gemini API** (implied via worker) for AI sentiment analysis
*   **Python 3**

## Getting Started

### Prerequisites

Ensure you have the following installed on your system:
*   Node.js (v20+ recommended)
*   Python (v3.10+ recommended)
*   Redis server (must be running for Celery and WebSockets)

### Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd ai-pulse-backend
    ```
2.  Create and activate a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Set up environment variables. Create a `.env` file in the `ai-pulse-backend` directory and add your necessary keys (e.g., `GEMINI_API_KEY`).
5.  Start the FastAPI development server:
    ```bash
    uvicorn main:app --reload
    ```
6.  In a separate terminal (within the backend directory/env), start the Celery worker:
    ```bash
    celery -A worker.celery_app worker --loglevel=info
    ```

### Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd ai-pulse-frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    # or yarn install / pnpm install
    ```
3.  Start the Next.js development server:
    ```bash
    npm run dev
    ```
4.  Open [http://localhost:3000](http://localhost:3000) in your browser to view the application.

## Core Features

*   **Real-time Stock Data**: Fetches and displays the last 50 data points for selected assets (Apple, Nvidia, Tesla, S&P 500, etc.) using `yfinance`.
*   **Asynchronous AI Analysis**: Users can submit text for sentiment analysis. The backend queues the task via Celery and processes it using the Gemini API without blocking the main event loop.
*   **Live Vibe Updates**: Uses WebSockets and Redis Pub/Sub to stream AI analysis results in real-time to the frontend dashboard.
*   **Interactive Dashboard**: A responsive, modern UI built with Next.js and Recharts, visualising price trends and AI-driven "Drift Curves".

## Repository

[https://github.com/wofwoff/ai-pulse-sentinel](https://github.com/wofwoff/ai-pulse-sentinel)
