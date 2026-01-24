## Student Housing Marketplace Backend

A **production-style backend system** for a student housing marketplace, designed to support seekers searching for accommodations and property owners managing listings.
Built with scalability, security, and real-world deployment concerns in mind.

This project is **actively under development** and is being built in collaboration with a frontend engineer.

---

## 🚀 Features Implemented

### Authentication & Authorization

* Secure authentication using **JWT** with **access and refresh tokens**
* Tokens delivered via **HttpOnly cookies**
* **Google OAuth2 / OpenID Connect** integration
* Role-based access control (**seeker, owner, admin**)

### Core Backend APIs

* RESTful APIs for:

  * Users
  * Listings
 
* Authorization enforced per role and resource ownership

### Media Storage (House Images)

* House images are stored in an **S3-compatible object storage service** (currently **Backblaze B2**)
* Images **never pass through the backend server**, reducing load and improving scalability

**Upload flow:**

1. Owner initiates image upload from the frontend
2. Frontend requests an **image upload URL** from the backend
3. Backend requests a **pre-signed upload URL** from the S3-compatible cloud service
4. Backend returns the upload URL to the frontend
5. Frontend uploads images **directly to cloud storage**
6. Frontend sends the resulting **file keys** (not image files) to the backend
7. Backend persists image file keys in the database

**Download flow:**

1. Seeker requests house details from the frontend
2. Frontend requests image download URLs using the `house_id`
3. Backend retrieves stored file keys from the database
4. Backend generates **pre-signed download URLs** from cloud storage
5. Download URLs are returned to the frontend for direct image access

This approach ensures efficient media handling, better performance, and improved security.

### Asynchronous & Background Processing

* **Celery + RabbitMQ** for long-running and non-blocking tasks
* Independent background worker for:

  * Email delivery
  * Other async jobs
* Prevents blocking of HTTP request/response cycle

### Email Infrastructure

* Email delivery implemented using **Resend API**
* Migrated away from SMTP due to **Railway SMTP port restrictions**
* Reliable, production-ready email delivery pipeline

### User Email Verification

* Implemented **email-based user verification** during account creation

* Uses **itsdangerous `URLSafeTimedSerializer`** to generate time-bound, signed verification tokens

* Verification flow:

  1. User account is created in an unverified state
  2. Backend generates a signed verification linkToken and sends a verification email
  3. Email contains a verification link pointing directly to the verification route
  4. User clicks the link and is verified if the token is valid and unexpired
  5. After successful verification, the user is redirected to the frontend home page

***Login and business related routes are only accessible to user after user verification**

* Email sending and verification tasks are handled asynchronously by a **separate Celery worker**

* Backend dispatches verification email tasks to the worker, preventing request blocking

* **Resend API** is used for reliable delivery of verification emails

This setup ensures secure, scalable, and non-blocking user verification.

### Performance & Reliability

* **Rate limiting** to protect APIs from abuse
* **Caching** applied to expensive operations and heavy queries
* Debugged and resolved:

  * Message broker connectivity issues
  * Environment misconfigurations
  * Runtime and deployment errors

### Deployment & Infrastructure

* Fully **containerized** using **Docker** and **Docker Compose**
* Database hosted on **Neon (PostgreSQL)**
* Secure service-to-service communication
* Designed for consistent local and production deployments

### Architecture

* Applied **Clean Architecture principles**
* Modular, testable, and maintainable codebase
* Clear separation of concerns between:

  * Domain logic
  * Application services
  * Infrastructure
  * API layer

---

## 🏗️ Work in Progress / Planned Features

The following features are **not yet implemented** and are part of ongoing development:

* Full **search-to-selection flow** for housing seekers
* Linking seekers to listings they are interested in
* Viewing and tracking saved or shortlisted listings
* **Seeker ↔ Owner interaction flow**
* **Bidding / negotiation process** between seekers and owners
* Booking and confirmation lifecycle
* Notifications around bids, approvals, and updates

---

## 🧰 Tech Stack

* **Backend:** FastAPI (Python)
* **Database:** PostgreSQL (Neon)
* **Authentication:** JWT, Google OAuth2 / OpenID Connect
* **Async Tasks:** Celery, RabbitMQ
* **Email:** Resend API
* **Media Storage:** S3-compatible object storage (Backblaze B2)
* **Containerization:** Docker, Docker Compose
* **Hosting:** Railway (services), Neon (database)

---

## 📦 Running Locally

> Requires Docker and Docker Compose

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
docker compose up --build
```

Environment variables are managed via `.env` files and are not committed to version control.

---

## 🎯 Project Goals

* Build a **real-world backend system**, not a demo
* Practice production concerns: authentication, async tasks, caching, rate limiting, and deployments
* Serve as a **portfolio-grade backend project**
* Provide a solid foundation for future feature expansion

---

## 📌 Status

🛠 **Active development**
Core infrastructure and backend foundations are complete.
Marketplace workflows and advanced user interactions are in progress.