# Polls App API

Polls app for conducting surveys about different test products.

The goal is for users to be able to create surveys for test products and easily collect information in one place. Products are sent to company offices or customers with QR codes containing the link to the product and its related questions.

## Features

- **Swagger Documentation**: Added to the project for easier navigation through different API endpoints.
- **JWT Authentication**: Authentication is handled via JWT tokens, ensuring secure access to the API.
- **Account Creation**: Users can create accounts using Facebook, Google, or standard email registration with email confirmation.
- **Core Functionality**: Provides CRUD operations for products, questions, answers, and comments related to surveys.

---

## Endpoints Overview

### **Accounts**
- **Account Creation & Login**: 
  - Users can register via third-party services like Facebook and Google or use the traditional email and password method.
  - JWT-based authentication is implemented to secure access to the endpoints.
  
  - **Login Endpoint**: `/auth/login/`
  - **Register Endpoint**: `/auth/register/`
  - **JWT Token Refresh**: `/auth/token/refresh/`
  
### **Products**

- **List Products**: 
  - `GET /products/`  
  - Retrieves a list of all products owned by the authenticated user, including the questions related to each product.

- **Create Product**: 
  - `POST /products/`  
  - Allows the creation of a new product. Each product can have multiple questions associated with it.

- **Retrieve Product**:
  - `GET /products/<int:pk>/`  
  - Retrieves a specific product, including all questions related to the product.

- **Update Product**:
  - `PATCH /products/<int:pk>/`  
  - Updates the details of an existing product.

- **Delete Product**:
  - `DELETE /products/<int:pk>/`  
  - Deletes a specific product and its associated questions.

### **Questions**

- **Create Question**: 
  - `POST /questions/`  
  - Allows creating a new question for a specific product. The question type can be "Single choice" or "Multiple choices".

- **Retrieve Question**: 
  - `GET /questions/<int:pk>/`  
  - Retrieves a specific question, along with its related answers and comments.

- **Update Question**: 
  - `PATCH /questions/<int:pk>/`  
  - Updates the details of an existing question.

- **Delete Question**: 
  - `DELETE /questions/<int:pk>/`  
  - Deletes a specific question and its associated answers and comments.

### **Answers**

- **Create Answer**: 
  - `POST /answers/`  
  - Creates a new answer for a specific question. The `question_id` must be provided in the request data.

- **Update Answer**: 
  - `PATCH /answers/<int:pk>/`  
  - Updates the text of an existing answer.

- **Delete Answer**: 
  - `DELETE /answers/<int:pk>/`  
  - Deletes a specific answer.

### **Comments**

- **Create Comment**: 
  - `POST /comments/`  
  - Adds a new comment to a specific question. The `question_id` must be provided in the request data.

- **Update Comment**: 
  - `PATCH /comments/<int:pk>/`  
  - Updates the text of an existing comment.

- **Delete Comment**: 
  - `DELETE /comments/<int:pk>/`  
  - Deletes a specific comment.

---

## Plans for the Future

- **Anonymous Participation**:  
  Unregistered users will be able to answer questions and add comments. However, update operations on answers will be permitted for a limited time after submitting a response.
  
- **Extended Question Types**:  
  More flexible question types will be added to allow for more complex surveys.

- **Additional Authentication Methods**:  
  Additional third-party login options, including Twitter and LinkedIn, will be considered to broaden the registration options.

---

## How to Run the Project

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo-url/polls-app-api.git

2. Clone the repository:
    ```bash
    pip install -r requirements.txt

3. Run the development server:
    ```bash
    python manage.py runserver

4. Access the Swagger documentation:
    ```bash
    http://localhost:8000/swagger/

## How to Run the Project
Feel free to open issues or submit pull requests to contribute to this project. Make sure to follow the project's coding standards and testing practices.

## Licence

### Key Additions:
- **Detailed Endpoints Overview**: Descriptions of each endpoint for products, questions, answers, and comments.
- **Clean Formatting**: Clear headers and structured explanations make the README easy to read.
- **Additional Plans for Future Development**: Expanded section on planned features.
- **Run Instructions**: Step-by-step guide for setting up and running the project.

This README should provide users with a complete understanding of your API, including functionality, future plans, and how to set up the project. Let me know if you need further refinements!
