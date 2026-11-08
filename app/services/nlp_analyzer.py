"""
NLP Analysis Pipeline for CV Processing
Handles section detection, entity extraction, and semantic analysis
"""
import re
import logging
from datetime import date
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class SectionResult:
    """Result for a detected CV section"""
    detected: bool = False
    quality_score: float = 0.0
    content: str = ""
    explanation: str = ""
    start_pos: int = -1
    end_pos: int = -1


@dataclass
class AnalysisResult:
    """Complete CV analysis result"""
    # Overall
    overall_score: float = 0.0
    experience_level: str = "Unknown"
    career_field: str = "General"
    
    # Score breakdown
    experience_score: float = 0.0
    skills_score: float = 0.0
    structure_score: float = 0.0
    career_score: float = 0.0
    readability_score: float = 0.0
    
    # Detected content
    sections: Dict[str, SectionResult] = field(default_factory=dict)
    skills_found: List[str] = field(default_factory=list)
    entities: Dict[str, List[str]] = field(default_factory=dict)
    
    # Analysis details
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    youtube_suggestions: List[Dict[str, str]] = field(default_factory=list)


class NLPAnalyzer:
    """
    NLP-based CV analyzer using spaCy and semantic similarity.
    Combines rule-based patterns with NLP for robust section detection.
    """
    
    # Section detection patterns (keywords and variations)
    SECTION_PATTERNS = {
        'professional_summary': [
            r'(?:professional\s+)?summary',
            r'(?:career\s+)?objective',
            r'profile\s*(?:summary)?',
            r'about\s+me',
            r'personal\s+statement',
            r'executive\s+summary'
        ],
        'education': [
            r'education(?:al)?\s*(?:background|qualifications?)?',
            r'academic\s*(?:background|qualifications?)',
            r'qualifications?',
            r'degrees?',
            r'schooling'
        ],
        'work_experience': [
            r'(?:work|professional|employment)\s+(?:experience|history)',
            r'experience',
            r'career\s+history',
            r'employment\s+record'
        ],
        'internship_experience': [
            r'internships?',
            r'training\s+(?:experience|program)',
            r'industrial\s+training',
            r'practical\s+experience'
        ],
        'skills': [
            r'(?:technical\s+)?skills?',
            r'competenc(?:ies|y)',
            r'expertise',
            r'proficiencies',
            r'technical\s+abilities',
            r'core\s+competencies'
        ],
        'projects': [
            r'projects?',
            r'portfolio',
            r'(?:key\s+)?accomplishments',
            r'works?'
        ],
        'certifications': [
            r'certifications?',
            r'licenses?',
            r'credentials?',
            r'professional\s+development',
            r'courses?\s+completed'
        ],
        'achievements': [
            r'achievements?',
            r'awards?\s*(?:and\s+honors?)?',
            r'honors?',
            r'accomplishments?',
            r'recognition'
        ],
        'hobbies': [
            r'hobbies?\s*(?:and\s+interests?)?',
            r'interests?',
            r'extra\s*curricular',
            r'activities',
            r'personal\s+interests?'
        ]
    }
    
    # Career field detection patterns - comprehensive across all industries
    # Each career has: primary keywords (high weight), secondary keywords (medium weight), and job titles (highest weight)
    CAREER_FIELDS = {
        # Data Science and AI Fields (with subfields)
        'Data Science': {
            'job_titles': ['data scientist', 'data science', 'senior data scientist', 'lead data scientist', 
                          'data science manager', 'principal data scientist', 'staff data scientist'],
            'primary': ['data science', 'data scientist', 'predictive modeling', 'statistical modeling',
                       'data mining', 'feature engineering', 'model deployment', 'a/b testing',
                       'experimental design', 'hypothesis testing', 'regression analysis', 'classification'],
            'secondary': ['statistics', 'statistical analysis', 'data visualization', 'python', 'r programming',
                         'jupyter', 'pandas', 'numpy', 'scikit-learn', 'matplotlib', 'seaborn', 'plotly']
        },
        'Machine Learning': {
            'job_titles': ['machine learning engineer', 'ml engineer', 'machine learning scientist',
                          'applied scientist', 'research scientist ml', 'ml ops engineer'],
            'primary': ['machine learning', 'ml engineer', 'deep learning', 'neural network', 'model training',
                       'supervised learning', 'unsupervised learning', 'reinforcement learning', 'mlops',
                       'feature extraction', 'model optimization', 'hyperparameter tuning'],
            'secondary': ['tensorflow', 'pytorch', 'keras', 'scikit-learn', 'xgboost', 'lightgbm',
                         'random forest', 'gradient boosting', 'svm', 'clustering', 'dimensionality reduction']
        },
        'Artificial Intelligence': {
            'job_titles': ['ai engineer', 'artificial intelligence engineer', 'ai researcher', 'ai scientist',
                          'ai developer', 'cognitive computing', 'ai architect'],
            'primary': ['artificial intelligence', 'ai engineer', 'cognitive computing', 'expert systems',
                       'knowledge representation', 'reasoning systems', 'ai research', 'intelligent systems'],
            'secondary': ['neural networks', 'deep learning', 'computer vision', 'nlp', 'robotics ai',
                         'autonomous systems', 'ai ethics', 'explainable ai']
        },
        'NLP Engineer': {
            'job_titles': ['nlp engineer', 'natural language processing engineer', 'nlp scientist',
                          'computational linguist', 'nlp researcher', 'text analytics engineer'],
            'primary': ['natural language processing', 'nlp', 'text mining', 'sentiment analysis',
                       'named entity recognition', 'text classification', 'language model', 'chatbot',
                       'conversational ai', 'speech recognition', 'text generation'],
            'secondary': ['spacy', 'nltk', 'transformers', 'bert', 'gpt', 'word embeddings', 'word2vec',
                         'tokenization', 'lemmatization', 'pos tagging', 'huggingface']
        },
        'Computer Vision': {
            'job_titles': ['computer vision engineer', 'cv engineer', 'image processing engineer',
                          'vision scientist', 'perception engineer'],
            'primary': ['computer vision', 'image processing', 'object detection', 'image recognition',
                       'image segmentation', 'facial recognition', 'ocr', 'video analytics'],
            'secondary': ['opencv', 'yolo', 'cnn', 'convolutional neural network', 'image classification',
                         'gan', 'generative adversarial', 'pytorch vision', 'detectron']
        },
        'Data Analytics': {
            'job_titles': ['data analyst', 'business analyst', 'analytics manager', 'bi analyst',
                          'reporting analyst', 'insights analyst', 'marketing analyst'],
            'primary': ['data analyst', 'data analysis', 'business intelligence', 'bi', 'reporting',
                       'dashboard', 'kpi', 'metrics', 'insights', 'analytics'],
            'secondary': ['excel', 'sql', 'tableau', 'power bi', 'looker', 'google analytics',
                         'data visualization', 'pivot table', 'vlookup', 'reporting tools']
        },
        'Data Engineering': {
            'job_titles': ['data engineer', 'etl developer', 'data pipeline engineer', 'big data engineer',
                          'data architect', 'analytics engineer'],
            'primary': ['data engineer', 'data engineering', 'etl', 'data pipeline', 'data warehouse',
                       'data lake', 'data modeling', 'data architecture', 'batch processing', 'streaming'],
            'secondary': ['spark', 'hadoop', 'airflow', 'kafka', 'snowflake', 'redshift', 'bigquery',
                         'dbt', 'databricks', 'hive', 'presto']
        },
        
        # Information Technology
        'Information Technology': {
            'job_titles': ['software developer', 'software engineer', 'programmer', 'web developer',
                          'full stack developer', 'backend developer', 'frontend developer', 'devops engineer',
                          'system administrator', 'network engineer', 'it manager', 'it support'],
            'primary': ['software development', 'programming', 'coding', 'web development', 'application development',
                       'system administration', 'network administration', 'it infrastructure', 'devops'],
            'secondary': ['python', 'java', 'javascript', 'c++', 'c#', 'react', 'angular', 'node.js',
                         'aws', 'azure', 'docker', 'kubernetes', 'linux', 'git', 'agile', 'scrum']
        },
        'Cybersecurity': {
            'job_titles': ['security analyst', 'cybersecurity analyst', 'security engineer', 'penetration tester',
                          'ethical hacker', 'soc analyst', 'security architect', 'ciso'],
            'primary': ['cybersecurity', 'information security', 'network security', 'penetration testing',
                       'vulnerability assessment', 'security audit', 'incident response', 'threat analysis'],
            'secondary': ['firewall', 'siem', 'ids', 'ips', 'encryption', 'malware', 'phishing',
                         'compliance', 'iso 27001', 'nist', 'cissp', 'ceh']
        },
        
        # Finance & Accounting
        'Accountant': {
            'job_titles': ['accountant', 'senior accountant', 'staff accountant', 'cpa', 'chartered accountant',
                          'tax accountant', 'audit accountant', 'cost accountant', 'management accountant'],
            'primary': ['accounting', 'bookkeeping', 'financial statements', 'general ledger', 'accounts payable',
                       'accounts receivable', 'tax preparation', 'audit', 'reconciliation', 'journal entries'],
            'secondary': ['gaap', 'ifrs', 'quickbooks', 'tally', 'sap', 'balance sheet', 'income statement',
                         'cash flow', 'trial balance', 'depreciation', 'accruals', 'tax returns']
        },
        'Finance': {
            'job_titles': ['financial analyst', 'finance manager', 'investment analyst', 'portfolio manager',
                          'treasury analyst', 'fp&a analyst', 'credit analyst', 'risk analyst'],
            'primary': ['financial analysis', 'investment', 'portfolio management', 'financial modeling',
                       'valuation', 'corporate finance', 'treasury', 'risk management', 'financial planning'],
            'secondary': ['excel', 'financial statements', 'dcf', 'npv', 'irr', 'bloomberg', 'capital markets',
                         'equity research', 'm&a', 'derivatives', 'cfa', 'budgeting', 'forecasting']
        },
        'Banking': {
            'job_titles': ['banker', 'bank manager', 'loan officer', 'credit analyst', 'relationship manager',
                          'branch manager', 'teller', 'investment banker', 'mortgage specialist'],
            'primary': ['banking', 'loan processing', 'credit analysis', 'retail banking', 'commercial banking',
                       'mortgage', 'deposit', 'kyc', 'aml', 'banking operations'],
            'secondary': ['customer service', 'financial products', 'interest rates', 'loan documentation',
                         'credit score', 'collateral', 'banking regulations', 'core banking']
        },
        
        # Legal
        'Advocate': {
            'job_titles': ['advocate', 'lawyer', 'attorney', 'legal counsel', 'paralegal', 'legal advisor',
                          'corporate counsel', 'litigation attorney', 'associate attorney'],
            'primary': ['legal', 'law', 'litigation', 'court', 'legal research', 'legal drafting',
                       'contract review', 'legal compliance', 'case management', 'legal advisory'],
            'secondary': ['civil law', 'criminal law', 'corporate law', 'contract law', 'intellectual property',
                         'patent', 'trademark', 'arbitration', 'mediation', 'bar council', 'legal proceedings']
        },
        
        # Agriculture
        'Agriculture': {
            'job_titles': ['agricultural officer', 'agronomist', 'farm manager', 'agricultural engineer',
                          'horticulturist', 'crop scientist', 'agricultural consultant'],
            'primary': ['agriculture', 'farming', 'crop', 'horticulture', 'agronomy', 'livestock',
                       'irrigation', 'pest control', 'soil management', 'agricultural practices'],
            'secondary': ['fertilizer', 'seeds', 'harvest', 'organic farming', 'dairy', 'poultry',
                         'fisheries', 'greenhouse', 'plantation', 'agricultural machinery']
        },
        
        # Fashion & Apparel
        'Apparel': {
            'job_titles': ['fashion designer', 'apparel designer', 'merchandiser', 'fashion buyer',
                          'stylist', 'textile designer', 'pattern maker', 'garment technologist'],
            'primary': ['fashion', 'apparel', 'garment', 'textile', 'clothing', 'fashion design',
                       'merchandising', 'pattern making', 'tailoring', 'fashion retail'],
            'secondary': ['fabric', 'embroidery', 'sewing', 'fashion illustration', 'collection',
                         'runway', 'boutique', 'visual merchandising', 'fashion marketing', 'trend analysis']
        },
        
        # Arts & Creative
        'Arts': {
            'job_titles': ['artist', 'painter', 'sculptor', 'illustrator', 'art director', 'creative director',
                          'animator', 'photographer', 'videographer', 'musician', 'curator'],
            'primary': ['art', 'artist', 'painting', 'sculpture', 'illustration', 'fine arts', 'visual arts',
                       'photography', 'animation', 'creative', 'artistic'],
            'secondary': ['gallery', 'exhibition', 'portfolio', 'canvas', 'drawing', 'sketch',
                         'cinematography', 'music', 'performing arts', 'theater', 'dance']
        },
        'Designer': {
            'job_titles': ['graphic designer', 'ui designer', 'ux designer', 'product designer', 'web designer',
                          'visual designer', 'interior designer', 'industrial designer', 'motion designer'],
            'primary': ['design', 'graphic design', 'ui design', 'ux design', 'visual design', 'product design',
                       'user interface', 'user experience', 'branding', 'logo design'],
            'secondary': ['photoshop', 'illustrator', 'figma', 'sketch', 'indesign', 'canva', 'adobe',
                         'typography', 'layout', 'wireframe', 'prototype', 'design thinking']
        },
        'Digital Media': {
            'job_titles': ['content creator', 'social media manager', 'digital marketer', 'video editor',
                          'multimedia specialist', 'community manager', 'influencer', 'youtuber'],
            'primary': ['digital media', 'social media', 'content creation', 'video production', 'video editing',
                       'digital content', 'multimedia', 'social media marketing', 'content strategy'],
            'secondary': ['youtube', 'instagram', 'tiktok', 'premiere pro', 'final cut', 'after effects',
                         'podcast', 'blog', 'streaming', 'engagement', 'followers', 'viral']
        },
        
        # Automotive & Aviation
        'Automobile': {
            'job_titles': ['automotive engineer', 'auto mechanic', 'vehicle technician', 'service advisor',
                          'automobile designer', 'quality engineer automotive', 'production engineer'],
            'primary': ['automobile', 'automotive', 'vehicle', 'car', 'auto', 'motor', 'automotive engineering',
                       'vehicle design', 'auto repair', 'automotive manufacturing'],
            'secondary': ['engine', 'transmission', 'chassis', 'brake', 'suspension', 'diagnostics',
                         'electric vehicle', 'ev', 'hybrid', 'assembly line', 'dealership']
        },
        'Aviation': {
            'job_titles': ['pilot', 'flight attendant', 'cabin crew', 'aircraft engineer', 'aerospace engineer',
                          'air traffic controller', 'ground staff', 'aviation manager'],
            'primary': ['aviation', 'airline', 'aircraft', 'flight', 'aerospace', 'airport',
                       'aviation safety', 'aircraft maintenance', 'flight operations'],
            'secondary': ['pilot license', 'cockpit', 'navigation', 'cargo', 'ground handling',
                         'commercial aviation', 'private pilot', 'helicopter', 'drone', 'aeronautical']
        },
        
        # Business & Management
        'Business Development': {
            'job_titles': ['business development manager', 'bd manager', 'business development executive',
                          'partnerships manager', 'strategic alliance manager', 'key account manager'],
            'primary': ['business development', 'client acquisition', 'partnership', 'strategic alliance',
                       'lead generation', 'market expansion', 'business growth', 'new business'],
            'secondary': ['pitching', 'proposal', 'rfp', 'contract negotiation', 'stakeholder management',
                         'b2b', 'market research', 'competitive analysis', 'revenue growth']
        },
        'Consultant': {
            'job_titles': ['consultant', 'management consultant', 'strategy consultant', 'senior consultant',
                          'associate consultant', 'principal consultant', 'advisory'],
            'primary': ['consulting', 'advisory', 'management consulting', 'strategy consulting',
                       'business consulting', 'process improvement', 'transformation'],
            'secondary': ['mckinsey', 'bcg', 'bain', 'deloitte', 'accenture', 'big four',
                         'change management', 'stakeholder management', 'recommendations', 'client engagement']
        },
        
        # Customer Service
        'BPO': {
            'job_titles': ['customer service representative', 'call center agent', 'csr', 'team leader bpo',
                          'process associate', 'customer support executive', 'technical support'],
            'primary': ['bpo', 'call center', 'customer service', 'customer support', 'customer care',
                       'helpdesk', 'technical support', 'voice process', 'non voice'],
            'secondary': ['inbound', 'outbound', 'telemarketing', 'first call resolution', 'aht',
                         'sla', 'chat support', 'email support', 'csat', 'quality score']
        },
        
        # Construction
        'Construction': {
            'job_titles': ['civil engineer', 'site engineer', 'project engineer', 'construction manager',
                          'quantity surveyor', 'architect', 'structural engineer', 'contractor'],
            'primary': ['construction', 'civil engineering', 'building', 'site management', 'project management construction',
                       'structural', 'architecture', 'quantity surveying'],
            'secondary': ['autocad', 'blueprint', 'concrete', 'foundation', 'plumbing', 'electrical',
                         'hvac', 'safety', 'building codes', 'renovation', 'real estate']
        },
        
        # Culinary & Hospitality
        'Chef': {
            'job_titles': ['chef', 'head chef', 'executive chef', 'sous chef', 'pastry chef', 'line cook',
                          'prep cook', 'culinary', 'kitchen manager', 'cook'],
            'primary': ['chef', 'culinary', 'cooking', 'kitchen', 'food preparation', 'cuisine',
                       'restaurant', 'catering', 'menu planning', 'food service'],
            'secondary': ['recipe', 'pastry', 'baking', 'fine dining', 'banquet', 'buffet',
                         'food safety', 'haccp', 'hospitality', 'hotel', 'barista', 'sommelier']
        },
        
        # Education
        'Teacher': {
            'job_titles': ['teacher', 'professor', 'lecturer', 'instructor', 'tutor', 'educator',
                          'faculty', 'academic', 'trainer', 'teaching assistant', 'headmaster', 'principal'],
            'primary': ['teaching', 'teacher', 'education', 'classroom', 'curriculum', 'lesson planning',
                       'pedagogy', 'instruction', 'academic', 'school'],
            'secondary': ['student', 'assessment', 'grading', 'examination', 'syllabus', 'mentoring',
                         'e-learning', 'online teaching', 'classroom management', 'educational']
        },
        
        # Engineering (Non-Software)
        'Engineering': {
            'job_titles': ['mechanical engineer', 'electrical engineer', 'electronics engineer', 'chemical engineer',
                          'production engineer', 'maintenance engineer', 'process engineer', 'quality engineer'],
            'primary': ['engineering', 'mechanical', 'electrical', 'electronics', 'manufacturing',
                       'production', 'maintenance', 'process engineering', 'quality control'],
            'secondary': ['cad', 'solidworks', 'autocad', 'plc', 'scada', 'automation', 'robotics',
                         'six sigma', 'lean', 'iso', 'r&d', 'prototype', 'technical drawing']
        },
        
        # Fitness
        'Fitness': {
            'job_titles': ['personal trainer', 'fitness trainer', 'fitness instructor', 'gym trainer',
                          'yoga instructor', 'sports coach', 'nutritionist', 'dietitian', 'wellness coach'],
            'primary': ['fitness', 'personal training', 'gym', 'workout', 'exercise', 'training',
                       'sports', 'yoga', 'nutrition', 'wellness'],
            'secondary': ['bodybuilding', 'strength training', 'cardio', 'pilates', 'aerobics',
                         'crossfit', 'diet plan', 'weight loss', 'muscle building', 'health coaching']
        },
        
        # Healthcare
        'Healthcare': {
            'job_titles': ['nurse', 'doctor', 'physician', 'surgeon', 'pharmacist', 'dentist', 'therapist',
                          'medical assistant', 'healthcare administrator', 'lab technician', 'paramedic'],
            'primary': ['healthcare', 'medical', 'hospital', 'clinic', 'patient care', 'nursing',
                       'clinical', 'health care', 'medical care', 'treatment'],
            'secondary': ['patient', 'diagnosis', 'medication', 'pharmacy', 'laboratory', 'radiology',
                         'icu', 'emergency', 'ehr', 'hipaa', 'medical records', 'vital signs']
        },
        
        # Human Resources
        'HR': {
            'job_titles': ['hr manager', 'hr executive', 'recruiter', 'talent acquisition', 'hr generalist',
                          'hr business partner', 'compensation manager', 'training manager', 'hr director'],
            'primary': ['human resources', 'hr', 'recruitment', 'talent acquisition', 'hiring',
                       'employee relations', 'performance management', 'hr management'],
            'secondary': ['onboarding', 'offboarding', 'payroll', 'benefits', 'hris', 'workday',
                         'training and development', 'employee engagement', 'retention', 'job posting']
        },
        
        # Public Relations
        'Public Relations': {
            'job_titles': ['pr manager', 'public relations manager', 'communications manager', 'pr executive',
                          'media relations', 'corporate communications', 'press officer', 'spokesperson'],
            'primary': ['public relations', 'pr', 'communications', 'media relations', 'press release',
                       'corporate communications', 'reputation management', 'public affairs'],
            'secondary': ['press conference', 'media coverage', 'crisis management', 'journalist',
                         'editor', 'copywriter', 'content writer', 'brand communications', 'stakeholder']
        },
        
        # Sales
        'Sales': {
            'job_titles': ['sales executive', 'sales manager', 'account executive', 'sales representative',
                          'business development', 'territory manager', 'regional sales manager', 'salesperson'],
            'primary': ['sales', 'selling', 'revenue', 'quota', 'target', 'client acquisition',
                       'account management', 'sales management', 'territory'],
            'secondary': ['crm', 'salesforce', 'cold calling', 'prospecting', 'closing', 'negotiation',
                         'pipeline', 'lead generation', 'commission', 'retail', 'b2b', 'b2c']
        }
    }
    
    # Skills database by category - comprehensive for all career fields
    SKILLS_DATABASE = {
        # Tech & Programming
        'programming_languages': [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'ruby', 'php', 'swift', 
            'kotlin', 'go', 'golang', 'rust', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash', 
            'powershell', 'sql', 'html', 'css', 'sass', 'less', 'objective-c', 'dart', 'lua',
            'groovy', 'visual basic', 'vba', 'cobol', 'fortran', 'assembly', 'haskell', 'elixir'
        ],
        'frameworks_libraries': [
            'react', 'angular', 'vue', 'svelte', 'django', 'flask', 'fastapi', 'spring', 'spring boot',
            'node.js', 'express', 'nestjs', 'rails', 'ruby on rails', 'laravel', 'symfony', '.net', 
            'asp.net', 'blazor', 'next.js', 'nuxt.js', 'gatsby', 'remix', 'jquery', 'bootstrap',
            'tailwind', 'material ui', 'chakra ui', 'redux', 'mobx', 'rxjs', 'graphql', 'apollo'
        ],
        'data_science_ml': [
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'sklearn', 'pandas', 'numpy', 'scipy',
            'matplotlib', 'seaborn', 'plotly', 'bokeh', 'xgboost', 'lightgbm', 'catboost',
            'machine learning', 'deep learning', 'neural networks', 'nlp', 'natural language processing',
            'computer vision', 'reinforcement learning', 'random forest', 'decision tree', 'svm',
            'clustering', 'regression', 'classification', 'feature engineering', 'model deployment',
            'mlops', 'kubeflow', 'mlflow', 'huggingface', 'transformers', 'bert', 'gpt', 'llm',
            'opencv', 'yolo', 'spacy', 'nltk', 'gensim', 'word2vec', 'embeddings'
        ],
        'databases': [
            'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'elasticsearch', 'oracle',
            'sql server', 'mssql', 'sqlite', 'cassandra', 'dynamodb', 'firebase', 'firestore',
            'neo4j', 'couchdb', 'mariadb', 'aurora', 'cockroachdb', 'timescaledb', 'influxdb'
        ],
        'data_engineering': [
            'spark', 'pyspark', 'hadoop', 'hive', 'presto', 'trino', 'airflow', 'luigi', 'dagster',
            'kafka', 'kinesis', 'rabbitmq', 'snowflake', 'redshift', 'bigquery', 'databricks',
            'dbt', 'fivetran', 'etl', 'elt', 'data pipeline', 'data warehouse', 'data lake',
            'delta lake', 'parquet', 'avro', 'iceberg', 'data modeling'
        ],
        'cloud_devops': [
            'aws', 'amazon web services', 'azure', 'microsoft azure', 'gcp', 'google cloud',
            'docker', 'kubernetes', 'k8s', 'jenkins', 'gitlab ci', 'github actions', 'circleci',
            'terraform', 'ansible', 'puppet', 'chef', 'cloudformation', 'pulumi', 'helm',
            'linux', 'unix', 'bash', 'shell scripting', 'nginx', 'apache', 'load balancing',
            'ci/cd', 'continuous integration', 'continuous deployment', 'devops', 'sre',
            'monitoring', 'prometheus', 'grafana', 'datadog', 'splunk', 'elk', 'new relic'
        ],
        'analytics_bi': [
            'tableau', 'power bi', 'looker', 'qlik', 'metabase', 'superset', 'google analytics',
            'adobe analytics', 'mixpanel', 'amplitude', 'excel', 'advanced excel', 'pivot tables',
            'vlookup', 'xlookup', 'data visualization', 'dashboard', 'reporting', 'kpi', 'metrics',
            'google data studio', 'domo', 'sisense', 'thoughtspot', 'sas', 'spss', 'stata'
        ],
        
        # Design & Creative
        'design_tools': [
            'photoshop', 'adobe photoshop', 'illustrator', 'adobe illustrator', 'indesign',
            'figma', 'sketch', 'xd', 'adobe xd', 'canva', 'lightroom', 'after effects',
            'premiere pro', 'final cut pro', 'davinci resolve', 'blender', 'maya', '3ds max',
            'cinema 4d', 'zbrush', 'substance painter', 'procreate', 'coreldraw', 'invision'
        ],
        'design_skills': [
            'ui design', 'ux design', 'user interface', 'user experience', 'graphic design',
            'visual design', 'product design', 'web design', 'mobile design', 'responsive design',
            'typography', 'color theory', 'layout', 'wireframing', 'prototyping', 'mockups',
            'design thinking', 'design systems', 'branding', 'logo design', 'illustration',
            'motion graphics', 'animation', 'video editing', 'photo editing', 'print design'
        ],
        
        # Business & Finance
        'finance_skills': [
            'financial analysis', 'financial modeling', 'valuation', 'dcf', 'npv', 'irr',
            'budgeting', 'forecasting', 'variance analysis', 'p&l', 'balance sheet', 'cash flow',
            'financial statements', 'gaap', 'ifrs', 'audit', 'tax', 'compliance', 'sox',
            'treasury', 'risk management', 'credit analysis', 'investment analysis',
            'portfolio management', 'equity research', 'm&a', 'due diligence', 'cfa', 'cpa'
        ],
        'accounting_skills': [
            'bookkeeping', 'accounts payable', 'accounts receivable', 'general ledger',
            'journal entries', 'reconciliation', 'trial balance', 'depreciation', 'amortization',
            'accruals', 'prepaid expenses', 'quickbooks', 'sage', 'xero', 'tally', 'sap',
            'oracle financials', 'cost accounting', 'management accounting', 'tax returns',
            'payroll processing', 'invoicing', 'billing', 'collections', 'year end closing'
        ],
        'sales_skills': [
            'sales', 'selling', 'b2b sales', 'b2c sales', 'inside sales', 'field sales',
            'account management', 'territory management', 'pipeline management', 'lead generation',
            'prospecting', 'cold calling', 'closing', 'negotiation', 'quota achievement',
            'crm', 'salesforce', 'hubspot', 'zoho', 'pipedrive', 'sales forecasting',
            'client relationship', 'customer acquisition', 'upselling', 'cross-selling'
        ],
        'marketing_skills': [
            'digital marketing', 'content marketing', 'social media marketing', 'email marketing',
            'seo', 'sem', 'ppc', 'google ads', 'facebook ads', 'instagram ads', 'linkedin ads',
            'marketing automation', 'hubspot', 'marketo', 'mailchimp', 'brand management',
            'market research', 'competitive analysis', 'campaign management', 'lead nurturing',
            'conversion optimization', 'a/b testing', 'analytics', 'roi analysis'
        ],
        
        # HR & Administration
        'hr_skills': [
            'recruitment', 'talent acquisition', 'sourcing', 'screening', 'interviewing',
            'onboarding', 'offboarding', 'employee relations', 'performance management',
            'compensation', 'benefits administration', 'payroll', 'hris', 'workday', 'successfactors',
            'bamboohr', 'adp', 'training and development', 'learning management', 'succession planning',
            'employee engagement', 'retention', 'labor law', 'compliance', 'hr policies'
        ],
        
        # Healthcare
        'healthcare_skills': [
            'patient care', 'clinical skills', 'nursing', 'medical terminology', 'ehr',
            'epic', 'cerner', 'hipaa', 'patient assessment', 'vital signs', 'medication administration',
            'wound care', 'iv therapy', 'phlebotomy', 'cpr', 'bls', 'acls', 'first aid',
            'infection control', 'patient education', 'care planning', 'documentation',
            'medical coding', 'icd-10', 'cpt', 'medical billing', 'health insurance'
        ],
        
        # Education
        'education_skills': [
            'teaching', 'instruction', 'curriculum development', 'lesson planning',
            'classroom management', 'student assessment', 'grading', 'differentiated instruction',
            'educational technology', 'lms', 'canvas', 'blackboard', 'moodle', 'google classroom',
            'special education', 'iep', 'student engagement', 'parent communication',
            'instructional design', 'e-learning development', 'articulate', 'storyline'
        ],
        
        # Culinary & Hospitality
        'culinary_skills': [
            'cooking', 'food preparation', 'knife skills', 'menu planning', 'recipe development',
            'food safety', 'haccp', 'servsafe', 'kitchen management', 'inventory management',
            'cost control', 'portion control', 'plating', 'presentation', 'baking', 'pastry',
            'grilling', 'sauteing', 'catering', 'banquet', 'fine dining', 'fast casual',
            'food allergies', 'dietary restrictions', 'nutrition', 'sanitation'
        ],
        'hospitality_skills': [
            'customer service', 'guest relations', 'front desk', 'reservations', 'check-in',
            'check-out', 'concierge', 'hotel operations', 'housekeeping', 'event planning',
            'banquet management', 'food and beverage', 'pos systems', 'opera', 'micros',
            'upselling', 'complaint handling', 'guest satisfaction'
        ],
        
        # Legal
        'legal_skills': [
            'legal research', 'legal writing', 'contract drafting', 'contract review',
            'litigation', 'legal compliance', 'regulatory', 'due diligence', 'discovery',
            'pleadings', 'motions', 'depositions', 'case management', 'westlaw', 'lexisnexis',
            'corporate law', 'intellectual property', 'employment law', 'real estate law',
            'criminal law', 'civil litigation', 'mediation', 'arbitration', 'negotiations'
        ],
        
        # Engineering & Manufacturing
        'engineering_skills': [
            'mechanical design', 'electrical design', 'circuit design', 'pcb design',
            'cad', 'autocad', 'solidworks', 'catia', 'creo', 'inventor', 'ansys', 'matlab',
            'simulink', 'plc programming', 'scada', 'hmi', 'pid control', 'automation',
            'robotics', 'cnc', 'manufacturing', 'quality control', 'six sigma', 'lean',
            'kaizen', 'iso 9001', 'fmea', 'root cause analysis', 'gd&t', 'tolerance analysis'
        ],
        
        # Agriculture
        'agriculture_skills': [
            'crop management', 'soil management', 'irrigation', 'pest control', 'fertilization',
            'harvesting', 'planting', 'greenhouse management', 'organic farming', 'sustainable agriculture',
            'livestock management', 'dairy farming', 'poultry farming', 'aquaculture',
            'agricultural machinery', 'tractor operation', 'precision agriculture', 'gis',
            'crop rotation', 'integrated pest management', 'seed selection', 'yield optimization'
        ],
        
        # Soft Skills
        'soft_skills': [
            'leadership', 'management', 'communication', 'verbal communication', 'written communication',
            'presentation', 'public speaking', 'teamwork', 'collaboration', 'problem solving',
            'critical thinking', 'analytical thinking', 'decision making', 'time management',
            'project management', 'agile', 'scrum', 'kanban', 'strategic thinking', 'planning',
            'organization', 'attention to detail', 'multitasking', 'adaptability', 'flexibility',
            'creativity', 'innovation', 'negotiation', 'conflict resolution', 'customer service',
            'interpersonal skills', 'emotional intelligence', 'stakeholder management',
            'cross-functional collaboration', 'mentoring', 'coaching', 'training'
        ],
        
        # Project Management
        'project_management': [
            'project management', 'pmp', 'prince2', 'agile', 'scrum', 'kanban', 'waterfall',
            'jira', 'asana', 'trello', 'monday.com', 'ms project', 'smartsheet', 'basecamp',
            'sprint planning', 'backlog management', 'stakeholder management', 'risk management',
            'resource planning', 'budget management', 'scope management', 'timeline management',
            'gantt chart', 'milestone tracking', 'status reporting', 'change management'
        ]
    }
    
    # Experience level keywords: the fallback when neither a stated "N years of experience" nor
    # dated work ranges give a number. Checked in this order (senior first), whole words only,
    # in the first EXPERIENCE_KEYWORD_SCAN_CHARS characters (name, title, summary).
    EXPERIENCE_INDICATORS = {
        'Senior': ['senior', 'lead', 'principal', 'architect', 'manager', '6+ years', '7 years', '8 years', '10 years'],
        'Mid-Level': ['mid level', 'intermediate', '3 years', '4 years', '5 years'],
        'Junior': ['junior', 'associate', '1 year', '2 years', 'trainee'],
        'Fresher': ['fresher', 'fresh graduate', 'entry level', 'graduate', 'recent graduate', 'no experience'],
    }
    EXPERIENCE_KEYWORD_SCAN_CHARS = 500
    
    def __init__(self):
        self.nlp = None
        self._load_spacy_model()
    
    def _load_spacy_model(self):
        """Load spaCy model"""
        try:
            import spacy
            try:
                self.nlp = spacy.load('en_core_web_sm')
                logger.info("Loaded spaCy model: en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found. Downloading en_core_web_sm...")
                import subprocess
                import sys
                subprocess.run([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'], check=True)
                self.nlp = spacy.load('en_core_web_sm')
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
            self.nlp = None
    
    def analyze(self, text: str) -> AnalysisResult:
        """
        Perform complete CV analysis.
        
        Args:
            text: Extracted CV text
            
        Returns:
            AnalysisResult with all analysis data
        """
        result = AnalysisResult()
        
        if not text or len(text.strip()) < 50:
            result.weaknesses.append("CV text is too short or empty")
            return result
        
        text_lower = text.lower()
        
        # Step 1: Detect sections
        result.sections = self._detect_sections(text)
        
        # Step 2: Extract skills
        result.skills_found = self._extract_skills(text_lower)
        
        # Step 3: Extract named entities
        result.entities = self._extract_entities(text)
        
        # Step 4: Detect career field
        result.career_field = self._detect_career_field(text_lower, result.skills_found)
        
        # Step 5: Detect experience level
        result.experience_level = self._detect_experience_level(text_lower, result.sections)
        
        # Step 6: Calculate scores
        scores = self._calculate_scores(text, result)
        result.experience_score = scores['experience']
        result.skills_score = scores['skills']
        result.structure_score = scores['structure']
        result.career_score = scores['career']
        result.readability_score = scores['readability']
        result.overall_score = scores['overall']
        
        # Step 7: Generate analysis
        result.strengths = self._identify_strengths(result)
        result.weaknesses = self._identify_weaknesses(result)
        result.recommendations = self._generate_recommendations(result)
        result.youtube_suggestions = self._generate_youtube_suggestions(result)
        
        return result
    
    def _detect_sections(self, text: str) -> Dict[str, SectionResult]:
        """Detect CV sections using pattern matching and NLP"""
        sections = {}
        text_lower = text.lower()
        lines = text.split('\n')
        
        for section_name, patterns in self.SECTION_PATTERNS.items():
            section_result = SectionResult()
            
            # Try to find section header
            for pattern in patterns:
                regex = re.compile(
                    rf'^[\s•\-\*]*({pattern})[\s:]*$',
                    re.IGNORECASE | re.MULTILINE
                )
                match = regex.search(text)
                
                if match:
                    section_result.detected = True
                    section_result.start_pos = match.start()
                    
                    # Extract section content (until next section or end)
                    content = self._extract_section_content(text, match.end())
                    section_result.content = content
                    
                    # Score section quality
                    section_result.quality_score = self._score_section_quality(
                        section_name, content
                    )
                    section_result.explanation = self._explain_section_quality(
                        section_name, section_result.quality_score, content
                    )
                    break
            
            # If not found by header, try content-based detection
            if not section_result.detected:
                content, confidence = self._detect_section_by_content(
                    text_lower, section_name
                )
                if confidence > 0.5:
                    section_result.detected = True
                    section_result.content = content
                    section_result.quality_score = confidence * 10
                    section_result.explanation = f"Detected by content analysis (confidence: {confidence:.0%})"
            
            sections[section_name] = section_result
        
        return sections
    
    def _extract_section_content(self, text: str, start_pos: int, max_chars: int = 2000) -> str:
        """Extract content of a section until next section header"""
        # Find all section headers
        section_starts = []
        for patterns in self.SECTION_PATTERNS.values():
            for pattern in patterns:
                regex = re.compile(
                    rf'^[\s•\-\*]*({pattern})[\s:]*$',
                    re.IGNORECASE | re.MULTILINE
                )
                for match in regex.finditer(text):
                    section_starts.append(match.start())
        
        section_starts.sort()
        
        # Find end position
        end_pos = len(text)
        for pos in section_starts:
            if pos > start_pos:
                end_pos = pos
                break
        
        content = text[start_pos:min(end_pos, start_pos + max_chars)].strip()
        return content
    
    def _detect_section_by_content(self, text: str, section_name: str) -> Tuple[str, float]:
        """Detect section by analyzing content patterns"""
        confidence = 0.0
        content = ""
        
        if section_name == 'education':
            # Look for education indicators
            edu_patterns = [
                r'(?:bachelor|master|phd|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?)\s*(?:of|in)?\s*\w+',
                r'(?:university|college|institute|school)\s+of\s+\w+',
                r'(?:gpa|cgpa)[\s:]*[\d\.]+',
                r'\d{4}\s*-\s*\d{4}'  # Year ranges
            ]
            matches = sum(1 for p in edu_patterns if re.search(p, text, re.IGNORECASE))
            confidence = min(matches / 3, 1.0)
            
        elif section_name == 'work_experience':
            # Look for job indicators
            work_patterns = [
                r'(?:worked|working)\s+(?:as|at|for)',
                r'(?:responsibilities|duties)\s*:',
                r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}',
                r'(?:present|current|ongoing)'
            ]
            matches = sum(1 for p in work_patterns if re.search(p, text, re.IGNORECASE))
            confidence = min(matches / 3, 1.0)
            
        elif section_name == 'skills':
            # Count skill keywords
            skill_count = len(self._extract_skills(text))
            confidence = min(skill_count / 5, 1.0)
        
        return content, confidence
    
    def _score_section_quality(self, section_name: str, content: str) -> float:
        """Score the quality of a section's content (0-10)"""
        if not content:
            return 0.0
        
        score = 5.0  # Base score
        word_count = len(content.split())
        
        # Adjust based on content length
        if word_count < 10:
            score -= 2
        elif word_count < 30:
            score -= 1
        elif word_count > 100:
            score += 1
        elif word_count > 200:
            score += 2
        
        # Section-specific scoring
        if section_name == 'professional_summary':
            # Good summaries are 50-150 words
            if 50 <= word_count <= 150:
                score += 2
            # Should mention key skills or goals
            if re.search(r'(?:experienced|skilled|passionate|seeking|goal)', content, re.IGNORECASE):
                score += 1
                
        elif section_name == 'education':
            # Should have degree and institution
            if re.search(r'(?:bachelor|master|phd|degree|diploma)', content, re.IGNORECASE):
                score += 1
            if re.search(r'(?:university|college|institute)', content, re.IGNORECASE):
                score += 1
            if re.search(r'(?:gpa|cgpa|grade)', content, re.IGNORECASE):
                score += 0.5
                
        elif section_name == 'work_experience':
            # Should have company, role, and dates
            if re.search(r'\d{4}', content):  # Has dates
                score += 1
            if re.search(r'(?:developed|managed|led|created|implemented)', content, re.IGNORECASE):
                score += 1
                
        elif section_name == 'skills':
            skill_count = len(self._extract_skills(content.lower()))
            score += min(skill_count / 3, 3)
            
        elif section_name == 'projects':
            # Should have project names and descriptions
            if re.search(r'(?:developed|built|created|designed)', content, re.IGNORECASE):
                score += 1
            if re.search(r'(?:using|with|technologies)', content, re.IGNORECASE):
                score += 1
        
        return max(0, min(10, score))
    
    def _explain_section_quality(self, section_name: str, score: float, content: str) -> str:
        """Generate explanation for section quality score"""
        if score >= 8:
            return f"Excellent {section_name.replace('_', ' ')} section with comprehensive details"
        elif score >= 6:
            return f"Good {section_name.replace('_', ' ')} section with adequate information"
        elif score >= 4:
            return f"Average {section_name.replace('_', ' ')} section - could use more details"
        elif score >= 2:
            return f"Weak {section_name.replace('_', ' ')} section - needs significant improvement"
        else:
            return f"Missing or very weak {section_name.replace('_', ' ')} section"
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from CV text"""
        found_skills = []
        text_lower = text.lower()
        
        for category, skills in self.SKILLS_DATABASE.items():
            for skill in skills:
                # Create pattern that matches whole words
                pattern = rf'\b{re.escape(skill)}\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in found_skills:
            if skill not in seen:
                seen.add(skill)
                unique_skills.append(skill)
        
        return unique_skills
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities using spaCy"""
        entities = {
            'names': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'emails': [],
            'phones': []
        }
        
        # Extract emails and phones with regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        
        entities['emails'] = re.findall(email_pattern, text)
        entities['phones'] = re.findall(phone_pattern, text)
        
        # Use spaCy for NER
        if self.nlp:
            try:
                doc = self.nlp(text[:100000])  # Limit text length
                
                for ent in doc.ents:
                    if ent.label_ == 'PERSON':
                        entities['names'].append(ent.text)
                    elif ent.label_ in ['ORG', 'COMPANY']:
                        entities['organizations'].append(ent.text)
                    elif ent.label_ in ['GPE', 'LOC']:
                        entities['locations'].append(ent.text)
                    elif ent.label_ == 'DATE':
                        entities['dates'].append(ent.text)
                
                # Deduplicate
                for key in entities:
                    entities[key] = list(set(entities[key]))
                    
            except Exception as e:
                logger.warning(f"spaCy NER failed: {e}")
        
        return entities
    
    def _detect_career_field(self, text: str, skills: List[str]) -> str:
        """
        Detect the most likely career field using weighted keyword matching.
        Uses job titles, primary keywords, and secondary keywords with different weights.
        """
        field_scores = {}
        text_lower = text.lower()
        skills_lower = set(s.lower() for s in skills)
        
        # Extract first ~500 chars which usually contains job title/objective
        header_text = text_lower[:500]
        
        for field, field_data in self.CAREER_FIELDS.items():
            score = 0
            matches = {'job_titles': [], 'primary': [], 'secondary': []}
            
            # Check job titles (highest weight - 10 points each)
            for title in field_data.get('job_titles', []):
                title_lower = title.lower()
                if title_lower in text_lower:
                    score += 10
                    matches['job_titles'].append(title_lower)
                    # Extra bonus if job title appears in header/summary
                    if title_lower in header_text:
                        score += 5
            
            # Check primary keywords (high weight - 4 points each)
            for keyword in field_data.get('primary', []):
                keyword_lower = keyword.lower()
                if keyword_lower in text_lower:
                    word_count = len(keyword_lower.split())
                    if word_count >= 2:
                        score += 6  # Multi-word phrases are more specific
                    else:
                        score += 4
                    matches['primary'].append(keyword_lower)
            
            # Check secondary keywords (medium weight - 2 points each)
            for keyword in field_data.get('secondary', []):
                keyword_lower = keyword.lower()
                if keyword_lower in text_lower:
                    score += 2
                    matches['secondary'].append(keyword_lower)
            
            # Bonus for skill matches
            all_field_keywords = set()
            for key in ['job_titles', 'primary', 'secondary']:
                all_field_keywords.update(k.lower() for k in field_data.get(key, []))
            
            for skill in skills_lower:
                if skill in all_field_keywords:
                    score += 3
            
            # Frequency bonus for primary keywords (indicates strong focus)
            for keyword in matches['primary']:
                count = text_lower.count(keyword)
                if count > 2:
                    score += min((count - 2) * 2, 8)  # Cap at 8 bonus points
            
            # Diversity bonus - having matches in multiple categories is stronger signal
            categories_matched = sum(1 for k in matches.values() if k)
            if categories_matched >= 2:
                score += 5
            if categories_matched == 3:
                score += 5  # Additional bonus for all three categories
            
            field_scores[field] = {
                'score': score,
                'matches': matches
            }
        
        # Find the best match
        if field_scores:
            # Sort by score descending
            sorted_fields = sorted(field_scores.items(), key=lambda x: x[1]['score'], reverse=True)
            
            if sorted_fields[0][1]['score'] > 0:
                best_field = sorted_fields[0][0]
                best_score = sorted_fields[0][1]['score']
                best_matches = sorted_fields[0][1]['matches']
                
                # Log for debugging
                logger.debug(f"Career detection - Best: {best_field} (score: {best_score})")
                logger.debug(f"Matches: {best_matches}")
                
                # Check if Data Science subfields should be grouped
                data_science_fields = ['Data Science', 'Machine Learning', 'Artificial Intelligence', 
                                       'NLP Engineer', 'Computer Vision', 'Data Analytics', 'Data Engineering']
                
                # If best match is a Data Science subfield, check if generic Data Science is better
                if best_field in data_science_fields and best_field != 'Data Science':
                    ds_score = field_scores.get('Data Science', {}).get('score', 0)
                    # If the specific subfield doesn't have job title matches but DS does, prefer DS
                    if not best_matches['job_titles'] and ds_score > best_score * 0.7:
                        if field_scores['Data Science']['matches']['job_titles']:
                            return 'Data Science'
                
                # Avoid false positives for IT
                # If IT wins but another specific field has strong job title matches, prefer that
                if best_field == 'Information Technology' and len(sorted_fields) > 1:
                    for field, data in sorted_fields[1:5]:  # Check top 5
                        if data['matches']['job_titles'] and data['score'] > best_score * 0.6:
                            # This field has explicit job title matches
                            if field not in ['Information Technology', 'Engineering']:
                                logger.debug(f"Switching from IT to {field} due to job title match")
                                return field
                
                return best_field
        
        return "General"
    
    def _detect_experience_level(self, text: str, sections: Dict[str, SectionResult]) -> str:
        """Detect experience level. Returns one of Fresher, Junior, Mid-Level, Senior, Unknown.

        Signals, first one that gives an answer wins:
        1. Stated years ("8+ years of experience"), the largest one in the CV.
        2. Years covered by dated ranges in the work section ("2019 - Present").
        3. Whole-word keywords near the top of the CV, senior first.
        4. A work or education section with nothing dated: Fresher.
        """
        text = text.lower()

        stated = [int(n) for n in re.findall(
            r'\b(\d{1,2})\s*\+?\s*years?\s+(?:of\s+)?(?:[a-z-]+\s+){0,2}?experience\b', text)]
        if stated:
            return self._level_from_years(max(stated))

        work_section = sections.get('work_experience')
        if work_section and work_section.detected:
            years = self._years_from_date_ranges(work_section.content.lower())
            if years > 0:
                return self._level_from_years(years)

        head = text[:self.EXPERIENCE_KEYWORD_SCAN_CHARS]
        for level, keywords in self.EXPERIENCE_INDICATORS.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword).replace(r'\ ', r'[\s-]+') + r'(?!\w)'
                if re.search(pattern, head):
                    return level

        edu_section = sections.get('education')
        if (work_section and work_section.detected) or (edu_section and edu_section.detected):
            return "Fresher"

        return "Unknown"

    @staticmethod
    def _level_from_years(years: int) -> str:
        if years < 1:
            return "Fresher"
        if years <= 2:
            return "Junior"
        if years <= 5:
            return "Mid-Level"
        return "Senior"

    @staticmethod
    def _years_from_date_ranges(text: str) -> int:
        """Years covered by 'YYYY - YYYY|present|current|now' ranges; overlapping ranges count once."""
        current_year = date.today().year
        spans = []
        for start, end in re.findall(
                r'\b((?:19|20)\d{2})\s*(?:-|–|—|to)\s*((?:19|20)\d{2}|present|current|now)\b', text):
            start = int(start)
            end = current_year if not end[0].isdigit() else int(end)
            end = min(end, current_year)
            if end > start:
                spans.append((start, end))

        total, covered_to = 0, None
        for start, end in sorted(spans):
            if covered_to is not None and start < covered_to:
                start = covered_to
            if end > start:
                total += end - start
                covered_to = end
        return total
    
    def _calculate_scores(self, text: str, result: AnalysisResult) -> Dict[str, float]:
        """Calculate all scores for the CV"""
        scores = {
            'experience': 0.0,
            'skills': 0.0,
            'structure': 0.0,
            'career': 0.0,
            'readability': 0.0,
            'overall': 0.0
        }
        
        # Experience score (25%)
        exp_map = {'Fresher': 40, 'Junior': 60, 'Mid-Level': 80, 'Senior': 100, 'Unknown': 30}
        scores['experience'] = exp_map.get(result.experience_level, 30)
        
        # Add points for work experience section quality
        work_section = result.sections.get('work_experience')
        if work_section and work_section.detected:
            scores['experience'] = min(100, scores['experience'] + work_section.quality_score * 3)
        
        # Skills score (25%)
        skill_count = len(result.skills_found)
        scores['skills'] = min(100, skill_count * 8)  # Each skill adds 8 points
        
        # Add bonus for diverse skills
        categories_found = set()
        for skill in result.skills_found:
            for category, skills in self.SKILLS_DATABASE.items():
                if skill in skills:
                    categories_found.add(category)
                    break
        scores['skills'] = min(100, scores['skills'] + len(categories_found) * 5)
        
        # Structure score (20%)
        sections_detected = sum(1 for s in result.sections.values() if s.detected)
        scores['structure'] = min(100, sections_detected * 12)  # 9 sections max
        
        # Add quality bonus
        avg_quality = sum(s.quality_score for s in result.sections.values() if s.detected) / max(sections_detected, 1)
        scores['structure'] = min(100, scores['structure'] + avg_quality * 2)
        
        # Career alignment score (15%)
        field_info = self.CAREER_FIELDS.get(result.career_field)
        if field_info:
            # 70 for a detected field, +5 per extracted skill listed for that field
            field_keywords = set(field_info['job_titles'] + field_info['primary'] + field_info['secondary'])
            matching_skills = sum(1 for s in result.skills_found if s.lower() in field_keywords)
            scores['career'] = min(100, 70 + matching_skills * 5)
        else:
            scores['career'] = 50  # "General": no field detected
        
        # Readability score (15%)
        word_count = len(text.split())
        sentence_count = len(re.findall(r'[.!?]+', text))
        
        # Ideal CV is 300-800 words
        if 300 <= word_count <= 800:
            scores['readability'] = 80
        elif 200 <= word_count <= 1000:
            scores['readability'] = 60
        elif word_count < 200:
            scores['readability'] = 40
        else:
            scores['readability'] = 50
        
        # Check for bullet points (good for readability)
        bullet_count = len(re.findall(r'^[\s]*[•\-\*]', text, re.MULTILINE))
        if bullet_count >= 5:
            scores['readability'] = min(100, scores['readability'] + 15)
        
        # Calculate overall score with weights
        weights = {
            'experience': 0.25,
            'skills': 0.25,
            'structure': 0.20,
            'career': 0.15,
            'readability': 0.15
        }
        
        scores['overall'] = sum(scores[k] * weights[k] for k in weights)
        
        return scores
    
    def _identify_strengths(self, result: AnalysisResult) -> List[str]:
        """Identify CV strengths"""
        strengths = []
        
        if len(result.skills_found) >= 10:
            strengths.append("Strong technical skill set")
        
        if result.experience_level in ['Mid-Level', 'Senior']:
            strengths.append(f"{result.experience_level} professional experience")
        
        sections_detected = sum(1 for s in result.sections.values() if s.detected)
        if sections_detected >= 7:
            strengths.append("Well-structured CV with comprehensive sections")
        
        # Check for high quality sections
        for name, section in result.sections.items():
            if section.detected and section.quality_score >= 8:
                strengths.append(f"Excellent {name.replace('_', ' ')} section")
        
        if result.career_field != "General":
            strengths.append(f"Clear career focus in {result.career_field}")
        
        if result.overall_score >= 80:
            strengths.append("Overall excellent CV quality")
        
        return strengths[:5]  # Limit to 5 strengths
    
    def _identify_weaknesses(self, result: AnalysisResult) -> List[str]:
        """Identify CV weaknesses"""
        weaknesses = []
        
        # Missing sections
        missing_sections = [
            name.replace('_', ' ') for name, section in result.sections.items()
            if not section.detected and name in ['professional_summary', 'education', 'work_experience', 'skills']
        ]
        for section in missing_sections:
            weaknesses.append(f"Missing {section} section")
        
        if len(result.skills_found) < 5:
            weaknesses.append("Limited skills listed")
        
        if result.experience_level == 'Fresher':
            weaknesses.append("Limited or no work experience")
        
        # Check for weak sections
        for name, section in result.sections.items():
            if section.detected and section.quality_score < 4:
                weaknesses.append(f"Weak {name.replace('_', ' ')} section needs improvement")
        
        if result.overall_score < 50:
            weaknesses.append("Overall CV needs significant improvement")
        
        return weaknesses[:5]  # Limit to 5 weaknesses
    
    def _generate_recommendations(self, result: AnalysisResult) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Missing section recommendations
        if not result.sections.get('professional_summary', SectionResult()).detected:
            recommendations.append("Add a professional summary highlighting your key qualifications and career goals")
        
        if not result.sections.get('skills', SectionResult()).detected:
            recommendations.append("Create a dedicated skills section with your technical and soft skills")
        
        if not result.sections.get('projects', SectionResult()).detected:
            recommendations.append("Add a projects section to showcase your practical experience")
        
        # Skill recommendations based on career field
        if result.career_field == "Software Development":
            if 'git' not in result.skills_found:
                recommendations.append("Consider adding version control skills (Git/GitHub)")
            if not any(s in result.skills_found for s in ['docker', 'kubernetes']):
                recommendations.append("Container technologies (Docker, Kubernetes) are in high demand")
        
        elif result.career_field == "Data Science":
            if 'python' not in result.skills_found:
                recommendations.append("Python is essential for Data Science - highlight your Python skills")
            if not any(s in result.skills_found for s in ['machine learning', 'deep learning']):
                recommendations.append("Add ML/DL frameworks you've worked with")
        
        # General recommendations
        if len(result.skills_found) < 10:
            recommendations.append("Consider adding more relevant technical skills")
        
        if result.experience_level == 'Fresher':
            recommendations.append("Highlight academic projects, internships, or personal projects to compensate for limited experience")
        
        recommendations.append("Use action verbs to describe achievements (developed, implemented, led, improved)")
        recommendations.append("Quantify achievements where possible (e.g., 'Improved performance by 30%')")
        
        return recommendations[:7]  # Limit to 7 recommendations
    
    def _generate_youtube_suggestions(self, result: AnalysisResult) -> List[Dict[str, str]]:
        """Generate YouTube learning suggestions based on weak areas and career field"""
        suggestions = []
        career = result.career_field
        
        # Career-specific suggestions
        career_suggestions = {
            # Data Science & AI Fields
            'Data Science': [
                {'title': 'Data Science Full Course', 'query': 'data science complete course 2024', 'video_id': '6_n30xS-Z2k', 'reason': 'Comprehensive data science training'},
                {'title': 'Python for Data Science', 'query': 'python data science tutorial pandas numpy', 'video_id': 'rfscVS0vtbw', 'reason': 'Essential Python skills for data science'},
                {'title': 'Statistics for Data Science', 'query': 'statistics for data science beginners', 'video_id': 'Vfo5le26IhY', 'reason': 'Strong statistics foundation'},
            ],
            'Machine Learning': [
                {'title': 'Machine Learning Course', 'query': 'machine learning full course andrew ng', 'video_id': 'PplB7zS_a8M', 'reason': 'Industry-standard ML education'},
                {'title': 'Deep Learning Specialization', 'query': 'deep learning neural networks course', 'video_id': '7ed442Uuyj0', 'reason': 'Master neural networks'},
                {'title': 'MLOps & Deployment', 'query': 'mlops machine learning deployment course', 'video_id': 'XIdIitv8TfQ', 'reason': 'Production ML skills'},
            ],
            'Artificial Intelligence': [
                {'title': 'AI Fundamentals Course', 'query': 'artificial intelligence course beginners', 'video_id': 'tS17Xf9Lq1o', 'reason': 'Core AI concepts'},
                {'title': 'LLM and Generative AI', 'query': 'large language models gpt course', 'video_id': 'm7ndFpIet-Q', 'reason': 'Latest AI technologies'},
            ],
            'NLP Engineer': [
                {'title': 'NLP with Python', 'query': 'natural language processing python course', 'video_id': 'CMrHM8a3hqw', 'reason': 'Master text processing'},
                {'title': 'Transformers & BERT', 'query': 'transformers bert nlp tutorial', 'video_id': 'XfpMkf4rD6E', 'reason': 'Modern NLP architectures'},
            ],
            'Computer Vision': [
                {'title': 'Computer Vision Course', 'query': 'computer vision opencv python course', 'video_id': 'oXlwWbU8l2o', 'reason': 'Image processing fundamentals'},
                {'title': 'Deep Learning for CV', 'query': 'convolutional neural networks course', 'video_id': 'YRhxdVk_sIs', 'reason': 'CNN for vision tasks'},
            ],
            'Data Analytics': [
                {'title': 'Data Analytics Bootcamp', 'query': 'data analytics course excel sql tableau', 'video_id': 'qS_S8Oq_zXk', 'reason': 'Core analytics skills'},
                {'title': 'SQL for Data Analysis', 'query': 'sql for data analysis complete course', 'video_id': 'HXV3zeQKqGY', 'reason': 'Essential data querying'},
            ],
            'Data Engineering': [
                {'title': 'Data Engineering Course', 'query': 'data engineering pipeline course', 'video_id': 'qS_S8Oq_zXk', 'reason': 'Build robust data pipelines'},
                {'title': 'Apache Spark Tutorial', 'query': 'apache spark pyspark course', 'video_id': '_C8kWso4ne4', 'reason': 'Big data processing'},
            ],
            'Cybersecurity': [
                {'title': 'Cybersecurity Fundamentals', 'query': 'cybersecurity course beginners', 'video_id': 'nzj7u9S_X8c', 'reason': 'Security essentials'},
                {'title': 'Ethical Hacking Course', 'query': 'ethical hacking penetration testing course', 'video_id': '3Kq1MIfTWCE', 'reason': 'Offensive security skills'},
            ],
            
            # Other Fields
            'Accountant': [
                {'title': 'Accounting Fundamentals Course', 'query': 'accounting basics tutorial beginners', 'video_id': 'yYX4bvQSqbo', 'reason': 'Master core accounting principles'},
                {'title': 'QuickBooks Tutorial', 'query': 'quickbooks tutorial full course', 'video_id': '197472099', 'reason': 'Learn essential accounting software'},
            ],
            'Advocate': [
                {'title': 'Legal Research Skills', 'query': 'legal research methods tutorial', 'video_id': 'MAtE0S8rRps', 'reason': 'Improve legal research capabilities'},
            ],
            'Agriculture': [
                {'title': 'Modern Farming Techniques', 'query': 'modern agriculture techniques course', 'video_id': 'vCUM0tX0vWc', 'reason': 'Stay updated with agricultural innovations'},
            ],
            'Apparel': [
                {'title': 'Fashion Design Fundamentals', 'query': 'fashion design course beginners', 'video_id': 'f7fAn_0C0p8', 'reason': 'Build core fashion design skills'},
            ],
            'Arts': [
                {'title': 'Digital Art Masterclass', 'query': 'digital art tutorial beginners', 'video_id': 'uS0M0LCH-7o', 'reason': 'Expand your artistic digital skills'},
            ],
            'Designer': [
                {'title': 'UI/UX Design Bootcamp', 'query': 'ui ux design course complete', 'video_id': 'p98uV7S3XUA', 'reason': 'Master modern design principles'},
                {'title': 'Figma Masterclass', 'query': 'figma tutorial complete course', 'video_id': 'Gu17A3Lp_vU', 'reason': 'Industry-standard design tool'},
            ],
            'Digital Media': [
                {'title': 'Video Editing Masterclass', 'query': 'video editing premiere pro tutorial', 'video_id': 'Hls3Tp7JS8E', 'reason': 'Create professional video content'},
            ],
            'Information Technology': [
                {'title': 'Full Stack Development Course', 'query': 'full stack web development course 2024', 'video_id': 'zJSY8tYvK2M', 'reason': 'Comprehensive tech skills'},
                {'title': 'Cloud Computing Fundamentals', 'query': 'aws azure cloud computing beginners', 'video_id': 'SOTamWNgDKc', 'reason': 'Cloud is essential for IT'},
            ],
            'HR': [
                {'title': 'HR Management Course', 'query': 'human resources management course', 'video_id': 'jLd7qG8X0_c', 'reason': 'Master HR fundamentals'},
            ],
            'Teacher': [
                {'title': 'Teaching Methods Course', 'query': 'effective teaching methods course', 'video_id': 'pje_Y0h9b_4', 'reason': 'Enhance teaching effectiveness'},
            ],
        }
        
        # Add career-specific suggestions
        if career in career_suggestions:
            suggestions.extend(career_suggestions[career][:2])  # Add top 2 for the career
        
        # Add based on missing skills
        if len(result.skills_found) < 5:
            suggestions.append({
                'title': f'Top Skills for {career} in 2024',
                'query': f'top skills {career.lower()} career 2024',
                'video_id': '6_n30xS-Z2k', # General educational video
                'reason': 'Expand your professional skill set'
            })
        
        # General suggestions
        suggestions.append({
            'title': f'How to Write a {career} CV/Resume',
            'query': f'{career.lower()} resume cv writing tips',
            'video_id': 'XvK1a272z_A',
            'reason': 'Improve your CV presentation for your field'
        })
        
        if result.experience_level == 'Fresher':
            suggestions.append({
                'title': f'Entry Level {career} Career Guide',
                'query': f'entry level {career.lower()} career tips',
                'video_id': '8zOCMvS-I70',
                'reason': 'Guide for starting your career'
            })
        
        suggestions.append({
            'title': f'{career} Interview Preparation',
            'query': f'{career.lower()} interview questions answers',
            'video_id': '7_0S_o1vEIk',
            'reason': 'Prepare for job interviews in your field'
        })
        
        return suggestions[:5]  # Limit to 5 suggestions


# Singleton instance
nlp_analyzer = NLPAnalyzer()
