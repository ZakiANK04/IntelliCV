"""
Sample CV text data for testing with known expected outcomes.
Each sample includes the CV text and expected analysis results for validation.
"""

# ============================================================================
# SAMPLE CV 1: Senior Software Engineer (High Quality)
# ============================================================================
SENIOR_SOFTWARE_ENGINEER_CV = {
    "text": """
JOHN MICHAEL SMITH
Senior Software Engineer

Contact Information:
Email: john.smith@email.com
Phone: +1 (555) 123-4567
LinkedIn: linkedin.com/in/johnsmith
Location: San Francisco, CA

PROFESSIONAL SUMMARY
Highly motivated Senior Software Engineer with 8+ years of experience in full-stack development,
specializing in Python, JavaScript, and cloud technologies. Proven track record of leading
development teams and delivering scalable solutions that improve business outcomes.
Strong expertise in agile methodologies and DevOps practices.

WORK EXPERIENCE

Senior Software Engineer | TechCorp Inc. | 2020 - Present
• Led a team of 5 developers to build a microservices architecture serving 2M+ users
• Designed and implemented RESTful APIs using Python/Django and Node.js
• Reduced system latency by 40% through performance optimization
• Implemented CI/CD pipelines using Jenkins and Docker
• Mentored junior developers and conducted code reviews

Software Engineer | InnovateTech LLC | 2017 - 2020
• Developed full-stack web applications using React and Django
• Built real-time data processing systems using Apache Kafka
• Collaborated with product managers to define technical requirements
• Implemented automated testing increasing code coverage to 85%

Junior Developer | StartupXYZ | 2015 - 2017
• Developed and maintained WordPress and custom PHP applications
• Assisted in database design and optimization
• Participated in agile sprints and daily standups

EDUCATION

Bachelor of Science in Computer Science
Stanford University | 2015
GPA: 3.8/4.0

SKILLS

Programming Languages: Python, JavaScript, TypeScript, Java, C++, Go
Frameworks: Django, React, Node.js, Express, Flask, FastAPI
Databases: PostgreSQL, MySQL, MongoDB, Redis
Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins, GitHub Actions
Tools: Git, JIRA, Confluence, VS Code, PyCharm

CERTIFICATIONS
• AWS Solutions Architect Associate (2022)
• Google Cloud Professional Developer (2021)
• Certified Scrum Master (CSM) (2020)

PROJECTS

Open Source Contribution - Django REST Framework
• Contributed authentication improvements merged into main repository
• 500+ GitHub stars on personal fork

E-commerce Platform (Personal Project)
• Built full-stack e-commerce solution with payment integration
• Technologies: React, Node.js, PostgreSQL, Stripe

ACHIEVEMENTS
• Employee of the Year 2022 at TechCorp Inc.
• Led team that won internal hackathon 2021
• Speaker at PyCon 2021 on "Scaling Python Applications"
""",
    "expected": {
        "experience_level": "Senior",  # System should detect "Senior" from 8+ years experience
        "career_field": "Information Technology",
        "min_score": 70,
        "max_score": 95,
        "required_sections": ["professional_summary", "work_experience", "education", "skills"],
        "required_skills": ["python", "javascript", "django", "react", "aws", "docker"],
        "has_certifications": True,
        "has_achievements": True
    }
}

# ============================================================================
# SAMPLE CV 2: Entry-Level Data Scientist
# ============================================================================
# Note on experience levels:
# System uses: Fresher, Junior, Mid-Level, Senior, Unknown

ENTRY_LEVEL_DATA_SCIENTIST_CV = {
    "text": """
SARAH JOHNSON
Aspiring Data Scientist

Email: sarah.johnson@gmail.com
Phone: (555) 987-6543

OBJECTIVE
Recent Computer Science graduate seeking an entry-level Data Scientist position to apply 
my knowledge of machine learning and statistical analysis in a dynamic organization.

EDUCATION

Master of Science in Data Science
MIT | 2024
Relevant Coursework: Machine Learning, Deep Learning, Statistical Methods, Big Data Analytics

Bachelor of Science in Mathematics
UCLA | 2022
GPA: 3.6/4.0

INTERNSHIP EXPERIENCE

Data Science Intern | DataDriven Co. | Summer 2023
• Developed predictive models using Python and scikit-learn
• Performed exploratory data analysis on customer datasets
• Created visualization dashboards using Tableau
• Collaborated with senior data scientists on NLP projects

Research Assistant | UCLA Data Lab | 2021 - 2022
• Assisted in research on neural network architectures
• Cleaned and preprocessed large datasets
• Wrote Python scripts for data collection

ACADEMIC PROJECTS

Sentiment Analysis on Social Media Data
• Built NLP model to classify sentiment from Twitter data
• Achieved 89% accuracy using BERT transformers
• Technologies: Python, PyTorch, Hugging Face

Customer Churn Prediction
• Developed machine learning pipeline for telecom churn prediction
• Used ensemble methods achieving 92% AUC-ROC
• Technologies: Python, scikit-learn, XGBoost

TECHNICAL SKILLS

Languages: Python, R, SQL, Java
ML/AI: TensorFlow, PyTorch, scikit-learn, Keras
Data Tools: Pandas, NumPy, Matplotlib, Seaborn
Big Data: Spark, Hadoop basics
Visualization: Tableau, Power BI
Statistics: Hypothesis testing, Regression, A/B testing

CERTIFICATIONS
• Google Data Analytics Professional Certificate (2023)
• IBM Data Science Professional Certificate (2023)

INTERESTS
Competitive programming, Kaggle competitions (Top 10% in 2 competitions), tech blogging
""",
    "expected": {
        "experience_level": "Fresher",  # Internship only, no full-time work
        "career_field": "Data Science",
        "min_score": 55,
        "max_score": 80,
        "required_sections": ["education", "skills"],
        "required_skills": ["python", "machine learning", "tensorflow", "pandas"],
        "has_certifications": True,
        "has_internship": True
    }
}

# ============================================================================
# SAMPLE CV 3: Mid-Level Marketing Professional
# ============================================================================
MID_LEVEL_MARKETING_CV = {
    "text": """
EMILY CHEN
Digital Marketing Manager

Contact: emily.chen@outlook.com | +1 (555) 234-5678

PROFILE SUMMARY
Results-driven Digital Marketing Manager with 5 years of experience in developing and 
executing comprehensive marketing strategies. Expert in SEO, SEM, social media marketing,
and content strategy. Proven ability to increase brand awareness and drive customer engagement.

PROFESSIONAL EXPERIENCE

Digital Marketing Manager | BrandBoost Agency | 2021 - Present
• Managed marketing campaigns for 15+ clients with combined budget of $2M+
• Increased organic traffic by 150% through SEO optimization strategies
• Led social media campaigns achieving 3x engagement rate improvement
• Developed content marketing strategies resulting in 50% lead generation increase
• Managed team of 3 marketing specialists

Marketing Specialist | GrowthMedia Inc. | 2019 - 2021
• Executed paid advertising campaigns on Google Ads and Facebook Ads
• Managed email marketing campaigns with 25% open rate improvement
• Conducted market research and competitor analysis
• Created compelling content for blogs, social media, and newsletters

Marketing Coordinator | StartBrand LLC | 2018 - 2019
• Assisted in planning and executing marketing events
• Managed social media accounts and community engagement
• Tracked and reported on marketing KPIs

EDUCATION

Bachelor of Business Administration - Marketing
NYU Stern School of Business | 2018

SKILLS

Digital Marketing: SEO, SEM, PPC, Content Marketing, Email Marketing
Social Media: Facebook, Instagram, LinkedIn, Twitter, TikTok
Tools: Google Analytics, HubSpot, Mailchimp, Hootsuite, SEMrush
Advertising: Google Ads, Facebook Ads Manager, LinkedIn Ads
Analytics: Google Data Studio, Tableau, Excel
Creative: Canva, Adobe Creative Suite basics

CERTIFICATIONS
• Google Analytics Certified (2023)
• HubSpot Content Marketing Certified (2022)
• Facebook Blueprint Certified (2021)

ACHIEVEMENTS
• Awarded "Best Digital Campaign" at Marketing Excellence Awards 2022
• Featured speaker at Digital Marketing Summit 2023
""",
    "expected": {
        "experience_level": "Mid-Level",  # 5 years experience (2018-present)
        "career_field": "Marketing",
        "min_score": 65,
        "max_score": 85,
        "required_sections": ["professional_summary", "work_experience", "education", "skills"],
        "required_skills": ["seo", "digital marketing", "google analytics", "social media"],
        "has_certifications": True,
        "has_achievements": True
    }
}

# ============================================================================
# SAMPLE CV 4: Healthcare Professional (Nurse)
# ============================================================================
HEALTHCARE_NURSE_CV = {
    "text": """
MARIA RODRIGUEZ, RN, BSN
Registered Nurse

Contact Information:
Email: maria.rodriguez@healthmail.com
Phone: (555) 456-7890
Location: Chicago, IL

PROFESSIONAL SUMMARY
Compassionate and dedicated Registered Nurse with 6 years of experience in acute care 
and emergency medicine. Strong clinical skills in patient assessment, medication 
administration, and emergency response. Committed to providing high-quality patient care 
and supporting interdisciplinary healthcare teams.

NURSING EXPERIENCE

Emergency Room Nurse | Chicago General Hospital | 2021 - Present
• Provide emergency care for 20+ patients per shift in Level 1 trauma center
• Perform triage assessments and prioritize patient care needs
• Administer medications and treatments following physician orders
• Collaborate with physicians, specialists, and healthcare team members
• Trained 5 new nurses in ER protocols and procedures
• Maintained 98% patient satisfaction scores

Staff Nurse - Medical-Surgical Unit | St. Mary's Hospital | 2018 - 2021
• Provided comprehensive nursing care for 6-8 patients per shift
• Monitored vital signs and assessed patient conditions
• Administered medications, IVs, and treatments
• Documented patient care in electronic health records (Epic)
• Participated in interdisciplinary care team meetings

EDUCATION

Bachelor of Science in Nursing (BSN)
University of Illinois at Chicago | 2018

Associate Degree in Nursing (ADN)
Chicago City College | 2016

LICENSES & CERTIFICATIONS

• Registered Nurse License - Illinois (Active)
• Basic Life Support (BLS) - American Heart Association
• Advanced Cardiovascular Life Support (ACLS)
• Pediatric Advanced Life Support (PALS)
• Trauma Nursing Core Course (TNCC)
• Certified Emergency Nurse (CEN) - 2023

CLINICAL SKILLS

Patient Care: Vital signs monitoring, IV insertion, catheterization, wound care
Emergency: Triage, trauma care, cardiac monitoring, emergency response
Technology: Epic EHR, Cerner, medication dispensing systems
Communication: Patient education, family communication, healthcare team collaboration

ACHIEVEMENTS
• Daisy Award for Excellence in Nursing (2022)
• Employee of the Month - Chicago General Hospital (March 2023)
• CPR Save Recognition for successful patient resuscitation
""",
    "expected": {
        "experience_level": "Senior",  # 6+ years nursing experience
        "career_field": "Healthcare",
        "min_score": 70,
        "max_score": 90,
        "required_sections": ["professional_summary", "work_experience", "education"],
        "required_skills": ["patient care", "nursing"],
        "has_certifications": True,
        "has_achievements": True
    }
}

# ============================================================================
# SAMPLE CV 5: Poor Quality CV (For Testing Low Scores)
# ============================================================================
POOR_QUALITY_CV = {
    "text": """
john doe

email: john123@email.com

i am looking for a job. i can do many things.

experience:
worked at some company for 2 years
did stuff

education:
high school

skills:
computer, microsoft word, typing

hobbies:
watching tv, sleeping, playing games
""",
    "expected": {
        "experience_level": "Junior",  # Has 2 years experience mentioned
        "career_field": "General",  # May detect Teacher due to 'watching tv' -> education context
        "min_score": 30,
        "max_score": 55,
        "required_sections": [],  # Poorly structured, sections may not be detected
        "required_skills": [],
        "has_certifications": False,
        "has_achievements": False
    }
}

# ============================================================================
# SAMPLE CV 6: Machine Learning Engineer
# ============================================================================
ML_ENGINEER_CV = {
    "text": """
ALEX KUMAR
Machine Learning Engineer

Email: alex.kumar@techmail.com | Phone: +1-555-789-0123 | GitHub: github.com/alexkumar

SUMMARY
Machine Learning Engineer with 4 years of experience building and deploying production ML systems.
Expertise in deep learning, NLP, and computer vision. Passionate about developing scalable AI 
solutions that drive business value.

EXPERIENCE

Machine Learning Engineer | AI Solutions Inc. | 2022 - Present
• Developed and deployed NLP models for sentiment analysis serving 1M+ daily requests
• Built recommendation system improving user engagement by 35%
• Implemented MLOps pipelines using MLflow, Kubeflow, and AWS SageMaker
• Reduced model inference latency by 60% through optimization techniques
• Led computer vision project for defect detection achieving 97% accuracy

Data Scientist | DataTech Corp | 2020 - 2022
• Built predictive models using XGBoost and Random Forest
• Developed ETL pipelines for feature engineering
• Created automated model monitoring and retraining systems
• Conducted A/B tests for model performance validation

EDUCATION

Master of Science in Computer Science (ML Specialization)
Carnegie Mellon University | 2020

Bachelor of Engineering in Computer Science
IIT Delhi | 2018

TECHNICAL SKILLS

ML Frameworks: TensorFlow, PyTorch, scikit-learn, Keras, JAX
Deep Learning: CNNs, RNNs, Transformers, GANs, BERT, GPT
MLOps: MLflow, Kubeflow, AWS SageMaker, DVC, Weights & Biases
Programming: Python, SQL, Java, Scala
Big Data: Spark, Hadoop, Kafka
Cloud: AWS, GCP, Azure
NLP: spaCy, NLTK, Hugging Face Transformers

PUBLICATIONS & PATENTS
• "Efficient Transformer Architectures for Low-Resource NLP" - EMNLP 2023
• Patent pending: "Method for Real-time Anomaly Detection in IoT Systems"

CERTIFICATIONS
• AWS Machine Learning Specialty (2023)
• TensorFlow Developer Certificate (2022)
• Deep Learning Specialization - Coursera (2021)

PROJECTS

Open Source Contributions
• Core contributor to popular ML library (1000+ GitHub stars)
• Maintainer of NLP preprocessing toolkit

Kaggle Competitions
• Top 1% in Natural Language Processing competition
• Gold medal in Computer Vision challenge
""",
    "expected": {
        "experience_level": "Mid-Level",  # 4 years ML experience (2020-present)
        "career_field": "Machine Learning",
        "min_score": 75,
        "max_score": 95,
        "required_sections": ["professional_summary", "work_experience", "education", "skills"],
        "required_skills": ["python", "tensorflow", "pytorch", "machine learning", "deep learning"],
        "has_certifications": True,
        "has_publications": True
    }
}

# ============================================================================
# SAMPLE CV 7: Accountant
# ============================================================================
ACCOUNTANT_CV = {
    "text": """
JENNIFER WILLIAMS, CPA
Senior Accountant

Email: jennifer.williams@financemail.com
Phone: (555) 321-6547
Location: Dallas, TX

PROFESSIONAL SUMMARY
Detail-oriented Certified Public Accountant with 7 years of experience in financial 
reporting, tax preparation, and audit. Strong knowledge of GAAP and IFRS standards.
Proven track record of improving financial processes and ensuring regulatory compliance.

WORK EXPERIENCE

Senior Accountant | Big Four Accounting Firm | 2020 - Present
• Lead audit engagements for clients with revenues up to $500M
• Prepare and review financial statements in accordance with GAAP
• Supervise team of 3 staff accountants
• Identify and implement process improvements reducing close time by 30%
• Ensure compliance with SOX requirements

Staff Accountant | MidSize Manufacturing Co. | 2017 - 2020
• Managed full-cycle accounts payable and accounts receivable
• Performed monthly bank reconciliations and journal entries
• Prepared quarterly and annual financial reports
• Assisted with external audit coordination
• Maintained fixed asset register and depreciation schedules

Junior Accountant | Local CPA Firm | 2016 - 2017
• Prepared individual and business tax returns
• Assisted with bookkeeping for small business clients
• Performed payroll processing

EDUCATION

Master of Accountancy
University of Texas at Austin | 2016

Bachelor of Business Administration - Accounting
Texas A&M University | 2014

LICENSES & CERTIFICATIONS
• Certified Public Accountant (CPA) - Texas
• Certified Management Accountant (CMA)
• QuickBooks ProAdvisor Certified

TECHNICAL SKILLS

Accounting Software: SAP, Oracle, QuickBooks, Sage
Microsoft Office: Advanced Excel (VLOOKUP, Pivot Tables, Macros)
ERP Systems: SAP S/4HANA, Oracle Cloud
Financial Reporting: GAAP, IFRS, SEC Reporting
Tax: Individual tax, Corporate tax, Tax research

ACHIEVEMENTS
• Promoted to Senior within 2 years (vs. typical 3-year track)
• Received "Excellence in Client Service" award 2022
• Identified $1.2M in tax savings for key client
""",
    "expected": {
        "experience_level": "Senior",  # 7+ years accounting experience
        "career_field": "Accountant",
        "min_score": 70,
        "max_score": 90,
        "required_sections": ["professional_summary", "work_experience", "education"],
        "required_skills": ["accounting", "gaap", "tax", "excel"],
        "has_certifications": True,
        "has_achievements": True
    }
}

# ============================================================================
# Collection of all sample CVs for iteration
# ============================================================================
ALL_SAMPLE_CVS = {
    "senior_software_engineer": SENIOR_SOFTWARE_ENGINEER_CV,
    "entry_level_data_scientist": ENTRY_LEVEL_DATA_SCIENTIST_CV,
    "mid_level_marketing": MID_LEVEL_MARKETING_CV,
    "healthcare_nurse": HEALTHCARE_NURSE_CV,
    "poor_quality": POOR_QUALITY_CV,
    "ml_engineer": ML_ENGINEER_CV,
    "accountant": ACCOUNTANT_CV
}

# Quick validation tests (lighter weight)
QUICK_TEST_CVS = {
    "senior_software_engineer": SENIOR_SOFTWARE_ENGINEER_CV,
    "poor_quality": POOR_QUALITY_CV,
    "ml_engineer": ML_ENGINEER_CV
}
