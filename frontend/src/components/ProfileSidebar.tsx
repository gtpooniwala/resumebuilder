'use client';

import { useState } from 'react';

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

interface ProfileSidebarProps {
  profileData: ProfileData;
  onProfileUpdate: (data: Partial<ProfileData>) => void;
}

export default function ProfileSidebar({ profileData, onProfileUpdate }: ProfileSidebarProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    name: profileData.name,
    title: profileData.title
  });

  const handleSave = () => {
    onProfileUpdate({
      name: editData.name,
      title: editData.title
    });
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditData({
      name: profileData.name,
      title: profileData.title
    });
    setIsEditing(false);
  };

  const calculateCompletion = () => {
    let completed = 0;
    let total = 7;
    
    if (profileData.name) completed++;
    if (profileData.title) completed++;
    if (profileData.email) completed++;
    if (profileData.phone) completed++;
    if (profileData.location) completed++;
    if (profileData.linkedin) completed++;
    if (profileData.bio) completed++;
    
    return Math.round((completed / total) * 100);
  };

  const menuItems = [
    { icon: "👤", label: "Personal Info", active: true },
    { icon: "💼", label: "Experience", active: false },
    { icon: "🎓", label: "Education", active: false },
    { icon: "🛠️", label: "Skills", active: false },
    { icon: "🏆", label: "Achievements", active: false },
    { icon: "📄", label: "Templates", active: false },
  ];

  const quickStats = [
    { label: "Profile Views", value: profileData.stats.profileViews.toString() },
    { label: "Downloads", value: profileData.stats.downloadsThisMonth.toString() },
    { label: "Resumes Created", value: profileData.stats.resumesCreated.toString() },
  ];

  return (
    <div className="w-80 bg-white border-r border-gray-200 h-screen flex flex-col">
      {/* Profile Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex flex-col items-center text-center">
          {/* Avatar */}
          <div className="relative mb-4">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              {profileData.name.split(' ').map((n: string) => n[0]).join('')}
            </div>
            <button className="absolute -bottom-1 -right-1 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs hover:bg-blue-700 transition-colors">
              ✏️
            </button>
          </div>

          {/* Name and Title */}
          {isEditing ? (
            <div className="w-full space-y-2">
              <input
                type="text"
                value={editData.name}
                onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                className="w-full px-3 py-1 text-lg font-semibold text-center border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="text"
                value={editData.title}
                onChange={(e) => setEditData({ ...editData, title: e.target.value })}
                className="w-full px-3 py-1 text-sm text-center text-gray-600 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="flex space-x-2 mt-3">
                <button
                  onClick={handleSave}
                  className="flex-1 px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors"
                >
                  Save
                </button>
                <button
                  onClick={handleCancel}
                  className="flex-1 px-3 py-1 bg-gray-300 text-gray-700 text-xs rounded hover:bg-gray-400 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <>
              <h2 className="text-xl font-bold text-gray-800 mb-1">{profileData.name}</h2>
              <p className="text-gray-600 text-sm mb-3">{profileData.title}</p>
              <button
                onClick={() => setIsEditing(true)}
                className="text-blue-600 hover:text-blue-700 text-xs flex items-center space-x-1"
              >
                <span>✏️</span>
                <span>Edit Profile</span>
              </button>
            </>
          )}
        </div>

        {/* Completion Progress */}
        <div className="mt-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Profile Completion</span>
            <span className="text-sm font-medium text-blue-600">{calculateCompletion()}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${calculateCompletion()}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Add more sections to improve your profile strength
          </p>
        </div>
      </div>

      {/* Navigation Menu */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Resume Sections
          </h3>
          <div className="space-y-1">
            {menuItems.map((item, index) => (
              <button
                key={index}
                className={`w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors ${
                  item.active 
                    ? 'bg-blue-50 text-blue-700 border border-blue-200' 
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <span className="mr-3 text-base">{item.icon}</span>
                {item.label}
                {item.active && (
                  <span className="ml-auto w-2 h-2 bg-blue-500 rounded-full"></span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="p-4 border-t border-gray-200">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Quick Stats
          </h3>
          <div className="space-y-3">
            {quickStats.map((stat, index) => (
              <div key={index} className="flex justify-between items-center">
                <span className="text-sm text-gray-600">{stat.label}</span>
                <span className="text-sm font-medium text-gray-900">{stat.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="p-4 border-t border-gray-200">
          <div className="space-y-2">
            <button className="w-full px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors">
              Download PDF
            </button>
            <button className="w-full px-4 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200 transition-colors">
              Share Resume
            </button>
            <button className="w-full px-4 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200 transition-colors">
              Preview Mode
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
