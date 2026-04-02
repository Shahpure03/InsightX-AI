
# 🧠 ET Insight AI — News Understanding Engine

## 📌 Overview

ET Insight AI is an AI-powered news experience that transforms passive reading into active understanding. Instead of just showing what happened, the system explains why it matters, how it affects the user personally, what actions can be taken next, and what future developments to watch.

---

## 🚨 Problem

Traditional news platforms:

* Deliver the same content to everyone
* Focus on events, not consequences
* Lack personalization and actionable insights

This results in:

* Information overload
* Low understanding
* Low engagement

---

## 💡 Solution

ET Insight AI introduces a multi-layered system that:

* Personalizes news feed based on user type
* Generates cause-effect impact chains
* Explains personal relevance
* Suggests actionable next steps
* Predicts what to watch next

---

## 🔥 Key Features

### 1. Personalized Feed

* News tailored to user type (Student, Investor, General)

---

### 2. Impact Reasoning Engine ⭐

* Generates structured cause-effect chains

**Example:**

```
Conflict → Oil supply ↓ → Oil prices ↑ → Inflation ↑
```

---

### 3. Personal Impact Layer

* Explains how news affects the individual user

---

### 4. Action Suggestions

* Provides contextual, non-prescriptive actions users can take

---

### 5. What to Watch Next

* Predicts future developments related to the news

---

### 6. Confidence Layer

* Adds uncertainty awareness and responsible AI disclaimers

---

## ✨ Extension Features

* 🌐 Multi-language support (English, Hindi, Marathi)
* 🎧 Audio mode (Text-to-Speech)
* 🎥 Video mode (UI simulated for demo)

---

## ⚙️ Tech Stack

* **Frontend:** Antigravity (UI builder)
* **AI (Planned):** OpenAI API / Google Gemini API
* **Audio:** gTTS / ElevenLabs
* **Translation:** LLM-based / LibreTranslate
* **Deployment:** Vercel

---

## 🎬 Demo Flow

1. User selects profile (Student / Investor / General)
2. Personalized feed is displayed
3. User selects a news article
4. System generates:

   * Impact chain
   * Personal impact
   * Action suggestions
   * What to watch next
5. Optional:

   * Language toggle
   * Audio playback
   * Video preview

---

## 🧱 Architecture Overview

The system follows a modular pipeline:

```
User → Feed Agent → Event Understanding → Impact Reasoning → 
Personalization → Action Layer → Prediction → Confidence Layer
```

---

## 📊 Impact Model

### Assumptions:

* Average user understanding of news: ~30%
* With system: ~70%

### Impact:

* ~2x improvement in comprehension
* Increased engagement and retention
* Better decision-making

---

## ⚠️ Prototype Note

This project is a **functional prototype/demo built within hackathon constraints**.

* The current implementation uses **hardcoded data and responses** to demonstrate the complete user flow and experience.
* AI-generated outputs such as:

  * Impact chains
  * Personalization
  * Action suggestions
  * Predictions
    are **simulated for demonstration purposes only**.

---

## 🔮 Intended Full Implementation

In a production-ready system, real AI APIs would be integrated, including:

* **Google Gemini API**
* **OpenAI API**

These would power:

* Event understanding
* Impact reasoning generation
* Personalized insights
* Action recommendations
* Multi-language translation
* Audio/video generation

👉 The current architecture is designed to seamlessly support these integrations.

---

## 🚀 Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/Shahpure03/ET-HACKATHON
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Run Locally

```bash
npm run dev
```

## 🌐 Live Demo

👉 https://insight-x-ai.vercel.app

---

## 📽️ Demo Video

 https://drive.google.com/drive/folders/1g7Qo_dHkeFFTkByJK4jvO2jMRysIe0Me?usp=sharing
  
---

## 🧠 Key Insight

> “We don’t just personalize the news you see — we help you understand its impact, act on it, and anticipate what comes next.”

---

## 📌 Note

* Video generation is simulated for demo purposes
* Designed for scalability into a full AI-powered system

---
# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
