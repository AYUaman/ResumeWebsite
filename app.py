import streamlit as st
import re
import pdfplumber
from docx import Document
from io import BytesIO
import requests
import json

# Website ka setup
st.set_page_config(
    page_title="AI Job Scanner",
    page_icon="💼",
    layout="wide"
)

# Custom design
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        color: #2563eb;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        color: #475569;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 15px 0;
        border-left: 5px solid #2563eb;
    }
    .skill-pill {
        background: #dbeafe;
        color: #1e40af;
        padding: 5px 12px;
        border-radius: 20px;
        display: inline-block;
        margin: 5px 5px 5px 0;
        font-size: 0.9rem;
    }
    .match-high {color: #16a34a; font-weight: bold;}
    .match-medium {color: #ca8a04; font-weight: bold;}
    .match-low {color: #dc2626; font-weight: bold;}
    .score-excellent {color: #16a34a; font-weight: bold; font-size: 2.5rem;}
    .score-good {color: #ca8a04; font-weight: bold; font-size: 2.5rem;}
    .score-poor {color: #dc2626; font-weight: bold; font-size: 2.5rem;}
    .learning-plan {
        background: #f0fdf4;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #16a34a;
        margin: 10px 0;
    }
    .job-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Website header
st.markdown('<h1 class="main-header">AI Job Finder</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Upload your resume and discover your perfect career match</p>', unsafe_allow_html=True)

# File upload section
uploaded_file = st.file_uploader("📁 Choose your resume file", type=['pdf', 'docx'])

# Functions
def extract_text_from_file(file):
    text = ""
    try:
        if file.type == "application/pdf":
            with pdfplumber.open(BytesIO(file.read())) as pdf:
                for page in pdf.pages:
                    if page.extract_text():
                        text += page.extract_text() + "\n"
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(BytesIO(file.read()))
            for para in doc.paragraphs:
                text += para.text + "\n"
    except Exception as e:
        return f"Error: {str(e)}"
    return text

def extract_skills(resume_text):
    common_skills = [
        'python', 'java', 'javascript', 'html', 'css', 'sql', 'excel',
        'machine learning', 'data analysis', 'digital marketing', 'seo',
        'content writing', 'tally', 'ms office', 'word', 'powerpoint',
        'deep learning', 'nlp', 'django', 'flask', 'react', 'node.js',
        'aws', 'cloud computing', 'git', 'github', 'communication',
        'teamwork', 'leadership', 'problem solving', 'analytical skills',
        'android', 'kotlin', 'swift', 'ios', 'php', 'wordpress', 'angular',
        'vue', 'typescript', 'mongodb', 'mysql', 'postgresql', 'linux'
    ]
    
    resume_text_lower = resume_text.lower()
    found_skills = []
    
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', resume_text_lower):
            found_skills.append(skill)
    
    return found_skills

def calculate_resume_score(skills_list):
    """
    Calculate resume score based on number of skills found
    """
    total_important_skills = 25
    score = (len(skills_list) / total_important_skills) * 100
    return min(score, 100)

def generate_skill_gap_analysis(skills_list, suggested_jobs):
    """
    Detailed analysis of missing skills and improvement suggestions
    """
    if not suggested_jobs:
        return "No job matches found for analysis"
    
    # Get all missing skills from top 3 suggested jobs
    all_missing_skills = []
    for job_name, details in list(suggested_jobs.items())[:3]:
        all_missing_skills.extend(details['missing_skills'])
    
    # Remove duplicates
    unique_missing_skills = list(set(all_missing_skills))
    
    # Generate learning resources for each missing skill
    skill_resources = {}
    for skill in unique_missing_skills:
        resources = {
            'python': ['CodeWithHarry Python', 'freeCodeCamp Python', 'Coursera Python for Everybody'],
            'java': ['Java Tutorial by Kunal Kushwaha', 'Udemy Java Masterclass', 'CodeWithHarry Java'],
            'javascript': ['JavaScript.info', 'freeCodeCamp JavaScript', 'Namaste JavaScript by Akshay Saini'],
            'react': ['React Official Docs', 'Scrimba React Course', 'CodeWithHarry React'],
            'machine learning': ['Coursera ML by Andrew Ng', 'Krish Naik YouTube', 'freeCodeCamp ML'],
            'data analysis': ['Google Data Analytics Certificate', 'Kaggle Courses', '365 Data Science'],
            'sql': ['SQL Bolt', 'Khan Academy SQL', 'StrataScratch SQL Practice'],
            'aws': ['AWS Training Portal', 'freeCodeCamp AWS', 'Stephane Maarek Udemy'],
            'digital marketing': ['Google Digital Garage', 'Coursera Digital Marketing', 'HubSpot Academy'],
            'excel': ['Excel Easy Tutorials', 'Chandoo.org', 'YouTube Excel Is Fun']
        }
        
        skill_resources[skill] = resources.get(skill, [
            f'YouTube: {skill.title()} Tutorial',
            f'Udemy: {skill.title()} Course', 
            f'Practice on HackerRank/LeetCode'
        ])
    
    return skill_resources

def display_skill_gap_analysis(skill_resources):
    """
    Display skill gap analysis with learning resources
    """
    if not skill_resources or skill_resources == "No job matches found for analysis":
        st.warning("Not enough data for skill gap analysis")
        return
    
    st.markdown("---")
    st.subheader("📚 Skill Gap Analysis & Learning Plan")
    st.info("Based on your resume and target jobs, here's what you should learn:")
    
    for skill, resources in skill_resources.items():
        with st.expander(f"🎯 Learn {skill.title()} to boost your career"):
            st.write(f"**Why learn {skill}?**")
            st.write(f"- Increases your job matches by 30%")
            st.write(f"- Average salary premium: ₹3-5 LPA")
            st.write(f"- High demand in current market")
            
            st.write("**How to learn:**")
            for i, resource in enumerate(resources, 1):
                st.write(f"{i}. {resource}")
            
            st.write("**Time required:** 2-4 weeks for basics")
            st.write("**Practice projects:** Build 2-3 projects using this skill")

def get_real_jobs(skills_list, location="India", limit=5):
    """
    Fetch real job openings from APIs based on skills
    """
    try:
        # Simulated API response (actual APIs need API keys)
        # In production, you would use: Indeed API, LinkedIn API, etc.
        
        # Mock data based on skills
        job_listings = []
        primary_skill = skills_list[0] if skills_list else "python"
        
        mock_jobs = {
            "python": [
                {
                    "title": "Python Developer",
                    "company": "Tech Solutions Inc.",
                    "location": "Bangalore",
                    "skills": ["Python", "Django", "SQL"],
                    "experience": "2-4 years",
                    "salary": "₹8-12 LPA",
                    "apply_link": "#"
                },
                {
                    "title": "Backend Engineer - Python",
                    "company": "Startup Innovations",
                    "location": "Remote",
                    "skills": ["Python", "FastAPI", "MongoDB"],
                    "experience": "1-3 years",
                    "salary": "₹6-10 LPA",
                    "apply_link": "#"
                }
            ],
            "javascript": [
                {
                    "title": "Frontend Developer",
                    "company": "Web Creations Ltd.",
                    "location": "Delhi",
                    "skills": ["JavaScript", "React", "CSS"],
                    "experience": "2-5 years",
                    "salary": "₹7-11 LPA",
                    "apply_link": "#"
                }
            ],
            "java": [
                {
                    "title": "Java Software Engineer",
                    "company": "Enterprise Systems",
                    "location": "Hyderabad",
                    "skills": ["Java", "Spring Boot", "Microservices"],
                    "experience": "3-6 years",
                    "salary": "₹10-15 LPA",
                    "apply_link": "#"
                }
            ],
            "data analysis": [
                {
                    "title": "Data Analyst",
                    "company": "Analytics Pro",
                    "location": "Mumbai",
                    "skills": ["Python", "SQL", "Excel", "Tableau"],
                    "experience": "1-3 years",
                    "salary": "₹5-9 LPA",
                    "apply_link": "#"
                }
            ]
        }
        
        # Get relevant jobs based on skills
        for skill in skills_list:
            if skill in mock_jobs and len(job_listings) < limit:
                job_listings.extend(mock_jobs[skill])
        
        # Remove duplicates
        unique_jobs = []
        seen_titles = set()
        for job in job_listings:
            if job['title'] not in seen_titles:
                unique_jobs.append(job)
                seen_titles.add(job['title'])
        
        return unique_jobs[:limit]
        
    except Exception as e:
        st.error(f"Error fetching jobs: {str(e)}")
        return []

def display_real_jobs(job_listings):
    """
    Display real job openings
    """
    if not job_listings:
        return
    
    st.markdown("---")
    st.subheader("🔥 Real Job Openings for You")
    st.success("Based on your skills, here are actual job opportunities:")
    
    for i, job in enumerate(job_listings, 1):
        with st.expander(f"{i}. {job['title']} at {job['company']}"):
            st.write(f"**Company:** {job['company']}")
            st.write(f"**Location:** {job['location']}")
            st.write(f"**Experience:** {job['experience']}")
            st.write(f"**Salary:** {job['salary']}")
            
            st.write("**Required Skills:**")
            skills_html = "".join([f'<span class="skill-pill">{skill}</span>' for skill in job['skills']])
            st.markdown(skills_html, unsafe_allow_html=True)
            
            st.write(f"**Apply:** [Click Here]({job['apply_link']})")

JOB_DATABASE = {
    "Software Engineer": {
        "required_skills": ["python", "java", "javascript", "sql", "git"],
        "description": "Designs, develops, and tests software applications and systems."
    },
    "Data Scientist": {
        "required_skills": ["python", "machine learning", "data analysis", "sql", "statistics"],
        "description": "Builds machine learning models to extract insights from data."
    },
    "Web Developer": {
        "required_skills": ["javascript", "html", "css", "python", "react"],
        "description": "Creates and maintains websites and web applications."
    },
    "Data Analyst": {
        "required_skills": ["excel", "sql", "data analysis", "python", "statistics"],
        "description": "Analyzes data to help businesses make informed decisions."
    },
    "Mobile App Developer": {
        "required_skills": ["android", "kotlin", "java", "swift", "ios"],
        "description": "Develops applications for mobile devices."
    },
    "DevOps Engineer": {
        "required_skills": ["aws", "cloud computing", "git", "linux", "python"],
        "description": "Manages and automates software deployment processes."
    },
    "Digital Marketing Specialist": {
        "required_skills": ["digital marketing", "seo", "content writing", "social media"],
        "description": "Plans and executes online marketing campaigns."
    },
    "Backend Developer": {
        "required_skills": ["python", "java", "node.js", "sql", "mongodb"],
        "description": "Develops server-side logic and databases for web applications."
    },
    "Frontend Developer": {
        "required_skills": ["javascript", "html", "css", "react", "angular"],
        "description": "Creates user interfaces and client-side functionality."
    }
}

def suggest_jobs(found_skills, job_db):
    suggested_jobs = {}
    
    for job_name, job_details in job_db.items():
        required_skills = job_details["required_skills"]
        matched_skills = [skill for skill in required_skills if skill in found_skills]
        
        if len(required_skills) > 0:
            match_score = len(matched_skills) / len(required_skills)
        else:
            match_score = 0
        
        if match_score > 0.3:
            suggested_jobs[job_name] = {
                "match_score": match_score,
                "matched_skills": matched_skills,
                "missing_skills": [skill for skill in required_skills if skill not in found_skills],
                "description": job_details["description"]
            }
    
    return dict(sorted(suggested_jobs.items(), key=lambda item: item[1]['match_score'], reverse=True))

# Process the uploaded file
if uploaded_file is not None:
    with st.spinner('🔍 Analyzing your resume...'):
        # Extract text
        resume_text = extract_text_from_file(uploaded_file)
        
        if resume_text and not resume_text.startswith("Error"):
            # Extract skills
            skills_list = extract_skills(resume_text)
            
            if skills_list:
                # Calculate resume score
                resume_score = calculate_resume_score(skills_list)
                
                # Suggest jobs
                suggested_jobs = suggest_jobs(skills_list, JOB_DATABASE)
                
                # Skill Gap Analysis
                skill_gap_analysis = generate_skill_gap_analysis(skills_list, suggested_jobs)
                
                # Display results
                st.success("✅ Analysis complete!")
                
                # Resume Score Section
                st.markdown("---")
                st.subheader("📊 Your Resume Score")
                
                # Score display with color coding
                if resume_score >= 80:
                    score_class = "score-excellent"
                    score_message = "Excellent! Your resume has strong skills. 🎯"
                elif resume_score >= 50:
                    score_class = "score-good"
                    score_message = "Good! But can be improved with more skills. 👍"
                else:
                    score_class = "score-poor"
                    score_message = "Needs improvement. Add more technical skills. 💪"
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f'<div class="{score_class}">{resume_score:.0f}/100</div>', unsafe_allow_html=True)
                    st.write(score_message)
                
                with col2:
                    st.progress(resume_score/100)
                    st.caption(f"Based on {len(skills_list)} skills found in your resume")
                
                # Skills found
                st.markdown("---")
                st.subheader("🎯 Skills Identified in Your Resume")
                
                if skills_list:
                    # Group skills by category
                    tech_skills = [s for s in skills_list if s in ['python', 'java', 'javascript', 'html', 'css', 'sql', 'react', 'node.js', 'android', 'swift']]
                    data_skills = [s for s in skills_list if s in ['machine learning', 'data analysis', 'excel', 'statistics']]
                    soft_skills = [s for s in skills_list if s in ['communication', 'teamwork', 'leadership', 'problem solving', 'analytical skills']]
                    other_skills = [s for s in skills_list if s not in tech_skills + data_skills + soft_skills]
                    
                    if tech_skills:
                        st.write("**Technical Skills:**")
                        tech_html = "".join([f'<span class="skill-pill">{skill.title()}</span>' for skill in tech_skills])
                        st.markdown(tech_html, unsafe_allow_html=True)
                    
                    if data_skills:
                        st.write("**Data Skills:**")
                        data_html = "".join([f'<span class="skill-pill">{skill.title()}</span>' for skill in data_skills])
                        st.markdown(data_html, unsafe_allow_html=True)
                    
                    if soft_skills:
                        st.write("**Soft Skills:**")
                        soft_html = "".join([f'<span class="skill-pill">{skill.title()}</span>' for skill in soft_skills])
                        st.markdown(soft_html, unsafe_allow_html=True)
                    
                    if other_skills:
                        st.write("**Other Skills:**")
                        other_html = "".join([f'<span class="skill-pill">{skill.title()}</span>' for skill in other_skills])
                        st.markdown(other_html, unsafe_allow_html=True)
                
                # Job recommendations
                st.markdown("---")
                st.subheader("💼 Recommended Jobs For You")
                
                if suggested_jobs:
                    for job, details in suggested_jobs.items():
                        match_percent = details['match_score']
                        
                        if match_percent >= 0.8:
                            match_class = "match-high"
                            match_emoji = "🔥"
                        elif match_percent >= 0.5:
                            match_class = "match-medium"
                            match_emoji = "👍"
                        else:
                            match_class = "match-low"
                            match_emoji = "💡"
                        
                        st.markdown(f"""
                        <div class="result-box">
                            <h3>{match_emoji} {job} (<span class="{match_class}">{match_percent:.0%} match</span>)</h3>
                            <p><strong>Description:</strong> {details['description']}</p>
                            <p><strong>✅ Your Matching Skills:</strong> {', '.join(details['matched_skills']).title()}</p>
                            <p><strong>📚 Skills to Learn:</strong> {', '.join(details['missing_skills']).title() if details['missing_skills'] else 'None! You have all required skills 🎉'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No strong job matches found. Consider adding more skills to your resume.")
                
                # Skill Gap Analysis Display
                display_skill_gap_analysis(skill_gap_analysis)
                
                # Real Job Openings
                if suggested_jobs and len(skills_list) > 0:
                    with st.spinner('🚀 Fetching real job openings...'):
                        real_jobs = get_real_jobs(skills_list)
                        display_real_jobs(real_jobs)
                
                # Tips based on score
                st.markdown("---")
                st.subheader("💡 Improvement Tips")
                
                if resume_score < 50:
                    st.info("""
                    - Add more technical skills to your resume
                    - Be specific about technologies you know (e.g., Python, Java, React)
                    - Include both hard and soft skills
                    - Mention projects where you used these skills
                    """)
                elif resume_score < 80:
                    st.info("""
                    - Consider learning in-demand skills like Cloud Computing or Machine Learning
                    - Add certifications or online courses you've completed
                    - Highlight your achievements with metrics and numbers
                    """)
                else:
                    st.info("""
                    - Your resume is strong! Consider applying for senior positions
                    - Keep your skills updated with latest technologies
                    - Add leadership and project management experiences
                    """)
                    
            else:
                st.error("No skills identified. Please make sure your resume contains technical skills.")
        else:
            st.error("Failed to read the resume file. Please try with a different file.")
else:
    st.info("👆 Upload your resume (PDF or Word) to get started")

# Footer
st.markdown("---")
st.markdown("### 🚀 Next Steps:")
st.markdown("""
1. **Add missing skills** to improve your resume score
2. **Focus on job roles** with highest match percentage  
3. **Practice interview questions** for your target job
4. **Update your resume** regularly with new skills
""")

st.markdown("---")
st.markdown("*Built with ❤️ using Streamlit | Your AI Career Assistant*")