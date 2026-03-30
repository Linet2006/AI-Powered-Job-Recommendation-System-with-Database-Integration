"""
dataset.py — Custom Job Dataset
================================
Contains 40+ real-world job roles across multiple domains.
Each job has a title, required skills, and a short description.

WHY a custom dataset?
  → Full control over data quality
  → No licensing issues
  → Covers diverse domains for better recommendation variety
"""

JOBS_DATA = [
    # ─── DATA SCIENCE & ANALYTICS ───────────────────────────────────────────
    {
        "job_title": "Data Scientist",
        "skills_required": "Python Machine Learning Statistics Pandas NumPy Scikit-learn Data Visualization SQL TensorFlow",
        "description": "Analyze complex datasets to extract insights, build predictive models, and support data-driven decisions."
    },
    {
        "job_title": "Data Analyst",
        "skills_required": "SQL Excel Python Pandas Data Visualization Tableau Power BI Statistics Reporting",
        "description": "Interpret data, generate reports, and create dashboards to support business decision-making."
    },
    {
        "job_title": "Business Intelligence Analyst",
        "skills_required": "SQL Power BI Tableau Excel Data Warehousing ETL Reporting KPI Dashboard",
        "description": "Design and maintain BI dashboards, perform trend analysis, and communicate findings to stakeholders."
    },
    {
        "job_title": "Data Engineer",
        "skills_required": "Python SQL Spark Kafka ETL Pipeline Airflow AWS Data Warehousing PostgreSQL Hadoop",
        "description": "Build and maintain data pipelines, warehouses, and infrastructure to make data accessible for analysis."
    },
    {
        "job_title": "Statistician",
        "skills_required": "Statistics R Python Hypothesis Testing Regression A/B Testing Data Analysis SPSS SAS",
        "description": "Apply statistical methods to collect, analyze, and interpret data for research and business use."
    },

    # ─── MACHINE LEARNING & AI ───────────────────────────────────────────────
    {
        "job_title": "Machine Learning Engineer",
        "skills_required": "Python Machine Learning TensorFlow PyTorch Scikit-learn MLOps Docker Kubernetes REST API",
        "description": "Design, build, and deploy scalable ML models into production environments."
    },
    {
        "job_title": "Deep Learning Engineer",
        "skills_required": "Python Deep Learning TensorFlow PyTorch CNN RNN LSTM GPU CUDA Neural Networks",
        "description": "Develop neural network architectures for computer vision, NLP, and other AI tasks."
    },
    {
        "job_title": "NLP Engineer",
        "skills_required": "Python NLP NLTK SpaCy Transformers BERT Hugging Face Text Classification Sentiment Analysis",
        "description": "Build natural language processing systems for text analysis, chatbots, and language understanding."
    },
    {
        "job_title": "Computer Vision Engineer",
        "skills_required": "Python OpenCV Deep Learning CNN Object Detection Image Segmentation TensorFlow PyTorch YOLO",
        "description": "Develop algorithms for image/video processing, recognition, and visual perception tasks."
    },
    {
        "job_title": "AI Research Scientist",
        "skills_required": "Machine Learning Deep Learning Python Research Mathematics Statistics PyTorch Reinforcement Learning",
        "description": "Conduct cutting-edge research to advance artificial intelligence methodologies and applications."
    },
    {
        "job_title": "MLOps Engineer",
        "skills_required": "Python MLOps Docker Kubernetes CI/CD MLflow Model Deployment AWS GCP Monitoring",
        "description": "Bridge ML and DevOps by automating model training, deployment, and monitoring pipelines."
    },
    {
        "job_title": "Reinforcement Learning Engineer",
        "skills_required": "Python Reinforcement Learning Deep Learning PyTorch OpenAI Gym Q-Learning Policy Gradient",
        "description": "Build agents that learn optimal behaviors through interaction with simulated or real environments."
    },

    # ─── WEB DEVELOPMENT ────────────────────────────────────────────────────
    {
        "job_title": "Frontend Developer",
        "skills_required": "HTML CSS JavaScript React Vue.js TypeScript Responsive Design REST API Git",
        "description": "Build responsive and interactive web interfaces using modern JavaScript frameworks."
    },
    {
        "job_title": "Backend Developer",
        "skills_required": "Python Node.js Django Flask REST API SQL PostgreSQL Docker Authentication JWT",
        "description": "Develop server-side logic, APIs, and database integrations for web applications."
    },
    {
        "job_title": "Full Stack Developer",
        "skills_required": "HTML CSS JavaScript React Node.js Python SQL REST API Git Docker AWS",
        "description": "Design and implement both frontend and backend components of web applications."
    },
    {
        "job_title": "React Developer",
        "skills_required": "React JavaScript TypeScript Redux HTML CSS REST API Git Webpack Testing",
        "description": "Build dynamic single-page applications using React and modern JavaScript ecosystem tools."
    },
    {
        "job_title": "Django Developer",
        "skills_required": "Python Django REST API SQL PostgreSQL ORM Authentication Testing Docker Celery",
        "description": "Develop robust web applications using the Django framework and Python ecosystem."
    },
    {
        "job_title": "Node.js Developer",
        "skills_required": "Node.js JavaScript Express.js REST API MongoDB SQL Authentication Docker Git",
        "description": "Build scalable server-side applications and APIs using Node.js and JavaScript."
    },

    # ─── CLOUD & DEVOPS ──────────────────────────────────────────────────────
    {
        "job_title": "Cloud Engineer",
        "skills_required": "AWS Azure GCP Docker Kubernetes Terraform CI/CD Linux Networking Security",
        "description": "Design, deploy, and manage cloud infrastructure and services for scalable applications."
    },
    {
        "job_title": "DevOps Engineer",
        "skills_required": "Docker Kubernetes CI/CD Jenkins Git Linux AWS Terraform Ansible Monitoring Shell Scripting",
        "description": "Automate software delivery pipelines and manage infrastructure to enable rapid deployments."
    },
    {
        "job_title": "Site Reliability Engineer",
        "skills_required": "Linux Python Go Kubernetes Docker Monitoring Alerting SLO Incident Management AWS",
        "description": "Ensure high availability and reliability of production systems through automation and monitoring."
    },
    {
        "job_title": "AWS Solutions Architect",
        "skills_required": "AWS EC2 S3 Lambda RDS VPC IAM CloudFormation Networking Security Cost Optimization",
        "description": "Design and implement scalable, cost-effective cloud solutions on Amazon Web Services."
    },

    # ─── CYBERSECURITY ───────────────────────────────────────────────────────
    {
        "job_title": "Cybersecurity Analyst",
        "skills_required": "Network Security Firewalls SIEM Incident Response Vulnerability Assessment Python Linux",
        "description": "Monitor systems for threats, analyze security incidents, and implement protective measures."
    },
    {
        "job_title": "Penetration Tester",
        "skills_required": "Ethical Hacking Kali Linux Metasploit Burp Suite Python Network Security OWASP Cryptography",
        "description": "Simulate cyberattacks to identify vulnerabilities in systems, networks, and applications."
    },
    {
        "job_title": "Security Engineer",
        "skills_required": "Cryptography Network Security Python Cloud Security DevSecOps Authentication Authorization SIEM",
        "description": "Build and maintain secure systems, implement security controls, and develop security tools."
    },

    # ─── MOBILE DEVELOPMENT ──────────────────────────────────────────────────
    {
        "job_title": "Android Developer",
        "skills_required": "Java Kotlin Android Studio REST API Firebase SQLite UI/UX Git MVP MVVM",
        "description": "Build native Android applications with clean architecture and excellent user experience."
    },
    {
        "job_title": "iOS Developer",
        "skills_required": "Swift Objective-C Xcode iOS REST API Core Data UIKit SwiftUI Git",
        "description": "Develop native iOS applications for iPhone and iPad with high performance and quality."
    },
    {
        "job_title": "Flutter Developer",
        "skills_required": "Flutter Dart Mobile Development REST API Firebase State Management Git UI/UX",
        "description": "Build cross-platform mobile applications for iOS and Android using Flutter framework."
    },

    # ─── DATABASE & BACKEND SYSTEMS ──────────────────────────────────────────
    {
        "job_title": "Database Administrator",
        "skills_required": "SQL PostgreSQL MySQL Oracle Database Tuning Backup Recovery Replication Security Indexing",
        "description": "Manage, optimize, and secure database systems to ensure performance and data integrity."
    },
    {
        "job_title": "Backend API Developer",
        "skills_required": "Python REST API FastAPI Flask Node.js Authentication SQL NoSQL Docker Testing",
        "description": "Design and develop high-performance REST APIs for web and mobile applications."
    },

    # ─── PRODUCT & DESIGN ────────────────────────────────────────────────────
    {
        "job_title": "Product Manager",
        "skills_required": "Product Strategy Roadmap Agile Scrum User Research Data Analysis Communication Stakeholder Management",
        "description": "Lead product development from ideation to launch, balancing user needs with business goals."
    },
    {
        "job_title": "UI/UX Designer",
        "skills_required": "Figma Adobe XD User Research Wireframing Prototyping CSS HTML Design Systems Usability Testing",
        "description": "Design intuitive and visually appealing user interfaces to improve user experience."
    },

    # ─── EMERGING TECH ───────────────────────────────────────────────────────
    {
        "job_title": "Blockchain Developer",
        "skills_required": "Solidity Ethereum Smart Contracts Web3.js Truffle Hardhat JavaScript Cryptography DeFi",
        "description": "Build decentralized applications and smart contracts on blockchain platforms."
    },
    {
        "job_title": "IoT Engineer",
        "skills_required": "Embedded Systems C Python MQTT Raspberry Pi Arduino Sensors Cloud IoT Protocols",
        "description": "Develop connected device solutions integrating hardware, firmware, and cloud services."
    },
    {
        "job_title": "AR/VR Developer",
        "skills_required": "Unity C# Unreal Engine 3D Modeling OpenGL AR VR Mixed Reality Spatial Computing",
        "description": "Create immersive augmented and virtual reality experiences for various platforms."
    },
    {
        "job_title": "Generative AI Engineer",
        "skills_required": "Python LLMs Prompt Engineering LangChain OpenAI RAG Vector Databases Fine-tuning Transformers",
        "description": "Build applications powered by large language models, image generation, and generative AI tools."
    },
    {
        "job_title": "Robotics Engineer",
        "skills_required": "ROS Python C++ Control Systems Computer Vision SLAM Motion Planning Embedded Systems",
        "description": "Design and program robotic systems for automation, navigation, and human interaction."
    },

    # ─── RESEARCH & ACADEMIA ─────────────────────────────────────────────────
    {
        "job_title": "Research Engineer",
        "skills_required": "Python Research Machine Learning Mathematics Statistics Publication LaTeX Experimentation",
        "description": "Conduct applied research, develop prototypes, and translate research findings into practical solutions."
    },
    {
        "job_title": "Quantitative Analyst",
        "skills_required": "Python R Mathematics Statistics Financial Modeling Machine Learning SQL Risk Analysis",
        "description": "Apply mathematical and statistical models for financial risk management and trading strategies."
    },

    # ─── ADDITIONAL ROLES ─────────────────────────────────────────────────────
    {
        "job_title": "Technical Writer",
        "skills_required": "Technical Writing Documentation Markdown API Documentation Git Communication Editing",
        "description": "Create clear and comprehensive technical documentation, guides, and API references."
    },
    {
        "job_title": "Software Engineer",
        "skills_required": "Python Java C++ Data Structures Algorithms OOP System Design Git Problem Solving SQL",
        "description": "Design, build, and maintain software systems with a focus on clean code and scalability."
    },
    {
        "job_title": "QA Engineer",
        "skills_required": "Testing Selenium Pytest Automation Manual Testing Bug Reporting API Testing CI/CD Python",
        "description": "Ensure software quality through comprehensive manual and automated testing strategies."
    },
]
