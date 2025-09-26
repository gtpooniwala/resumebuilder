# Resume Builder - TODO List

## High Priority Items

### 🔧 Backend - Tool & LLM Issues

- [ ] **Fix LLM not making proper tool calls**
  - LLM is only using read tools (`get_resume_section`) but not editing tools (`manage_skills`, `edit_professional_summary`)
  - Need to strengthen prompt to force tool usage for modifications
  - Add tool call validation and fallback mechanisms
  - Test tool call behavior with different request types

- [ ] **Structured comprehensive logging**
  - ✅ Basic tool monitoring implemented with emojis and timing
  - [ ] Add log levels configuration (DEBUG, INFO, WARN, ERROR)
  - [ ] Create structured JSON logging for production
  - [ ] Add request/response correlation IDs
  - [ ] Implement log aggregation and search
  - [ ] Add performance metrics and alerts

### 🎨 Frontend - UI/UX Improvements

- [ ] **Fix chat history list**
  - Current chat history component exists but may not be fully functional
  - Implement proper session loading and switching
  - Add timestamps and message previews
  - Fix session persistence across page refreshes

- [ ] **Fix left sidebar to use real data**
  - ProfileSidebar currently shows placeholder data
  - Connect to actual user profile API endpoints
  - Display real resume sections and data
  - Add edit capabilities for profile information

- [ ] **Diff tracker in the frontend**
  - Implement change tracking UI component
  - Show before/after comparisons for resume edits
  - Add visual diff highlighting
  - Allow users to accept/reject changes
  - Store change history with timestamps

### 📄 Resume Features

- [ ] **Resume template and formatting**
  - Create multiple professional resume templates
  - Implement PDF export functionality
  - Add customizable styling options
  - Support different resume formats (chronological, functional, hybrid)
  - Add print-friendly layouts

## Medium Priority Items

### 🔐 Security & Multi-tenancy

- [ ] **Authentication and multi tenancy**
  - Implement user registration/login system
  - Add JWT token authentication
  - Create user isolation and data security
  - Implement role-based access control
  - Add OAuth integration (Google, LinkedIn)

### 👤 User Experience

- [ ] **Detailed user profile**
  - Expand user profile beyond basic resume data
  - Add profile photo upload
  - Include career preferences and goals
  - Add skills assessment and recommendations
  - Implement profile completion tracking

## Low Priority / Future Enhancements

### 🚀 Advanced Features

- [ ] **AI-powered suggestions**
  - Industry-specific resume recommendations
  - Skill gap analysis
  - Job description matching
  - ATS optimization suggestions

- [ ] **Collaboration features**
  - Share resume for feedback
  - Real-time collaborative editing
  - Comments and suggestions system
  - Version history and branching

- [ ] **Integration capabilities**
  - LinkedIn profile import
  - Job board integrations
  - ATS system compatibility
  - Calendar integration for interview scheduling

### 🛠️ Technical Improvements

- [ ] **Performance optimizations**
  - Database query optimization
  - Frontend bundle size reduction
  - Caching strategies implementation
  - API response time improvements

- [ ] **Testing & Quality**
  - Increase test coverage (currently basic)
  - Add integration tests
  - Implement E2E testing
  - Add performance testing

- [ ] **DevOps & Deployment**
  - CI/CD pipeline improvements
  - Production monitoring and alerting
  - Database backup and recovery
  - Horizontal scaling capabilities

## Technical Debt

### 🔧 Code Quality

- [ ] **Refactoring needs**
  - Clean up chat service prompt management
  - Standardize error handling across services
  - Improve type safety in TypeScript components
  - Remove unused imports and dependencies

- [ ] **Database improvements**
  - Add proper indexing for performance
  - Implement database migrations
  - Add data validation at database level
  - Consider database partitioning for scale

## Completed Items ✅

- ✅ Chat UI improvements (sidebar size, new session button)
- ✅ Session management implementation
- ✅ Change tracking backend functionality
- ✅ Tool monitoring and logging system
- ✅ Basic resume editing tools (6 tools implemented)
- ✅ Database schema and models setup
- ✅ Docker containerization
- ✅ Basic frontend-backend integration

---

## Notes

- **Current Status**: MVP functionality working, tools integrated but LLM behavior needs fixing
- **Next Sprint Focus**: Fix LLM tool calls and improve chat history functionality
- **Technical Priority**: Logging and monitoring improvements for production readiness
- **User Priority**: Better diff tracking and real data integration in UI

**Last Updated**: September 26, 2025
