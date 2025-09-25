# Resume Builder App

This project is a Resume Builder application that allows users to interact with a chatbot to improve their resumes. The application is structured with a separate backend and frontend, utilizing FastAPI for the backend and Next.js for the frontend.

## Project Structure

The project is organized as follows:

```
resume-builder-app
├── backend                # Backend application using FastAPI
│   ├── app                # Main application package
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Dockerfile for backend
│   └── .env.example        # Example environment variables
├── frontend               # Frontend application using Next.js
│   ├── src                # Source files for the frontend
│   ├── package.json       # npm dependencies and scripts
│   ├── next.config.js     # Next.js configuration
│   ├── tailwind.config.js  # Tailwind CSS configuration
│   └── tsconfig.json      # TypeScript configuration
├── docker-compose.yml     # Docker Compose configuration
├── .gitignore             # Git ignore file
└── README.md              # Project documentation
```

## Setup Instructions

### Quick Start with Docker (Recommended)

The easiest way to run the entire application stack is using Docker Compose:

1. **Clone and navigate to the project directory:**
   ```bash
   git clone <repository-url>
   cd resumebuilder
   ```

2. **Start all services (database, backend, and frontend):**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Database: localhost:5432

4. **Stop all services:**
   ```bash
   docker-compose down
   ```

### Manual Setup (Development)

If you prefer to run services individually:

#### Database Setup
```bash
# Start only the PostgreSQL database
docker-compose up db -d
```

#### Backend Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI application:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Start the Next.js application:
   ```bash
   npm run dev
   ```

### Environment Variables

The application uses the following default environment variables in Docker:
- `DATABASE_URL`: postgresql://user:password@db:5432/resume_builder
- `NEXT_PUBLIC_API_URL`: http://localhost:8000

For production deployment, create appropriate `.env` files in the backend and frontend directories.

## TODO

- Implement user management for multiple users in the backend and frontend.

## Features

- Chatbot interface to interact with users and provide suggestions for resume improvement.
- Display of the resume on the left side of the application with a fixed HTML template.
- Responsive design using Tailwind CSS.

## License

This project is licensed under the MIT License.
