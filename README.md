# AI-Powered Resume Builder

An intelligent resume builder application that uses AI agents to help users create, edit, and optimize their resumes through natural language conversations. The system features a React frontend with an AI chatbot powered by LangGraph and OpenAI, backed by a FastAPI backend with PostgreSQL storage.

## 🚀 Key Features

- **AI-Powered Chat Interface**: Natural language conversations to edit and improve resumes
- **LangGraph Agent System**: Intelligent tool orchestration for resume operations
- **Real-time Resume Editing**: Direct database modifications through AI tools
- **Session Management**: Persistent chat sessions with conversation history
- **Change Tracking**: Monitor and log all resume modifications
- **Comprehensive Tool Monitoring**: Detailed logging of AI agent tool usage
- **Responsive Design**: Modern React frontend with Tailwind CSS

## 🏗️ Architecture

```
resumebuilder/
├── backend/                    # FastAPI + LangGraph Backend
│   ├── app/
│   │   ├── api/               # REST API endpoints
│   │   ├── database/          # PostgreSQL models and connections
│   │   ├── models/            # Pydantic data models
│   │   └── services/          # Core business logic
│   │       ├── chat_service.py      # LangGraph agent orchestration
│   │       ├── resume_tools.py      # AI tools for resume operations
│   │       ├── conversation_manager.py # Session & history management
│   │       └── context_manager.py   # Context window management
│   ├── tests/                 # Test suite
│   └── requirements.txt       # Python dependencies
├── frontend/                  # Next.js + TypeScript Frontend
│   └── src/
│       ├── app/               # Next.js 13+ app router
│       └── components/        # React components
│           ├── CollapsibleChatbot.tsx  # Main chat interface
│           ├── ChatHistory.tsx         # Session management UI
│           ├── Resume.tsx              # Resume display component
│           └── ProfileSidebar.tsx      # User profile sidebar
├── docker-compose.yml         # Multi-container orchestration
└── TODO.md                   # Development roadmap
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

#### Required Backend Variables
```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration (handled by Docker Compose)
DATABASE_URL=postgresql://user:password@db:5432/resume_builder

# Logging Level (optional)
LOG_LEVEL=INFO
```

#### Frontend Variables
```bash
# API Endpoint
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note**: For local development with Docker, only `OPENAI_API_KEY` needs to be set. Create a `.env` file in the backend directory with your OpenAI API key.

## 🤖 AI Agent System

The application uses **LangGraph** to orchestrate an intelligent agent system with the following capabilities:

### Available Tools
- `get_full_profile` - Retrieves complete user resume data
- `get_resume_section` - Gets specific resume sections (skills, experience, etc.)
- `edit_professional_summary` - Updates the professional summary
- `update_work_experience` - Adds/edits/removes work experience entries
- `manage_skills` - Manages technical and soft skills
- `search_resume_content` - Searches through resume content

### Agent Behavior
- **Intelligent Tool Selection**: Automatically chooses appropriate tools based on user requests
- **Context Awareness**: Maintains conversation context and session history
- **Action-Oriented**: Makes direct changes to the database rather than just providing suggestions
- **Comprehensive Logging**: Tracks all tool usage with detailed monitoring

## 📊 Current Status

### ✅ Completed Features
- Core chat interface with collapsible sidebar (500px width)
- Session management and chat history
- Complete backend API with 6 resume editing tools
- PostgreSQL database with proper schema
- Docker containerization for easy deployment
- Comprehensive tool monitoring and logging system
- Change tracking and conversation management

### 🚧 In Progress / Known Issues
- **LLM Tool Usage**: Agent currently uses read tools but needs improvement in edit tool usage
- **Frontend Data Integration**: ProfileSidebar needs connection to real API data
- **Chat History UI**: Component exists but needs full functionality implementation

### 📋 Development Roadmap
See [TODO.md](./TODO.md) for detailed development priorities and planned features.

## 🛠️ Technology Stack

- **Frontend**: Next.js 13+, TypeScript, React, Tailwind CSS
- **Backend**: FastAPI, Python 3.12+
- **AI/ML**: LangGraph, OpenAI GPT, LangChain
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Infrastructure**: Docker, Docker Compose
- **Testing**: pytest, React Testing Library

## 📚 Documentation

- **[Agents.md](./Agents.md)** - Detailed explanation of the AI agent system, architecture, and behavior patterns
- **[TODO.md](./TODO.md)** - Development roadmap and planned features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For questions or support, please:
1. Check the [Agents.md](./Agents.md) for system behavior details
2. Review the [TODO.md](./TODO.md) for known issues
3. Open an issue on GitHub for bugs or feature requests
