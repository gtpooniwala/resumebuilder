interface ResumeData {
  name: string;
  title: string;
  email: string;
  phone: string;
  location: string;
  summary: string;
  experience: Array<{
    company: string;
    position: string;
    duration: string;
    description: string;
  }>;
  skills: string[];
  education: Array<{
    degree: string;
    school: string;
    year: string;
  }>;
}

interface ResumeProps {
  data: ResumeData;
}

export default function Resume({ data }: ResumeProps) {
  return (
    <div className="resume-container bg-white text-gray-800 font-serif leading-relaxed">
      {/* Header */}
      <div className="text-center mb-8 pb-6 border-b-2 border-blue-200">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{data.name}</h1>
        <h2 className="text-xl text-blue-600 font-semibold mb-4">{data.title}</h2>
        <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-600">
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
              <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
            </svg>
            {data.email}
          </span>
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"/>
            </svg>
            {data.phone}
          </span>
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd"/>
            </svg>
            {data.location}
          </span>
        </div>
      </div>

      {/* Summary */}
      <div className="mb-6">
        <h3 className="text-lg font-bold text-gray-900 mb-3 pb-1 border-b border-gray-300">
          Professional Summary
        </h3>
        <p className="text-gray-700 leading-relaxed">{data.summary}</p>
      </div>

      {/* Experience */}
      <div className="mb-6">
        <h3 className="text-lg font-bold text-gray-900 mb-3 pb-1 border-b border-gray-300">
          Professional Experience
        </h3>
        <div className="space-y-4">
          {data.experience.map((exp, index) => (
            <div key={index} className="border-l-2 border-blue-200 pl-4">
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start mb-1">
                <h4 className="font-semibold text-gray-900">{exp.position}</h4>
                <span className="text-sm text-gray-600 font-medium">{exp.duration}</span>
              </div>
              <p className="text-blue-600 font-medium mb-2">{exp.company}</p>
              <p className="text-gray-700 text-sm leading-relaxed">{exp.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Skills */}
      <div className="mb-6">
        <h3 className="text-lg font-bold text-gray-900 mb-3 pb-1 border-b border-gray-300">
          Technical Skills
        </h3>
        <div className="flex flex-wrap gap-2">
          {data.skills.map((skill, index) => (
            <span 
              key={index}
              className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full font-medium"
            >
              {skill}
            </span>
          ))}
        </div>
      </div>

      {/* Education */}
      <div className="mb-6">
        <h3 className="text-lg font-bold text-gray-900 mb-3 pb-1 border-b border-gray-300">
          Education
        </h3>
        <div className="space-y-2">
          {data.education.map((edu, index) => (
            <div key={index} className="border-l-2 border-blue-200 pl-4">
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start">
                <div>
                  <h4 className="font-semibold text-gray-900">{edu.degree}</h4>
                  <p className="text-blue-600 font-medium">{edu.school}</p>
                </div>
                <span className="text-sm text-gray-600 font-medium">{edu.year}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// TODO: Implement dynamic resume generation and user management features in the future.