#!/usr/bin/env python3
"""
Comprehensive Resume Tools Validation Script

This script tests EVERY resume editing tool with before/after database verification:
1. get_resume_section (read tool)
2. get_full_profile (read tool)
3. update_work_experience (write tool)
4. edit_professional_summary (write tool)
5. manage_skills (write tool)
6. search_resume_content (read tool)

Each tool is tested with various scenarios and database state is verified.
"""

import os
import sys
import uuid
import json
from typing import Dict, Any, Optional

# Set up environment
os.environ["DATABASE_URL"] = "postgresql://user:password@localhost:5433/resume_builder"
os.environ["OPENAI_API_KEY"] = "sk-test-key-for-testing"

# Add project root to path
sys.path.append('/Users/gauravpooniwala/Documents/code/projects/resumebuilder/backend')

from app.database.connection import SessionLocal
from app.database.models import ProfileTable, ResumeTable
from app.services.resume_tools import ResumeEditingTools


class ComprehensiveResumeToolsTester:
    """Comprehensive tester for all resume editing tools"""
    
    def __init__(self):
        self.test_user_id = f"tools-test-{uuid.uuid4()}"
        self.results = []
        
    def setup_test_user(self) -> bool:
        """Create a test user with comprehensive initial resume data"""
        try:
            with SessionLocal() as db:
                # Create profile
                profile = ProfileTable(
                    id=self.test_user_id,
                    name="Jane Smith",
                    title="Software Developer",
                    email=f"test-{self.test_user_id}@example.com",
                    phone="+1 (555) 123-4567",
                    location="New York, NY",
                    linkedin="https://linkedin.com/in/janesmith",
                    website="https://janesmith.dev"
                )
                db.add(profile)
                
                # Create comprehensive resume
                resume = ResumeTable(
                    id=f"resume-{self.test_user_id}",
                    profile_id=self.test_user_id,
                    name="Jane Smith",
                    title="Software Developer",
                    email=f"test-{self.test_user_id}@example.com",
                    phone="+1 (555) 123-4567",
                    location="New York, NY",
                    linkedin="https://linkedin.com/in/janesmith",
                    website="https://janesmith.dev",
                    summary="Experienced software developer with 4 years in web development.",
                    experience=json.dumps([
                        {
                            "id": "exp1",
                            "company": "TechStart Inc",
                            "title": "Junior Developer",
                            "start_date": "2020-06",
                            "end_date": "2022-12",
                            "description": "Developed web applications using React and Node.js",
                            "location": "Remote"
                        },
                        {
                            "id": "exp2", 
                            "company": "WebCorp LLC",
                            "title": "Software Developer",
                            "start_date": "2023-01",
                            "end_date": "Present",
                            "description": "Building scalable web services with Python and PostgreSQL",
                            "location": "New York, NY"
                        }
                    ]),
                    skills=json.dumps({
                        "technical": ["Python", "JavaScript", "React", "PostgreSQL"],
                        "soft": ["Problem Solving", "Team Collaboration", "Communication"]
                    }),
                    education=json.dumps([
                        {
                            "id": "edu1",
                            "institution": "State University",
                            "degree": "BS Computer Science",
                            "start_date": "2016",
                            "end_date": "2020",
                            "gpa": "3.8"
                        }
                    ])
                )
                db.add(resume)
                db.commit()
                
                print(f"✅ Created comprehensive test user: {self.test_user_id}")
                return True
                
        except Exception as e:
            print(f"❌ Failed to create test user: {e}")
            return False
    
    def cleanup_test_user(self):
        """Clean up test data"""
        try:
            with SessionLocal() as db:
                db.query(ResumeTable).filter(ResumeTable.profile_id == self.test_user_id).delete()
                db.query(ProfileTable).filter(ProfileTable.id == self.test_user_id).delete()
                db.commit()
                print(f"✅ Cleaned up test user: {self.test_user_id}")
        except Exception as e:
            print(f"❌ Failed to cleanup: {e}")
    
    def get_current_resume_data(self) -> Optional[Dict[str, Any]]:
        """Get current resume data from database"""
        try:
            with SessionLocal() as db:
                resume = db.query(ResumeTable).filter(ResumeTable.profile_id == self.test_user_id).first()
                if resume:
                    return {
                        "summary": resume.summary,
                        "experience": json.loads(resume.experience) if resume.experience else [],
                        "skills": json.loads(resume.skills) if resume.skills else {},
                        "education": json.loads(resume.education) if resume.education else [],
                        "name": resume.name,
                        "title": resume.title,
                        "email": resume.email,
                        "phone": resume.phone,
                        "location": resume.location
                    }
                return None
        except Exception as e:
            print(f"❌ Failed to get resume data: {e}")
            return None
    
    def test_tool(self, tool_name: str, test_description: str, tool_call_func, expected_success: bool = True, 
                  validate_change_func=None) -> bool:
        """Generic tool testing framework"""
        print(f"\n🧪 TESTING: {tool_name}")
        print(f"📝 Description: {test_description}")
        
        # Get before state for write operations
        before_data = None
        if validate_change_func:
            before_data = self.get_current_resume_data()
        
        try:
            # Execute tool
            result = tool_call_func()
            print(f"🔧 Tool Result: {json.dumps(result, indent=2)[:200]}...")
            
            # Validate result structure
            if not isinstance(result, dict):
                print(f"❌ Tool returned invalid format: {type(result)}")
                return False
            
            # Check success expectation
            actual_success = result.get('success', False)
            if expected_success and not actual_success:
                print(f"❌ Expected success but got failure: {result.get('error', 'Unknown error')}")
                return False
            elif not expected_success and actual_success:
                print("❌ Expected failure but got success")
                return False
            
            # Validate database changes for write operations
            if validate_change_func and before_data:
                after_data = self.get_current_resume_data()
                if validate_change_func(before_data, after_data, result):
                    print("✅ Database change validation: PASSED")
                    return True
                else:
                    print("❌ Database change validation: FAILED")
                    return False
            
            print("✅ Tool execution: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Tool execution failed: {e}")
            return False
    
    def run_all_tool_tests(self):
        """Run comprehensive tests for all 6 resume tools"""
        print("🚀 COMPREHENSIVE RESUME TOOLS VALIDATION")
        print("=" * 60)
        
        if not self.setup_test_user():
            return False
        
        try:
            # ============================================
            # TEST 1: get_resume_section (READ TOOL)
            # ============================================
            
            # Test 1a: Get valid section
            result1a = self.test_tool(
                "get_resume_section - Valid Section",
                "Retrieve work experience section",
                lambda: ResumeEditingTools.get_resume_section.invoke({
                    "user_id": self.test_user_id,
                    "section_name": "experience"
                }),
                expected_success=True
            )
            self.results.append(("get_resume_section (valid)", result1a))
            
            # Test 1b: Get invalid section 
            result1b = self.test_tool(
                "get_resume_section - Invalid Section",
                "Attempt to retrieve non-existent section",
                lambda: ResumeEditingTools.get_resume_section.invoke({
                    "user_id": self.test_user_id,
                    "section_name": "invalid_section"
                }),
                expected_success=False
            )
            self.results.append(("get_resume_section (invalid)", result1b))
            
            # Test 1c: Non-existent user
            result1c = self.test_tool(
                "get_resume_section - Non-existent User",
                "Attempt to retrieve section for non-existent user",
                lambda: ResumeEditingTools.get_resume_section.invoke({
                    "user_id": "non-existent-user",
                    "section_name": "experience"
                }),
                expected_success=False
            )
            self.results.append(("get_resume_section (no user)", result1c))
            
            # ============================================
            # TEST 2: get_full_profile (READ TOOL)
            # ============================================
            
            # Test 2a: Get existing user profile
            result2a = self.test_tool(
                "get_full_profile - Existing User",
                "Retrieve complete profile for existing user",
                lambda: ResumeEditingTools.get_full_profile.invoke({
                    "user_id": self.test_user_id
                }),
                expected_success=True
            )
            self.results.append(("get_full_profile (valid)", result2a))
            
            # Test 2b: Non-existent user
            result2b = self.test_tool(
                "get_full_profile - Non-existent User",
                "Attempt to retrieve profile for non-existent user",
                lambda: ResumeEditingTools.get_full_profile.invoke({
                    "user_id": "non-existent-user"
                }),
                expected_success=False
            )
            self.results.append(("get_full_profile (no user)", result2b))
            
            # ============================================
            # TEST 3: edit_professional_summary (WRITE TOOL)
            # ============================================
            
            def validate_summary_change(before, after, result):
                return (before["summary"] != after["summary"] and 
                       "Senior Software Engineer" in after["summary"])
            
            result3 = self.test_tool(
                "edit_professional_summary",
                "Update professional summary with new content",
                lambda: ResumeEditingTools.edit_professional_summary.invoke({
                    "user_id": self.test_user_id,
                    "new_summary": "Senior Software Engineer with 5+ years of experience in full-stack development, specializing in Python, React, and cloud technologies."
                }),
                expected_success=True,
                validate_change_func=validate_summary_change
            )
            self.results.append(("edit_professional_summary", result3))
            
            # ============================================
            # TEST 4: manage_skills (WRITE TOOL)
            # ============================================
            
            # Test 4a: Add skills
            def validate_skills_add(before, after, result):
                before_tech = set(before["skills"].get("technical", []))
                after_tech = set(after["skills"].get("technical", []))
                new_skills = {"Docker", "Kubernetes"}
                return new_skills.issubset(after_tech) and before_tech.issubset(after_tech)
            
            result4a = self.test_tool(
                "manage_skills - Add Skills",
                "Add Docker and Kubernetes to technical skills",
                lambda: ResumeEditingTools.manage_skills.invoke({
                    "user_id": self.test_user_id,
                    "skills_data": ["Docker", "Kubernetes"],
                    "action": "add"
                }),
                expected_success=True,
                validate_change_func=validate_skills_add
            )
            self.results.append(("manage_skills (add)", result4a))
            
            # Test 4b: Remove skills
            def validate_skills_remove(before, after, result):
                before_tech = set(before["skills"].get("technical", []))
                after_tech = set(after["skills"].get("technical", []))
                return "JavaScript" not in after_tech and "JavaScript" in before_tech
            
            result4b = self.test_tool(
                "manage_skills - Remove Skills",
                "Remove JavaScript from technical skills",
                lambda: ResumeEditingTools.manage_skills.invoke({
                    "user_id": self.test_user_id,
                    "skills_data": ["JavaScript"],
                    "action": "remove"
                }),
                expected_success=True,
                validate_change_func=validate_skills_remove
            )
            self.results.append(("manage_skills (remove)", result4b))
            
            # ============================================
            # TEST 5: update_work_experience (WRITE TOOL)
            # ============================================
            
            # Test 5a: Add new work experience
            def validate_experience_add(before, after, result):
                return (len(after["experience"]) > len(before["experience"]) and
                       any(exp.get("company") == "Google Inc" for exp in after["experience"]))
            
            result5a = self.test_tool(
                "update_work_experience - Add Experience",
                "Add new work experience at Google",
                lambda: ResumeEditingTools.update_work_experience.invoke({
                    "user_id": self.test_user_id,
                    "experience_data": {
                        "company": "Google Inc",
                        "title": "Senior Software Engineer",
                        "start_date": "2024-01",
                        "end_date": "Present",
                        "description": "Leading development of cloud infrastructure solutions",
                        "location": "Mountain View, CA"
                    },
                    "action": "add"
                }),
                expected_success=True,
                validate_change_func=validate_experience_add
            )
            self.results.append(("update_work_experience (add)", result5a))
            
            # Test 5b: Update existing work experience
            def validate_experience_update(before, after, result):
                # Check if first experience was updated
                first_exp = after["experience"][0] if after["experience"] else {}
                return first_exp.get("title") == "Senior Developer"
            
            result5b = self.test_tool(
                "update_work_experience - Update Experience",
                "Update first work experience title",
                lambda: ResumeEditingTools.update_work_experience.invoke({
                    "user_id": self.test_user_id,
                    "experience_data": {
                        "company": "TechStart Inc",
                        "title": "Senior Developer",
                        "start_date": "2020-06",
                        "end_date": "2022-12",
                        "description": "Led development of web applications using React and Node.js",
                        "location": "Remote"
                    },
                    "action": "update",
                    "experience_index": 0
                }),
                expected_success=True,
                validate_change_func=validate_experience_update
            )
            self.results.append(("update_work_experience (update)", result5b))
            
            # ============================================
            # TEST 6: search_resume_content (READ TOOL)
            # ============================================
            
            # Test 6a: Search for existing content
            result6a = self.test_tool(
                "search_resume_content - Valid Search",
                "Search for 'Python' in resume content",
                lambda: ResumeEditingTools.search_resume_content.invoke({
                    "user_id": self.test_user_id,
                    "query": "Python"
                }),
                expected_success=True
            )
            self.results.append(("search_resume_content (valid)", result6a))
            
            # Test 6b: Search for non-existent content
            result6b = self.test_tool(
                "search_resume_content - No Results",
                "Search for 'COBOL' in resume content",
                lambda: ResumeEditingTools.search_resume_content.invoke({
                    "user_id": self.test_user_id,
                    "query": "COBOL"
                }),
                expected_success=True  # Search should succeed even with no results
            )
            self.results.append(("search_resume_content (no results)", result6b))
            
            # ============================================
            # RESULTS SUMMARY
            # ============================================
            
            self.print_results_summary()
            return self.calculate_success_rate()
            
        finally:
            self.cleanup_test_user()
    
    def print_results_summary(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE TOOL TEST RESULTS")
        print("=" * 60)
        
        # Group results by tool
        tool_groups = {}
        for test_name, result in self.results:
            tool = test_name.split('(')[0].strip()
            if tool not in tool_groups:
                tool_groups[tool] = []
            tool_groups[tool].append((test_name, result))
        
        total_passed = 0
        total_tests = len(self.results)
        
        for tool, tests in tool_groups.items():
            print(f"\n🔧 {tool.upper()}:")
            tool_passed = 0
            for test_name, result in tests:
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"    {status}: {test_name}")
                if result:
                    tool_passed += 1
                    total_passed += 1
            print(f"    📊 {tool} Success Rate: {tool_passed}/{len(tests)} ({tool_passed/len(tests)*100:.1f}%)")
        
        print("\n📈 OVERALL RESULTS:")
        print(f"    Total Tests: {total_tests}")
        print(f"    Passed: {total_passed}")
        print(f"    Failed: {total_tests - total_passed}")
        print(f"    Success Rate: {total_passed/total_tests*100:.1f}%")
        
        if total_passed == total_tests:
            print("\n🎉 ALL TOOLS WORKING PERFECTLY!")
            print("✅ Every resume editing tool passed comprehensive validation")
        else:
            print(f"\n⚠️  {total_tests - total_passed} tools need attention")
            print("🔧 Check failed tests above for specific issues")
    
    def calculate_success_rate(self) -> float:
        """Calculate overall success rate"""
        if not self.results:
            return 0.0
        passed = sum(1 for _, result in self.results if result)
        return passed / len(self.results)


def main():
    """Main test execution"""
    tester = ComprehensiveResumeToolsTester()
    
    try:
        success_rate = tester.run_all_tool_tests()
        
        if success_rate >= 0.9:  # 90% or higher
            print(f"\n🎉 EXCELLENT: {success_rate*100:.1f}% success rate!")
            return True
        elif success_rate >= 0.7:  # 70% or higher
            print(f"\n✅ GOOD: {success_rate*100:.1f}% success rate")
            return True
        else:
            print(f"\n⚠️  NEEDS WORK: {success_rate*100:.1f}% success rate")
            return False
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
