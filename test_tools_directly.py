#!/usr/bin/env python3
"""
Direct test script for resume tools with seeded data
"""

import requests
import json
import sys
import os

# Add the backend directory to the path
sys.path.append('/Users/gauravpooniwala/Documents/code/projects/resumebuilder/backend')

# Set environment variables for testing
os.environ["DATABASE_URL"] = "postgresql://user:password@localhost:5433/resume_builder"
os.environ["OPENAI_API_KEY"] = "sk-proj-kmfo..."  # Use actual key

# Test the tools directly
def test_tools_directly():
    """Test all resume tools directly with profile-1"""
    
    from app.services.resume_tools import ResumeEditingTools
    
    user_id = "profile-1"
    
    print("=== Testing Resume Tools with Seeded Data ===\n")
    
    # Test 1: Get full profile
    print("1. Testing get_full_profile...")
    result = ResumeEditingTools.get_full_profile.invoke({"user_id": user_id})
    if result["success"]:
        print(f"✅ SUCCESS: Found profile for {result['data']['name']}")
        print(f"   Title: {result['data']['title']}")
        print(f"   Email: {result['data']['email']}")
        print(f"   Subscription: {result['data']['subscription_plan']}")
    else:
        print(f"❌ FAILED: {result['error']}")
    print()
    
    # Test 2: Get resume sections
    sections_to_test = ["contact", "summary", "experience", "skills", "education"]
    
    for section in sections_to_test:
        print(f"2.{sections_to_test.index(section)+1} Testing get_resume_section: {section}...")
        result = ResumeEditingTools.get_resume_section.invoke({
            "user_id": user_id, 
            "section_name": section
        })
        
        if result["success"]:
            print(f"✅ SUCCESS: Got {section} data")
            if section == "experience":
                print(f"   Found {len(result['data'])} work experiences")
                for i, exp in enumerate(result['data']):
                    print(f"     {i+1}. {exp['company']} - {exp['position']}")
            elif section == "skills":
                if isinstance(result['data'], dict):
                    for category, skills in result['data'].items():
                        print(f"   {category}: {len(skills)} skills")
                else:
                    print(f"   {len(result['data'])} skills total")
            elif section == "contact":
                print(f"   Name: {result['data']['name']}")
                print(f"   Location: {result['data']['location']}")
        else:
            print(f"❌ FAILED: {result['error']}")
        print()
    
    # Test 3: Search resume content
    print("3. Testing search_resume_content...")
    result = ResumeEditingTools.search_resume_content.invoke({
        "user_id": user_id,
        "query": "microservices"
    })
    
    if result["success"]:
        print(f"✅ SUCCESS: Found {result['total_matches']} matches for 'microservices'")
        for match in result['matches']:
            print(f"   Section: {match['section']}, Type: {match['match_type']}")
    else:
        print(f"❌ FAILED: {result['error']}")
    print()
    
    # Test 4: Edit professional summary
    print("4. Testing edit_professional_summary...")
    new_summary = "Senior Software Engineer with 8+ years of expertise in full-stack development, microservices architecture, and team leadership. Proven track record of mentoring developers and delivering scalable solutions."
    
    result = ResumeEditingTools.edit_professional_summary.invoke({
        "user_id": user_id,
        "new_summary": new_summary
    })
    
    if result["success"]:
        print("✅ SUCCESS: Updated professional summary")
        print(f"   New summary: {new_summary[:80]}...")
    else:
        print(f"❌ FAILED: {result['error']}")
    print()
    
    # Test 5: Add skills
    print("5. Testing manage_skills (add)...")
    new_skills = {"technical": ["Go", "Kubernetes"], "soft": ["Strategic Planning"]}
    
    result = ResumeEditingTools.manage_skills.invoke({
        "user_id": user_id,
        "skills_data": new_skills,
        "action": "add"
    })
    
    if result["success"]:
        print("✅ SUCCESS: Added new skills")
        print(f"   Added: {new_skills}")
    else:
        print(f"❌ FAILED: {result['error']}")
    print()
    
    print("=== All Direct Tool Tests Complete ===")


def test_tools_via_api():
    """Test tools via the chat API"""
    
    print("\n=== Testing Tools via Chat API ===\n")
    
    test_queries = [
        "What's my name and current job title?",
        "How many work experiences do I have?", 
        "List my technical skills",
        "Search my resume for 'microservices'",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. Testing: '{query}'")
        
        try:
            response = requests.post(
                "http://localhost:8000/chat",
                headers={"Content-Type": "application/json"},
                json={
                    "message": query,
                    "user_id": "profile-1"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: Got response")
                print(f"   Response: {data['response'][:100]}...")
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
        
        print()
    
    print("=== API Tests Complete ===")


if __name__ == "__main__":
    # Run direct tool tests
    test_tools_directly()
    
    # Run API tests
    test_tools_via_api()
