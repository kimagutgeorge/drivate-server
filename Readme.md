# Car Dealership Flask API

A comprehensive Flask REST API for managing a car dealership system with features for inventory management, user authentication, contact forms, blogs, reviews, and more.

## Features

- **Car Management**: Add, edit, view, and delete cars with detailed specifications
- **User Authentication**: Registration, login, forgot password, and JWT-based authentication
- **Google OAuth Integration**: Sign in with Google (configuration required)
- **File Upload Support**: Handle image uploads for cars, blogs, carousel, etc.
- **Review System**: Customer reviews with ratings and images
- **Blog Management**: Create and manage blog posts
- **FAQ System**: Categorized frequently asked questions
- **Contact Forms**: Handle customer inquiries
- **Selling System**: Allow customers to list cars for sale
- **Location & Make Management**: Organize cars by location and manufacturer
- **Real-time Communication**: Socket.IO support for real-time features

## Database Tables

The system includes the following main entities:

- `carousel` - Homepage carousel images and content
- `features` - Car features/amenities
- `makes` - Car manufacturers with logos
- `models` - Car models linked to manufacturers
- `body_style` - Car body types (sedan, SUV, etc.)
- `locations` - Dealership locations
- `cars` - Main car inventory with detailed specifications
- `car_images` - Multiple images per car
- `car_features` - Features associated with specific cars
- `reviews` - Customer reviews and ratings
- `blogs` - Blog posts with rich text content
- `faqs` & `faqs_category` - Categorized FAQ system
- `users` - User authentication and profiles
- `contact_us` - Customer contact form submissions
- `selling` & `car_to_sell_details` - Customer car selling system

## Installation

1. **Clone or create the project files**:
   ```bash
   mkdir car_dealership_api
   cd car_dealership_api
   ```

2. **Create the following files** with the provided code:
   - `config.py`
   - `models.py`
   - `functions.py`
   - `app.py`
   - `requirements.txt`

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables** (optional):
   ```bash
   export SECRET_KEY="your-secret-key-here"
   export JWT_SECRET_KEY="jwt-secret-string"
   export DATABASE_URL="sqlite:///car_dealership.db"
   export GOOGLE_OAUTH_CLIENT_ID="your-google-client-id"
   export GOOGLE_OAUTH_CLIENT_SECRET="your-google-client-secret"
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000` and will accept requests from `http://localhost:8081` and `http://192.168.2.38:8081`.

## API Endpoints

### Authentication
- `POST /register` - Register a new user
- `POST /login` - User login
- `POST /forgot-password` - Request password reset
- `POST /reset-password` - Reset password with token
- `GET /protected` - Protected route example

### Car Management
- `POST /add-car` - Add a new car
- `PUT /edit-car/<car_id>` - Edit car details
- `GET /view-car/<car_id>` - View specific car
- `GET /view-all-cars` - View all cars
- `DELETE /delete-car/<car_id>` - Delete a car

### Car Images
- `POST /add-car-image` - Add image to a car
- `GET /view-car-images/<car_id>` - Get all images for a car

### Car Features
- `POST /add-car-feature` - Add feature to a car
- `GET /view-car-features/<car_id>` - Get all features for a car

### Makes & Models
- `POST /add-make` - Add car manufacturer
- `GET /view-all-makes` - Get all manufacturers
- `POST /add-model` - Add car model
- `GET /view-all-models` - Get all models

### Features
- `POST /add-feature` - Add a new feature
- `GET /view-all-features` - Get all features
- `PUT /edit-feature/<feature_id>` - Edit feature
- `DELETE /delete-feature/<feature_id>` - Delete feature

### Locations
- `POST /add-location` - Add dealership location
- `GET /view-all-locations` - Get all locations

### Carousel
- `POST /add-carousel` - Add carousel item
- `GET /view-all-carousel` - Get all carousel items
- `PUT /edit-carousel/<carousel_id>` - Edit carousel item

### Blogs
- `POST /add-blog` - Create blog post
- `GET /view-all-blogs` - Get all blog posts
- `GET /view-blog/<blog_id>` - Get specific blog post

### Reviews
- `POST /add-review` - Add customer review

### Contact & Company Info
- `POST /add-contact-us` - Submit contact form
- `GET /view-all-contacts` - Get all contact submissions
- `POST /add-company-info` - Add company contact info

### FAQs
- `POST /add-faq-category` - Add FAQ category
- `POST /add-faq` - Add FAQ
- `GET /view-all-faqs` - Get all FAQs
- `GET /view-faqs-by-category/<category_id>` - Get FAQs by category

### Selling System
- `POST /add-selling` - Add seller information
- `POST /add-car-to-sell` - Add car for sale
- `GET /view-all-cars-to-sell` - Get all cars for sale

## File Upload

The system supports image uploads for:
- Car images
- Carousel images
- Blog images
- Review images
- Make logos
- Body style logos

Supported formats: PNG, JPG, JPEG, GIF
Maximum file size: 16MB

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:8081`
- `http://192.168.2.38:8081`

## Database

By default, the application uses SQLite with the database file `car_dealership.db`. You can change this by setting the `DATABASE_URL` environment variable.

## Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Secure file uploads with validation
- CORS protection
- SQL injection prevention through SQLAlchemy ORM

## Development

To extend the API:

1. Add new models in `models.py`
2. Create corresponding routes in `functions.py`
3. Update database by restarting the application (tables are created automatically)

## Production Deployment

For production deployment:

1. Set proper environment variables
2. Use a production WSGI server like Gunicorn
3. Configure a production database (PostgreSQL, MySQL)
4. Set up proper file storage (AWS S3, etc.)
5. Configure email service for password reset functionality
6. Set up Google OAuth credentials for social login

## Notes

- The application creates all database tables automatically on startup
- File uploads are stored in the `uploads/` directory
- JWT tokens expire after 24 hours
- Password reset tokens expire after 1 hour
- The forgot password feature currently returns the reset token in the response (remove this in production and send via email instead)