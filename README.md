# Egarage - Vehicle Service Booking System 🚗🔧

Hi there! 👋 This is **Egarage**, a web application I developed as my 8th-semester internship project at **Royal Technosoft Pvt Ltd**.

The main idea behind this project is simple: a platform where local mechanics can list their garage services (like Car Wash, Engine Repair) and customers can easily book them online.

## 🚀 What I Built (Key Features)
I built this project from scratch step-by-step. Here is what the system can do:
* **Two Types of Logins:** I created separate dashboards for 'Garage Owners' and 'Customers' using custom role-based logic in Django.
* **Owner Dashboard (CRUD):** Owners can add new services, upload service photos, edit details, or delete them. 
* **Customer Dashboard:** Users can see all the services added by owners. If a service is available, they get a blue **Book Now** button.
* **Live Booking Logic:** Once a user confirms the booking and pays the service charge (₹499), the database automatically updates. The service status instantly changes to "Currently Unavailable" (in Red) so nobody else can book it.
* **Secure Signup:** Built a custom user model and connected Gmail SMTP to verify emails when a new user creates an account.

## 💻 Tech Stack I Used
* **Backend:** Python, Django
* **Database:** SQLite
* **Frontend:** HTML, CSS (Custom Design & Flexbox)

## 👨‍💻 About Me
**Mihir Patel**
* Information Technology (Sem 8)
* Government Engineering College, Modasa
