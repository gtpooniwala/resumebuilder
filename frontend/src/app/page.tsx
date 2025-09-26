'use client';

import { useState } from 'react';
import Resume from '@/components/Resume';
import CollapsibleChatbot from '@/components/CollapsibleChatbot';
import ProfileSidebar from '@/components/ProfileSidebar';

interface Message {
  type: 'user' | 'bot';
  message: string;
  timestamp?: Date;
}

interface ProfileData {
  id: string;
  name: string;
  title: string;
  email: string;
  phone: string;
  location: string;
  linkedin?: string;
  website?: string;
  avatar?: string;
  bio?: string;
  preferences: {
    theme: 'light' | 'dark';
    notifications: boolean;
    autoSave: boolean;
  };
  subscription: {
    plan: 'free' | 'pro' | 'premium';
    expiresAt?: Date;
  };
  stats: {
    resumesCreated: number;
    profileViews: number;
    downloadsThisMonth: number;
    lastActive: Date;
  };
}

interface ResumeData {
  personalInfo: {
    name: string;
    title: string;
    email: string;
    phone: string;
    location: string;
    linkedin: string;
    website: string;
  };
  summary: string;
  experience: Array<{
    company: string;
    position: string;
    duration: string;
    description: string;
  }>;
  skills: {
    technical: string[];
    soft: string[];
  };
  education: Array<{
    institution: string;
    degree: string;
    year: string;
    gpa?: string;
  }>;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      type: 'bot',
      message: 'Hello! I\'m here to help you improve your resume. What would you like to work on today?',
      timestamp: new Date()
    }
  ]);

  const [profileData, setProfileData] = useState<ProfileData>({
    id: "profile-1",
    name: "John Doe",
    title: "Senior Software Engineer", 
    email: "john.doe@email.com",
    phone: "(555) 123-4567",
    location: "San Francisco, CA",
    linkedin: "linkedin.com/in/johndoe",
    website: "johndoe.dev",
    bio: "Passionate software engineer with expertise in full-stack development.",
    preferences: {
      theme: 'light',
      notifications: true,
      autoSave: true
    },
    subscription: {
      plan: 'pro',
      expiresAt: new Date('2024-12-31')
    },
    stats: {
      resumesCreated: 3,
      profileViews: 247,
      downloadsThisMonth: 12,
      lastActive: new Date()
    }
  });

  const [resumeData, setResumeData] = useState<ResumeData>({
    personalInfo: {
      name: "John Doe", 
      title: "Senior Software Engineer",
      email: "john.doe@email.com",
      phone: "(555) 123-4567",
      location: "San Francisco, CA",
      linkedin: "linkedin.com/in/johndoe",
      website: "johndoe.dev"
    },
    summary: "Experienced software engineer with 8+ years developing scalable web applications and leading cross-functional teams. Passionate about clean code, system architecture, and mentoring junior developers.",
    experience: [
      {
        company: "Tech Corp",
        position: "Senior Software Engineer",
        duration: "2021 - Present",
        description: "Lead development of microservices architecture serving 1M+ users daily. Mentored 5 junior developers and improved system performance by 40%."
      },
      {
        company: "StartupXYZ",
        position: "Full Stack Developer",
        duration: "2019 - 2021", 
        description: "Built and deployed 15+ features using React, Node.js, and PostgreSQL. Collaborated with design team to improve user experience and increase conversion by 25%."
      },
      {
        company: "Digital Agency",
        position: "Frontend Developer",
        duration: "2017 - 2019",
        description: "Developed responsive websites for 20+ clients using modern JavaScript frameworks. Optimized loading times by 60% through performance improvements."
      }
    ],
    skills: {
      technical: ["JavaScript", "TypeScript", "React", "Node.js", "Python", "PostgreSQL", "AWS", "Docker"],
      soft: ["Leadership", "Communication", "Problem Solving", "Team Collaboration", "Project Management"]
    },
    education: [
      {
        institution: "University of California, Berkeley",
        degree: "Bachelor of Science in Computer Science",
        year: "2017",
        gpa: "3.8"
      }
    ]
  });

  const handleSendMessage = async (message: string) => {
    const newMessage: Message = {
      type: 'user',
      message,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, newMessage]);
    
    try {
      // Call the LangGraph chat API
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          user_id: profileData.id,
          context: {
            profile: profileData,
            resume: resumeData
          }
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const botResponse: Message = {
        type: 'bot',
        message: data.response,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, botResponse]);
    } catch (error) {
      console.error('Chat API error:', error);
      
      // Fallback to local response
      const fallbackResponse: Message = {
        type: 'bot',
        message: "I'm sorry, I'm having trouble connecting to the chat service right now. Please try again later.",
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, fallbackResponse]);
    }
  };

  const generateBotResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.includes('summary') || lowerMessage.includes('improve')) {
      return "I can help you enhance your professional summary. Consider highlighting your most impactful achievements and quantifying your results. Would you like me to suggest specific improvements?";
    } else if (lowerMessage.includes('skills')) {
      return "Great! Let's work on your skills section. I notice you have a good mix of technical and soft skills. Would you like to add any emerging technologies or leadership experience?";
    } else if (lowerMessage.includes('experience')) {
      return "Your work experience looks solid! To make it even stronger, try to include more specific metrics and outcomes. For example, 'Led team of X developers' or 'Increased performance by Y%'. What specific achievements would you like to highlight?";
    } else if (lowerMessage.includes('format')) {
      return "The current format looks clean and professional. Would you like me to suggest any layout improvements or different ways to organize your information?";
    } else {
      return "I'm here to help you improve your resume! I can assist with enhancing your summary, adding more impactful descriptions to your work experience, optimizing your skills section, or improving the overall format. What would you like to focus on?";
    }
  };

  const handleResumeUpdate = (newData: Partial<ResumeData>) => {
    setResumeData(prev => ({
      ...prev,
      ...newData
    }));
  };

  const handleProfileUpdate = (data: Partial<ProfileData>) => {
    setProfileData(prev => ({
      ...prev,
      ...data
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 py-4 px-6 shadow-sm">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            AI Resume Builder
          </h1>
          <p className="text-gray-600 text-sm mt-1">
            Transform your resume with intelligent suggestions and real-time feedback
          </p>
        </div>
      </header>
      
      {/* Three-column layout */}
      <div className="flex h-screen overflow-hidden">
        {/* Left Sidebar - Profile */}
        <div className="w-80 bg-white border-r border-gray-200 flex-shrink-0">
          <ProfileSidebar 
            profileData={profileData}
            onProfileUpdate={handleProfileUpdate}
          />
        </div>
        
        {/* Center - Resume (flexible width) */}
        <div className="flex-1 bg-white overflow-y-auto">
          <div className="p-8 max-w-4xl mx-auto">
            <Resume data={resumeData} />
          </div>
        </div>
        
        {/* Right Sidebar - Collapsible Chatbot */}
        <CollapsibleChatbot 
          messages={messages}
          onSendMessage={handleSendMessage}
          onResumeUpdate={handleResumeUpdate}
        />
      </div>
    </div>
  );
}
