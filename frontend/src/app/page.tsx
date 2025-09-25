'use client';

import { useState, useEffect } from 'react';
import Resume from '@/components/Resume';
import Chatbot from '@/components/Chatbot';

export default function Home() {
  const [resumeData, setResumeData] = useState({
    name: "John Doe",
    title: "Software Engineer",
    email: "john.doe@email.com",
    phone: "(555) 123-4567",
    location: "San Francisco, CA",
    summary: "Experienced software engineer with 5+ years of experience in full-stack development. Passionate about creating scalable web applications and solving complex problems.",
    experience: [
      {
        company: "Tech Corp",
        position: "Senior Software Engineer",
        duration: "2021 - Present",
        description: "Led development of microservices architecture, improved system performance by 40%"
      },
      {
        company: "StartupXYZ",
        position: "Full Stack Developer",
        duration: "2019 - 2021",
        description: "Built responsive web applications using React and Node.js, managed database design"
      }
    ],
    skills: ["JavaScript", "Python", "React", "Node.js", "PostgreSQL", "Docker"],
    education: [
      {
        degree: "Bachelor of Science in Computer Science",
        school: "University of California",
        year: "2019"
      }
    ]
  });

  const [chatMessages, setChatMessages] = useState<Array<{type: 'user' | 'bot', message: string}>>([
    {
      type: 'bot',
      message: "Hi! I'm here to help improve your resume. What would you like to work on today?"
    }
  ]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Resume Builder
          </h1>
          <p className="text-gray-600">
            Chat with AI to improve your resume in real-time
          </p>
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-2 gap-8 max-w-7xl mx-auto">
          {/* Resume Section */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4">
              <h2 className="text-xl font-semibold flex items-center">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm2 6a1 1 0 110-2h8a1 1 0 110 2H6zm0 4a1 1 0 110-2h8a1 1 0 110 2H6z" />
                </svg>
                Your Resume
              </h2>
            </div>
            <div className="p-6 max-h-[800px] overflow-y-auto">
              <Resume data={resumeData} />
            </div>
          </div>

          {/* Chatbot Section */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-green-600 to-teal-600 text-white p-4">
              <h2 className="text-xl font-semibold flex items-center">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
                </svg>
                AI Resume Assistant
              </h2>
            </div>
            <div className="flex flex-col h-[800px]">
              <Chatbot 
                messages={chatMessages}
                onSendMessage={(message: string) => {
                  // TODO: Integrate with backend API for chat functionality
                  setChatMessages(prev => [...prev, 
                    { type: 'user' as const, message },
                    { type: 'bot' as const, message: "Thanks for your message! I'm still learning. This will be connected to the backend soon." }
                  ]);
                }}
                onResumeUpdate={setResumeData}
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500">
          <p>Built with Next.js, FastAPI, and AI ✨</p>
        </div>
      </div>
    </div>
  );
}