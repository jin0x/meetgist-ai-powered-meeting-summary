# 🚀 MeetGist: Meeting Intelligence Reimagined 🚀

_Transform your meetings into actionable insights with AI-powered intelligence_

---

## 🌟 About the Project

**MeetGist** is an AI-powered meeting intelligence platform that automates transcription, summarization, and knowledge sharing. This hackathon project tackles the challenge of inefficient meeting documentation and knowledge sharing by combining advanced AI technologies with seamless team collaboration tools.

---

## 👥 Meet the Team

We are a group of passionate developers and AI enthusiasts!

| Name                    | Role                                | LinkedIn                                                           | GitHub                                      |
| ----------------------- | ----------------------------------- | ------------------------------------------------------------------ | ------------------------------------------- |
| **John Leskas**         | Lead Architect and Team Coordinator | [LinkedIn](https://www.linkedin.com/in/john-leskas/)               | [GitHub](https://github.com/jin0x)          |
| **Andreas Vlaniadis**   | AI Engineer                         | [LinkedIn](https://www.linkedin.com/in/andreasvlaniadis/)          | [GitHub](https://github.com/Vlaniadisa)     |
| **Vasiliki Doropoulou** | AI Engineer                         | [LinkedIn](https://www.linkedin.com/in/vasilikidoropoulou/)        | [GitHub](https://github.com/vassod)         |
| **Muhammad Hanzla**     | Frontend Engineer                   | [LinkedIn](https://www.linkedin.com/in/muhammad-hanzla-787081279/) | [GitHub](https://github.com/hanzlikhan)     |
| **Sikander Nawaz**      | Backend Engineer                    | [LinkedIn](https://www.linkedin.com/in/sikander-nawaz/)            | [GitHub](https://github.com/sikander-nawaz) |

---

## 🎯 Problem & Our Solution

### ❓ The Challenge

- **Problem Statement:** Teams spend countless hours manually transcribing meetings, extracting key points, and sharing information across channels. This process is time-consuming, error-prone, and often results in lost insights.
- **Why It Matters:** Inefficient meeting documentation leads to missed action items, unclear decisions, and poor team alignment, ultimately affecting productivity and project outcomes.

### 💡 Our Innovative Approach

- **Solution:** MeetGist automates the entire meeting documentation workflow using AI, from transcription to summary generation and team sharing.
- **How It Works:** We combine AssemblyAI for accurate transcription, IBM Watson for intelligent summarization, IBM Granite for synthetic meeting generation, and Slack integration for seamless team communication.

---

## 🔍 Product Overview

### 🚀 What is MeetGist?

MeetGist is designed to streamline meeting documentation and knowledge sharing. It leverages advanced AI models to automatically process meeting recordings and generate comprehensive, actionable insights.

### 🌈 Key Features

- **Smart Transcription:** Automatic audio transcription with speaker detection _🎙️_
- **AI Summarization:** Intelligent extraction of key points, decisions, and action items _✨_
- **Synthetic Meetings:** AI-generated meeting summaries using IBM Granite _🤖_
- **Slack Integration:** Automated sharing and interactive command support _🔄_
- **Multiple Input Options:** Support for audio files, text transcripts, and synthetic meetings _📝_
- **Centralized Dashboard:** Easy access to all meeting content and insights _📊_

---

## 🛠️ Tech Stack

Our project is built with modern technologies:

- **Frontend:** Streamlit for a responsive and user-friendly interface
- **Backend:** FastAPI for efficient API endpoints
- **Database:** Supabase for secure data storage
- **AI Services:**
  - AssemblyAI for speech-to-text
  - IBM Granite for summarization
  - IBM Granite for synthetic meeting generation
- **Integration:** Slack API for team collaboration
- **Development:** Python, JavaScript

---

## 🔧 Architecture & Workflow

### 🖥️ Front-End & UI/UX

- **Tools:** Streamlit, Custom CSS
- **User Flow:**
  1. Upload meeting recording or input transcript
  2. View real-time processing status
  3. Access generated summaries and insights
  4. Share automatically with the team via Slack

### ⚙️ Back-End & API

- **Core Services:**
  - Transcription service using AssemblyAI
  - Summarization service using IBM Granite
  - Synthetic meeting generation using IBM Granite
  - Database management with Supabase
  - Slack bot for notifications and commands
- **Data Flow:** Secure file handling, async processing, and real-time updates

---

## 🚀 Installation & Setup

1. **Clone the Repository:**

   ```
   git clone https://github.com/yourusername/meetgist.git
   ```

2. **Install Dependencies:**

   ```
   cd meetgist
   uv venv
   source .venv/bin/activate # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Create a `.env` file with:

   ```
   ASSEMBLYAI_API_KEY=your_key
   IBM_API_KEY=your_key
   IBM_PROJECT_ID=your_id
   SLACK_BOT_TOKEN=your_token
   SLACK_CHANNEL_ID=your_channel
   ```

4. **Run the Application:**
   ```
   streamlit run app.py
   ```

---

## 🎮 How to Use

1. Navigate to the **Transcript Management** tab
2. Choose an input method:
   - Upload audio file (WAV/MP3)
   - Paste text transcript
   - Generate a synthetic meeting using IBM Granite
3. Process content and view results
4. Access summaries in the **Generate Summary** tab
5. Use Slack commands for quick access:
   ```
   /list summaries
   /list transcripts
   ```

---

## 📊 Future Roadmap

### 🚀 Upcoming Features

- **Advanced Analytics:** Meeting metrics and trend analysis
- **Custom AI Models:** Domain-specific summarization
- **Team Collaboration:** Comments and annotations
- **Integration:** MS Teams and Zoom support
- **Enterprise Features:** Role-based access and compliance tools

---

## 📈 Market Potential & Impact

- **Target Users:** Remote teams, project managers, meeting organizers
- **Market Size:** Growing remote work market ($1T+ by 2030)
- **Impact:**
  - 70% reduction in meeting documentation time
  - Improved team alignment and decision tracking
  - Enhanced knowledge management

---

## 💰 Revenue Model

- **SaaS Subscription:** Tiered pricing based on usage
- **Enterprise Plans:** Custom solutions with advanced features
- **API Access:** For integration with existing tools

---

## 🤝 Acknowledgements & Credits

- **AssemblyAI** for transcription technology
- **IBM Granite** for AI summarization
- **IBM Granite** for synthetic meeting generation
- **Streamlit** for frontend framework
- **Supabase** for database services

---

## 🔗 Useful Links

- **[Project Demo](https://meetgist.streamlit.app/)**
- **[Slides Presentation](https://storage.googleapis.com/lablab-static-eu/presentations/submissions/cm7huq4vq000p3b73pwghsclk/cm7huq4vq000p3b73pwghsclk-1740329207748_pq10u0nnf.pdf)**
- **[Video Presentation](https://storage.googleapis.com/lablab-video-submissions/cm6rtr6pf000c356ytb4y55ol/raw/submission-video-x-cm6rtr6pf000c356ytb4y55ol-cm7610ub3004i3b736g148x1a_8x17470gr2.mp4)**

---

**Built with ❤️ during Lab Lab AI Hackathon 2024**
