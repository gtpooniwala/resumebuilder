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

interface ResumeProps {
  data: ResumeData;
}

export default function Resume({ data }: ResumeProps) {
  return (
    <div className="resume-container bg-white text-gray-800 font-serif leading-relaxed">
      {/* Header - Enhanced */}
      <div className="mb-8 bg-gradient-to-r from-blue-600 to-purple-600 text-white p-8 rounded-lg -mx-8 -mt-8 mb-8">
        <h1 className="text-4xl font-bold mb-2">{data.personalInfo.name}</h1>
        <h2 className="text-2xl text-blue-100 mb-6">{data.personalInfo.title}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-50">
          <div className="flex items-center">
            <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
              <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
            </svg>
            {data.personalInfo.email}
          </div>
          <div className="flex items-center">
            <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"/>
            </svg>
            {data.personalInfo.phone}
          </div>
          <div className="flex items-center">
            <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd"/>
            </svg>
            {data.personalInfo.location}
          </div>
          <div className="flex items-center">
            <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.083 9h1.946c.089-1.546.383-2.97.837-4.118A6.004 6.004 0 004.083 9zM10 2a8 8 0 100 16 8 8 0 000-16zm0 2c-.076 0-.232.032-.465.262-.238.234-.497.623-.737 1.182-.389.907-.673 2.142-.766 3.556h3.936c-.093-1.414-.377-2.649-.766-3.556-.24-.559-.499-.948-.737-1.182C10.232 4.032 10.076 4 10 4zm3.971 5c-.089-1.546-.383-2.97-.837-4.118A6.004 6.004 0 0115.917 9h-1.946zm-2.003 2H8.032c.093 1.414.377 2.649.766 3.556.24.559.499.948.737 1.182.233.23.389.262.465.262.076 0 .232-.032.465-.262.238-.234.497-.623.737-1.182.389-.907.673-2.142.766-3.556zm1.166 4.118c.454-1.147.748-2.572.837-4.118h1.946a6.004 6.004 0 01-2.783 4.118zm-6.268 0C6.412 13.97 6.118 12.546 6.03 11H4.083a6.004 6.004 0 002.783 4.118z" clipRule="evenodd"/>
            </svg>
            {data.personalInfo.website}
          </div>
          {data.personalInfo.linkedin && (
            <div className="flex items-center md:col-span-2">
              <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.338 16.338H13.67V12.16c0-.995-.017-2.277-1.387-2.277-1.39 0-1.601 1.086-1.601 2.207v4.248H8.014v-8.59h2.559v1.174h.037c.356-.675 1.227-1.387 2.526-1.387 2.703 0 3.203 1.778 3.203 4.092v4.711zM5.005 6.575a1.548 1.548 0 11-.003-3.096 1.548 1.548 0 01.003 3.096zm-1.337 9.763H6.34v-8.59H3.667v8.59zM17.668 1H2.328C1.595 1 1 1.581 1 2.298v15.403C1 18.418 1.595 19 2.328 19h15.34c.734 0 1.332-.582 1.332-1.299V2.298C19 1.581 18.402 1 17.668 1z" clipRule="evenodd"/>
              </svg>
              {data.personalInfo.linkedin}
            </div>
          )}
        </div>
      </div>

      {/* Summary - Enhanced */}
      <div className="mb-10">
        <h3 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
          <div className="w-1 h-8 bg-gradient-to-b from-blue-600 to-purple-600 rounded-full mr-4"></div>
          Professional Summary
        </h3>
        <div className="bg-gray-50 p-6 rounded-lg border-l-4 border-blue-600">
          <p className="text-gray-700 leading-relaxed text-lg">{data.summary}</p>
        </div>
      </div>

      {/* Experience - Enhanced */}
      <div className="mb-10">
        <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <div className="w-1 h-8 bg-gradient-to-b from-blue-600 to-purple-600 rounded-full mr-4"></div>
          Professional Experience
        </h3>
        <div className="space-y-8">
          {data.experience.map((job, index) => (
            <div key={index} className="relative bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-600 to-purple-600 rounded-l-lg"></div>
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h4 className="text-xl font-semibold text-gray-900 mb-1">{job.position}</h4>
                  <p className="text-lg text-blue-600 font-medium">{job.company}</p>
                </div>
                <span className="text-sm text-gray-500 bg-blue-100 px-3 py-1 rounded-full font-medium">
                  {job.duration}
                </span>
              </div>
              <p className="text-gray-700 leading-relaxed text-base">{job.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Skills - Enhanced */}
      <div className="mb-10">
        <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <div className="w-1 h-8 bg-gradient-to-b from-blue-600 to-purple-600 rounded-full mr-4"></div>
          Skills & Expertise
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
            <h4 className="text-lg font-semibold text-blue-900 mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd"/>
              </svg>
              Technical Skills
            </h4>
            <div className="flex flex-wrap gap-2">
              {data.skills.technical.map((skill, index) => (
                <span
                  key={index}
                  className="px-3 py-2 bg-blue-600 text-white text-sm rounded-full font-medium shadow-sm hover:bg-blue-700 transition-colors"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
          
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-6 rounded-lg border border-purple-200">
            <h4 className="text-lg font-semibold text-purple-900 mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z"/>
              </svg>
              Soft Skills
            </h4>
            <div className="flex flex-wrap gap-2">
              {data.skills.soft.map((skill, index) => (
                <span
                  key={index}
                  className="px-3 py-2 bg-purple-600 text-white text-sm rounded-full font-medium shadow-sm hover:bg-purple-700 transition-colors"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Education - Enhanced */}
      <div className="mb-8">
        <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <div className="w-1 h-8 bg-gradient-to-b from-blue-600 to-purple-600 rounded-full mr-4"></div>
          Education
        </h3>
        <div className="space-y-4">
          {data.education.map((edu, index) => (
            <div key={index} className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-1">{edu.degree}</h4>
                  <p className="text-blue-600 font-medium text-base">{edu.institution}</p>
                  {edu.gpa && (
                    <p className="text-gray-600 text-sm mt-1">GPA: {edu.gpa}</p>
                  )}
                </div>
                <span className="text-sm text-gray-500 bg-blue-100 px-3 py-1 rounded-full font-medium">
                  {edu.year}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// TODO: Implement dynamic resume generation and user management features in the future.
