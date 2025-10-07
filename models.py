from config import *
# from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash

class Carousel(db.Model):
    __tablename__ = 'carousel'
    carousel_id = db.Column(db.Integer, primary_key=True)
    heading_1 = db.Column(db.String(200), nullable=False)
    heading_2 = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    image_alt = db.Column(db.String(255), nullable = False)
    
    def to_dict(self):
        return {
            'carousel_id': self.carousel_id,
            'heading_1': self.heading_1,
            'heading_2': self.heading_2,
            'image': self.image,
            'image_alt': self.image_alt
        }
    
    

class Features(db.Model):
    __tablename__ = 'features'
    feature_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    def to_dict(self):
        return {
            'feature_id': self.feature_id,
            'name': self.name
        }

class Categories(db.Model):
    __tablename__ = 'categories'
    category_id = db.Column(db.Integer, primary_key = True)
    category_name = db.Column(db.String(100), nullable = False)

    def to_dict(self):
        return{
            'category_id': self.category_id,
            'category_name' :self.category_name
        }

class Makes(db.Model):
    __tablename__ = 'makes'
    make_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo_image = db.Column(db.String(255))
    
    # Relationships
    models = db.relationship('Models', backref='make_ref', lazy=True)
    cars = db.relationship('Cars', backref='make_ref', lazy=True)
    
    def to_dict(self):
        return {
            'make_id': self.make_id,
            'name': self.name,
            'logo_image': self.logo_image
        }

class Models(db.Model):
    __tablename__ = 'models'
    model_id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    make = db.Column(db.Integer, db.ForeignKey('makes.make_id'), nullable=False)
    
    def to_dict(self):
        return {
            'model_id': self.model_id,
            'model_name': self.model_name,
            'make': self.make,
            'make_name': self.make_ref.name if self.make_ref else None
        }

class BodyStyle(db.Model):
    __tablename__ = 'body_style'
    style_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    logo_image = db.Column(db.String(255))
    
    # Relationships
    cars = db.relationship('Cars', backref='body_style_ref', lazy=True)
    
    def to_dict(self):
        return {
            'style_id': self.style_id,
            'name': self.name,
            'logo_image': self.logo_image
        }

class Locations(db.Model):
    __tablename__ = 'locations'
    location_id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(100), nullable=False)
    
    # Relationships
    cars = db.relationship('Cars', backref='location_ref', lazy=True)
    
    def to_dict(self):
        return {
            'location_id': self.location_id,
            'location_name': self.location_name
        }

class AboutUs(db.Model):
    __tablename__ = 'about_us'
    about_id = db.Column(db.Integer, primary_key=True)
    statement = db.Column(db.Text, nullable=False)
    image_1 = db.Column(db.Text, nullable =  False)
    image_2 = db.Column(db.Text, nullable = False)
    image_1_alt = db.Column(db.String(255))
    image_2_alt = db.Column(db.String(255))


    
    def to_dict(self):
        return {
            'about_id': self.about_id,
            'statement': self.statement,
            'image_1': self.image_1,
            'image_2': self.image_2,
            'image_1_alt': self.image_1_alt,
            'image_2_alt': self.image_2_alt,
        }

class WhyChooseUs(db.Model):
    __tablename__ = 'why_choose_us'
    why_id = db.Column(db.Integer, primary_key=True)
    icon = db.Column(db.String(100), nullable=False)
    heading = db.Column(db.String(200), nullable=False)
    statement = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        return {
            'why_id': self.why_id,
            'icon': self.icon,
            'heading': self.heading,
            'statement': self.statement
        }

class Blogs(db.Model):
    __tablename__ = 'blogs'
    blog_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    excerpt = db.Column(db.String(200), nullable = False)
    image = db.Column(db.Text)
    image_alt = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'blog_id': self.blog_id,
            'title': self.title,
            'image': self.image,
            'image_alt': self.image_alt,
            'excerpt' : self.excerpt,
            'content': self.content,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Reviews(db.Model):
    __tablename__ = 'reviews'
    review_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    reviewer = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    text = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    car_id = db.Column(db.Integer, db.ForeignKey('cars.car_id'))
    status = db.Column(db.String(10), default = "Inactive")
    
    
    def to_dict(self):
        return {
            'review_id': self.review_id,
            'title': self.title,
            'rating': self.rating,
            'reviewer': self.reviewer,
            'date': self.date.isoformat() if self.date else None,
            'text': self.text,
            'image': self.image,
            'status': self.status,
            'car_id': self.car_id
        }

# class FaqsCategory(db.Model):
#     __tablename__ = 'faqs_category'
#     category_id = db.Column(db.Integer, primary_key=True)
#     category = db.Column(db.String(100), nullable=False)
    
#     # Relationships
#     faqs = db.relationship('Faqs', backref='category_ref', lazy=True)
    
#     def to_dict(self):
#         return {
#             'category_id': self.category_id,
#             'category': self.category
#         }


class FaqsCategories(db.Model):
    __tablename__ = 'faqs_categories'
    category_id = db.Column(db.Integer, primary_key = True)
    category_name = db.Column(db.String(100), nullable = False)

    faqs = db.relationship('Faqs', backref='category_ref', lazy=True)

    def to_dict(self):
        return{
            'category_id': self.category_id,
            'category_name' :self.category_name
        }

class Faqs(db.Model):
    __tablename__ = 'faqs'
    faq_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('faqs_categories.category_id'), nullable=False)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        return {
            'faq_id': self.faq_id,
            'category_id': self.category_id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category_ref.category_name if self.category_ref else None
        }

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    contact_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'phone', 'email', 'social'
    value = db.Column(db.String(255), nullable=False)  # phone number, email, or platform name
    fontawesome_icon = db.Column(db.String(500), nullable=True)  # website link for phone/email
    social_link = db.Column(db.String(500), nullable=True)  # social media profile link
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'contact_id': self.contact_id,
            'name': self.name,
            'type': self.type,
            'value': self.value,
            'icon': self.fontawesome_icon,
            'social_link': self.social_link,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ContactUs(db.Model):
    __tablename__ = 'contact_us'
    contact_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    full_name = db.Column(db.String(100), nullable = False)
    phone = db.Column(db.Integer, nullable = False)
    email = db.Column(db.String(100))
    message = db.Column(db.Text, nullable=False)
    contact_type = db.Column(db.String(20), default='Contact')
    status = db.Column(db.String(15), default='Unread')

    def to_dict(self):
        return{
            'contact_id': self.contact_id,
            'name': self.full_name,
            'phone': self.phone,
            'email': self.email,
            'message': self.message,
            'contact_type': self.contact_type,
            'status' : self.status,
        }

class Enquiries(db.Model):
    __tablename__ = 'enquiries'
    enquiry_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(150), nullable = False)
    car = db.Column(db.String(255), nullable = False)
    phone = db.Column(db.Integer, nullable = False)
    address = db.Column(db.String(255), nullable = False)
    message = db.Column(db.Text)
    enquiry_mode = db.Column(db.String(20))
    status = db.Column(db.String(15), default='Unread')

    def to_dict(self):
        return{
            'enquiry_id': self.enquiry_id,
            'name': self.name,
            'email' :self.email,
            'car' :self.car,
            'phone' :self.phone,
            'address' :self.address,
            'message' :self.message,
            'enquiry_mode': self.enquiry_mode,
            'status': self.status
        }

class CompanyInfo(db.Model):
    __tablename__ = 'company_info'
    info_id = db.Column(db.Integer, primary_key=True)
    contact = db.Column(db.String(200), nullable=False)
    contact_type = db.Column(db.Integer, nullable=False)  # 1=email, 2=phone, 3=external link
    link = db.Column(db.String(255))
    
    def to_dict(self):
        return {
            'info_id': self.info_id,
            'contact': self.contact,
            'contact_type': self.contact_type,
            'link': self.link
        }

class Cars(db.Model):
    __tablename__ = 'cars'
    car_id = db.Column(db.Integer, primary_key=True)
    
    # Basic vehicle information
    name = db.Column(db.String(200), nullable=True)  # NEW: Vehicle name like "TOYOTA CAMPRI BILAKAO"
    price = db.Column(db.Numeric(15, 2), nullable=True)  # NEW: Vehicle price
    condition = db.Column(db.String(50), nullable=True)  # NEW: New/Used condition
    model_id = db.Column(db.Integer, db.ForeignKey('models.model_id'), nullable=True)  # NEW: Link to specific model
    
    # Existing fields
    make = db.Column(db.Integer, db.ForeignKey('makes.make_id'), nullable=False)
    body_style = db.Column(db.Integer, db.ForeignKey('body_style.style_id'), nullable=True)  # Made nullable
    mileage = db.Column(db.String(50))
    year = db.Column(db.Integer, nullable=False)
    engine = db.Column(db.String(100))  # This will store engine_size
    location = db.Column(db.Integer, db.ForeignKey('locations.location_id'), nullable=True)
    ref_no = db.Column(db.String(50), unique=True)  # This stores ref_number
    model_code = db.Column(db.String(50))
    steering = db.Column(db.String(50))  # This stores steering_wheel
    exterior_color = db.Column(db.String(50))
    fuel = db.Column(db.String(50))  # This stores fuel_type
    seats = db.Column(db.Integer)
    interior_color = db.Column(db.String(50))
    seats_color = db.Column(db.String(50))
    drive = db.Column(db.String(50))  # This stores drive_type
    doors = db.Column(db.String(50))
    transmission = db.Column(db.String(50))
    weight = db.Column(db.String(50))
    status = db.Column(db.String(20), default='In Stock')
    
    # Timestamp fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    model_ref = db.relationship('Models', backref='cars_with_model', lazy=True)  # NEW: Relationship to Models
    images = db.relationship('CarImages', backref='car_ref', lazy=True, cascade='all, delete-orphan')
    features = db.relationship('CarFeatures', backref='car_ref', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Reviews', backref='car_ref', lazy=True)
    
    def to_dict(self):
        return {
            'car_id': self.car_id,
            'name': self.name,
            'price': float(self.price) if self.price else None,
            'condition': self.condition,
            'model_id': self.model_id,
            'model_name': self.model_ref.model_name if self.model_ref else None,
            'make': self.make,
            'make_name': self.make_ref.name if self.make_ref else None,
            'body_style': self.body_style,
            'body_style_name': self.body_style_ref.name if self.body_style_ref else None,
            'mileage': self.mileage,
            'year': self.year,
            'engine': self.engine,
            'location': self.location,
            'location_name': self.location_ref.location_name if self.location_ref else None,
            'ref_no': self.ref_no,
            'model_code': self.model_code,
            'steering': self.steering,
            'exterior_color': self.exterior_color,
            'fuel': self.fuel,
            'seats': self.seats,
            'interior_color': self.interior_color,
            'seats_color': self.seats_color,
            'drive': self.drive,
            'doors': self.doors,
            'transmission': self.transmission,
            'weight': self.weight,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'images': [img.to_dict() for img in self.images],
            'features': [feat.to_dict() for feat in self.features],
            'status': self.status
        }



class CarImages(db.Model):
    __tablename__ = 'car_images'
    car_image_id = db.Column(db.Integer, primary_key=True)
    car = db.Column(db.Integer, db.ForeignKey('cars.car_id'), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    
    def to_dict(self):
        return {
            'car_image_id': self.car_image_id,
            'car': self.car,
            'image': self.image
        }

class CarFeatures(db.Model):
    __tablename__ = 'car_features'
    car_feature_id = db.Column(db.Integer, primary_key=True)
    feature = db.Column(db.Integer, db.ForeignKey('features.feature_id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.car_id'), nullable=False)
    
    # Relationships
    feature_ref = db.relationship('Features', backref='car_features')
    
    def to_dict(self):
        return {
            'car_feature_id': self.car_feature_id,
            'feature': self.feature,
            'car_id': self.car_id,
            'feature_name': self.feature_ref.name if self.feature_ref else None
        }

class Currency(db.Model):
    __tablename__ = 'currency'
    currency_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    
    def to_dict(self):
        return {
            'currency_id': self.currency_id,
            'name': self.name
        }

class Selling(db.Model):
    __tablename__ = 'selling'
    sell_id = db.Column(db.Integer, primary_key=True)
    seller = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')
    
    # Relationships
    car_details = db.relationship('CarToSellDetails', backref='seller_ref', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'sell_id': self.sell_id,
            'seller': self.seller,
            'phone_number': self.phone_number,
            'email': self.email,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
class Tracker(db.Model):
    __tablename__ = 'tracker'
    tracker_id = db.Column(db.Integer, primary_key = True)
    car_id = db.Column(db.Integer, nullable = False)
    car_count = db.Column(db.Integer, nullable = False)

    def to_dict(self):
        return{
            'tracker_id' : self.tracker_id,
            'car_id' : self.car_id,
            'car_count' : self.car_count
        }

class CarToSellDetails(db.Model):
    __tablename__ = 'car_to_sell_details'
    car_sell_id = db.Column(db.Integer, primary_key=True)
    selling_id = db.Column(db.Integer, db.ForeignKey('selling.sell_id'), nullable=False)
    make = db.Column(db.Integer, db.ForeignKey('makes.make_id'), nullable=False)
    model = db.Column(db.Integer, db.ForeignKey('models.model_id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    mileage = db.Column(db.String(50))
    selling_price = db.Column(db.Numeric(15, 2), nullable=False)
    fuel_type = db.Column(db.String(50))
    body_type = db.Column(db.Integer, db.ForeignKey('body_style.style_id'), nullable=False)
    transmission = db.Column(db.String(50))
    steering = db.Column(db.String(50))
    drive_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    
    # Relationships
    make_ref = db.relationship('Makes', backref='selling_cars')
    model_ref = db.relationship('Models', backref='selling_cars')
    body_type_ref = db.relationship('BodyStyle', backref='selling_cars')
    images = db.relationship('CarSellingImages', backref='car_sell_ref', lazy=True, cascade='all, delete-orphan')
    features = db.relationship('CarSellingFeatures', backref='car_sell_ref', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'car_sell_id': self.car_sell_id,
            'selling_id': self.selling_id,
            'make': self.make,
            'make_name': self.make_ref.name if self.make_ref else None,
            'model': self.model,
            'model_name': self.model_ref.model_name if self.model_ref else None,
            'year': self.year,
            'mileage': self.mileage,
            'selling_price': float(self.selling_price) if self.selling_price else None,
            'fuel_type': self.fuel_type,
            'body_type': self.body_type,
            'body_type_name': self.body_type_ref.name if self.body_type_ref else None,
            'transmission': self.transmission,
            'steering': self.steering,
            'drive_type': self.drive_type,
            'description': self.description,
            'images': [img.to_dict() for img in self.images],
            'features': [feat.to_dict() for feat in self.features]
        }

class CarSellingImages(db.Model):
    __tablename__ = 'car_selling_images'
    car_selling_image_id = db.Column(db.Integer, primary_key=True)
    car_to_sell_id = db.Column(db.Integer, db.ForeignKey('car_to_sell_details.car_sell_id'), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    
    def to_dict(self):
        return {
            'car_selling_image_id': self.car_selling_image_id,
            'car_to_sell_id': self.car_to_sell_id,
            'image': url_for('static', filename=f'images/selling/{self.image}', _external=True) 
        }

class CarSellingFeatures(db.Model):
    __tablename__ = 'car_selling_features'
    id = db.Column(db.Integer, primary_key=True)
    feature = db.Column(db.Integer, db.ForeignKey('features.feature_id'), nullable=False)
    car_to_sell_id = db.Column(db.Integer, db.ForeignKey('car_to_sell_details.car_sell_id'), nullable=False)
    
    # Relationships
    feature_ref = db.relationship('Features', backref='selling_car_features')
    
    def to_dict(self):
        return {
            'id': self.id,
            'feature': self.feature,
            'car_to_sell_id': self.car_to_sell_id,
            'feature_name': self.feature_ref.name if self.feature_ref else None
        }

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(50), default= "Drivate")
    
    def set_password(self, password):
        # Simple password storage (not secure - for development only)
        self.password = password
    
    def check_password(self, password):
        # Simple password check (not secure - for development only)
        return self.password == password
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_admin': self.is_admin,
            'name': self.name
        }

class PasswordResets(db.Model):
    __tablename__ = 'password_resets'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'token': self.token,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'used': self.used
        }


