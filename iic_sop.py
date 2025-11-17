import streamlit as st
from datetime import datetime, date, time as dt_time
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from io import BytesIO
import re

# Page Configuration
st.set_page_config(
    page_title="HIVE Hub - Advanced IIC SOP Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .main {
        background: transparent;
    }
    
    .header-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 8s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .header-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.5);
        letter-spacing: -1px;
        position: relative;
        z-index: 1;
    }
    
    .header-subtitle {
        text-align: center;
        color: #ffffff;
        font-size: 1.25rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        position: relative;
        z-index: 1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    }
    
    .section-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .form-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .form-card:hover {
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.875rem 2.5rem;
        border-radius: 12px;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.5);
        background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
    }
    
    .success-banner {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .info-card {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-left: 4px solid #3b82f6;
        padding: 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #f59e0b;
        padding: 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
    
    .add-button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        padding: 0.625rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.95rem;
    }
    
    .remove-button {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        border: none;
        padding: 0.625rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.95rem;
    }
    
    .budget-table {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 1rem 0;
    }
    
    .stNumberInput>div>div>input {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background-color: white;
        color: #1f2937;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #4f46e5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
    }
    
    .stSelectbox>div>div>select {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        padding: 0.75rem;
        font-size: 1rem;
        background-color: white;
        color: #1f2937;
    }
    
    label {
        color: #1f2937 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    .stMarkdown {
        color: #1f2937;
    }
    
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        text-align: center;
        border-top: 4px solid #4f46e5;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #1e293b;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'coordinators' not in st.session_state:
    st.session_state.coordinators = [{'name': '', 'designation': '', 'department': ''}]

if 'resource_persons' not in st.session_state:
    st.session_state.resource_persons = [{
        'name': '', 'designation': '', 'organization': '', 
        'phone': '', 'email': '', 'address': ''
    }]

if 'budget_items' not in st.session_state:
    st.session_state.budget_items = [
        {'category': 'Refreshments', 'description': '', 'amount': 0.0},
        {'category': 'Materials & Stationery', 'description': '', 'amount': 0.0},
        {'category': 'Resource Person Honorarium', 'description': '', 'amount': 0.0},
    ]

if 'income_sources' not in st.session_state:
    st.session_state.income_sources = [
        {'source': 'Departmental Fund', 'amount': 0.0},
    ]

# IIC Activity Database
IIC_ACTIVITIES = {
    "Q1": {
        "thrust_area": "Inspiration, Motivation, and Ideation",
        "period": "September - November",
        "activities": [
            "Awareness Workshop on Entrepreneurship & Innovation",
            "My Story/Motivational Expert Sessions",
            "Boot camp on Problem Solving/Ideation",
            "Workshop on AI and I4.0 Tools",
            "IPR Basics for Innovators & Entrepreneurs",
            "Session on Achieving Problem-Solution Fit",
            "Inter/Intra Institutional Hackathon/Idea Challenge",
            "Demo Day/Idea Showcase"
        ]
    },
    "Q2": {
        "thrust_area": "Validation and Concept Development",
        "period": "December - February",
        "activities": [
            "Workshop on Design Thinking, Critical Thinking & Innovation Design",
            "Innovation & Entrepreneurship Outreach Program",
            "AI & Innovation Sprints: Rapid Prototyping",
            "Expert Talk on TRL, MRL, IRL, IP Commercialization",
            "Workshop on Sales and Marketing Strategies",
            "Field/Exposure Visit to Preincubation Units",
            "Innovation Competition/Hackathon",
            "Innovation Showcase: Demo Day/Exhibition"
        ]
    },
    "Q3": {
        "thrust_area": "Prototype, Design, Business Model Development",
        "period": "March - May",
        "activities": [
            "Workshop on Product-Market fit & MVP Development",
            "Session on Business Model Canvas (BMC)",
            "AI-Powered Solution Expo",
            "Field Visit to Incubation Units/Patent Centers",
            "Session on Start-up Legal & Ethical Steps",
            "Workshop on Raising Capital and Finance Management",
            "Workshop on Protecting IPR and IP Management",
            "B-Plan Competition",
            "Demo Day/Poster Presentation of Business Plans"
        ]
    },
    "Q4": {
        "thrust_area": "Start-up Ecosystem & Scale Up",
        "period": "June - August",
        "activities": [
            "Session on Innovation/Prototype Validation",
            "Workshop on AI for Fundraising & Investor Pitch",
            "Session on Accelerators/Incubation Opportunities",
            "Lean Start-up & MVP Boot Camp",
            "Session on Angel Investment/VC Funding",
            "Panel Discussions with Startup Ecosystem Enablers",
            "Innovation & Entrepreneurship Outreach Program",
            "Start-up Competition",
            "Demo Day/Exhibition of Start-Ups"
        ]
    }
}

EVENT_TYPES = {
    "Expert Talk": {"level": "Level 1", "duration": "2-4 hours"},
    "Mentoring Session": {"level": "Level 1", "duration": "2-4 hours"},
    "Workshop": {"level": "Level 2", "duration": "5-8 hours"},
    "Seminar": {"level": "Level 2", "duration": "5-8 hours"},
    "Panel Discussion": {"level": "Level 2", "duration": "5-8 hours"},
    "Boot Camp": {"level": "Level 3", "duration": "9-18 hours"},
    "Hackathon": {"level": "Level 3", "duration": "9-18 hours"},
    "Competition": {"level": "Level 3", "duration": "9-18 hours"},
    "Demo Day": {"level": "Level 3", "duration": "9-18 hours"},
    "Exhibition": {"level": "Level 3", "duration": "9-18 hours"},
    "Challenge": {"level": "Level 4", "duration": ">18 hours"},
    "Tech Fest": {"level": "Level 4", "duration": ">18 hours"},
}

BUDGET_CATEGORIES = [
    "Refreshments & Meals",
    "Materials & Stationery",
    "Resource Person Honorarium",
    "Transportation",
    "Venue & Equipment",
    "Printing & Documentation",
    "Marketing & Publicity",
    "Certificates & Prizes",
    "Technical Support",
    "Miscellaneous"
]

INCOME_SOURCES = [
    "Departmental Fund",
    "College Fund",
    "Sponsorship",
    "Registration Fee",
    "Government Grant",
    "Industry Partnership",
    "Alumni Contribution",
    "Other Sources"
]

def get_quarter_info(event_date):
    """Determine quarter based on event date"""
    month = event_date.month
    
    if 9 <= month <= 11:
        return {"quarter": "Q1", **IIC_ACTIVITIES["Q1"]}
    elif month == 12 or 1 <= month <= 2:
        return {"quarter": "Q2", **IIC_ACTIVITIES["Q2"]}
    elif 3 <= month <= 5:
        return {"quarter": "Q3", **IIC_ACTIVITIES["Q3"]}
    else:
        return {"quarter": "Q4", **IIC_ACTIVITIES["Q4"]}

def generate_objective(event_title, event_type, quarter_info):
    """Generate sophisticated objective based on event type and IIC guidelines"""
    
    objectives = {
        "Expert Talk": f"This program is strategically designed to expose students to industry insights and entrepreneurial wisdom through expert discourse on {event_title}. The session aims to catalyze entrepreneurial thinking by providing students with real-world perspectives, success narratives, and practical frameworks for innovation. By connecting students with accomplished professionals, we seek to demystify the entrepreneurial journey and inspire them to pursue innovation-driven career paths.",
        
        "Mentoring Session": f"This mentoring initiative is structured to provide personalized guidance and strategic direction to aspiring innovators in the domain of {event_title}. The program aims to bridge the gap between academic knowledge and practical entrepreneurship by facilitating one-on-one interactions with experienced mentors. Through this engagement, students will gain actionable insights, identify their entrepreneurial strengths, and develop customized roadmaps for their innovation journey.",
        
        "Workshop": f"This comprehensive workshop on {event_title} is engineered to build practical competencies and hands-on skills essential for modern entrepreneurs and innovators. The program employs experiential learning methodologies to ensure participants not only understand theoretical concepts but also develop the ability to apply them in real-world scenarios. Through interactive sessions, case studies, and practical exercises, students will acquire tools and techniques necessary for successful innovation implementation.",
        
        "Seminar": f"This seminar serves as an intellectual platform for in-depth exploration of {event_title}, fostering critical thinking and analytical discourse on contemporary innovation challenges. The program aims to enhance participants' understanding of emerging trends, best practices, and strategic approaches in entrepreneurship. By engaging with expert speakers and thought leaders, students will develop a comprehensive perspective on the innovation ecosystem and their potential role within it.",
        
        "Panel Discussion": f"This panel discussion brings together diverse perspectives on {event_title}, creating a dynamic forum for exploring multiple dimensions of innovation and entrepreneurship. The program is designed to expose students to varied viewpoints, industry insights, and practical experiences shared by accomplished panelists. Through moderated dialogue and audience interaction, participants will gain nuanced understanding of challenges, opportunities, and strategic approaches in the innovation landscape.",
        
        "Boot Camp": f"This intensive boot camp represents an immersive learning experience in {event_title}, designed to accelerate skill development and foster entrepreneurial mindset through concentrated, project-based learning. The program employs a rigorous curriculum that combines theoretical foundation with extensive practical application, enabling participants to achieve rapid competency development. Through collaborative projects, expert mentorship, and intensive workshops, students will emerge with both confidence and capability to execute innovative ventures.",
        
        "Hackathon": f"This hackathon is conceptualized as a high-energy innovation sprint focused on {event_title}, challenging participants to ideate, prototype, and present viable solutions within compressed timeframes. The program aims to cultivate rapid problem-solving abilities, technical excellence, and collaborative innovation while addressing real-world challenges. By simulating the startup environment's intensity and creativity, students will develop resilience, agility, and the ability to transform ideas into tangible prototypes.",
        
        "Competition": f"This competition is strategically designed to identify, nurture, and reward exceptional innovation and entrepreneurial thinking in {event_title}. The program provides a structured platform for students to showcase their creative solutions, receive expert evaluation, and refine their innovations based on constructive feedback. Through competitive engagement, participants will develop presentation skills, business acumen, and the confidence to pitch their ideas to diverse stakeholders.",
        
        "Demo Day": f"This demo day is orchestrated to provide maximum visibility to student innovations in {event_title}, connecting emerging solutions with potential mentors, investors, and industry partners. The program aims to transform prototype presentations into meaningful business opportunities by facilitating networking and feedback exchange. Through professional showcasing and stakeholder engagement, students will gain valuable insights for scaling their innovations and navigating the commercialization pathway.",
        
        "Exhibition": f"This exhibition serves as a comprehensive showcase platform for innovations in {event_title}, providing students with opportunities to demonstrate their creative solutions to a wide audience. The program is designed to celebrate innovation while facilitating knowledge exchange, networking, and potential collaboration opportunities. Through public demonstration and interactive presentations, participants will gain experience in articulating technical concepts and engaging diverse audiences.",
        
        "Challenge": f"This innovation challenge presents participants with complex, real-world problems in {event_title}, requiring sustained effort, strategic thinking, and collaborative problem-solving over an extended period. The program is structured to push the boundaries of creativity and technical capability, encouraging participants to develop comprehensive solutions that address multiple stakeholder needs. Through this intensive engagement, students will experience the full spectrum of innovation processes from ideation through validation.",
        
        "Tech Fest": f"This technology festival creates a vibrant ecosystem for celebrating and advancing innovation in {event_title}, bringing together multiple events, competitions, and interactive sessions under one umbrella. The program aims to energize the student community around entrepreneurship and innovation while providing diverse opportunities for skill demonstration, learning, and networking. Through this multi-faceted approach, participants will experience the dynamism and collaborative spirit essential to successful innovation ecosystems."
    }
    
    event_category = next((k for k in objectives.keys() if k == event_type), "Workshop")
    base_objective = objectives[event_category]
    
    quarter_context = f"\n\nThis program is strategically aligned with IIC {quarter_info['quarter']} ({quarter_info['period']}) thrust area: '{quarter_info['thrust_area']}', ensuring systematic progression in the institution's innovation and entrepreneurship development roadmap. The initiative contributes to building institutional capability in fostering innovation culture and developing entrepreneurial competencies among students."
    
    return base_objective + quarter_context

def generate_student_development(event_title, event_type):
    """Generate comprehensive student development contribution"""
    
    contributions = {
        "Expert Talk": f"This session catalyzes transformational learning by exposing students to real-world entrepreneurial journeys and industry insights in {event_title}. Participants develop enhanced understanding of career possibilities in innovation ecosystems while building aspiration and motivation to pursue entrepreneurial paths. The program cultivates critical thinking, professional networking skills, and the ability to learn from others' experiences. Students gain confidence in their entrepreneurial potential through exposure to role models who have successfully navigated similar journeys. Additionally, the session helps participants develop the ability to extract actionable insights from expert narratives and apply them to their own contexts, fostering self-directed learning and growth mindset essential for long-term entrepreneurial success.",
        
        "Mentoring Session": f"Through personalized guidance in {event_title}, students receive tailored support for their specific innovation challenges and entrepreneurial aspirations. The program enhances self-awareness by helping participants identify their unique strengths, weaknesses, and areas for development. Students develop strategic thinking capabilities and learn to create actionable plans for achieving their entrepreneurial goals. The mentoring relationship builds communication skills, receptiveness to feedback, and the ability to leverage expert guidance effectively. Participants gain confidence from validated support and develop resilience through constructive challenge. Moreover, students learn the art of meaningful professional relationship-building, which proves invaluable throughout their entrepreneurial journey, creating lasting impact beyond the immediate session.",
        
        "Workshop": f"This hands-on workshop in {event_title} fundamentally enhances students' practical capabilities through experiential learning and skill-building exercises. Participants develop technical proficiency in relevant tools and methodologies while simultaneously building problem-solving and critical thinking skills. The interactive format cultivates collaboration abilities, communication skills, and the confidence to tackle complex challenges. Students gain experience in applying theoretical concepts to practical scenarios, bridging the crucial gap between knowledge and application. The program fosters self-reliance and entrepreneurial self-efficacy by enabling students to independently execute innovation-related tasks. Furthermore, participants develop learning agility and adaptability—crucial competencies in the rapidly evolving entrepreneurship landscape—preparing them to continuously upskill throughout their careers.",
        
        "Seminar": f"The seminar experience in {event_title} significantly broadens students' intellectual horizons and deepens their understanding of innovation ecosystems and entrepreneurial frameworks. Participants develop analytical thinking capabilities and learn to engage critically with complex ideas and emerging trends. The program enhances research orientation and the ability to synthesize information from multiple sources, crucial skills for informed decision-making. Students build professional communication skills through engagement with speakers and peers, while developing the confidence to participate in intellectual discourse. The exposure to cutting-edge thinking prepares students to stay current with industry developments and positions them as knowledgeable professionals. Additionally, the seminar cultivates curiosity and lifelong learning orientation, fundamental attributes for sustained entrepreneurial success.",
        
        "Panel Discussion": f"Through this panel discussion on {event_title}, students develop sophisticated understanding by exposure to diverse expert perspectives and multifaceted viewpoints on innovation challenges. The program enhances critical thinking by requiring participants to analyze, compare, and synthesize different approaches and opinions. Students build active listening skills and learn to extract valuable insights from complex discussions while developing the ability to formulate thoughtful questions. The interactive format cultivates confidence in professional engagement and improves ability to navigate ambiguity—essential skills in entrepreneurship. Participants gain appreciation for diverse problem-solving approaches and develop more nuanced thinking about innovation challenges. Furthermore, students learn to construct balanced perspectives by considering multiple viewpoints, preparing them for strategic decision-making in their entrepreneurial ventures.",
        
        "Boot Camp": f"This intensive boot camp experience in {event_title} accelerates students' competency development through immersive, concentrated learning and practical application. Participants undergo rapid skill acquisition in a high-intensity environment that mirrors real startup conditions, building both technical capabilities and entrepreneurial resilience. The program cultivates time management, prioritization skills, and the ability to perform under pressure—critical attributes for entrepreneurial success. Students develop deep expertise through repeated practice and immediate feedback, while building confidence through tangible achievement of challenging objectives. The collaborative nature enhances teamwork, leadership, and interpersonal skills. Moreover, participants develop grit, perseverance, and growth mindset as they push beyond their perceived limitations, experiencing transformational personal development that extends far beyond technical skills.",
        
        "Hackathon": f"The hackathon experience in {event_title} develops students' ability to ideate, prototype, and present innovative solutions under time constraints, simulating real entrepreneurial conditions. Participants enhance creative problem-solving skills, technical proficiency, and the ability to work collaboratively in diverse teams toward common goals. The program builds resilience, stress management capabilities, and the confidence to tackle ambiguous challenges with limited resources. Students gain practical experience in the complete innovation lifecycle—from concept to prototype—while developing rapid learning and adaptation skills. The competitive element fosters excellence-oriented mindset and teaches graceful handling of both success and setback. Furthermore, participants develop pitching and presentation skills crucial for entrepreneurial success, learning to articulate technical concepts compellingly to various audiences.",
        
        "Competition": f"Through this competition in {event_title}, students develop crucial entrepreneurial skills including business communication, presentation capabilities, and the ability to articulate value propositions compellingly. Participants learn to handle critical feedback constructively and refine their innovations based on expert input, building resilience and adaptability. The program enhances strategic thinking as students learn to position their innovations competitively and differentiate their solutions effectively. The experience builds confidence through public presentation and expert validation while teaching important lessons about preparation, professionalism, and continuous improvement. Students develop emotional intelligence and stress management capabilities essential for entrepreneurial journeys. Moreover, participants learn from observing peer innovations, gaining broader perspective on different approaches to similar challenges and building their innovation repertoire.",
        
        "Demo Day": f"This demo day experience in {event_title} develops students' ability to showcase their innovations professionally and engage effectively with diverse stakeholders including investors, mentors, and industry professionals. Participants enhance communication skills, learning to adapt their messaging for different audiences and articulate technical concepts accessibly. The program builds confidence through public demonstration and stakeholder interaction while developing networking capabilities crucial for entrepreneurial success. Students gain valuable market validation insights through direct audience feedback and learn to handle questions and challenges professionally. The experience teaches the importance of presentation, packaging, and storytelling in innovation commercialization. Furthermore, participants develop business acumen by understanding stakeholder perspectives and learning to position their innovations for various purposes—investment, partnership, or customer acquisition.",
        
        "Exhibition": f"Through this exhibition on {event_title}, students develop comprehensive communication skills by demonstrating their innovations to diverse audiences with varying levels of technical knowledge. Participants enhance their ability to engage visitors interactively, answer spontaneous questions, and maintain enthusiasm throughout extended presentation periods. The program builds confidence through repeated explanation and demonstration of their work while developing adaptability in communication style. Students gain experience in visual presentation, booth design, and creating compelling demonstrations that capture attention. The networking opportunities help participants build professional relationships and develop comfort in representing themselves and their work. Moreover, the exhibition experience teaches students about audience engagement, value communication, and the importance of creating memorable impressions—skills vital for entrepreneurial success.",
        
        "Challenge": f"This extended innovation challenge in {event_title} develops students' capacity for sustained creative effort, strategic planning, and systematic problem-solving over extended periods. Participants build project management skills, learning to break complex problems into manageable components and execute solutions methodically. The program enhances research capabilities, resourcefulness, and the ability to seek and leverage appropriate support. Students develop deeper technical expertise through sustained engagement with complex problems while building perseverance and commitment to seeing projects through completion. The comprehensive nature of the challenge develops systems thinking and the ability to address multiple stakeholder needs simultaneously. Furthermore, participants gain experience in managing ambiguity, pivoting strategies based on learnings, and maintaining motivation through extended problem-solving cycles—essential capabilities for entrepreneurial ventures.",
        
        "Tech Fest": f"Through participation in this technology festival focused on {event_title}, students experience a holistic development journey encompassing technical skills, creative thinking, and professional networking capabilities. The diverse activities expose participants to multiple facets of innovation and entrepreneurship, broadening their perspective and skill set. Students develop event participation skills, time management in handling multiple concurrent activities, and the ability to learn rapidly from diverse experiences. The program builds community connection, collaborative spirit, and appreciation for diverse innovation approaches. Participants gain confidence through engagement in varied formats—competitions, demonstrations, workshops—each contributing unique developmental benefits. Moreover, the festival atmosphere cultivates enthusiasm, energy, and passion for innovation while creating lasting memories and relationships that sustain long-term entrepreneurial engagement."
    }
    
    event_category = next((k for k in contributions.keys() if k == event_type), "Workshop")
    return contributions[event_category]

def generate_institution_development(event_title, event_type):
    """Generate comprehensive institution development contribution"""
    
    contributions = {
        "Expert Talk": f"This expert session on {event_title} significantly enhances the institution's reputation as a forward-thinking educational center that prioritizes industry connectivity and real-world learning. By facilitating high-quality expert interactions, the institution demonstrates commitment to providing students with holistic education beyond traditional curricula. The program strengthens institutional networks with industry leaders, successful entrepreneurs, and innovation ecosystem enablers, creating valuable partnerships for future collaboration. This initiative positions the institution favorably in rankings and accreditation processes by demonstrating active engagement with entrepreneurship education best practices. The session attracts prospective students seeking institutions with strong industry connections and comprehensive innovation support. Furthermore, it enhances alumni engagement by creating opportunities for successful alumni entrepreneurs to contribute back, strengthening the institutional community and creating a positive feedback loop of mentorship and support.",
        
        "Mentoring Session": f"Through organizing this mentoring program in {event_title}, the institution establishes itself as a nurturing environment that provides personalized support for student innovation and entrepreneurship aspirations. This demonstrates institutional commitment to student success beyond academic instruction, significantly enhancing brand value and student satisfaction. The program creates structured channels for expert engagement, building a sustainable mentorship ecosystem that becomes a distinctive institutional asset. This initiative attracts quality faculty and students who value individualized attention and comprehensive support structures. The mentoring relationships often translate into long-term institutional partnerships, internship opportunities, and industry collaborations. Additionally, the program generates positive word-of-mouth and testimonials from participants, enhancing institutional reputation organically. The structured approach to mentoring positions the institution as a professionally managed center for innovation, attracting attention from funding agencies, corporate partners, and potential collaborators.",
        
        "Workshop": f"By organizing this comprehensive workshop on {event_title}, the institution showcases its capability to deliver high-quality, skill-focused educational programs that complement academic curriculum with practical, industry-relevant competencies. This positions the institution as progressive and responsive to evolving educational needs, significantly enhancing its competitive positioning. The workshop demonstrates institutional investment in state-of-the-art learning methodologies and infrastructure, attracting quality students and faculty. Such initiatives strengthen the institution's standing in accreditation assessments and ranking evaluations by demonstrating commitment to experiential learning. The program often attracts external participants, expanding institutional visibility and creating new networking opportunities. Furthermore, successful workshops generate positive media coverage, social media engagement, and stakeholder appreciation, contributing to brand building. The demonstrated capability to organize professional development programs positions the institution as a potential hub for corporate training and continuing education, creating additional revenue streams.",
        
        "Seminar": f"This seminar on {event_title} establishes the institution as an intellectual hub and thought leadership center in innovation and entrepreneurship education. By hosting high-quality academic and professional discourse, the institution enhances its reputation within academic and industry circles. The program attracts distinguished speakers, creating visibility among influential professionals and organizations while demonstrating institutional credibility. Such initiatives strengthen research culture and academic rigor, positioning the institution favorably for grants, collaborations, and partnerships. The seminar creates content and knowledge resources that benefit the wider community, establishing the institution as a public thought leader. External participation from other institutions and industry professionals expands institutional networks and creates collaboration opportunities. Moreover, the seminar demonstrates institutional commitment to continuous learning and knowledge dissemination, aligning with national innovation and entrepreneurship development objectives, thereby attracting policy attention and support.",
        
        "Panel Discussion": f"By organizing this panel discussion on {event_title}, the institution positions itself as a convening platform for diverse expert perspectives on innovation and entrepreneurship, enhancing its reputation as a collaborative, open-minded educational center. The program brings together distinguished professionals from varied backgrounds, creating unprecedented networking value for the institution. This diversity of perspectives demonstrates institutional sophistication and commitment to comprehensive education. The panel format attracts significant attention from external stakeholders, media, and prospective students, generating valuable publicity. Such initiatives often lead to formal partnerships with panelists' organizations, creating opportunities for internships, projects, and knowledge exchange. The institution gains reputation for facilitating meaningful dialogue on contemporary issues, positioning it as relevant and engaged with current challenges. Furthermore, panel discussions create rich content for institutional communication channels, enhancing online presence and demonstrating thought leadership in innovation education.",
        
        "Boot Camp": f"This intensive boot camp on {event_title} establishes the institution as a center of excellence for immersive, high-impact learning experiences that go beyond conventional education models. The program demonstrates institutional capability to deliver intensive, professionally structured programs that produce tangible skill development in compressed timeframes. This attracts students seeking transformational learning experiences and positions the institution competitively against alternatives. The boot camp format demonstrates institutional agility and innovation in educational delivery, earning recognition from accreditation bodies and ranking agencies. Such programs often attract external sponsorships and partnerships, bringing financial support and corporate credibility. The intensive nature creates strong participant bonding and lasting alumni connections, building a dedicated institutional community. Moreover, successful boot camps generate compelling success stories and testimonials, providing powerful marketing content. The demonstrated ability to execute complex, multi-day intensive programs positions the institution for hosting larger events, conferences, and ecosystem-level initiatives.",
        
        "Hackathon": f"By organizing this hackathon on {event_title}, the institution establishes itself as a vibrant innovation hub and active participant in the startup ecosystem, significantly enhancing its brand among technology companies, investors, and the broader innovation community. The event attracts significant external participation, media coverage, and stakeholder attention, creating substantial visibility. Successful hackathons often attract corporate sponsors, bringing financial support and establishing valuable industry partnerships. The program demonstrates institutional capability in event management, infrastructure support, and innovation facilitation—capabilities valued by potential partners and funding agencies. Hackathons generate excitement and energy, creating a dynamic institutional image that attracts entrepreneurial students and innovative faculty. The innovations produced often become institutional success stories, providing tangible evidence of innovation capability. Furthermore, hosting hackathons positions the institution as a potential incubation partner, attracting ecosystem resources and support while creating pathways for student startup success.",
        
        "Competition": f"This innovation competition in {event_title} positions the institution as an active catalyst for entrepreneurial excellence, demonstrating commitment to identifying and nurturing exceptional talent. The program creates a platform for showcasing student capabilities to external stakeholders including investors, industry partners, and media, generating significant institutional visibility. Successful competitions attract participation from other institutions, positioning the host institution as an ecosystem leader. The evaluation process brings distinguished judges to campus, creating networking opportunities and potential partnerships. Prize distribution and recognition ceremonies generate positive publicity and demonstrate institutional investment in student success. Competition winners become institutional ambassadors and success stories, providing compelling evidence of educational effectiveness. Moreover, well-executed competitions attract corporate sponsorships and partnerships, bringing financial support and establishing long-term relationships. The institution gains reputation for merit-based recognition and professional program organization, enhancing credibility across stakeholder groups.",
        
        "Demo Day": f"By organizing this demo day for {event_title}, the institution transforms itself into a showcase venue for innovation, attracting investors, mentors, industry leaders, and potential partners to campus. This creates unprecedented networking value and positions the institution at the center of regional innovation ecosystems. The event generates significant media coverage and social media engagement, substantially enhancing institutional visibility and brand recognition. Demo days demonstrate institutional success in translating education into tangible innovations, providing powerful evidence of educational effectiveness for prospective students and stakeholders. The program often catalyzes investment and partnership opportunities for participating students, creating success stories that enhance institutional reputation. External stakeholder participation establishes the institution as a credible source of talent and innovation, leading to recruitment partnerships, internship opportunities, and collaborative projects. Furthermore, demo days create opportunities for institutional leadership to engage with ecosystem stakeholders, strengthening relationships and identifying strategic partnership possibilities.",
        
        "Exhibition": f"This exhibition on {event_title} transforms the institution into a public showcase for innovation and entrepreneurship, creating opportunities for community engagement and stakeholder interaction at scale. The program attracts diverse audiences including prospective students, parents, alumni, industry professionals, and community members, creating extensive visibility. Exhibitions demonstrate institutional commitment to celebrating and supporting student innovation, creating a positive brand image. The visual and interactive nature generates compelling content for marketing and communication, enhancing online and offline presence. Such events often attract local media coverage and government attention, positioning the institution as a community asset and innovation driver. The exhibition format allows for showcasing institutional infrastructure, facilities, and capabilities, impressing visitors and potential partners. Moreover, successful exhibitions become annual traditions, creating institutional identity and community anticipation, while building the institution's reputation as a center for innovation celebration and public engagement in science and technology.",
        
        "Challenge": f"By organizing this extended innovation challenge in {event_title}, the institution demonstrates capability for sustained support of complex innovation projects and commitment to deep learning experiences. This positions the institution as serious about innovation outcomes rather than superficial engagement, enhancing credibility with industry and funding agencies. Long-duration challenges often attract significant sponsorship and partnership opportunities as corporate partners value sustained engagement. The program allows for comprehensive mentorship and support infrastructure demonstration, showcasing institutional resources and capabilities. Successful challenges produce well-developed innovations that can progress toward commercialization, creating compelling institutional success narratives. The extended format builds deep relationships between participants, mentors, and the institution, creating lasting loyalty and engagement. Moreover, such challenges often attract policy attention and alignment with national innovation missions, positioning the institution for government support and recognition. The demonstrated capacity for complex program execution establishes institutional reputation for professional management and innovation capability.",
        
        "Tech Fest": f"This comprehensive technology festival on {event_title} positions the institution as a dynamic innovation hub and creates a landmark event that becomes synonymous with institutional identity. The multi-day, multi-activity format attracts massive participation, creating unprecedented visibility and brand recognition. Tech fests generate significant media coverage, social media buzz, and community engagement, substantially enhancing institutional profile. The festival format allows showcasing diverse institutional strengths—infrastructure, faculty expertise, student talent, and organizational capability—in a single compelling package. Such events attract substantial corporate sponsorships, bringing financial support and establishing strategic partnerships. The excitement and energy generated create lasting impressions on participants, visitors, and stakeholders, building strong institutional affinity. Alumni often return for such events, strengthening community bonds. Moreover, successful tech fests become regional or national attractions, positioning the institution as an ecosystem anchor. The demonstrated capability to execute large-scale, complex events establishes institutional credibility for hosting conferences, competitions, and other high-profile programs, creating ongoing opportunities for visibility and partnership."
    }
    
    event_category = next((k for k in contributions.keys() if k == event_type), "Workshop")
    return contributions[event_category]

def create_professional_pdf(data):
    """Generate highly professional PDF with perfect formatting"""
    buffer = BytesIO()
    
    # Page setup with margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=15*mm,
        bottomMargin=15*mm,
        title="IIC Event SOP"
    )
    
    # Professional color palette
    primary_color = colors.HexColor('#1e3c72')
    secondary_color = colors.HexColor('#2a5298')
    accent_color = colors.HexColor('#7e22ce')
    text_color = colors.HexColor('#1f2937')
    light_bg = colors.HexColor('#f3f4f6')
    table_header = colors.HexColor('#e0e7ff')
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Professional Styles
    title_style = ParagraphStyle(
        'ProfessionalTitle',
        parent=styles['Title'],
        fontSize=14,
        textColor=primary_color,
        spaceAfter=4,
        spaceBefore=0,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=16
    )
    
    subtitle_style = ParagraphStyle(
        'ProfessionalSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=secondary_color,
        spaceAfter=3,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=13
    )
    
    heading_style = ParagraphStyle(
        'ProfessionalHeading',
        parent=styles['Heading2'],
        fontSize=10,
        textColor=primary_color,
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=primary_color,
        borderPadding=6,
        backColor=table_header,
        leading=12
    )
    
    normal_style = ParagraphStyle(
        'ProfessionalNormal',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=12,
        textColor=text_color,
        fontName='Helvetica'
    )
    
    small_style = ParagraphStyle(
        'SmallText',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_LEFT,
        leading=10,
        textColor=text_color,
        fontName='Helvetica'
    )
    
    table_text_style = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontSize=8.5,
        alignment=TA_LEFT,
        leading=11,
        textColor=text_color,
        fontName='Helvetica'
    )
    
    # Header Section
    story.append(Paragraph("SRI RAMAKRISHNA INSTITUTE OF TECHNOLOGY", title_style))
    story.append(Paragraph("COIMBATORE - 641 010", subtitle_style))
    story.append(Paragraph("<b>HIVE HUB FOR INNOVATION AND ENTREPRENEURSHIP</b>", subtitle_style))
    story.append(Paragraph("Institution's Innovation Council (IIC)", small_style))
    story.append(Spacer(1, 8))
    
    # Title with border
    title_table = Table(
        [[Paragraph("<b>APPLICATION FOR ORGANIZING PROGRAMME</b>", heading_style)]],
        colWidths=[170*mm]
    )
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), table_header),
        ('BOX', (0, 0), (-1, -1), 1, primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(title_table)
    story.append(Spacer(1, 10))
    
    # Date
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d.%m.%Y')}", normal_style))
    story.append(Spacer(1, 8))
    
    # Main Information Table
    main_data = []
    
    # Row 1: Department
    main_data.append([
        Paragraph("<b>1</b>", table_text_style),
        Paragraph("<b>Department, Association, Club</b>", table_text_style),
        Paragraph(data['department'], table_text_style)
    ])
    
    # Row 2: Nature
    main_data.append([
        Paragraph("<b>2</b>", table_text_style),
        Paragraph("<b>Nature of Programme</b>", table_text_style),
        Paragraph(f"<b>{data['event_type']}</b> ({data['event_level']})", table_text_style)
    ])
    
    # Row 3: Title
    main_data.append([
        Paragraph("<b>3</b>", table_text_style),
        Paragraph("<b>Title of the Programme</b>", table_text_style),
        Paragraph(f"<b>{data['event_title']}</b>", table_text_style)
    ])
    
    # Row 4: Coordinators (Multiple)
    coordinators_text = ""
    for i, coord in enumerate(data['coordinators'], 1):
        if i > 1:
            coordinators_text += "<br/>"
        coordinators_text += f"<b>{i}.</b> {coord['name']}"
        if coord['designation']:
            coordinators_text += f", {coord['designation']}"
        if coord['department']:
            coordinators_text += f", {coord['department']}"
    
    main_data.append([
        Paragraph("<b>4</b>", table_text_style),
        Paragraph("<b>Name of the Faculty<br/>Coordinator(s)</b>", table_text_style),
        Paragraph(coordinators_text, table_text_style)
    ])
    
    # Row 5: Date
    main_data.append([
        Paragraph("<b>5</b>", table_text_style),
        Paragraph("<b>Date and Day</b>", table_text_style),
        Paragraph(f"<b>{data['date_day']}</b>", table_text_style)
    ])
    
    # Row 6: Time
    main_data.append([
        Paragraph("<b>6</b>", table_text_style),
        Paragraph("<b>Time</b>", table_text_style),
        Paragraph(data['time'], table_text_style)
    ])
    
    # Row 7: Venue
    main_data.append([
        Paragraph("<b>7</b>", table_text_style),
        Paragraph("<b>Venue</b>", table_text_style),
        Paragraph(f"<b>{data['venue']}</b>", table_text_style)
    ])
    
    # Row 8: Participants
    main_data.append([
        Paragraph("<b>8</b>", table_text_style),
        Paragraph("<b>Target Participants</b>", table_text_style),
        Paragraph(data['participants'], table_text_style)
    ])
    
    # Row 9: Expected Audience
    main_data.append([
        Paragraph("<b>9</b>", table_text_style),
        Paragraph("<b>Total Audience Expected</b>", table_text_style),
        Paragraph(f"<b>{str(data['expected_audience'])}</b>", table_text_style)
    ])
    
    # Row 10: Resource Persons (Multiple)
    resource_persons_text = ""
    for i, rp in enumerate(data['resource_persons'], 1):
        if i > 1:
            resource_persons_text += "<br/><br/>"
        resource_persons_text += f"<b>Resource Person {i}:</b><br/>"
        resource_persons_text += f"<b>Name:</b> {rp['name']}<br/>"
        if rp['designation']:
            resource_persons_text += f"<b>Designation:</b> {rp['designation']}<br/>"
        if rp['organization']:
            resource_persons_text += f"<b>Organization:</b> {rp['organization']}<br/>"
        if rp['address']:
            resource_persons_text += f"<b>Address:</b> {rp['address']}<br/>"
        if rp['phone']:
            resource_persons_text += f"<b>Phone:</b> {rp['phone']}<br/>"
        if rp['email']:
            resource_persons_text += f"<b>Email:</b> {rp['email']}"
    
    main_data.append([
        Paragraph("<b>10</b>", table_text_style),
        Paragraph("<b>Details of Resource<br/>Person(s)</b><br/><i style='font-size:7pt'>(Name, Designation,<br/>Organization, Address,<br/>Phone, Email)</i>", table_text_style),
        Paragraph(resource_persons_text, table_text_style)
    ])
    
    # Create main table with better proportions
    main_table = Table(main_data, colWidths=[10*mm, 50*mm, 110*mm])
    main_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, -1), table_header),
        ('TEXTCOLOR', (0, 0), (-1, -1), text_color),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 2, primary_color),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, 0), (-1, 0), 2, primary_color),
    ]))
    story.append(main_table)
    story.append(Spacer(1, 15))
    
    # Financial Details Section
    if data.get('budget_items') and len(data['budget_items']) > 0:
        story.append(Paragraph("<b>11. BUDGET STATEMENT</b>", heading_style))
        story.append(Spacer(1, 8))
        
        # Income Section
        story.append(Paragraph("<b>A. SOURCES OF INCOME</b>", ParagraphStyle(
            'SubHeading',
            parent=normal_style,
            fontSize=10,
            textColor=primary_color,
            fontName='Helvetica-Bold',
            spaceAfter=6
        )))
        
        income_data = [
            [Paragraph("<b>S.No</b>", table_text_style),
             Paragraph("<b>Source of Income</b>", table_text_style),
             Paragraph("<b>Amount (₹)</b>", table_text_style)]
        ]
        
        total_income = 0
        for i, source in enumerate(data['income_sources'], 1):
            if source['amount'] > 0:
                income_data.append([
                    Paragraph(f"<b>{i}</b>", table_text_style),
                    Paragraph(source['source'], table_text_style),
                    Paragraph(f"{source['amount']:,.2f}", ParagraphStyle(
                        'AmountStyle',
                        parent=table_text_style,
                        alignment=TA_RIGHT
                    ))
                ])
                total_income += source['amount']
        
        income_data.append([
            Paragraph("", table_text_style),
            Paragraph("<b>TOTAL INCOME</b>", ParagraphStyle(
                'BoldText',
                parent=table_text_style,
                fontName='Helvetica-Bold',
                fontSize=9
            )),
            Paragraph(f"<b>₹ {total_income:,.2f}</b>", ParagraphStyle(
                'BoldAmount',
                parent=table_text_style,
                fontName='Helvetica-Bold',
                fontSize=9,
                alignment=TA_RIGHT
            ))
        ])
        
        income_table = Table(income_data, colWidths=[15*mm, 115*mm, 40*mm])
        income_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 2, primary_color),
            ('BACKGROUND', (0, -1), (-1, -1), table_header),
            ('LINEABOVE', (0, -1), (-1, -1), 2, primary_color),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(income_table)
        story.append(Spacer(1, 12))
        
        # Expenditure Section
        story.append(Paragraph("<b>B. EXPENDITURE DETAILS</b>", ParagraphStyle(
            'SubHeading',
            parent=normal_style,
            fontSize=10,
            textColor=primary_color,
            fontName='Helvetica-Bold',
            spaceAfter=6
        )))
        
        expense_data = [
            [Paragraph("<b>S.No</b>", table_text_style),
             Paragraph("<b>Category</b>", table_text_style),
             Paragraph("<b>Description</b>", table_text_style),
             Paragraph("<b>Amount (₹)</b>", table_text_style)]
        ]
        
        total_expense = 0
        for i, item in enumerate(data['budget_items'], 1):
            if item['amount'] > 0:
                expense_data.append([
                    Paragraph(f"<b>{i}</b>", table_text_style),
                    Paragraph(item['category'], table_text_style),
                    Paragraph(item['description'] if item['description'] else '-', table_text_style),
                    Paragraph(f"{item['amount']:,.2f}", ParagraphStyle(
                        'AmountStyle',
                        parent=table_text_style,
                        alignment=TA_RIGHT
                    ))
                ])
                total_expense += item['amount']
        
        expense_data.append([
            Paragraph("", table_text_style),
            Paragraph("<b>TOTAL EXPENDITURE</b>", ParagraphStyle(
                'BoldText',
                parent=table_text_style,
                fontName='Helvetica-Bold',
                fontSize=9
            )),
            Paragraph("", table_text_style),
            Paragraph(f"<b>₹ {total_expense:,.2f}</b>", ParagraphStyle(
                'BoldAmount',
                parent=table_text_style,
                fontName='Helvetica-Bold',
                fontSize=9,
                alignment=TA_RIGHT
            ))
        ])
        
        expense_table = Table(expense_data, colWidths=[15*mm, 50*mm, 65*mm, 40*mm])
        expense_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (2, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 2, primary_color),
            ('BACKGROUND', (0, -1), (-1, -1), table_header),
            ('LINEABOVE', (0, -1), (-1, -1), 2, primary_color),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(expense_table)
        story.append(Spacer(1, 12))
        
        # Summary
        balance = total_income - total_expense
        balance_color = colors.HexColor('#10b981') if balance >= 0 else colors.HexColor('#ef4444')
        
        summary_data = [
            [Paragraph("<b>Total Income</b>", ParagraphStyle(
                'SummaryLabel',
                parent=table_text_style,
                fontSize=10,
                fontName='Helvetica-Bold'
            )), 
            Paragraph(f"<b>₹ {total_income:,.2f}</b>", ParagraphStyle(
                'SummaryAmount',
                parent=table_text_style,
                fontSize=10,
                fontName='Helvetica-Bold',
                alignment=TA_RIGHT
            ))],
            [Paragraph("<b>Total Expenditure</b>", ParagraphStyle(
                'SummaryLabel',
                parent=table_text_style,
                fontSize=10,
                fontName='Helvetica-Bold'
            )), 
            Paragraph(f"<b>₹ {total_expense:,.2f}</b>", ParagraphStyle(
                'SummaryAmount',
                parent=table_text_style,
                fontSize=10,
                fontName='Helvetica-Bold',
                alignment=TA_RIGHT
            ))],
            [Paragraph("<b>Balance</b>", ParagraphStyle(
                'SummaryLabel',
                parent=table_text_style,
                fontSize=11,
                fontName='Helvetica-Bold',
                textColor=balance_color
            )), 
            Paragraph(f"<b>₹ {balance:,.2f}</b>", ParagraphStyle(
                'SummaryAmount',
                parent=table_text_style,
                fontSize=11,
                fontName='Helvetica-Bold',
                alignment=TA_RIGHT,
                textColor=balance_color
            ))]
        ]
        
        summary_table = Table(summary_data, colWidths=[130*mm, 40*mm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), table_header),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 2, primary_color),
            ('LINEABOVE', (0, -1), (-1, -1), 2, balance_color),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 15))
    else:
        story.append(Paragraph("<b>11. ESTIMATED EXPENDITURE</b>", heading_style))
        story.append(Paragraph("NIL", normal_style))
        story.append(Spacer(1, 10))
    
    # Objective
    story.append(Paragraph("<b>12. OBJECTIVE OF THE PROGRAMME</b>", heading_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(data['objective'], normal_style))
    story.append(Spacer(1, 10))
    
    # Student Development
    story.append(Paragraph("<b>13. CONTRIBUTION TO STUDENT DEVELOPMENT</b>", heading_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(data['student_development'], normal_style))
    story.append(Spacer(1, 10))
    
    # Institution Development
    story.append(Paragraph("<b>14. CONTRIBUTION TO INSTITUTION DEVELOPMENT / BRAND BUILDING</b>", heading_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(data['institution_development'], normal_style))
    story.append(Spacer(1, 15))
    
    # Signatures Section
    sig_data = [
        [Paragraph("Signature of Faculty Coordinator(s):", small_style), Paragraph("", small_style)],
        [Paragraph("", small_style), Paragraph("", small_style)],
        [Paragraph("<b>Recommendation of HOD:</b>", small_style), Paragraph("Recommended / Not Recommended", small_style)],
        [Paragraph("", small_style), Paragraph("", small_style)],
        [Paragraph("", small_style), Paragraph("Signature: ___________________", small_style)],
        [Paragraph("", small_style), Paragraph("", small_style)],
        [Paragraph("<b>Approval of Principal:</b>", small_style), Paragraph("Permitted / Not Permitted", small_style)],
        [Paragraph("", small_style), Paragraph("", small_style)],
        [Paragraph("", small_style), Paragraph("Signature: ___________________", small_style)],
    ]
    
    sig_table = Table(sig_data, colWidths=[85*mm, 85*mm])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(sig_table)
    
    # Footer
    story.append(Spacer(1, 10))
    footer_style = ParagraphStyle(
        'Footer',
        parent=small_style,
        fontSize=7,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        f"Generated by HIVE Hub IIC SOP Generator | {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        footer_style
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def main():
    # Header
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🚀 HIVE Hub</h1>
        <p class="header-subtitle">Hub for Innovation, Venture & Entrepreneurship | Advanced IIC SOP Generator</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📋 About HIVE Hub")
        st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; color: white;'>
        <b>Professional SOP Generator</b><br/>
        ✨ AI-Powered Content<br/>
        📊 IIC Guideline Compliant<br/>
        💼 Professional PDF Export<br/>
        🎯 Multi-Coordinator Support<br/>
        💰 Advanced Budget Sheet
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📊 IIC Activity Levels")
        st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; color: white; font-size: 0.85rem;'>
        <b>Level 1:</b> Talks (2-4 hrs)<br/>
        <b>Level 2:</b> Workshops (5-8 hrs)<br/>
        <b>Level 3:</b> Competitions (9-18 hrs)<br/>
        <b>Level 4:</b> Challenges (>18 hrs)
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎯 Current Quarter")
        today = date.today()
        quarter_info = get_quarter_info(today)
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                    padding: 1rem; border-radius: 10px; color: white;'>
        <b>{quarter_info['quarter']}</b> ({quarter_info['period']})<br/>
        <small>{quarter_info['thrust_area']}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Content
    st.markdown('<div class="section-header">📝 Event Information</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        
        department = st.text_area(
            "Department / Association / Club *",
            value="Department of Computer Science Engineering &\nInstitute Innovation Council",
            height=80,
            help="Enter organizing department(s)"
        )
        
        event_type = st.selectbox(
            "Nature of Programme *",
            options=list(EVENT_TYPES.keys()),
            help="Select the type of event"
        )
        
        event_info = EVENT_TYPES[event_type]
        st.info(f"**{event_info['level']}** • Duration: {event_info['duration']}")
        
        event_title = st.text_area(
            "Title of the Programme *",
            placeholder="e.g., Workshop on Artificial Intelligence and Machine Learning for Innovation",
            height=80,
            help="Enter the complete event title"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        
        # Date range instead of single date
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            event_date_from = st.date_input(
                "Event Start Date *",
                min_value=date.today(),
                help="Select the event start date"
            )
        with col_date2:
            event_date_to = st.date_input(
                "Event End Date *",
                min_value=event_date_from,
                value=event_date_from,
                help="Select the event end date"
            )
        
        # Manual quarter selection
        quarter_options = {
            "Q1 (Sep-Nov): Inspiration, Motivation, Ideation": "Q1",
            "Q2 (Dec-Feb): Validation, Concept Development": "Q2",
            "Q3 (Mar-May): Prototype, Business Model Development": "Q3",
            "Q4 (Jun-Aug): Start-up Ecosystem, Scale Up": "Q4"
        }
        
        selected_quarter_display = st.selectbox(
            "IIC Quarter *",
            options=list(quarter_options.keys()),
            help="Select the IIC quarter for this event"
        )
        
        selected_quarter = quarter_options[selected_quarter_display]
        quarter_info = IIC_ACTIVITIES[selected_quarter]
        quarter_info['quarter'] = selected_quarter
        
        st.success(f"📅 {quarter_info['quarter']} • {quarter_info['thrust_area']}")
        
        col_time1, col_time2 = st.columns(2)
        with col_time1:
            time_from = st.time_input("From Time *", value=dt_time(10, 0))
        with col_time2:
            time_to = st.time_input("To Time *", value=dt_time(16, 0))
        
        venue = st.text_input(
            "Venue *",
            placeholder="e.g., Seminar Hall, E-Learning Center",
            help="Enter the event venue"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Participants Section
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        participants = st.text_area(
            "Target Participants *",
            placeholder="e.g., I & II Year CSE, IT, AI&ML Students",
            height=80,
            help="Enter target participant groups"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        expected_audience = st.number_input(
            "Expected Audience *",
            min_value=1,
            value=50,
            help="Enter expected number of participants"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Faculty Coordinators Section (Dynamic)
    st.markdown('<div class="section-header">👥 Faculty Coordinator(s)</div>', unsafe_allow_html=True)
    
    for i, coordinator in enumerate(st.session_state.coordinators):
        st.markdown(f'<div class="form-card">', unsafe_allow_html=True)
        st.markdown(f"**Coordinator {i+1}**")
        
        col_c1, col_c2, col_c3 = st.columns([3, 3, 1])
        
        with col_c1:
            coordinator['name'] = st.text_input(
                f"Name",
                value=coordinator['name'],
                key=f"coord_name_{i}",
                placeholder="e.g., Dr. Rajesh Kumar"
            )
        
        with col_c2:
            coordinator['designation'] = st.text_input(
                f"Designation",
                value=coordinator['designation'],
                key=f"coord_desig_{i}",
                placeholder="e.g., Assistant Professor"
            )
        
        with col_c3:
            if len(st.session_state.coordinators) > 1:
                if st.button("🗑️", key=f"remove_coord_{i}", help="Remove coordinator"):
                    st.session_state.coordinators.pop(i)
                    st.rerun()
        
        coordinator['department'] = st.text_input(
            f"Department",
            value=coordinator['department'],
            key=f"coord_dept_{i}",
            placeholder="e.g., CSE"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("➕ Add Another Coordinator", key="add_coordinator"):
        st.session_state.coordinators.append({'name': '', 'designation': '', 'department': ''})
        st.rerun()
    
    # Resource Persons Section (Dynamic)
    st.markdown('<div class="section-header">🎤 Resource Person(s)</div>', unsafe_allow_html=True)
    
    for i, rp in enumerate(st.session_state.resource_persons):
        st.markdown(f'<div class="form-card">', unsafe_allow_html=True)
        
        col_rp_header = st.columns([6, 1])
        with col_rp_header[0]:
            st.markdown(f"**Resource Person {i+1}**")
        with col_rp_header[1]:
            if len(st.session_state.resource_persons) > 1:
                if st.button("🗑️", key=f"remove_rp_{i}", help="Remove resource person"):
                    st.session_state.resource_persons.pop(i)
                    st.rerun()
        
        col_rp1, col_rp2 = st.columns(2)
        
        with col_rp1:
            rp['name'] = st.text_input(
                "Name *",
                value=rp['name'],
                key=f"rp_name_{i}",
                placeholder="e.g., Dr. Aravind Krishnan"
            )
            
            rp['designation'] = st.text_input(
                "Designation",
                value=rp['designation'],
                key=f"rp_desig_{i}",
                placeholder="e.g., Chief Technology Officer"
            )
            
            rp['organization'] = st.text_input(
                "Organization",
                value=rp['organization'],
                key=f"rp_org_{i}",
                placeholder="e.g., Tech Innovations Pvt Ltd"
            )
        
        with col_rp2:
            rp['phone'] = st.text_input(
                "Phone Number",
                value=rp['phone'],
                key=f"rp_phone_{i}",
                placeholder="e.g., +91 9876543210"
            )
            
            rp['email'] = st.text_input(
                "Email Address",
                value=rp['email'],
                key=f"rp_email_{i}",
                placeholder="e.g., aravind@techinnovations.com"
            )
            
            rp['address'] = st.text_input(
                "Address",
                value=rp['address'],
                key=f"rp_address_{i}",
                placeholder="City, State"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("➕ Add Another Resource Person", key="add_rp"):
        st.session_state.resource_persons.append({
            'name': '', 'designation': '', 'organization': '', 
            'phone': '', 'email': '', 'address': ''
        })
        st.rerun()
    
    # Budget Section
    st.markdown('<div class="section-header">💰 Financial Details & Budget Statement</div>', unsafe_allow_html=True)
    
    # Income Sources
    st.markdown("#### A. Sources of Income")
    
    for i, source in enumerate(st.session_state.income_sources):
        col_inc1, col_inc2, col_inc3 = st.columns([4, 3, 1])
        
        with col_inc1:
            source['source'] = st.selectbox(
                f"Source {i+1}",
                options=INCOME_SOURCES,
                index=INCOME_SOURCES.index(source['source']) if source['source'] in INCOME_SOURCES else 0,
                key=f"income_source_{i}"
            )
        
        with col_inc2:
            source['amount'] = st.number_input(
                f"Amount (₹)",
                min_value=0.0,
                value=float(source['amount']),
                step=100.0,
                key=f"income_amount_{i}",
                format="%.2f"
            )
        
        with col_inc3:
            if len(st.session_state.income_sources) > 1:
                if st.button("🗑️", key=f"remove_income_{i}"):
                    st.session_state.income_sources.pop(i)
                    st.rerun()
    
    if st.button("➕ Add Income Source", key="add_income"):
        st.session_state.income_sources.append({'source': 'Departmental Fund', 'amount': 0.0})
        st.rerun()
    
    total_income = sum(source['amount'] for source in st.session_state.income_sources)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Income</div>
        <div class="metric-value">₹ {total_income:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Expenditure Items
    st.markdown("#### B. Expenditure Details")
    
    for i, item in enumerate(st.session_state.budget_items):
        col_exp1, col_exp2, col_exp3, col_exp4 = st.columns([3, 4, 2, 1])
        
        with col_exp1:
            item['category'] = st.selectbox(
                f"Category {i+1}",
                options=BUDGET_CATEGORIES,
                index=BUDGET_CATEGORIES.index(item['category']) if item['category'] in BUDGET_CATEGORIES else 0,
                key=f"budget_category_{i}"
            )
        
        with col_exp2:
            item['description'] = st.text_input(
                f"Description",
                value=item['description'],
                key=f"budget_desc_{i}",
                placeholder="Brief description"
            )
        
        with col_exp3:
            item['amount'] = st.number_input(
                f"Amount (₹)",
                min_value=0.0,
                value=float(item['amount']),
                step=100.0,
                key=f"budget_amount_{i}",
                format="%.2f"
            )
        
        with col_exp4:
            if len(st.session_state.budget_items) > 1:
                if st.button("🗑️", key=f"remove_budget_{i}"):
                    st.session_state.budget_items.pop(i)
                    st.rerun()
    
    if st.button("➕ Add Expenditure Item", key="add_budget"):
        st.session_state.budget_items.append({'category': 'Miscellaneous', 'description': '', 'amount': 0.0})
        st.rerun()
    
    total_expense = sum(item['amount'] for item in st.session_state.budget_items)
    balance = total_income - total_expense
    
    col_metric1, col_metric2, col_metric3 = st.columns(3)
    with col_metric1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Expenditure</div>
            <div class="metric-value">₹ {total_expense:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_metric2:
        balance_color = "#10b981" if balance >= 0 else "#ef4444"
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: {balance_color};">
            <div class="metric-label">Balance</div>
            <div class="metric-value" style="color: {balance_color};">₹ {balance:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_metric3:
        if balance < 0:
            status_color = "#ef4444"
            status_icon = "⚠️"
            status_text = "Budget Deficit"
        elif balance > 0:
            status_color = "#10b981"
            status_icon = "✅"
            status_text = "Budget Surplus"
        else:
            status_color = "#3b82f6"
            status_icon = "⚖️"
            status_text = "Balanced Budget"
        
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: {status_color};">
            <div class="metric-label">Budget Status</div>
            <div class="metric-value" style="color: {status_color}; font-size: 1.3rem;">{status_icon} {status_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Generate Button
    st.markdown("---")
    col_gen = st.columns([1, 2, 1])
    
    with col_gen[1]:
        generate_btn = st.button("🎯 GENERATE PROFESSIONAL SOP DOCUMENT", use_container_width=True, type="primary")
    
    if generate_btn:
        # Validation
        errors = []
        
        if not department.strip():
            errors.append("Department/Association/Club is required")
        if not event_title.strip():
            errors.append("Event title is required")
        if not venue.strip():
            errors.append("Venue is required")
        if not participants.strip():
            errors.append("Target participants is required")
        
        # Validate coordinators
        valid_coordinators = [c for c in st.session_state.coordinators if c['name'].strip()]
        if not valid_coordinators:
            errors.append("At least one coordinator with name is required")
        
        # Validate resource persons
        valid_resource_persons = [rp for rp in st.session_state.resource_persons if rp['name'].strip()]
        if not valid_resource_persons:
            errors.append("At least one resource person with name is required")
        
        if errors:
            st.error("⚠️ Please fix the following errors:")
            for error in errors:
                st.error(f"• {error}")
        else:
            with st.spinner("🔄 Generating your professional SOP document with AI-powered content..."):
                # Generate content
                day_name_from = event_date_from.strftime("%A")
                day_name_to = event_date_to.strftime("%A")
                date_str_from = event_date_from.strftime("%d.%m.%Y")
                date_str_to = event_date_to.strftime("%d.%m.%Y")
                
                # Create date display
                if event_date_from == event_date_to:
                    date_display = f"{date_str_from} ({day_name_from})"
                else:
                    date_display = f"{date_str_from} ({day_name_from}) to {date_str_to} ({day_name_to})"
                
                objective = generate_objective(event_title, event_type, quarter_info)
                student_dev = generate_student_development(event_title, event_type)
                institution_dev = generate_institution_development(event_title, event_type)
                
                # Prepare data
                sop_data = {
                    'department': department,
                    'event_type': event_type,
                    'event_level': event_info['level'],
                    'event_title': event_title,
                    'coordinators': valid_coordinators,
                    'date_day': date_display,
                    'time': f"From {time_from.strftime('%I:%M %p')} to {time_to.strftime('%I:%M %p')}",
                    'venue': venue,
                    'participants': participants,
                    'expected_audience': expected_audience,
                    'resource_persons': valid_resource_persons,
                    'budget_items': [item for item in st.session_state.budget_items if item['amount'] > 0],
                    'income_sources': [source for source in st.session_state.income_sources if source['amount'] > 0],
                    'objective': objective,
                    'student_development': student_dev,
                    'institution_development': institution_dev
                }
                
                # Generate PDF
                pdf_buffer = create_professional_pdf(sop_data)
                
                # Success
                st.markdown("""
                <div class="success-banner">
                    ✅ Professional SOP Document Generated Successfully!
                </div>
                """, unsafe_allow_html=True)
                
                # Preview
                st.markdown("### 📄 Document Preview")
                
                col_prev1, col_prev2 = st.columns([1, 1])
                
                with col_prev1:
                    st.markdown("#### 📋 Event Summary")
                    st.markdown(f"""
                    <div class="info-card">
                    <b>Event:</b> {event_title}<br/>
                    <b>Type:</b> {event_type} ({event_info['level']})<br/>
                    <b>Date:</b> {date_display}<br/>
                    <b>Quarter:</b> {quarter_info['quarter']} - {quarter_info['thrust_area']}<br/>
                    <b>Coordinators:</b> {len(valid_coordinators)}<br/>
                    <b>Resource Persons:</b> {len(valid_resource_persons)}<br/>
                    <b>Expected Audience:</b> {expected_audience}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_prev2:
                    st.markdown("#### 💰 Budget Summary")
                    st.markdown(f"""
                    <div class="info-card">
                    <b>Total Income:</b> ₹ {total_income:,.2f}<br/>
                    <b>Total Expenditure:</b> ₹ {total_expense:,.2f}<br/>
                    <b>Balance:</b> ₹ {balance:,.2f}<br/>
                    <b>Income Sources:</b> {len([s for s in st.session_state.income_sources if s['amount'] > 0])}<br/>
                    <b>Expense Items:</b> {len([i for i in st.session_state.budget_items if i['amount'] > 0])}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Content Preview
                with st.expander("📌 View Generated Objective", expanded=False):
                    st.write(objective)
                
                with st.expander("👨‍🎓 View Student Development Contribution"):
                    st.write(student_dev)
                
                with st.expander("🏛️ View Institution Development Contribution"):
                    st.write(institution_dev)
                
                # Download
                st.markdown("---")
                col_dl = st.columns([1, 2, 1])
                
                with col_dl[1]:
                    filename = f"IIC_SOP_{event_date_from.strftime('%Y%m%d')}_{event_title[:40].replace(' ', '_')}.pdf"
                    st.download_button(
                        label="📥 DOWNLOAD PROFESSIONAL SOP DOCUMENT (PDF)",
                        data=pdf_buffer,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary"
                    )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #1e3c72 0%, #7e22ce 100%); 
                border-radius: 15px; color: white; margin-top: 2rem;'>
        <h3 style='margin: 0; color: white;'>🚀 HIVE Hub</h3>
        <p style='margin: 0.5rem 0; font-size: 1.1rem;'><b>Hub for Innovation, Venture & Entrepreneurship</b></p>
        <p style='margin: 0; font-size: 0.9rem;'>Sri Ramakrishna Institute of Technology, Coimbatore</p>
        <p style='font-size: 0.85rem; margin-top: 1rem; opacity: 0.9;'>
            Empowering Innovation | Fostering Entrepreneurship | Building Future Leaders
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
