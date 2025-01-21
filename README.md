# MentorStartAI: Empowering Moroccan Entrepreneurs

## Overview

**MentorStartAI** is an AI-powered platform designed to assist aspiring entrepreneurs in Morocco with personalized guidance, localized legal advice, and practical examples to help them create successful startups. This tool combines cutting-edge technologies like AI, web scraping, and NoSQL databases to bridge the knowledge gap and make entrepreneurship accessible to everyone.

---

## Features

- **Step-by-Step Guidance**: A clear roadmap for startup creation, from ideation to execution.
- **Localized Legal Advice**: Insights into Moroccan laws and regulations.
- **Practical Examples**: Real-world startup examples to inspire and guide users.
- **AI-Powered Assistance**: Accurate, tailored answers to user queries using advanced NLP models.
- **Accessible Design**: A user-friendly interface for individuals of all technical skill levels.

---

## Tools and Technologies

### **Backend**
- **Pinecone**: Manages embeddings for efficient query processing.
- **MongoDB & MongoDB Atlas**: NoSQL databases storing structured data and real-world startup examples.

### **Frontend**
- **Flask**: Lightweight web framework connecting the frontend with backend and AI.
- **HTML, Bootstrap, and JavaScript**: Responsive and interactive interface.

### **AI Model**
- **Gemini AI**: Processes natural language queries with advanced NLP.
- **facebook/seamless-m4t-v2-large**: Provides Darija translation support.

### **Web Scraping**
- Collects real-world startup data to enrich the MongoDB database.

---

## Project Structure

1. **Frontend Module**:
- User interface for submitting questions and viewing results.
- Built with HTML, Bootstrap, and JavaScript.

2. **Backend Module**:
- Query processing and database management.
- Powered by Flask, Pinecone, and MongoDB.

3. **AI Module**:
- Processes and interprets user queries.
- Provides precise, actionable answers.

4. **Deployment and Integration**:
- Securely deployed for accessibility and scalability.

---

## Usage

### Prerequisites
- Python 3.8+
- MongoDB
- Flask
- Necessary libraries listed in `requirements.txt`

---

## Authors

This project was developed by:
- **Hiba Benkaddour**
- **Belahcen Nada**
- **Cherqi Aya**
- **Senhaji Kaoutar**

---

### Installation

Clone the repository:
```bash
git clone https://github.com/your-username/MentorStartAI.git
cd MentorStartAI
