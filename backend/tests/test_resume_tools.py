"""
Tests for Resume Editing Tools - Core Resume Modification Functionality
"""
import json

from app.services.resume_tools import ResumeEditingTools, ResumeVersionManager
from app.database.models import ResumeTable, ResumeVersionTable
from app.database.connection import SessionLocal


class TestResumeEditingTools:
    """Test Resume Editing Tools functionality"""
    
    def test_get_resume_section_experience(self, setup_test_user):
        """Test getting work experience section"""
        test_user_id, _, _ = setup_test_user
        
        result = ResumeEditingTools.get_resume_section.invoke({
            "user_id": test_user_id, 
            "section_name": "experience"
        })
        
        assert result["success"] is True
        assert result["section"] == "experience"
        assert isinstance(result["data"], list)
        assert len(result["data"]) == 1
        
        # Verify experience data structure
        experience = result["data"][0]
        assert experience["company"] == "Tech Corp"
        assert experience["title"] == "Software Engineer"
        assert experience["start_date"] == "2020-01"
    
    def test_get_resume_section_contact(self, setup_test_user):
        """Test getting contact information section"""
        test_user_id, _, _ = setup_test_user
        
        result = ResumeEditingTools.get_resume_section.invoke({
            "user_id": test_user_id, 
            "section_name": "contact"
        })
        
        assert result["success"] is True
        assert result["section"] == "contact"
        assert result["data"]["name"] == "John Doe"
        assert result["data"]["email"] == "john.doe@example.com"
        assert result["data"]["phone"] == "+1-555-0123"
    
    def test_get_resume_section_skills(self, setup_test_user):
        """Test getting skills section""" 
        test_user_id, _, _ = setup_test_user
        
        result = ResumeEditingTools.get_resume_section.invoke({
            "user_id": test_user_id, 
            "section_name": "skills"
        })
        
        assert result["success"] is True
        assert result["section"] == "skills"
        assert isinstance(result["data"], list)
        expected_skills = ["Python", "JavaScript", "React", "PostgreSQL", "Docker"]
        assert result["data"] == expected_skills
    
    def test_get_resume_section_invalid(self, setup_test_user):
        """Test getting invalid section"""
        test_user_id, _, _ = setup_test_user
        
        result = ResumeEditingTools.get_resume_section.invoke({
            "user_id": test_user_id, 
            "section_name": "invalid_section"
        })
        
        assert result["success"] is False
        assert "Unknown section" in result["error"]
    
    def test_get_resume_section_no_user(self):
        """Test getting section for non-existent user"""
        result = ResumeEditingTools.get_resume_section.invoke({
            "user_id": "non-existent", 
            "section_name": "experience"
        })
        
        assert result["success"] is False
        assert "No resume found" in result["error"]
    
    def test_get_full_profile(self, setup_test_user):
        """Test getting complete profile information"""
        test_user_id, _, _ = setup_test_user
        
        result = ResumeEditingTools.get_full_profile.invoke({
            "user_id": test_user_id
        })
        
        assert result["success"] is True
        profile_data = result["data"]
        assert profile_data["name"] == "John Doe"
        assert profile_data["title"] == "Software Engineer"
        assert profile_data["email"] == "john.doe@example.com"
        assert profile_data["subscription_plan"] == "free"
        assert "id" in profile_data
        assert "last_active" in profile_data


class TestWorkExperienceManagement:
    """Test work experience CRUD operations"""
    
    def test_add_work_experience(self, setup_test_user, sample_work_experience):
        """Test adding new work experience"""
        test_user_id, _, resume_id = setup_test_user
        
        # Get initial experience count
        initial_result = ResumeEditingTools.get_resume_section.invoke({"user_id": test_user_id, "section_name": "experience"})
        initial_count = len(initial_result["data"])
        
        # Add new experience
        result = ResumeEditingTools.update_work_experience.invoke({
            "user_id": test_user_id,
            "experience_data": sample_work_experience,
            "action": "add"
        })
        
        assert result["success"] is True
        assert "Successfully added work experience" in result["message"]
        assert result["preview"]["action"] == "add"
        
        # Verify in database
        with SessionLocal() as db:
            resume = db.query(ResumeTable).filter(ResumeTable.id == resume_id).first()
            experience_data = json.loads(resume.experience)
            
            assert len(experience_data) == initial_count + 1
            
            # Find the new experience
            new_experience = None
            for exp in experience_data:
                if exp["company"] == "New Tech Company":
                    new_experience = exp
                    break
            
            assert new_experience is not None
            assert new_experience["title"] == "Senior Software Engineer"
            assert new_experience["location"] == "Remote"
            assert "id" in new_experience
            assert "created_at" in new_experience
    
    def test_update_work_experience(self, setup_test_user):
        """Test updating existing work experience"""
        test_user_id, _, resume_id = setup_test_user
        
        # Update the existing experience (index 0)
        updates = {
            "title": "Senior Software Engineer",
            "description": "Updated description with new responsibilities"
        }
        
        result = ResumeEditingTools.update_work_experience.invoke({
            "user_id": test_user_id,
            "experience_data": updates,
            "action": "update",
            "experience_index": 0
        })
        
        assert result["success"] is True
        assert "Successfully updated work experience" in result["message"]
        
        # Verify in database
        with SessionLocal() as db:
            resume = db.query(ResumeTable).filter(ResumeTable.id == resume_id).first()
            experience_data = json.loads(resume.experience)
            
            updated_exp = experience_data[0]
            assert updated_exp["title"] == "Senior Software Engineer"
            assert updated_exp["description"] == "Updated description with new responsibilities"
            assert "updated_at" in updated_exp
    
    def test_remove_work_experience(self, setup_test_user, sample_work_experience):
        """Test removing work experience"""
        test_user_id, _, resume_id = setup_test_user
        
        # First add an experience to remove
        ResumeEditingTools.update_work_experience.invoke({
            "user_id": test_user_id,
            "experience_data": sample_work_experience,
            "action": "add"
        })
        
        # Get current count
        current_result = ResumeEditingTools.get_resume_section.invoke({"user_id": test_user_id, "section_name": "experience"})
        current_count = len(current_result["data"])
        
        # Remove experience (index 1 - the one we just added)
        result = ResumeEditingTools.update_work_experience.invoke({
            "user_id": test_user_id,
            "experience_data": {},
            "action": "remove",
            "experience_index": 1
        })
        
        assert result["success"] is True
        assert "Successfully removed work experience" in result["message"]
        
        # Verify in database
        with SessionLocal() as db:
            resume = db.query(ResumeTable).filter(ResumeTable.id == resume_id).first()
            experience_data = json.loads(resume.experience)
            
            assert len(experience_data) == current_count - 1
    
    def test_add_work_experience_validation(self, setup_test_user):
        """Test validation for adding work experience"""
        test_user_id, _, _ = setup_test_user
        
        # Missing required fields
        incomplete_data = {
            "company": "Test Company"
            # Missing title and start_date
        }
        
        result = ResumeEditingTools.update_work_experience.invoke({
            "user_id": test_user_id,
            "experience_data": incomplete_data,
            "action": "add"
        })
        
        assert result["success"] is False
        assert "Missing required field" in result["error"]
    
    def test_update_work_experience_invalid_index(self, setup_test_user):
        """Test updating with invalid index"""
        test_user_id, _, _ = setup_test_user
        
        result = ResumeEditingTools.update_work_experience.invoke({
            "user_id": test_user_id,
            "experience_data": {"title": "New Title"},
            "action": "update",
            "experience_index": 999  # Invalid index
        })
        
        assert result["success"] is False
        assert "Invalid experience index" in result["error"]


class TestProfessionalSummaryManagement:
    """Test professional summary editing"""
    
    def test_edit_professional_summary(self, setup_test_user):
        """Test updating professional summary"""
        test_user_id, _, resume_id = setup_test_user
        
        new_summary = "Experienced software engineer with 8+ years of expertise in full-stack development and cloud technologies."
        
        result = ResumeEditingTools.edit_professional_summary.invoke({"user_id": test_user_id, "new_summary": new_summary})
        
        assert result["success"] is True
        assert "Successfully updated professional summary" in result["message"]
        assert result["preview"]["action"] == "update_summary"
        assert result["preview"]["after"] == new_summary
        
        # Verify in database
        with SessionLocal() as db:
            resume = db.query(ResumeTable).filter(ResumeTable.id == resume_id).first()
            assert resume.summary == new_summary
    
    def test_edit_professional_summary_no_user(self):
        """Test updating summary for non-existent user"""
        result = ResumeEditingTools.edit_professional_summary.invoke({"user_id": "non-existent", "new_summary": "New summary"})
        
        assert result["success"] is False
        assert "No resume found" in result["error"]


class TestSkillsManagement:
    """Test skills management functionality"""
    
    def test_add_skills(self, setup_test_user):
        """Test adding new skills"""
        test_user_id, _, resume_id = setup_test_user
        
        new_skills = ["Go", "Kubernetes", "AWS"]
        
        result = ResumeEditingTools.manage_skills.invoke({
            "user_id": test_user_id,
            "skills_data": new_skills,
            "action": "add"
        })
        
        assert result["success"] is True
        assert "Successfully added skills" in result["message"]
        
        # Verify in database
        with SessionLocal() as db:
            resume = db.query(ResumeTable).filter(ResumeTable.id == resume_id).first()
            skills_data = json.loads(resume.skills)
            
            # Should have original skills + new skills
            assert "Go" in skills_data
            assert "Kubernetes" in skills_data
            assert "AWS" in skills_data
            assert "Python" in skills_data  # Original skill still there
    
    def test_remove_skills(self, setup_test_user):
        """Test removing skills"""
        test_user_id, _, resume_id = setup_test_user
        
        skills_to_remove = ["JavaScript", "React"]
        
        result = ResumeEditingTools.manage_skills.invoke({
            "user_id": test_user_id,
            "skills_data": skills_to_remove,
            "action": "remove"
        })
        
        assert result["success"] is True
        assert "Successfully removed skills" in result["message"]
        
        # Verify in database
        with SessionLocal() as db:
            resume = db.query(ResumeTable).filter(ResumeTable.id == resume_id).first()
            skills_data = json.loads(resume.skills)
            
            assert "JavaScript" not in skills_data
            assert "React" not in skills_data
            assert "Python" in skills_data  # Other skills remain
    
    def test_replace_skills(self, setup_test_user):
        """Test replacing all skills"""
        test_user_id, _, resume_id = setup_test_user
        
        new_skills = ["Java", "Spring Boot", "MySQL", "Redis"]
        
        result = ResumeEditingTools.manage_skills.invoke({
            "user_id": test_user_id,
            "skills_data": new_skills,
            "action": "replace"
        })
        
        assert result["success"] is True
        assert "Successfully replaced skills" in result["message"]
        
        # Verify in database
        with SessionLocal() as db:
            resume = db.query(ResumeTable).filter(ResumeTable.id == resume_id).first()
            skills_data = json.loads(resume.skills)
            
            # Should only have new skills
            assert set(skills_data) == set(new_skills)
            assert "Python" not in skills_data  # Original skills replaced
    
    def test_manage_skills_categorized(self, setup_test_user):
        """Test managing categorized skills"""
        test_user_id, _, _ = setup_test_user
        
        categorized_skills = {
            "Programming Languages": ["Java", "Go"],
            "Frameworks": ["Spring Boot", "Gin"],
            "Databases": ["MySQL", "MongoDB"]
        }
        
        result = ResumeEditingTools.manage_skills.invoke({
            "user_id": test_user_id,
            "skills_data": categorized_skills,
            "action": "add"
        })
        
        assert result["success"] is True
        
        # Verify skills are flattened and added
        final_result = ResumeEditingTools.get_resume_section.invoke({"user_id": test_user_id, "section_name": "skills"})
        skills_list = final_result["data"]
        
        assert "Java" in skills_list
        assert "Go" in skills_list
        assert "Spring Boot" in skills_list
        assert "MySQL" in skills_list


class TestResumeContentSearch:
    """Test resume content search functionality"""
    
    def test_search_resume_content_experience(self, setup_test_user):
        """Test searching in experience section"""
        test_user_id, _, _ = setup_test_user
        
        result = ResumeEditingTools.search_resume_content.invoke({"user_id": test_user_id, "query": "Tech Corp"})
        
        assert result["success"] is True
        assert result["query"] == "Tech Corp"
        assert result["total_matches"] >= 1
        
        # Should find match in experience
        experience_matches = [m for m in result["matches"] if m["section"] == "experience"]
        assert len(experience_matches) >= 1
        assert experience_matches[0]["match_type"] == "experience_entry"
    
    def test_search_resume_content_skills(self, setup_test_user):
        """Test searching in skills section"""
        test_user_id, _, _ = setup_test_user
        
        result = ResumeEditingTools.search_resume_content.invoke({"user_id": test_user_id, "query": "Python"})
        
        assert result["success"] is True
        assert result["total_matches"] >= 1
        
        # Should find match in skills
        skills_matches = [m for m in result["matches"] if m["section"] == "skills"]
        assert len(skills_matches) >= 1
        assert "Python" in skills_matches[0]["content"]
    
    def test_search_resume_content_summary(self, setup_test_user):
        """Test searching in summary section"""
        test_user_id, _, _ = setup_test_user
        
        result = ResumeEditingTools.search_resume_content.invoke({"user_id": test_user_id, "query": "software engineer"})
        
        assert result["success"] is True
        assert result["total_matches"] >= 1
        
        # Should find match in summary
        summary_matches = [m for m in result["matches"] if m["section"] == "summary"]
        assert len(summary_matches) >= 1
    
    def test_search_resume_content_no_matches(self, setup_test_user):
        """Test searching with no matches"""
        test_user_id, _, _ = setup_test_user
        
        result = ResumeEditingTools.search_resume_content.invoke({"user_id": test_user_id, "query": "nonexistentterm"})
        
        assert result["success"] is True
        assert result["total_matches"] == 0
        assert len(result["matches"]) == 0


class TestResumeVersioning:
    """Test resume version tracking"""
    
    def test_version_creation_on_changes(self, setup_test_user):
        """Test that versions are created when making changes"""
        test_user_id, _, resume_id = setup_test_user
        
        # Make a change that should create a version
        ResumeEditingTools.edit_professional_summary.invoke({"user_id": 
            test_user_id, "new_summary": "Updated summary to create a version"
        })
        
        # Check that version was created
        with SessionLocal() as db:
            versions = db.query(ResumeVersionTable).filter(
                ResumeVersionTable.user_id == test_user_id,
                ResumeVersionTable.resume_id == resume_id
            ).all()
            
            assert len(versions) >= 1
            
            latest_version = versions[-1]
            assert latest_version.created_by == "ai"
            assert "summary" in latest_version.changes_summary
            assert latest_version.content is not None
    
    def test_version_manager_directly(self, setup_test_user):
        """Test version manager functionality directly"""
        test_user_id, _, resume_id = setup_test_user
        
        version_manager = ResumeVersionManager()
        
        success = version_manager.create_version(
            user_id=test_user_id,
            resume_id=resume_id,
            section_changed="skills",
            change_summary="Added new programming skills"
        )
        
        assert success is True
        
        # Verify version was created
        with SessionLocal() as db:
            version = db.query(ResumeVersionTable).filter(
                ResumeVersionTable.user_id == test_user_id,
                ResumeVersionTable.resume_id == resume_id
            ).order_by(ResumeVersionTable.version_number.desc()).first()
            
            assert version is not None
            assert "skills: Added new programming skills" in version.changes_summary
            assert version.version_number >= 1


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
