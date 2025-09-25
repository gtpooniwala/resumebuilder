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

### Backend

1. Navigate to the `backend` directory.
2. Create a virtual environment and activate it.
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up the PostgreSQL database using Docker:
   ```
   docker-compose up -d
   ```
5. Run the FastAPI application:
   ```
   uvicorn app.main:app --reload
   ```

### Frontend

1. Navigate to the `frontend` directory.
2. Install the required npm packages:
   ```
   npm install
   ```
3. Start the Next.js application:
   ```
   npm run dev
   ```

## TODO

- Implement user management for multiple users in the backend and frontend.

## Features

- Chatbot interface to interact with users and provide suggestions for resume improvement.
- Display of the resume on the left side of the application with a fixed HTML template.
- Responsive design using Tailwind CSS.

## License

This project is licensed under the MIT License.