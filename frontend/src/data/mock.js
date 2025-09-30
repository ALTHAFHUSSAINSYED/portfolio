// Mock data for Althaf Hussain Syed's TechAssistant
export const portfolioData = {
  personalInfo: {
    name: "Althaf Hussain Syed",
    title: "DevOps Engineer | Cloud & Infrastructure Specialist",
    email: "allualthaf42@gmail.com",
    phone: "8184812249",
    location: "Hyderabad, India",
    linkedin: "https://linkedin.com/in/althafhussainsyed",
    summary: "Certified DevOps Engineer with 3+ years of experience in cloud infrastructure, automation, and CI/CD pipeline engineering. Multi-cloud certified professional with expertise in AWS, GCP, Azure, and Oracle Cloud. Proven track record of reducing operational overhead by 40% and improving incident response time by 30%."
  },

  skills: {
    cloudPlatforms: [
      { name: "AWS", level: "Expert", certifications: 3 },
      { name: "Google Cloud Platform", level: "Advanced", certifications: 1 },
      { name: "Microsoft Azure", level: "Advanced", certifications: 2 },
      { name: "Oracle Cloud", level: "Intermediate", certifications: 7 }
    ],
    devopsTools: [
      { name: "Jenkins", level: "Expert" },
      { name: "Docker", level: "Advanced" },
      { name: "Kubernetes", level: "Advanced" },
      { name: "Terraform", level: "Advanced" },
      { name: "Ansible", level: "Advanced" },
      { name: "GitHub Actions", level: "Intermediate" }
    ],
    programming: [
      { name: "Python", level: "Advanced" },
      { name: "Bash Scripting", level: "Advanced" },
      { name: "Java", level: "Intermediate" }
    ],
    storage: [
      { name: "Brocade SAN", level: "Expert" },
      { name: "HPE 3PAR", level: "Expert" },
      { name: "HPE Primera", level: "Advanced" },
      { name: "Dell EMC", level: "Advanced" }
    ]
  },

  experience: [
    {
      company: "DXC Technology",
      position: "Analyst III Infrastructure Services / DevOps Engineer",
      duration: "Aug 2022 – Present",
      location: "Hyderabad, India",
      achievements: [
        "Automated infrastructure provisioning using Terraform and Ansible, reducing manual effort by 40%",
        "Designed and deployed CI/CD pipelines using Jenkins and AWS CodePipeline for multi-tier applications",
        "Containerized applications with Docker and orchestrated them using Kubernetes (EKS, GKE, AKS)",
        "Implemented comprehensive monitoring solutions with AWS CloudWatch and GCP Cloud Monitoring, improving incident response time by 30%",
        "Managed enterprise storage solutions (Brocade SAN, HPE 3PAR, Primera) ensuring 99.9% uptime",
        "Collaborated with cross-functional teams to streamline infrastructure reliability and migrations"
      ],
      technologies: ["AWS", "GCP", "Azure", "Jenkins", "Docker", "Kubernetes", "Terraform", "Ansible", "Python", "Bash"]
    }
  ],

  education: [
    {
      degree: "Master of Science in Computer Science",
      institution: "Acharya Nagarjuna University",
      duration: "Dec 2022 – June 2024",
      location: "Andhra Pradesh, India"
    },
    {
      degree: "Bachelor of Science in Computer Science",
      institution: "Acharya Nagarjuna University",
      duration: "June 2019 – June 2022",
      location: "Andhra Pradesh, India"
    }
  ],

  certifications: [
    {
      name: "AWS Certified Solutions Architect – Associate",
      issuer: "Amazon Web Services",
      year: "2024",
      category: "aws"
    },
    {
      name: "Google Cloud Professional Cloud Architect",
      issuer: "Google Cloud",
      year: "2024",
      category: "gcp"
    },
    {
      name: "Microsoft Azure Administrator Associate (AZ-104)",
      issuer: "Microsoft",
      year: "2024",
      category: "azure"
    },
    {
      name: "Oracle Cloud Infrastructure Architect Associate",
      issuer: "Oracle",
      year: "2024",
      category: "oracle"
    },
    {
      name: "AWS Certified AI Practitioner",
      issuer: "Amazon Web Services",
      year: "2024",
      category: "aws"
    },
    {
      name: "AWS Cloud Practitioner",
      issuer: "Amazon Web Services",
      year: "2023",
      category: "aws"
    },
    {
      name: "Azure Fundamentals (AZ-900)",
      issuer: "Microsoft",
      year: "2023",
      category: "azure"
    },
    {
      name: "GitHub Foundations",
      issuer: "GitHub",
      year: "2024",
      category: "devops"
    },
    {
      name: "Generative AI Certified Professional",
      issuer: "Oracle",
      year: "2024",
      category: "ai"
    }
  ],

  achievements: [
    {
      title: "Infrastructure Automation Champion",
      description: "Reduced manual infrastructure provisioning time by 40% through comprehensive automation"
    },
    {
      title: "Multi-Cloud Expert",
      description: "Achieved 14+ professional certifications across AWS, GCP, Azure, and Oracle Cloud platforms"
    },
    {
      title: "Incident Response Optimization",
      description: "Improved incident response time by 30% through proactive monitoring and alerting systems"
    },
    {
      title: "High Availability Specialist",
      description: "Maintained 99.9% uptime for critical enterprise storage infrastructure"
    }
  ],

  projects: [
    {
      title: "Multi-Cloud CI/CD Pipeline",
      description: "Designed and implemented end-to-end CI/CD pipelines across AWS, GCP, and Azure environments",
      technologies: ["Jenkins", "AWS CodePipeline", "GCP Cloud Build", "Docker", "Kubernetes"],
      achievements: ["Reduced deployment time by 60%", "Improved code quality through automated testing"]
    },
    {
      title: "Infrastructure as Code Implementation",
      description: "Automated infrastructure provisioning using Terraform and Ansible across multiple cloud platforms",
      technologies: ["Terraform", "Ansible", "AWS", "GCP", "Azure"],
      achievements: ["40% reduction in manual provisioning", "Standardized infrastructure deployment"]
    },
    {
      title: "Enterprise Storage Optimization",
      description: "Managed and optimized enterprise storage solutions for high-performance computing environments",
      technologies: ["Brocade SAN", "HPE 3PAR", "HPE Primera", "Dell EMC"],
      achievements: ["99.9% uptime achievement", "30% improvement in storage efficiency"]
    }
  ]
};