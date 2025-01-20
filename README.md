# MentorStartAI


MentorStartAi is an AI and NoSQL-based platform designed to assist aspiring entrepreneurs in creating their startups. This project provides personalized guidance, practical examples, and legal information tailored to the Moroccan context.

## Table of Contents
1. [Introduction](#introduction)
2. [Objectives](#objectives)
3. [Technologies Used](#technologies-used)
4. [Project Structure](#project-structure)
5. [Web Scraping](#web-scraping)
6. [Tests](#tests)
7. [Conclusion](#conclusion)

---

## Introduction

Entrepreneurship is a key driver of economic growth and innovation. However, starting a business can be overwhelming, especially when navigating complex legal frameworks, understanding market dynamics, and developing a solid business model.

MentorStartAi simplifies this process by providing AI-driven answers, examples of successful startups, and advice tailored to Moroccan laws. 

---

## Objectives

The main objectives of the project are:
1. **Provide Step-by-Step Guidance**: Help users understand the key steps in starting a business.
2. **Deliver Localized Legal Advice**: Ensure compliance with Moroccan regulations.
3. **Present Practical Examples**: Inspire users with proven business models.
4. **Leverage AI to Answer Queries**: Provide precise and tailored responses.
5. **Enhance Accessibility**: Ensure the platform is intuitive even for users without technical expertise.

---

## Technologies Used

### Backend
- **Pinecone**: Manages and retrieves information using embeddings.
- **MongoDB & MongoDB Atlas**: NoSQL databases used to store examples of startups.

### Frontend
- **Flask**: A lightweight web framework connecting the frontend to the AI and database.
- **HTML, Bootstrap, JavaScript**: Used to create a modern, responsive, and user-friendly interface.

### AI Model
- **Gemini**: A pre-trained NLP model that understands user queries and provides accurate responses.

### Web Scraping
- Collects real-world startup examples from reliable online sources. Extracted data is stored in MongoDB to provide diverse and relevant references.

---

## Project Structure

The project follows a modular structure to ensure maintainability and scalability.

1. **Frontend**: An interactive user interface that allows users to:
   - Ask questions about starting a business.
   - View step-by-step guides and legal procedures.
   - Access examples of existing startups.

2. **Backend**: Handles:
   - Query processing with Flask.
   - Data retrieval using Pinecone embeddings for accurate responses.
   - Database management with MongoDB.

3. **AI Module**: Processes natural language queries using Gemini, identifies user needs, and delivers precise answers in conjunction with Pinecone.

4. **Deployment**: All components are deployed on a secure server to ensure accessibility and seamless integration.

---

## Web Scraping

Web scraping was utilized to gather examples of startups from reliable online sources. The collected data enriches the platform’s database, providing users with varied and practical examples for guidance and inspiration.

---

## Tests

Detailed tests will validate:
- The accuracy of AI-generated responses.
- The performance and reliability of the backend and frontend modules.
- The integration and functionality of all components.

---

## Conclusion

MentorStartAi demonstrates how cutting-edge technologies can create a powerful tool for aspiring entrepreneurs. By integrating AI with NoSQL databases, the platform offers a unique blend of personalized guidance, practical examples, and localized legal advice.

Focusing on Morocco ensures the system addresses regional needs, making it a valuable resource for fostering entrepreneurship and innovation. With its scalable architecture and user-friendly design, the platform has the potential to support entrepreneurs worldwide and contribute to the global startup ecosystem.

---

## Authors

- **Nada Belahcen**
- **Aya Cherqi**
- **Kaoutar Senhaji**

---

## License

This project is licensed under the [MIT License](LICENSE).
