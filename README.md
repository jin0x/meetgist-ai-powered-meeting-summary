# AI-Powered Meeting Summary & Decision Tracker

## 🌟 About the Project

**AI-Powered Meeting Summary & Decision Tracker** is a hackathon MVP focused on automating the meeting workflow. This project tackles the challenge of unstructured meeting data—such as tedious manual transcription, summarization, and decision tracking—by leveraging AI to generate concise meeting summaries, extract key decisions and action items, and optionally notify stakeholders via Slack.

---

## 👥 Meet the Team

We are a group of passionate developers, designers, and problem-solvers!

| Name           | Role   | LinkedIn                                                                         | GitHub                                                                         |
| -------------- | ------ | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **Teammate 1** | _Role_ | [LinkedIn](https://www.notion.so/README-19f761c30c8e80bb83decb887fad1466?pvs=21) | [GitHub](https://www.notion.so/README-19f761c30c8e80bb83decb887fad1466?pvs=21) |
| **Teammate 2** | _Role_ | [LinkedIn](https://www.notion.so/README-19f761c30c8e80bb83decb887fad1466?pvs=21) | [GitHub](https://www.notion.so/README-19f761c30c8e80bb83decb887fad1466?pvs=21) |
| **Teammate 3** | _Role_ | [LinkedIn](https://www.notion.so/README-19f761c30c8e80bb83decb887fad1466?pvs=21) | [GitHub](https://www.notion.so/README-19f761c30c8e80bb83decb887fad1466?pvs=21) |

_Feel free to add or remove rows as needed._

---

## 🎯 Problem & Our Solution

### ❓ The Challenge

- **Problem Statement:** Business meetings produce vast amounts of unstructured data. Manual transcription, summarization, and tracking decisions is both time-consuming and error-prone.
- **Why It Matters:** Capturing key insights and actionable items quickly can dramatically improve productivity and ensure nothing important is overlooked.

### 💡 Our Innovative Approach

- **Solution:** Leverage AI to automate transcript management and generate concise meeting summaries along with extracted key decisions and action items.
- **How It Works:** Users can upload or generate meeting transcripts. Audio files are transcribed using IBM Watson, and then the transcript is processed using Agno/IBM Granite to produce summaries and extract actionable insights. Optionally, notifications are sent via Slack to keep stakeholders informed.

---

## 🔍 Product Overview

### 🚀 What is AI-Powered Meeting Summary & Decision Tracker?

AI-Powered Meeting Summary & Decision Tracker is designed to streamline post-meeting workflows. It automates the creation, storage, and processing of meeting transcripts by leveraging AI to deliver actionable meeting summaries, extracted decisions, and task lists.

### Project Overview Video

[AI-Powered Meeting Summary & Decision Tracker](<attachment:7502986d-8f2d-453e-8db0-2af955f535d7:AI-Powered_Meeting_Summary_Decision_Tracker_(1)_(2).mp4>)

### **Description**

This hackathon MVP focuses on automating the meeting workflow. Our solution enables users to:

- Upload or generate meeting transcripts.
- Process transcripts using AI to create concise summaries.
- Extract key decisions and action items.
- Optionally send notifications (e.g., via Slack) to stakeholders.

### **Key Objectives**

- **Transcript Management:** Upload and store meeting transcripts (from audio or text).
- **AI-Driven Meeting Generation:** Generate meeting transcripts using AI agents based on provided topics or agendas.
- **Summary & Decision Tracking:** Process transcripts to produce meeting summaries, key decisions, and action items.
- **Notification Integration (Optional):** Send notifications upon successful summary generation.

---

## 📋 Detailed Overview

### 1. Overview

#### 1.1 Product Vision

Our product streamlines the post-meeting workflow by automating the creation, storage, and processing of meeting transcripts. It enables users to:

- **Upload and store transcripts:** Whether from audio files (transcribed via IBM Watson) or direct text input.
- **Generate meeting notes:** Use AI agents to simulate meeting conversations based on a topic or agenda.
- **Generate summaries:** Select any saved transcript to create a detailed meeting summary along with key decisions and action items.
- **Receive notifications:** Get Slack notifications containing meeting summaries and metadata.

#### 1.2 Problem Statement

Manual transcription and summarization of meetings results in lost time and potentially overlooked details. Our solution automates these processes to ensure that essential insights are captured and easily accessible.

#### 1.3 Goals and Objectives

- Automate Transcript Management to simplify uploading audio or text transcripts.
- Facilitate Meeting Generation through simulated conversations with AI agents.
- Empower Summary Generation by creating clear, concise meeting summaries with key decisions and action items.
- Enhance Collaboration via Slack integration to promptly notify stakeholders.
- Provide a user-friendly interface using Streamlit for managing transcripts and summaries.

---

### 2. Scope

#### 2.1 In-Scope Features

**Transcript Management**

- **Audio Upload:**
  - Upload audio files (WAV, MP3) and transcribe them using IBM Watson.
- **Transcript Upload:**
  - Upload or paste text transcripts directly.
- **Meeting Generator Agents:**
  - Initiate a new meeting session by providing a topic or agenda; AI agents generate a simulated conversation.
- **Storage:**
  - Store all transcripts in PostgreSQL with metadata (meeting title, date, source type).

**Meeting Summary & Decision Tracker**

- **Summary Generation:**
  - Select a saved transcript to generate a meeting summary, key decisions, and action items using Agno/IBM Granite.
- **Slack Integration:**
  - Optionally send a Slack notification containing the meeting summary and metadata.

---

### 3. User Personas

#### Business Professional

- **Role:** Team leader, project manager, or executive.
- **Needs:** Quick access to automated meeting summaries and actionable insights.
- **Pain Points:** Manual transcription, overlooked action items, and difficulty retrieving past meeting details.

#### Administrative/Support Staff

- **Role:** Office manager or assistant.
- **Needs:** Automated documentation to reduce manual data entry.
- **Pain Points:** Managing multiple meeting records and tracking follow-ups.

---

### 4. Features

#### Transcript Management

- Upload audio files (WAV, MP3) and transcribe them using IBM Watson.
- Upload or paste text transcripts.
- Provide AI agents to generate simulated meeting conversations based on a provided topic or agenda.
- Store all transcripts along with relevant metadata in PostgreSQL.

#### Meeting Summary & Decision Tracker

- View a list of saved transcripts.
- Select a transcript and generate a meeting summary, key decisions, and action items using Agno/IBM Granite.
- Display the generated summary and extracted information clearly in the UI.
- Optionally send a Slack notification with the meeting summary and metadata.

#### General Functionality

- Support multi-tab navigation between Transcript Management and Summary Generation views.
- Render a clear, user-friendly interface using Streamlit.
- Log key actions and errors for effective monitoring and troubleshooting.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For any questions or feedback, please reach out at [your.email@example.com].
