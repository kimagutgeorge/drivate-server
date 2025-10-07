from models import *
from config import *

# 
# utility classses
#
def validate_user(user_logged_in):
    
    user = Users.query.filter_by(email = user_logged_in).first()
    print("User Email", user.email)
    return True
    # # Clean the input thoroughly
    # original_user = user_logged_in.replace("-", " ")
    # cleaned_user = ' '.join(original_user.split()).strip()
    # print("Cleaned user input: '" + str(cleaned_user) + "'")
    
    # # Get all users and compare after normalizing both sides
    # all_users = Users.query.all()
    
    # for user in all_users:
    #     # Normalize the database name the same way
    #     db_name_normalized = ' '.join(user.email.split()).strip()
        
    #     if db_name_normalized.lower() == cleaned_user.lower():
    #         print(f"Match found: '{user.email}' -> '{db_name_normalized}'")
    #         return True
    
        
    # print("No user found")
    # return False


def process_images(image_files, destination_folder, max_width=1920, max_height=1080, quality=85):
    """
    Process multiple images: resize, maintain transparency, and convert to AVIF
    
    Args:
        image_files: List of FileStorage objects or single FileStorage object
        destination_folder: Folder to save processed images
        max_width: Maximum width for resizing (default: 1920)
        max_height: Maximum height for resizing (default: 1080)  
        quality: AVIF quality (default: 85)
    
    Returns:
        List of processed filenames or None if processing fails
    """
    
    # Ensure image_files is a list
    if not isinstance(image_files, list):
        image_files = [image_files]
    
    processed_filenames = []
    temp_files = []  # Keep track of temp files for cleanup
    
    try:
        for image_file in image_files:
            if not image_file or image_file.filename == '':
                continue
                
            if not allowed_file(image_file.filename):
                # Clean up any temp files created so far
                cleanup_temp_files(temp_files)
                raise ValueError(f"Invalid file type for {image_file.filename}")
            
            # Generate unique filename
            unique_filename = str(uuid.uuid4())
            original_filename = secure_filename(image_file.filename)
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            temp_filename = f"{unique_filename}_temp.{file_extension}"
            avif_filename = f"{unique_filename}.avif"
            
            # Paths
            temp_path = os.path.join(destination_folder, temp_filename)
            avif_path = os.path.join(destination_folder, avif_filename)
            
            # Save temporary file
            image_file.save(temp_path)
            temp_files.append(temp_path)
            
            # Process and convert to AVIF with transparency support
            if convert_to_avif_with_transparency(temp_path, avif_path, max_width, max_height, quality):
                processed_filenames.append(avif_filename)
            else:
                # Clean up and raise error
                cleanup_temp_files(temp_files)
                raise Exception(f"Failed to process image: {original_filename}")
        
        # Clean up temporary files
        cleanup_temp_files(temp_files)
        
        return processed_filenames
        
    except Exception as e:
        # Clean up temporary files in case of error
        cleanup_temp_files(temp_files)
        # Clean up any successfully processed files
        for filename in processed_filenames:
            file_path = os.path.join(destination_folder, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        raise e

def convert_to_avif_with_transparency(input_path, output_path, max_width=1920, max_height=1080, quality=85):
    """
    Convert image to AVIF while preserving transparency
    
    Args:
        input_path: Path to input image
        output_path: Path for output AVIF
        max_width: Maximum width for resizing
        max_height: Maximum height for resizing
        quality: AVIF quality (0-100)
    
    Returns:
        Boolean indicating success
    """
    try:
        with Image.open(input_path) as img:
            # Convert RGBA to RGB only if no transparency is present
            if img.mode in ('RGBA', 'LA'):
                # Check if image actually has transparency
                if img.mode == 'RGBA':
                    # Check alpha channel
                    alpha = img.getchannel('A')
                    if alpha.getbbox() is not None and min(alpha.getdata()) < 255:
                        # Image has transparency, keep RGBA
                        pass
                    else:
                        # No actual transparency, convert to RGB
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        img = background
                elif img.mode == 'LA':
                    # Grayscale with alpha
                    alpha = img.getchannel('A')
                    if alpha.getbbox() is not None and min(alpha.getdata()) < 255:
                        # Convert to RGBA to preserve transparency
                        img = img.convert('RGBA')
                    else:
                        # No transparency, convert to RGB
                        img = img.convert('RGB')
            elif img.mode == 'P':
                # Palette mode - check for transparency
                if 'transparency' in img.info:
                    img = img.convert('RGBA')
                else:
                    img = img.convert('RGB')
            elif img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')
            
            # Resize image while maintaining aspect ratio
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save as AVIF
            img.save(output_path, 'AVIF', quality=quality, speed=6)
            return True
            
    except Exception as e:
        print(f"Error converting image to AVIF: {e}")
        return False

def cleanup_temp_files(temp_files):
    """Clean up temporary files"""
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except OSError as e:
                print(f"Error removing temp file {temp_file}: {e}")


# 
# end of utility classes 
#


# login
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # print(generate_password_hash(password))
    if not username or not password:
        return jsonify({"message":"3"}), 200 # no credentials

    user = Users.query.filter_by(email=username).first()

    if user and check_password_hash(user.password, password):
        return jsonify({"success":True, "message": "1", "user": user.email}), 200
    else:
        return jsonify({"success": False, "message": "2"}), 200 # user does not exist

# fetch carousels
@app.route('/get-carousels', methods=['GET'])
def get_carousel():
    try:
        carousels = Carousel.query.order_by(Carousel.carousel_id.desc()).all()

        carousel_data = []  # Initialize empty list
        for carousel in carousels:
            # Fix the path to match your actual folder structure
            image_url = url_for('static', filename=f'images/carousel/{carousel.image}', _external=True)
            
            # Create individual carousel object
            carousel_item = {
                'id': carousel.carousel_id,
                'heading_1': carousel.heading_1,
                'heading_2': carousel.heading_2,
                'image_url': image_url,
                'image_alt': carousel.image_alt,
            }
            
            # APPEND to list instead of overwriting
            carousel_data.append(carousel_item)

        return jsonify({
            'message': '1',
            'success': True,
            'carousels': carousel_data
        }), 200
    
    except Exception as e:
        print(f"Error fetching carousel: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch carousel',
            'details': str(e)
        }), 500
    
# add carousel
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_avif(input_path, output_path):
    """Convert image to AVIF format"""
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (for transparency handling)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Save as AVIF with optimization
            img.save(output_path, 'AVIF', quality=80, optimize=True)
            return True
    except Exception as e:
        print(f"Error converting to AVIF: {e}")
        return False

@app.route('/add-carousel', methods=['POST'])
def add_carousel():
    
    try:
        # Get form data
        heading_1 = request.form.get('heading_1')
        heading_2 = request.form.get('heading_2')
        image_file = request.files.get('image')
        image_alt = request.form.get('image_alt')
        
        # Validation
        if not heading_1 or not heading_2:
            return jsonify({
                'success': False, 
                'error': 'Both headings are required'
                }), 200
        
        if not image_file or image_file.filename == '':
            return jsonify({'success': False, 'error': 'Image file is required'}), 200
        
        # Process image using the new processing method
        processed_filenames = process_images(image_file, CAROUSEL_FOLDER)
        
        if not processed_filenames:
            return jsonify({
                'success': False, 
                'error': 'Failed to process image'
                }), 200
        
        # Create new carousel entry
        new_carousel = Carousel(
            heading_1=heading_1,
            heading_2=heading_2,
            image_alt = image_alt,
            image=processed_filenames[0]  # Single image for carousel
        )
        
        # Add to database
        db.session.add(new_carousel)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Carousel item added',
            'carousel': new_carousel.to_dict()
        }), 201
        
    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': str(ve)
            }), 200
    except Exception as e:
        # Rollback database changes if any error occurs
        db.session.rollback()
        print(f"Error in add_carousel: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
            }), 500

# delete carousel
@app.route('/del-carousel', methods=['POST'])
def del_carousel():
    print("Deleting carousel")
    
    try:
        # Get the carousel ID from form data
        carousel_id = request.form.get("id")
        
        # Validation
        if not carousel_id:
            return jsonify({'error': 'Carousel ID is required'}), 400
        
        # Find the carousel in the database
        carousel = Carousel.query.get(carousel_id)
        if not carousel:
            return jsonify({'error': 'Carousel not found'}), 404
        
        # Store image filename before deleting from database
        image_filename = carousel.image
        
        # Delete from database first
        db.session.delete(carousel)
        db.session.commit()
        
        # Delete the image file if it exists
        if image_filename:
            image_path = os.path.join(CAROUSEL_FOLDER, image_filename)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"Deleted image file: {image_path}")
                except OSError as e:
                    print(f"Error deleting image file: {e}")
                    # Don't fail the request if image deletion fails
                    # The database record is already deleted
        
        return jsonify({
            'message': '1',
            'success': True
        }), 200
        
    except Exception as e:
        # Rollback database changes if any error occurs
        db.session.rollback()
        print(f"Error in del_carousel: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        return jsonify({
            'error': 'Internal server error',
            'success': False,
            'details': str(e)
        }), 500

# get makes
@app.route('/get-makes', methods=['GET'])
def get_brands():
    try:
        makes = Makes.query.order_by(Makes.make_id.desc()).all()

        makes_data = []  # Initialize empty list
        for make in makes:
            # Fix the path to match your actual folder structure
            image_url = url_for('static', filename=f'images/make_logos/{make.logo_image}', _external=True)
            
            # Create individual carousel object
            make_item = {
                'id': make.make_id,
                'name': make.name,
                'image_url': image_url
            }
            
            # APPEND to list instead of overwriting
            makes_data.append(make_item)

        return jsonify({
            'message': '1',
            'success': True,
            'brands': makes_data
        }), 200
    
    except Exception as e:
        print(f"Error fetching brands: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch brands',
            'details': str(e)
        }), 500
# get body styles
@app.route('/get-body-styles', methods=['GET'])
def get_body_styles():
    try:
        body_styles = BodyStyle.query.order_by(BodyStyle.style_id.desc()).all()

        body_styles_data = []  # Initialize empty list
        for body_style in body_styles:
            # Fix the path to match your actual folder structure
            image_url = url_for('static', filename=f'images/body_logos/{body_style.logo_image}', _external=True)
            
            # Create individual carousel object
            body_style_item = {
                'id': body_style.style_id,
                'name': body_style.name,
                'image_url': image_url
            }
            
            # APPEND to list instead of overwriting
            body_styles_data.append(body_style_item)

        return jsonify({
            'message': '1',
            'success': True,
            'body_styles': body_styles_data
        }), 200
    
    except Exception as e:
        print(f"Error fetching body styles: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch body styles',
            'details': str(e)
        }), 500

# add brand
@app.route('/add-make', methods=['POST'])
def add_make():
    print("Adding make")
    
    try:
        # Get form data
        name = request.form.get('name')
        image_file = request.files.get('image')
        
        # Validation
        if not name:
            return jsonify({'error': 'Make name is required'}), 400
        
        if not image_file or image_file.filename == '':
            return jsonify({'error': 'Image file is required'}), 400
        
        # Process image
        processed_filenames = process_images(image_file, MAKE_LOGO)
        
        if not processed_filenames:
            return jsonify({'error': 'Failed to process image'}), 500
        
        # Create new make entry
        new_make = Makes(
            name=name,
            logo_image=processed_filenames[0]  # Single image for make
        )
        
        # Add to database
        db.session.add(new_make)
        db.session.commit()
        
        return jsonify({
            'message': '1',
            'success': True,
            'make': new_make.to_dict()
        }), 201
        
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        # Rollback database changes if any error occurs
        db.session.rollback()
        print(f"Error in add_make: {e}")
        return jsonify({'error': 'Internal server error'}), 500
# add body style
@app.route('/add-body-style', methods=['POST'])
def add_body_style():
    print("Adding body style")
    
    try:
        # Get form data
        name = request.form.get('name')
        image_file = request.files.get('image')
        
        # Validation
        if not name:
            return jsonify({'error': 'Make name is required'}), 400
        
        if not image_file or image_file.filename == '':
            return jsonify({'error': 'Image file is required'}), 400
        
        # Process image
        processed_filenames = process_images(image_file, BODY_LOGO)
        
        if not processed_filenames:
            return jsonify({'error': 'Failed to process image'}), 500
        
        # Create new make entry
        new_model = BodyStyle(
            name=name,
            logo_image=processed_filenames[0]  # Single image for make
        )
        
        # Add to database
        db.session.add(new_model)
        db.session.commit()
        
        return jsonify({
            'message': '1',
            'success': True,
            'body_style': new_model.to_dict()
        }), 201
        
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        # Rollback database changes if any error occurs
        db.session.rollback()
        print(f"Error in add-body-style: {e}")
        return jsonify({'error': 'Internal server error'}), 500
   
# delete make
@app.route('/del-make', methods=['POST'])
def del_make():
    print("Deleting make")
    
    try:
        # Get the make ID from form data
        make_id = request.form.get("id")
        
        # Validation
        if not make_id:
            return jsonify({'error': 'Make ID is required'}), 400
        
        # Find the make in the database
        make = Makes.query.get(make_id)
        if not make:
            return jsonify({'error': 'Make not found'}), 404
        
        # Store image filename before deleting from database
        image_filename = make.logo_image
        
        # Get all models under this make (for logging purposes)
        models_count = len(make.models)
        print(f"Found {models_count} models under make '{make.name}'")
        
        # Delete from database first (this will cascade delete all related models)
        db.session.delete(make)
        db.session.commit()
        
        # Delete the image file if it exists
        if image_filename:
            image_path = os.path.join(MAKE_LOGO, image_filename)  # Assuming you have MAKES_FOLDER defined
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"Deleted make image file: {image_path}")
                except OSError as e:
                    print(f"Error deleting make image file: {e}")
                    # Don't fail the request if image deletion fails
                    # The database record is already deleted
        
        return jsonify({
            'message': '1',
            'success': True,
            'deleted_models': models_count
        }), 200
        
    except Exception as e:
        # Rollback database changes if any error occurs
        db.session.rollback()
        print(f"Error in del_make: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        return jsonify({
            'error': 'Internal server error',
            'success': False,
            'details': str(e)
        }), 500
# delete body style
@app.route('/del-body-style', methods=['POST'])
def del_body_style():
    print("Deleting body")
    
    try:
        # Get the make ID from form data
        body_id = request.form.get("id")
        
        # Validation
        if not body_id:
            return jsonify({'error': 'Body ID is required'}), 400
        
        # Find the make in the database
        body_style = BodyStyle.query.get(body_id)
        if not body_style:
            return jsonify({'error': 'Make not found'}), 404
        
        # Store image filename before deleting from database
        image_filename = body_style.logo_image
        
        # Delete from database first (this will cascade delete all related models)
        db.session.delete(body_style)
        db.session.commit()
        
        # Delete the image file if it exists
        if image_filename:
            image_path = os.path.join(BODY_LOGO, image_filename)  # Assuming you have MAKES_FOLDER defined
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"Deleted make image file: {image_path}")
                except OSError as e:
                    print(f"Error deleting make image file: {e}")
                    # Don't fail the request if image deletion fails
                    # The database record is already deleted
        
        return jsonify({
            'message': '1',
            'success': True,
        }), 200
        
    except Exception as e:
        # Rollback database changes if any error occurs
        db.session.rollback()
        print(f"Error in del_make: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        return jsonify({
            'error': 'Internal server error',
            'success': False,
            'details': str(e)
        }), 500

# get models
@app.route('/get-models', methods=['GET'])
def get_models():
    try:
        # Use the relationship to eager load makes data
        models = Models.query.options(db.joinedload(Models.make_ref)).order_by(Models.model_id.desc()).all()
        
        models_data = []  # Initialize empty list
        
        for model in models:
            # Fix: Access logo_image directly from make_ref, not from name
            image_url = None
            if model.make_ref and model.make_ref.logo_image:
                image_url = url_for('static', filename=f'images/make_logos/{model.make_ref.logo_image}', _external=True)
            
            # Create model object with brand information using the relationship
            model_item = {
                'model_id': model.model_id,
                'model_name': model.model_name,
                'make_id': model.make,
                'make_name': model.make_ref.name if model.make_ref else None,
                'make_logo': image_url
            }
            
            # Append to list
            models_data.append(model_item)

        return jsonify({
            'message': '1',
            'success': True,
            'models': models_data
        }), 200
            
    except Exception as e:
        print(f"Error fetching models: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch models',
            'details': str(e)
        }), 500

# add model
@app.route('/add-model', methods=['POST'])
def add_or_update_model():
    try:
        name = request.form.get('name')
        brand = request.form.get('brand') 
        model_id = request.form.get('model_id')
        
        # Validate required fields
        if not name or not brand:
            return jsonify({
                'success': False,
                'error': 'Model name and brand are required'
            }), 400
        
        # Validate that the brand (make_id) exists
        make = Makes.query.get(brand)
        if not make:
            return jsonify({
                'success': False,
                'error': 'Invalid brand selected'
            }), 400
        
        # Determine if we're updating or adding
        is_update = model_id and model_id.strip()
        
        if is_update:
            # UPDATE MODE
            try:
                model_id = int(model_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'Invalid model ID format'
                }), 400
            
            # Find the existing model
            existing_model = Models.query.get(model_id)
            if not existing_model:
                return jsonify({
                    'success': False,
                    'error': 'Model not found for update'
                }), 404
            
            # Check if another model with same name and brand exists (excluding current model)
            duplicate_model = Models.query.filter(
                Models.model_name == name,
                Models.make == int(brand),
                Models.model_id != model_id
            ).first()
            
            if duplicate_model:
                return jsonify({
                    'success': False,
                    'error': 'Another model with this name already exists for this brand'
                }), 400
            
            # Update the model
            existing_model.model_name = name
            existing_model.make = int(brand)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '1',
                'action': 'updated',
                'model': existing_model.to_dict()
            }), 200
            
        else:
            # ADD MODE
            # Check if model already exists for this make
            existing_model = Models.query.filter_by(
                model_name=name, 
                make=int(brand)
            ).first()
            
            if existing_model:
                return jsonify({
                    'success': False,
                    'error': 'Model already exists for this brand'
                }), 400
            
            # Create new model
            new_model = Models(
                model_name=name,
                make=int(brand)
            )
            
            # Save to database
            db.session.add(new_model)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '1',
                'action': 'added',
                'model': new_model.to_dict()
            }), 201
        
    except ValueError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Invalid brand ID format'
        }), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error in add_or_update_model: {e}")
        return jsonify({
            'success': False,
            'error': 'Database error occurred'
        }), 500
# delete model
@app.route('/del-model', methods=['POST'])
def del_model():
    
    try:
        # Get the model ID from form data
        model_id = request.form.get("id")
        
        # Validation
        if not model_id:
            return jsonify({'error': 'Model ID is required'}), 400
        
        # Find the model in the database
        model = Models.query.get(model_id)
        if not model:
            return jsonify({'error': 'Model not found'}), 404
        
        # Get associated cars count (for logging purposes)
        cars_count = len(model.cars) if hasattr(model, 'cars') and model.cars else 0
        print(f"Found {cars_count} cars under model '{model.model_name}'")
        
        # Delete from database (this will cascade delete all related cars if configured)
        db.session.delete(model)
        db.session.commit()
        
        return jsonify({
            'message': '1',
            'success': True,
            'deleted_cars': cars_count
        }), 200
        
    except Exception as e:
        # Rollback database changes if any error occurs
        db.session.rollback()
        print(f"Error in del_model: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        return jsonify({
            'error': 'Internal server error',
            'success': False,
            'details': str(e)
        }), 500

# get features

@app.route('/get-features', methods=['GET'])
def get_features():
    try:
        # Get all features from database
        features = Features.query.order_by(Features.feature_id.desc()).all()
        
        # Convert to dictionary format
        features_list = [feature.to_dict() for feature in features]
        
        return jsonify({
            'success': True,
            'features': features_list,
            'count': len(features_list)
        }), 200
        
    except Exception as e:
        print(f"Error in get_features: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch features'
        }), 500

# fetch locaitons
@app.route('/get-locations', methods=['GET'])
def get_locations():
    try:
        # Get all features from database
        locations = Locations.query.order_by(Locations.location_id.desc()).all()
        
        # Convert to dictionary format
        location_list = [location.to_dict() for location in locations]
        
        return jsonify({
            'success': True,
            'locations': location_list,
            'count': len(location_list)
        }), 200
        
    except Exception as e:
        print(f"Error in get_features: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch locations'
        }), 500
    
# fetch categories
@app.route('/get-categories', methods=['GET'])
def get_categories():
    try:
        # Get all features from database
        categories = Categories.query.all()
        
        # Convert to dictionary format
        category_list = [category.to_dict() for category in categories]
        
        return jsonify({
            'success': True,
            'categories': category_list,
            'count': len(category_list)
        }), 200
        
    except Exception as e:
        print(f"Error in get_features: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch categories'
        }), 500
    
# get contact us
@app.route('/get-contact-us/<status>/<web_enquiries>', methods = ['GET'])
def get_contact_us(status, web_enquiries):
    try:
        if status == 'all':
            contacts_us_enquiries = []
            if web_enquiries == 'web_enquiries':
                contacts_us_enquiries = ContactUs.query.filter_by(contact_type = 'Contact').order_by(ContactUs.contact_id.desc()).all()

            else:
                contacts_us_enquiries = ContactUs.query.filter_by(contact_type = 'Import').order_by(ContactUs.contact_id.desc()).all()
            
            enquiry_list = [enquiry.to_dict() for enquiry in contacts_us_enquiries]

            return jsonify({
                'success': True,
                'enquiries': enquiry_list,
            }), 200
        
        else:
            contacts_us_enquiries = []

            if web_enquiries == 'imports':
                contacts_us_enquiries = ContactUs.query.filter(
                    ContactUs.status == status,
                    ContactUs.contact_type == 'Import'
                    ).order_by(ContactUs.contact_id.desc()).all()

            else:
                contacts_us_enquiries = ContactUs.query.filter(
                    ContactUs.status == status,
                    ContactUs.contact_type == 'Contact'
                    ).order_by(ContactUs.contact_id.desc()).all()
            
            enquiry_list = [enquiry.to_dict() for enquiry in contacts_us_enquiries]

            return jsonify({
                'success': True,
                'enquiries': enquiry_list,
            }), 200
    
    except Exception as e:
        print("Error fetching contact enquiries: ", str(e))
        return jsonify({
            'success': False,
            'error': 'Failed. An unexpected error occured',
            'details': str(e)
        }), 500
    
# get enquiries
@app.route('/get-enquiries/<mode>', methods = ['GET'])
def get_enquiries(mode):
    try:
        if mode == 'all':
            enquiries = Enquiries.query.order_by(Enquiries.enquiry_id.desc()).all()
            
            enquiry_list = [enquiry.to_dict() for enquiry in enquiries]

            return jsonify({
                'success': True,
                'enquiries': enquiry_list,
            }), 200
        
        else:
            enquiries = Enquiries.query.filter_by(status = mode).order_by(Enquiries.enquiry_id.desc()).all()
            
            enquiry_list = [enquiry.to_dict() for enquiry in enquiries]

            return jsonify({
                'success': True,
                'enquiries': enquiry_list,
            }), 200
    
    except Exception as e:
        print("Error fetching enquiries: ", str(e))
        return jsonify({
            'success': False,
            'error': 'Failed. An unexpected error occured',
            'details': str(e)
        }), 500

# add contact 
@app.route('/add-contact-us', methods = ['POST'])
def add_contact_us():
    try:
        full_name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        message = request.form.get('message')
        subject = request.form.get('subject')
        
        if subject:
            new_contact = ContactUs(
                full_name = full_name,
                phone = phone,
                email = email,
                message = message,
                contact_type = 'Import'
            )
        
        else:
            new_contact = ContactUs(
                full_name = full_name,
                phone = phone,
                email = email,
                message = message
            )

        db.session.add(new_contact)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Thank you. We will get back to you soon'
        }), 200
    
    except Exception as e:
        print("Error sending contact enquiry: ", str(e))
        return jsonify({
            'success': False,
            'error': 'Failed. An unexpected error occurred',
            'details': str(e)
        })

# add enquiry 
@app.route('/save-enquiry', methods = ['POST'])
def save_enquiry():
    try:
        client_name = request.form.get('client_name')
        client_email = request.form.get('client_email')
        car_name = request.form.get('car_name')
        client_phone = request.form.get('client_phone')
        client_address = request.form.get('client_address')
        client_message = request.form.get('client_message')
        mode = request.form.get('mode')

        new_enquiry = Enquiries(
            name = client_name,
            email = client_email,
            car = car_name,
            phone = client_phone,
            address = client_address,
            message = client_message,
            enquiry_mode = mode
        )

        db.session.add(new_enquiry)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Thank you. We will get back to you soon'
        }), 200
    
    except Exception as e:
        print("Error saving contact enquiry: ", str(e))
        return jsonify({
            'success': False,
            'error': 'Failed. An unexpected error occurred',
            'details': str(e)
        })

# fetch faqs categories
@app.route('/get-faq-categories', methods=['GET'])
def get_faqs_categories():
    try:
        # Get all features from database
        categories = FaqsCategories.query.all()
        
        # Convert to dictionary format
        category_list = [category.to_dict() for category in categories]
        
        return jsonify({
            'success': True,
            'categories': category_list,
            'count': len(category_list)
        }), 200
        
    except Exception as e:
        print(f"Error in get_features: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch categories'
        }), 500
    
# add feature
@app.route('/add-feature', methods=['POST'])
def add_or_update_feature():
    try:
        name = request.form.get('feature_name')
        feature_id = request.form.get('feature_id')

        print("Name is: ", str(name))
        
        # Validate required fields
        if not name or not name.strip():
            return jsonify({
                'success': False,
                'error': 'Feature name is required'
            }), 201
        
        # Clean the name
        name = name.strip()
        
        # Determine if we're updating or adding
        is_update = feature_id and feature_id.strip()
        
        if is_update:
            # UPDATE MODE
            try:
                feature_id = int(feature_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'Invalid feature ID format'
                }), 201
            
            # Find the existing feature
            existing_feature = Features.query.get(feature_id)
            if not existing_feature:
                return jsonify({
                    'success': False,
                    'error': 'Feature not found for update'
                }), 201
            
            # Check if another feature with same name exists (excluding current feature)
            duplicate_feature = Features.query.filter(
                Features.name == name,
                Features.feature_id != feature_id
            ).first()
            
            if duplicate_feature:
                return jsonify({
                    'success': False,
                    'error': 'Another feature with this name already exists'
                }), 201
            
            # Update the feature
            existing_feature.name = name
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '1',
                'action': 'updated',
                'feature': existing_feature.to_dict()
            }), 201
            
        else:
            # ADD MODE
            # Check if feature already exists
            existing_feature = Features.query.filter_by(name=name).first()
            
            if existing_feature:
                return jsonify({
                    'success': False,
                    'error': 'Feature already exists'
                }), 201
            
            # Create new feature
            new_feature = Features(name=name)
            
            # Save to database
            db.session.add(new_feature)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '1',
                'action': 'added',
                'feature': new_feature.to_dict()
            }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in add_or_update_feature: {e}")
        return jsonify({
            'success': False,
            'error': 'Database error occurred'
        }), 500

# add location
@app.route('/add-location', methods=['POST'])
def add_or_update_location():
    try:
        name = request.form.get('location_name')
        location_id = request.form.get('location_id')

        print("Name is: ", str(name))
        
        # Validate required fields
        if not name or not name.strip():
            return jsonify({
                'success': False,
                'error': 'Location name is required'
            }), 200
        
        # Clean the name
        name = name.strip()
        
        # Determine if we're updating or adding
        is_update = location_id and location_id.strip()
        
        if is_update:
            # UPDATE MODE
            try:
                location_id = int(location_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'Invalid location ID format'
                }), 200
            
            # Find the existing feature
            existing_location = Locations.query.get(location_id)
            if not existing_location:
                return jsonify({
                    'success': False,
                    'error': 'Location not found for update'
                }), 200
            
            # Check if another feature with same name exists (excluding current feature)
            duplicate_location = Locations.query.filter(
                Locations.location_name == name,
                Locations.location_id != location_id
            ).first()
            
            if duplicate_location:
                return jsonify({
                    'success': False,
                    'error': 'Another location with this name already exists'
                }), 200
            
            # Update the feature
            existing_location.location_name = name
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Location updated',
                'action': 'updated',
                'feature': existing_location.to_dict()
            }), 200
            
        else:
            # ADD MODE
            # Check if feature already exists
            existing_location = Locations.query.filter_by(location_name=name).first()
            
            if existing_location:
                return jsonify({
                    'success': False,
                    'error': 'Location already exists'
                }), 200
            
            # Create new feature
            new_location = Locations(location_name=name)
            
            # Save to database
            db.session.add(new_location)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Location added',
                'action': 'added',
                'feature': new_location.to_dict()
            }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in add_or_update_location: {e}")
        return jsonify({
            'success': False,
            'error': 'Database error occurred'
        }), 500
    
# add category
@app.route('/add-category', methods=['POST'])
def add_or_update_category():
    try:
        name = request.form.get('category_name')
        category_id = request.form.get('category_id')

        print("Name is: ", str(name))
        
        # Validate required fields
        if not name or not name.strip():
            return jsonify({
                'success': False,
                'error': 'category name is required'
            }), 200
        
        # Clean the name
        name = name.strip()
        
        # Determine if we're updating or adding
        is_update = category_id and category_id.strip()
        
        if is_update:
            # UPDATE MODE
            try:
                category_id = int(category_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'Invalid category ID format'
                }), 200
            
            # Find the existing feature
            existing_category = Categories.query.get(category_id)
            if not existing_category:
                return jsonify({
                    'success': False,
                    'error': 'Category not found for update'
                }), 200
            
            # Check if another feature with same name exists (excluding current feature)
            duplicate_category = Categories.query.filter(
                Categories.category_name == name,
                Categories.category_id != category_id
            ).first()
            
            if duplicate_category:
                return jsonify({
                    'success': False,
                    'error': 'Another category with this name already exists'
                }), 200
            
            # Update the feature
            existing_category.category_name = name
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Category updated',
                'action': 'updated',
                'feature': existing_category.to_dict()
            }), 200
            
        else:
            # ADD MODE
            # Check if feature already exists
            existing_category = Categories.query.filter_by(category_name=name).first()
            
            if existing_category:
                return jsonify({
                    'success': False,
                    'error': 'Category already exists'
                }), 200
            
            # Create new feature
            new_category = Categories(category_name=name)
            
            # Save to database
            db.session.add(new_category)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Category added',
                'action': 'added',
                'feature': new_category.to_dict()
            }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in add_or_update_location: {e}")
        return jsonify({
            'success': False,
            'error': 'Database error occurred'
        }), 500


# add category
@app.route('/add-faq-category', methods=['POST'])
def add_or_update_faq__category():
    try:
        name = request.form.get('category_name')
        category_id = request.form.get('category_id')

        print("Name is: ", str(name))
        
        # Validate required fields
        if not name or not name.strip():
            return jsonify({
                'success': False,
                'error': 'category name is required'
            }), 200
        
        # Clean the name
        name = name.strip()
        
        # Determine if we're updating or adding
        is_update = category_id and category_id.strip()
        
        if is_update:
            # UPDATE MODE
            try:
                category_id = int(category_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'Invalid category ID format'
                }), 200
            
            # Find the existing feature
            existing_category = FaqsCategories.query.get(category_id)
            if not existing_category:
                return jsonify({
                    'success': False,
                    'error': 'Category not found for update'
                }), 200
            
            # Check if another feature with same name exists (excluding current feature)
            duplicate_category = FaqsCategories.query.filter(
                Categories.category_name == name,
                Categories.category_id != category_id
            ).first()
            
            if duplicate_category:
                return jsonify({
                    'success': False,
                    'error': 'Another category with this name already exists'
                }), 200
            
            # Update the feature
            existing_category.category_name = name
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Category updated',
                'action': 'updated',
                'feature': existing_category.to_dict()
            }), 200
            
        else:
            # ADD MODE
            # Check if feature already exists
            existing_category = FaqsCategories.query.filter_by(category_name=name).first()
            
            if existing_category:
                return jsonify({
                    'success': False,
                    'error': 'Category already exists'
                }), 200
            
            # Create new feature
            new_category = FaqsCategories(category_name=name)
            
            # Save to database
            db.session.add(new_category)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Category added',
                'action': 'added',
                'feature': new_category.to_dict()
            }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in add_or_update_location: {e}")
        return jsonify({
            'success': False,
            'error': 'Database error occurred'
        }), 500

# delete feature
@app.route('/del-feature', methods=['POST'])
def del_feature():
    print("Deleting feature")
    
    try:
        # Get the model ID from form data
        feature_id = request.form.get("id")
        
        # Validation
        if not feature_id:
            return jsonify({'error': 'Feature ID is required'}), 400
        
        # Find the model in the database
        feature = Features.query.get(feature_id)
        if not feature:
            return jsonify({'error': 'Feature not found'}), 404
        
        db.session.delete(feature)
        db.session.commit()
        
        return jsonify({
            'message': '1',
            'success': True,
        }), 200
    
    except Exception as e:
        # Rollback database changes if any error occurs
        db.session.rollback()
        print(f"Error in del_feature: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        return jsonify({
            'error': 'Internal server error',
            'success': False,
            'details': str(e)
        }), 500


# delete category
@app.route('/del-category', methods=['POST'])
def del_category():
    print("Deleting category")
    
    try:
        # Get the model ID from form data
        category_id = request.form.get("id")
        
        # Validation
        if not category_id:
            return jsonify({'error': 'Category ID is required'}), 400
        
        # Find the model in the database
        category = Categories.query.get(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category deleted',
            'success': True,
        }), 200
    
    except Exception as e:
        # Rollback database changes if any error occurs
        db.session.rollback()
        print(f"Error in del_feature: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        return jsonify({
            'error': 'Internal server error',
            'success': False,
            'details': str(e)
        }), 500

# delete category
@app.route('/del-faq-category', methods=['POST'])
def del_faq_category():
    print("Deleting category")
    
    try:
        # Get the model ID from form data
        category_id = request.form.get("id")
        
        # Validation
        if not category_id:
            return jsonify({'error': 'Category ID is required'}), 400
        
        # Find the model in the database
        category = FaqsCategories.query.get(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category deleted',
            'success': True,
        }), 200
    
    except Exception as e:
        # Rollback database changes if any error occurs
        db.session.rollback()
        print(f"Error in del_feature: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        return jsonify({
            'error': 'Internal server error',
            'success': False,
            'details': str(e)
        }), 500
    
# delete location
@app.route('/del-location', methods=['POST'])
def del_location():
    print("Deleting location")
    
    try:
        # Get the model ID from form data
        location_id = request.form.get("id")
        
        # Validation
        if not location_id:
            return jsonify({'error': 'Location ID is required'}), 400
        
        # Find the model in the database
        location = Locations.query.get(location_id)
        if not location:
            return jsonify({'error': 'Location not found'}), 404
        
        db.session.delete(location)
        db.session.commit()
        
        return jsonify({
            'message': 'Feature deleted',
            'success': True,
        }), 200
    

    except Exception as e:
        # Rollback database changes if any error occurs
        db.session.rollback()
        print(f"Error in del_location: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        return jsonify({
            'error': 'Internal server error',
            'success': False,
            'details': str(e)
        }), 500


# add/update vehicle
@app.route('/add-vehicle', methods=['POST'])
def add_vehicle():
    """
    Complete function to add or update a vehicle with image processing and database storage
    """
    print("Saving car...")

    try:
        # Regular form fields
        form_data = request.form.to_dict()
        print("Form Data:", form_data)
        
        # Check if this is an update operation
        vehicle_id = form_data.get('id') or form_data.get('car_id')
        is_update = vehicle_id is not None
        
        if is_update:
            print(f"Updating existing vehicle with ID: {vehicle_id}")
            # Get existing vehicle
            existing_car = Cars.query.get(int(vehicle_id))
            if not existing_car:
                return jsonify({
                    "success": False,
                    "message": "Vehicle not found"
                }), 404
        else:
            print("Adding new vehicle")

        # Features (may be JSON string or already parsed)
        features = request.form.get("features")
        print("Features (raw):", features)
        
        # Parse features if it's a JSON string
        if features:
            try:
                if isinstance(features, str):
                    features = json.loads(features)
            except json.JSONDecodeError:
                return jsonify({
                    "success": False,
                    "message": "Invalid features format"
                }), 400

        # Get uploaded images - Handle both file uploads and base64 data
        images = request.files.getlist("vehicle_images")
        print(f"Raw images from getlist: {len(images)}")
        
        # Also check for base64 image data in form data
        base64_images = []
        image_data_keys = [key for key in request.form.keys() if key.startswith('image_data_')]
        for key in image_data_keys:
            image_data = request.form.get(key)
            if image_data:
                base64_images.append(image_data)
        
        print(f"Found {len(base64_images)} base64 images in form data")
        
        # Filter out empty files
        valid_images = []
        for img in images:
            if img and img.filename and img.filename != '':
                # Check if file has content
                img.seek(0, 2)  # Seek to end
                file_size = img.tell()
                img.seek(0)  # Seek back to beginning
                
                if file_size > 0:
                    valid_images.append(img)
                    print(f"Valid image: {img.filename}, size: {file_size} bytes")
                else:
                    print(f"Empty image file: {img.filename}")
            else:
                print(f"Invalid image object: {img}")

        # Convert base64 images to file-like objects
        for i, base64_data in enumerate(base64_images):
            try:
                # Parse data URL: data:image/jpeg;base64,/9j/4AAQ...
                if base64_data.startswith('data:image/'):
                    header, data = base64_data.split(',', 1)
                    mime_type = header.split(';')[0].split(':')[1]
                    file_extension = mime_type.split('/')[1]
                    
                    # Decode base64
                    import base64
                    from io import BytesIO
                    image_bytes = base64.b64decode(data)
                    
                    # Create a file-like object
                    image_file = BytesIO(image_bytes)
                    image_file.filename = f"image_{i}.{file_extension}"
                    image_file.content_type = mime_type
                    
                    valid_images.append(image_file)
                    print(f"Converted base64 image: {image_file.filename}, size: {len(image_bytes)} bytes")
            except Exception as e:
                print(f"Error processing base64 image {i}: {e}")
                continue

        print(f"Found {len(valid_images)} valid images total")

        # Validate required fields
        required_fields = ['make_id', 'name', 'registration_year']
        for field in required_fields:
            if not form_data.get(field):
                return jsonify({
                    "success": False,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Parse registration year from date string
        try:
            registration_date = form_data.get('registration_year')
            if registration_date:
                # Parse date like '2025-08-31' to get year
                year = int(registration_date.split('-')[0])
            else:
                year = None
        except (ValueError, IndexError):
            return jsonify({
                "success": False,
                "message": "Invalid registration year format"
            }), 400

        # Process images if any
        processed_image_filenames = []
        if valid_images:
            # Define destination folder for vehicle images
            destination_folder = VEHICLE_IMAGES
            os.makedirs(destination_folder, exist_ok=True)
            
            try:
                processed_image_filenames = process_images(
                    valid_images, 
                    destination_folder,
                    max_width=1920,
                    max_height=1080,
                    quality=85
                )
                print(f"Processed {len(processed_image_filenames)} images successfully")
            except Exception as e:
                print(f"Error processing images: {e}")
                return jsonify({
                    "success": False,
                    "message": f"Failed to process images: {str(e)}"
                }), 500

        # Find or create location
        location = form_data.get('location')

        # Create or update car record
        try:
            if is_update:
                # Update existing vehicle
                car = existing_car
                car.name = form_data.get('name')
                car.price = float(form_data['price']) if form_data.get('price') else None
                car.condition = form_data.get('condition')
                car.model_id = int(form_data['model_id']) if form_data.get('model_id') else None
                car.make = int(form_data['make_id'])
                car.body_style = int(form_data.get('body_id', 1)) if form_data.get('body_id') else None
                car.mileage = form_data.get('mileage')
                car.year = year
                car.engine = form_data.get('engine_size')
                car.location = location
                car.ref_no = form_data.get('ref_number')
                car.model_code = form_data.get('model_code')
                car.steering = form_data.get('steering_wheel')
                car.exterior_color = form_data.get('exterior_color')
                car.fuel = form_data.get('fuel_type')
                car.seats = int(form_data['seats']) if form_data.get('seats') else None
                car.interior_color = form_data.get('interior_color')
                car.seats_color = form_data.get('seats_color')
                car.drive = form_data.get('drive_type')
                car.weight = form_data.get('weight')
                car.doors = form_data.get('doors')
                car.transmission = form_data.get('transmission')
                car.updated_at = datetime.utcnow()
                
                # Handle images for update
                if processed_image_filenames:
                    # Option 1: Delete old images and add new ones
                    # Get old image filenames for cleanup
                    old_images = CarImages.query.filter_by(car=car.car_id).all()
                    old_image_filenames = [img.image for img in old_images]
                    
                    # Delete old image records
                    CarImages.query.filter_by(car=car.car_id).delete()
                    
                    # Add new images
                    for image_filename in processed_image_filenames:
                        car_image = CarImages(
                            car=car.car_id,
                            image=image_filename
                        )
                        db.session.add(car_image)
                    
                    # Delete old image files from disk
                    for old_filename in old_image_filenames:
                        old_file_path = os.path.join(destination_folder, old_filename)
                        if os.path.exists(old_file_path):
                            try:
                                os.remove(old_file_path)
                                print(f"Deleted old image: {old_filename}")
                            except OSError as e:
                                print(f"Error deleting old image {old_filename}: {e}")
                
                # Handle features for update
                if features is not None:  # Allow empty list to clear all features
                    # Delete existing features
                    CarFeatures.query.filter_by(car_id=car.car_id).delete()
                    
                    # Add new features
                    if isinstance(features, list):
                        for feature_id in features:
                            try:
                                car_feature = CarFeatures(
                                    feature=int(feature_id),
                                    car_id=car.car_id
                                )
                                db.session.add(car_feature)
                            except (ValueError, TypeError):
                                print(f"Invalid feature ID: {feature_id}")
                                continue
                
                success_message = "Vehicle updated successfully"
                
            else:
                # Create new vehicle
                new_car = Cars(
                    name=form_data.get('name'),
                    price=float(form_data['price']) if form_data.get('price') else None,
                    condition=form_data.get('condition'),
                    model_id=int(form_data['model_id']) if form_data.get('model_id') else None,
                    make=int(form_data['make_id']),
                    body_style=int(form_data.get('body_id', 1)) if form_data.get('body_id') else None,
                    mileage=form_data.get('mileage'),
                    year=year,
                    engine=form_data.get('engine_size'),
                    location=location,
                    ref_no=form_data.get('ref_number'),
                    model_code=form_data.get('model_code'),
                    steering=form_data.get('steering_wheel'),
                    exterior_color=form_data.get('exterior_color'),
                    fuel=form_data.get('fuel_type'),
                    seats=int(form_data['seats']) if form_data.get('seats') else None,
                    interior_color=form_data.get('interior_color'),
                    seats_color=form_data.get('seats_color'),
                    drive=form_data.get('drive_type'),
                    weight=form_data.get('weight'),
                    doors=form_data.get('doors'),
                    transmission=form_data.get('transmission')
                )
                
                db.session.add(new_car)
                db.session.flush()  # Get the car_id without committing
                car = new_car
                
                # Add images to database
                for image_filename in processed_image_filenames:
                    car_image = CarImages(
                        car=car.car_id,
                        image=image_filename
                    )
                    db.session.add(car_image)
                
                # Add features to database
                if features and isinstance(features, list):
                    for feature_id in features:
                        try:
                            car_feature = CarFeatures(
                                feature=int(feature_id),
                                car_id=car.car_id
                            )
                            db.session.add(car_feature)
                        except (ValueError, TypeError):
                            print(f"Invalid feature ID: {feature_id}")
                            continue
                
                success_message = "Vehicle added successfully"
            
            # Commit all changes
            db.session.commit()
            
            return jsonify({
                "success": True,
                "message": success_message,
                "car_id": car.car_id,
                "vehicle_name": form_data.get('name'),
                "price": form_data.get('price'),
                "condition": form_data.get('condition'),
                "model_id": form_data.get('model_id'),
                "processed_images": len(processed_image_filenames),
                "features_added": len(features) if features else 0,
            })
            
        except Exception as e:
            db.session.rollback()
            # Clean up processed images if database operation failed
            if processed_image_filenames and not is_update:
                for filename in processed_image_filenames:
                    file_path = os.path.join(destination_folder, filename)
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except OSError:
                            pass
            
            print(f"Database error: {e}")
            return jsonify({
                "success": False,
                "message": f"Database error: {str(e)}"
            }), 500
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }), 500

# get vehicles
@app.route('/get-vehicle/<int:car_id>', methods=['GET'])
def get_vehicle(car_id):
    """
    Retrieve all data related to a specific vehicle including images, features, and related information
    """
    try:
        # Get the car with all its relationships
        car = Cars.query.options(
            db.joinedload(Cars.images),
            db.joinedload(Cars.features).joinedload(CarFeatures.feature_ref),
            db.joinedload(Cars.make_ref),
            db.joinedload(Cars.model_ref),
            db.joinedload(Cars.body_style_ref),
            db.joinedload(Cars.location_ref)
        ).filter_by(car_id=car_id).first()
        
        if not car:
            return jsonify({
                "success": False,
                "message": "Vehicle not found"
            }), 404

        # update tracker for car
        car_id = car.car_id

        existing_car = Tracker.query.filter_by(car_id = car_id).first()
        if existing_car:
            existing_car.car_count += 1
        
        else:
            new_car_count = Tracker(
                car_id = car_id,
                car_count = 1
            )

            db.session.add(new_car_count)
        db.session.commit()

        # Build comprehensive vehicle data
        vehicle_data = {
            "success": True,
            "vehicle": {
                # Basic vehicle information
                "car_id": car.car_id,
                "name": car.name,
                "price": float(car.price) if car.price else None,
                "condition": car.condition,
                "ref_no": car.ref_no,
                "model_code": car.model_code,
                
                # Year and mileage
                "year": car.year,
                "mileage": car.mileage,
                
                # Engine and performance
                "engine": car.engine,
                "fuel": car.fuel,
                "transmission": car.transmission,
                "drive": car.drive,
                
                # Physical attributes
                "exterior_color": car.exterior_color,
                "interior_color": car.interior_color,
                "seats_color": car.seats_color,
                "seats": car.seats,
                "doors": car.doors,
                "steering": car.steering,
                "weight": car.weight,
                "status": car.status,
                
                # Make information
                "make": {
                    "make_id": car.make_ref.make_id if car.make_ref else None,
                    "name": car.make_ref.name if car.make_ref else None,
                    "logo_image": car.make_ref.logo_image if car.make_ref else None
                },
                
                # Model information
                "model": {
                    "model_id": car.model_ref.model_id if car.model_ref else None,
                    "model_name": car.model_ref.model_name if car.model_ref else None
                } if car.model_ref else None,
                
                # Body style information
                "body_style": {
                    "style_id": car.body_style_ref.style_id if car.body_style_ref else None,
                    "name": car.body_style_ref.name if car.body_style_ref else None,
                    "logo_image": car.body_style_ref.logo_image if car.body_style_ref else None
                } if car.body_style_ref else None,
                
                # Location information
                "location": {
                    "location_id": car.location_ref.location_id if car.location_ref else None,
                    "location_name": car.location_ref.location_name if car.location_ref else None
                } if car.location_ref else None,
                
                # Images
                "images": [
                    {
                        "car_image_id": img.car_image_id,
                        "image": img.image,
                        "image_url": url_for('static', filename=f'uploads/{img.image}', _external=True)
                    } for img in car.images
                ],
                
                # Features
                "features": [
                    {
                        "car_feature_id": feat.car_feature_id,
                        "feature_id": feat.feature,
                        "feature_name": feat.feature_ref.name if feat.feature_ref else None
                    } for feat in car.features
                ],
                
                # Timestamps
                "created_at": car.created_at.isoformat() if car.created_at else None,
                "updated_at": car.updated_at.isoformat() if car.updated_at else None
            }
        }
        
        return jsonify(vehicle_data), 200
        
    except Exception as e:
        print(f"Error retrieving vehicle: {e}")
        return jsonify({
            "success": False,
            "message": f"Error retrieving vehicle: {str(e)}"
        }), 500


@app.route('/get-vehicles', methods=['GET'])
def get_vehicles():
    """
    Retrieve all vehicles with optional filtering and pagination
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        make_id = request.args.get('make_id', type=int)
        model_id = request.args.get('model_id', type=int)
        condition = request.args.get('condition')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        min_year = request.args.get('min_year', type=int)
        max_year = request.args.get('max_year', type=int)
        
        # Build query with filters
        query = Cars.query.options(
            db.joinedload(Cars.images),
            db.joinedload(Cars.make_ref),
            db.joinedload(Cars.model_ref),
            db.joinedload(Cars.body_style_ref),
            db.joinedload(Cars.location_ref)
        )
        
        # Apply filters
        if make_id:
            query = query.filter(Cars.make == make_id)
        if model_id:
            query = query.filter(Cars.model_id == model_id)
        if condition:
            query = query.filter(Cars.condition.ilike(f'%{condition}%'))
        if min_price:
            query = query.filter(Cars.price >= min_price)
        if max_price:
            query = query.filter(Cars.price <= max_price)
        if min_year:
            query = query.filter(Cars.year >= min_year)
        if max_year:
            query = query.filter(Cars.year <= max_year)
        
        # Order by created_at descending (newest first)
        query = query.order_by(Cars.created_at.desc())
        
        # Paginate results
        paginated = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Build response
        vehicles = []
        for car in paginated.items:
            vehicle_data = {
                "car_id": car.car_id,
                "name": car.name,
                "price": float(car.price) if car.price else None,
                "condition": car.condition,
                "year": car.year,
                "mileage": car.mileage,
                "ref_no": car.ref_no,
                "steering": car.steering,
                "engine": car.engine,
                "fuel": car.fuel,
                "transmission": car.transmission,
                "seats": car.seats,
                "status": car.status,
                
                
                # Make and model info
                "make": {
                    "make_id": car.make_ref.make_id if car.make_ref else None,
                    "name": car.make_ref.name if car.make_ref else None,
                    "logo_image": car.make_ref.logo_image if car.make_ref else None
                },
                "model": {
                    "model_id": car.model_ref.model_id if car.model_ref else None,
                    "model_name": car.model_ref.model_name if car.model_ref else None
                } if car.model_ref else None,
                
                # Body style
                "body_style": {
                    "style_id": car.body_style_ref.style_id if car.body_style_ref else None,
                    "name": car.body_style_ref.name if car.body_style_ref else None
                } if car.body_style_ref else None,
                
                # Location
                "location": {
                    "location_id": car.location_ref.location_id if car.location_ref else None,
                    "location_name": car.location_ref.location_name if car.location_ref else None
                } if car.location_ref else None,
                
                # All images
                # All images
                "images": [
                    {
                        "car_image_id": img.car_image_id,
                        "image": img.image,
                        "image_url": url_for('static', filename=f'uploads/{img.image}', _external=True)
                    } for img in car.images
                ],

                # Primary image for backward compatibility
                "primary_image_url": url_for('static', filename=f'uploads/{car.images[0].image}', _external=True) if car.images else None,
                
                # Image count
                "image_count": len(car.images),
                
                # Timestamps
                "created_at": car.created_at.isoformat() if car.created_at else None,
                "updated_at": car.updated_at.isoformat() if car.updated_at else None
            }
            vehicles.append(vehicle_data)
        
        return jsonify({
            "success": True,
            "vehicles": vehicles,
            "pagination": {
                "page": paginated.page,
                "per_page": paginated.per_page,
                "total": paginated.total,
                "pages": paginated.pages,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev,
                "next_num": paginated.next_num,
                "prev_num": paginated.prev_num
            }
        }), 200
        
    except Exception as e:
        print(f"Error retrieving vehicles: {e}")
        return jsonify({
            "success": False,
            "message": f"Error retrieving vehicles: {str(e)}"
        }), 500

# get popular vehicles
@app.route('/get-popular-vehicles', methods=['GET'])
def get_popular_vehicles():
    """
    Retrieve the most popular vehicles based on view count
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        make_id = request.args.get('make_id', type=int)
        model_id = request.args.get('model_id', type=int)
        condition = request.args.get('condition')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        min_year = request.args.get('min_year', type=int)
        max_year = request.args.get('max_year', type=int)
        
        # Build query with filters and join with Tracker table
        query = Cars.query.join(
            Tracker, Cars.car_id == Tracker.car_id
        ).options(
            db.joinedload(Cars.images),
            db.joinedload(Cars.make_ref),
            db.joinedload(Cars.model_ref),
            db.joinedload(Cars.body_style_ref),
            db.joinedload(Cars.location_ref)
        )
        
        # Apply filters
        if make_id:
            query = query.filter(Cars.make == make_id)
        if model_id:
            query = query.filter(Cars.model_id == model_id)
        if condition:
            query = query.filter(Cars.condition.ilike(f'%{condition}%'))
        if min_price:
            query = query.filter(Cars.price >= min_price)
        if max_price:
            query = query.filter(Cars.price <= max_price)
        if min_year:
            query = query.filter(Cars.year >= min_year)
        if max_year:
            query = query.filter(Cars.year <= max_year)
        
        # Order by car_count descending (most viewed first) and limit to 9
        query = query.order_by(Tracker.car_count.desc()).limit(9)
        
        # Get the results
        cars = query.all()
        
        # Build response
        vehicles = []
        for car in cars:
            vehicle_data = {
                "car_id": car.car_id,
                "name": car.name,
                "price": float(car.price) if car.price else None,
                "condition": car.condition,
                "year": car.year,
                "mileage": car.mileage,
                "ref_no": car.ref_no,
                "steering": car.steering,
                "engine": car.engine,
                "fuel": car.fuel,
                "transmission": car.transmission,
                "seats": car.seats,
                
                
                # Make and model info
                "make": {
                    "make_id": car.make_ref.make_id if car.make_ref else None,
                    "name": car.make_ref.name if car.make_ref else None,
                    "logo_image": car.make_ref.logo_image if car.make_ref else None
                },
                "model": {
                    "model_id": car.model_ref.model_id if car.model_ref else None,
                    "model_name": car.model_ref.model_name if car.model_ref else None
                } if car.model_ref else None,
                
                # Body style
                "body_style": {
                    "style_id": car.body_style_ref.style_id if car.body_style_ref else None,
                    "name": car.body_style_ref.name if car.body_style_ref else None
                } if car.body_style_ref else None,
                
                # Location
                "location": {
                    "location_id": car.location_ref.location_id if car.location_ref else None,
                    "location_name": car.location_ref.location_name if car.location_ref else None
                } if car.location_ref else None,
                
                # All images
                "images": [
                    {
                        "car_image_id": img.car_image_id,
                        "image": img.image,
                        "image_url": url_for('static', filename=f'uploads/{img.image}', _external=True)
                    } for img in car.images
                ],

                # Primary image for backward compatibility
                "primary_image_url": url_for('static', filename=f'uploads/{car.images[0].image}', _external=True) if car.images else None,
                
                # Image count
                "image_count": len(car.images),
                
                # Timestamps
                "created_at": car.created_at.isoformat() if car.created_at else None,
                "updated_at": car.updated_at.isoformat() if car.updated_at else None
            }
            vehicles.append(vehicle_data)
        
        return jsonify({
            "success": True,
            "vehicles": vehicles,
            "total": len(vehicles)
        }), 200
        
    except Exception as e:
        print(f"Error retrieving vehicles: {e}")
        return jsonify({
            "success": False,
            "message": f"Error retrieving vehicles: {str(e)}"
        }), 500
    
# fetch similar vehicles
@app.route('/get-similar-vehicles/<body_style>/<car_id>', methods=['GET'])
def get_simillar_vehicles(body_style, car_id):
    """
    Retrieve 6 random vehicles by body style
    """
    try:
        # Build query with joinedload for relationships
        query = Cars.query.options(
            db.joinedload(Cars.images),
            db.joinedload(Cars.make_ref),
            db.joinedload(Cars.model_ref),
            db.joinedload(Cars.body_style_ref),
            db.joinedload(Cars.location_ref)
        )
        
        # Filter by body_style, order randomly, and limit to 6
        cars = query.filter_by(body_style=body_style).filter(Cars.car_id != car_id).order_by(db.func.random()).limit(6).all()
        
        # Build response
        vehicles = []
        for car in cars:
            vehicle_data = {
                "car_id": car.car_id,
                "name": car.name,
                "price": float(car.price) if car.price else None,
                "condition": car.condition,
                "year": car.year,
                "mileage": car.mileage,
                "ref_no": car.ref_no,
                "steering": car.steering,
                "engine": car.engine,
                "fuel": car.fuel,
                "transmission": car.transmission,
                "seats": car.seats,
                
                # Make and model info
                "make": {
                    "make_id": car.make_ref.make_id if car.make_ref else None,
                    "name": car.make_ref.name if car.make_ref else None,
                    "logo_image": car.make_ref.logo_image if car.make_ref else None
                },
                "model": {
                    "model_id": car.model_ref.model_id if car.model_ref else None,
                    "model_name": car.model_ref.model_name if car.model_ref else None
                } if car.model_ref else None,
                
                # Body style
                "body_style": {
                    "style_id": car.body_style_ref.style_id if car.body_style_ref else None,
                    "name": car.body_style_ref.name if car.body_style_ref else None
                } if car.body_style_ref else None,
                
                # Location
                "location": {
                    "location_id": car.location_ref.location_id if car.location_ref else None,
                    "location_name": car.location_ref.location_name if car.location_ref else None
                } if car.location_ref else None,
                
                # All images
                "images": [
                    {
                        "car_image_id": img.car_image_id,
                        "image": img.image,
                        "image_url": url_for('static', filename=f'uploads/{img.image}', _external=True)
                    } for img in car.images
                ],

                # Primary image for backward compatibility
                "primary_image_url": url_for('static', filename=f'uploads/{car.images[0].image}', _external=True) if car.images else None,
                
                # Image count
                "image_count": len(car.images),
                
                # Timestamps
                "created_at": car.created_at.isoformat() if car.created_at else None,
                "updated_at": car.updated_at.isoformat() if car.updated_at else None
            }
            vehicles.append(vehicle_data)
        
        return jsonify({
            "success": True,
            "vehicles": vehicles,
            "total": len(vehicles)
        }), 200
        
    except Exception as e:
        print(f"Error retrieving vehicles: {e}")
        return jsonify({
            "success": False,
            "message": f"Error retrieving vehicles: {str(e)}"
        }), 500


@app.route('/search-vehicles', methods=['GET'])
def search_vehicles():
    """
    Search vehicles by name, make, model, or other criteria
    """
    try:
        search_term = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if not search_term:
            return jsonify({
                "success": False,
                "message": "Search term is required"
            }), 400
        
        # Build search query
        query = Cars.query.options(
            db.joinedload(Cars.images),
            db.joinedload(Cars.make_ref),
            db.joinedload(Cars.model_ref),
            db.joinedload(Cars.body_style_ref),
            db.joinedload(Cars.location_ref)
        )
        
        # Search in multiple fields
        search_filter = db.or_(
            Cars.name.ilike(f'%{search_term}%'),
            Cars.ref_no.ilike(f'%{search_term}%'),
            Cars.model_code.ilike(f'%{search_term}%'),
            Cars.make_ref.has(Makes.name.ilike(f'%{search_term}%')),
            Cars.model_ref.has(Models.model_name.ilike(f'%{search_term}%')),
            Cars.body_style_ref.has(BodyStyle.name.ilike(f'%{search_term}%'))
        )
        
        query = query.filter(search_filter).order_by(Cars.created_at.desc())
        
        # Paginate results
        paginated = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Build response with all images
        vehicles = []
        for car in paginated.items:
            vehicle_data = {
                "car_id": car.car_id,
                "name": car.name,
                "price": float(car.price) if car.price else None,
                "condition": car.condition,
                "year": car.year,
                "ref_no": car.ref_no,
                "make_name": car.make_ref.name if car.make_ref else None,
                "model_name": car.model_ref.model_name if car.model_ref else None,
                
                # All images
                # All images
                "images": [
                    {
                        "car_image_id": img.car_image_id,
                        "image": img.image,
                        "image_url": url_for('static', filename=f'uploads/{img.image}', _external=True)
                    } for img in car.images
                ],

                # Primary image for backward compatibility
                "primary_image_url": url_for('static', filename=f'uploads/{car.images[0].image}', _external=True) if car.images else None,
            }
            vehicles.append(vehicle_data)
        
        return jsonify({
            "success": True,
            "search_term": search_term,
            "vehicles": vehicles,
            "pagination": {
                "page": paginated.page,
                "per_page": paginated.per_page,
                "total": paginated.total,
                "pages": paginated.pages,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev
            }
        }), 200
        
    except Exception as e:
        print(f"Error searching vehicles: {e}")
        return jsonify({
            "success": False,
            "message": f"Error searching vehicles: {str(e)}"
        }), 500
    
# contacts
@app.route('/get-contacts', methods=['GET'])
def get_contacts():
    """Get all contacts"""
    try:
        contacts = Contact.query.order_by(Contact.created_at.desc()).all()
        contacts_data = [contact.to_dict() for contact in contacts]
        
        return jsonify({
            'success': True,
            'contacts': contacts_data,
            'count': len(contacts_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch contacts: {str(e)}'
        }), 500

@app.route('/add-contact', methods=['POST'])
def add_contact():
    """Add or update a contact"""
    try:
        # Get form data
        contact_name = request.form.get('contact_name', '').strip()
        contact_id = request.form.get('contact_id', '').strip()
        contact_type = request.form.get('contact_type', '').strip()
        contact_value = request.form.get('contact_value', '').strip()
        fontawesome_icon = request.form.get('contact_icon', '').strip()
        # contact_link = request.form.get('contact_link', '').strip()
        social_link = request.form.get('social_link', '').strip()
        
        # Validation
        if not contact_name:
            return jsonify({
                'success': False,
                'error': 'Contact name is required'
            }), 400
            
        if not contact_type or contact_type not in ['phone', 'email', 'social', 'whatsapp']:
            return jsonify({
                'success': False,
                'error': 'Valid contact type is required (phone, email, or social)'
            }), 400
            
            
        # Additional validation for social media
        if contact_type == 'social' and not social_link:
            return jsonify({
                'success': False,
                'error': 'Social media link is required for social contacts'
            }), 400
        
        # Check if updating existing contact
        if contact_id and contact_id.isdigit():
            contact = Contact.query.get(int(contact_id))
            if contact:
                # Update existing contact
                contact.name = contact_name
                contact.type = contact_type
                contact.value = contact_value
                contact.fontawesome_icon = fontawesome_icon
                contact.social_link = social_link if contact_type == 'social' else None
                contact.updated_at = datetime.utcnow()
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': '1',
                    'action': 'updated',
                    'contact': contact.to_dict()
                }), 200
        
        # Create new contact
        new_contact = Contact(
            name=contact_name,
            type=contact_type,
            value=contact_value,
            fontawesome_icon=fontawesome_icon,
            social_link=social_link if contact_type == 'social' else None
        )
        
        db.session.add(new_contact)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '1',
            'action': 'added',
            'contact': new_contact.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to save contact: {str(e)}'
        }), 500

@app.route('/del-contact', methods=['POST'])
def delete_contact():
    """Delete a contact"""
    try:
        contact_id = request.form.get('id')
        
        if not contact_id or not contact_id.isdigit():
            return jsonify({
                'success': False,
                'error': 'Valid contact ID is required'
            }), 400
        
        contact = Contact.query.get(int(contact_id))
        if not contact:
            return jsonify({
                'success': False,
                'error': 'Contact not found'
            }), 404
        
        db.session.delete(contact)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '1'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to delete contact: {str(e)}'
        }), 500


@app.route('/save-blog', methods=['POST'])
def save_blog():
    try:
        # Get form data
        title = request.form.get('title')
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
        image_alt = request.form.get('image_alt')
        category = request.form.get("category")
        
        # Validate required fields
        if not title or not title.strip():
            return jsonify({'message': 'Title is required'}), 400
            
        if not content or not content.strip():
            return jsonify({'message': 'Content is required'}), 400
        
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            image_file = request.files['image']
            
            if image_file and image_file.filename != '':
                try:
                    # Process the image
                    processed_filenames = process_images(
                        image_files=image_file,
                        destination_folder=BLOGS_FOLDER,
                        max_width=1920,
                        max_height=1080,
                        quality=85
                    )
                    
                    if processed_filenames and len(processed_filenames) > 0:
                        image_filename = processed_filenames[0]
                    else:
                        return jsonify({'message': 'Failed to process image'}), 500
                        
                except ValueError as ve:
                    return jsonify({'message': f'Image validation error: {str(ve)}'}), 400
                except Exception as e:
                    print(f"Error processing image: {e}")
                    return jsonify({'message': 'Error processing image'}), 500
        
        # Create new blog entry
        new_blog = Blogs(
            title=title.strip(),
            content=content.strip(),
            image_alt = image_alt,
            excerpt = excerpt,
            category = category,
            image=image_filename  # This will be None if no image was uploaded
        )
        
        # Save to database
        try:
            db.session.add(new_blog)
            db.session.commit()
            
            return jsonify({
                'success': True,  # Success indicator as expected by your frontend
                'message': "Blog saved",
            }), 200
            
        
        except Exception as db_error:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Failed to save blog'
                }), 200
    
    except Exception as e:
        print(f"Unexpected error in save_blog: {e}")
        return jsonify({
            'success': False,
            'error' : "Unexcpeted error occured",
            'details': str(e)
            }), 500


# get blogs
@app.route('/get-blogs', methods=['GET'])
def get_all_blogs():
    """
    Fetch all blogs sorted by creation date (newest first)
    """
    try:
        # Get all blogs ordered by creation date (newest first)
        blogs = Blogs.query.order_by(Blogs.created_at.desc()).all()
        
        # Convert to dictionary format
        blogs_data = []
       
        for blog in blogs:
            blog_dict = blog.to_dict()
            
            # Add full image URL if image exists
            if blog_dict['image']:
                blog_dict['image_url'] =  url_for('static', filename=f'images/blogs/{blog_dict['image']}', _external=True)
            else:
                blog_dict['image_url'] = None

            if blog_dict['excerpt']:
                blog_dict['excerpt'] = blog.excerpt

            else:
                blog_dict['excerpt'] = ""

            if blog_dict['category']: 
                cat_id = blog_dict['category']
                category = Categories.query.filter_by(category_id = cat_id).first()
                blog_dict['category'] = category.category_name
            
            else:
                blog_dict['category'] = ""
                
            blogs_data.append(blog_dict)
        
        return jsonify({
            'success': True,
            'blogs': blogs_data,
            'count': len(blogs_data)
        }), 200
        
    except Exception as e:
        print(f"Error fetching blogs: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch blogs',
            'message': str(e)
        }), 500


@app.route('/get-blog/<int:blog_id>', methods=['GET'])
def get_blog_by_id(blog_id):
    """
    Fetch a single blog by ID
    """
    try:
        blog = Blogs.query.get(blog_id)
        
        if not blog:
            return jsonify({
                'error': 'Blog not found'
            }), 404
            
        blog_data = blog.to_dict()
        
        # Add full image URL if image exists
        if blog_data['image']:
            blog_data['image_url'] = url_for('static', filename=f'images/blogs/{blog_data['image']}', _external=True) 
        else:
            blog_data['image_url'] = None
        
        if blog_data['category']: 
                cat_id = blog_data['category']
                category = Categories.query.filter_by(category_id = cat_id).first()
                blog_data['category'] = category.category_name
            
        else:
            blog_data['category'] = ""
            
        return jsonify({
            'success': True,
            'blog': blog_data
        }), 200
        
    except Exception as e:
        print(f"Error fetching blog {blog_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch blog',
            'message': str(e)
        }), 500


# get about us
@app.route('/get-about-us', methods = ['GET'])
def get_about_us():
    try:
        about_us = AboutUs.query.first()
        why_chose_us = WhyChooseUs.query.all()
        why_chose_us_data = []
        for why in why_chose_us:
            why_chose_us_item = {
                'why_id': why.why_id,
                'icon': why.icon,
                'heading': why.heading,
                'description': why.statement,
            }
            why_chose_us_data.append(why_chose_us_item)
        if about_us: 
            about = {
                'statement': about_us.statement,
                'image_1' :  url_for('static', filename=f'images/about_us/{about_us.image_1}', _external=True),
                'image_2': url_for('static', filename=f'images/about_us/{about_us.image_2}', _external=True),
                'image_1_alt' : about_us.image_1_alt,
                'image_2_alt' : about_us.image_2_alt,
                'why_choose_us': why_chose_us_data
            }
        
            return{
                'success': True,
                'about_us' : about
            }
        
        else:
            return{
                'success' : False,
                'error' : 'No about us found'
            }

    except Exception as e:
        print(f"Error fetching about: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch about',
            'details': str(e)
        }), 500 
    
# add why choose us
@app.route('/add-why-choose-us', methods=['POST'])
def add_why_choose_us():
    try:
        heading = request.form.get('heading')
        description = request.form.get('description')
        icon = request.form.get('icon')
        why_id = request.form.get('id')

        prev_why_choose_us = WhyChooseUs.query.filter_by(heading = heading).first()
        if prev_why_choose_us:
            return jsonify({
                'success': False,
                'error': 'Already exists'
            }), 200
        
        else: 
            # update if it exists
            if why_id:
                why_with_id = WhyChooseUs.query.filter_by(why_id = why_id).first()
                if why_with_id:
                    why_with_id.icon = icon
                    why_with_id.heading = heading
                    why_with_id.statement = description

                    db.session.commit()

                    # return response
                    return({
                        'success': True,
                        'message': 'Why choose us updated'
                    }), 200
                
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to update'
                    }), 200
                
            # add new record
            else: 
                new_why_choose_us = WhyChooseUs(
                    icon = icon,
                    heading = heading,
                    statement = description
                )
                db.session.add(new_why_choose_us)
                db.session.commit()

                # return response
                return({
                    'success': True,
                    'message': 'Why choose us added'
                }), 200
    except Exception as e:
        print(f"Error adding about: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to add why choose us',
            'details': str(e)
        }), 500

# delete why choose us
@app.route('/del-why-choose-us/', methods = ['POST'])
def del_why_choose_us():
    try:
        why_id = request.form.get('id')
        existing_why_choose_us = WhyChooseUs.query.filter_by(why_id = why_id).first()
        if  existing_why_choose_us:
            db.session.delete(existing_why_choose_us)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Record deleted'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Record not found'
            }), 200
    except Exception as e: 
        return jsonify({
            'success': False,
            'error': 'Failed to delete record',
            'details': str(e)
        }), 500
    
# Add FAQ
@app.route('/add-faq', methods=['POST'])
def add_faq():
    try:
        question = request.form.get('question')
        answer = request.form.get('answer')
        category_id = request.form.get('category')
        faq_id = request.form.get('faq_id')
        
        # Update existing FAQ
        if faq_id:
            faq = Faqs.query.get(faq_id)
            if faq:
                faq.question = question
                faq.answer = answer
                faq.category_id = category_id
                db.session.commit()
                return jsonify({'success': True, 'message': 'FAQ updated', 'action': 'updated'}), 200
        
        # Check if question already exists
        existing_faq = Faqs.query.filter_by(question=question).first()
        if existing_faq:
            return jsonify({'success': False, 'error': 'Question already exists'}), 200
        
        # Add new FAQ
        new_faq = Faqs(
            question=question,
            answer=answer,
            category_id=category_id
        )
        db.session.add(new_faq)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'FAQ added', 'action': 'added', 'faq': new_faq.to_dict()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e) }), 500
    

# Get all FAQs
@app.route('/get-faqs', methods=['GET'])
def get_faqs():
    try:
        faqs = Faqs.query.all()
        faqs_list = []
        
        for faq in faqs:
            faq_dict = {
                'faq_id': faq.faq_id,
                'faq_question': faq.question,
                'faq_answer': faq.answer,
                'category_id': faq.category_id,
                'category_name': faq.category_ref.category_name if faq.category_ref else None
            }
            faqs_list.append(faq_dict)
        
        return jsonify({'success': True, 'faqs': faqs_list})
    
    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to fetch faqs'}), 500


# Delete FAQ
@app.route('/del-faq', methods=['POST'])
def delete_faq():
    try:
        faq_id = request.form.get('id')
        
        faq = Faqs.query.get(faq_id)
        if not faq:
            return jsonify({'success': False, 'error': 'FAQ not found'})
        
        db.session.delete(faq)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'FAQ Deleted'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error':'Failed to delete faq'}), 500
    

# get vehicle names
@app.route('/get-vehicle-names', methods=['GET'])
def get_vehicle_names():
   
    try:
        cars = Cars.query.all()
        # Build response
        vehicle_names = []
        for car in cars:
            vehicle_data = {
                "car_id": car.car_id,
                "name": car.name,
            }
            vehicle_names.append(vehicle_data)
        
        return jsonify({
            "success": True,
            "vehicle_names": vehicle_names,
        }), 200
        
    except Exception as e:
        print(f"Error retrieving vehicles: {e}")
        return jsonify({
            "success": False,
            "message": f"Error retrieving vehicle names: {str(e)}"
        }), 500


# add review
@app.route('/add-review', methods = ['POST'])
def add_review():
    try:
        car_id = request.form.get('car_id')
        title = request.form.get('title')
        rating = request.form.get('rating')
        review = request.form.get('review')
        reviewer = request.form.get('reviewer')

        if not rating:
            rating = 0

        image_filename = None
        if 'image' in request.files:
            image_file = request.files['image']

            if image_file and image_file.filename != '':
                try:
                    # Process the image
                        processed_filenames = process_images(
                            image_files=image_file,
                            destination_folder=REVIEWS_FOLDER,
                            max_width=1920,
                            max_height=1080,
                            quality=85
                        )
                        
                        if processed_filenames and len(processed_filenames) > 0:
                            image_filename = processed_filenames[0]
                        else:
                            return jsonify({'message': 'Failed to process image'}), 500
                            
                except ValueError as ve:
                    return jsonify({'success': False,'message': f'Image validation error'}), 400
                except Exception as e:
                    print(f"Error processing image: {e}")
                    return jsonify({'success': False,'message': 'Error processing image'}), 500
                
        # save review
        new_review = Reviews(
            title = title,
            rating = rating,
            reviewer = reviewer,
            text = review,
            image = image_filename,
            car_id = car_id,
        )
        db.session.add(new_review)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Thank you for your review',
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed. Unexpected error occurred.',
            'details': str(e)
        }), 200

# get reviews
@app.route('/get-reviews/<review_status>', methods = ['GET'])
def get_reviews(review_status):
    try:
        all_reviews = []
        average_rating = 0

        if review_status == 'all':
            reviews = Reviews.query.all()

            total_rating = 0
            count = 0

            for review in reviews:
                vehicle = Cars.query.filter_by(car_id=review.car_id).first()
                car_name = vehicle.name if vehicle else None

                # review image
                review_image = url_for(
                    'static',
                    filename=f'images/reviews/{review.image}',
                    _external=True
                )

                review_data = {
                    'review_id': review.review_id,
                    'title': review.title,
                    'rating': review.rating,
                    'reviewer': review.reviewer,
                    'date': review.date.isoformat(),
                    'review': review.text,
                    'image': review_image,
                    'status': review.status,
                    'car_id': review.car_id,
                    'car_name': car_name,
                }

                all_reviews.append(review_data)

                
                if review.rating is not None:
                    total_rating += review.rating
                    count += 1

            average_rating = total_rating / count if count > 0 else 0


        else:
            reviews = Reviews.query.filter_by(status = review_status).all()
            total_rating = 0
            count = 0

            for review in reviews:
                vehicle = Cars.query.filter_by(car_id=review.car_id).first()
                car_name = vehicle.name if vehicle else None

                # review image
                review_image = url_for(
                    'static',
                    filename=f'images/reviews/{review.image}',
                    _external=True
                )

                review_data = {
                    'review_id': review.review_id,
                    'title': review.title,
                    'rating': review.rating,
                    'reviewer': review.reviewer,
                    'date': review.date.isoformat(),
                    'review': review.text,
                    'image': review_image,
                    'status': review.status,
                    'car_id': review.car_id,
                    'car_name': car_name,
                }

                all_reviews.append(review_data)

                
                if review.rating is not None:
                    total_rating += review.rating
                    count += 1

            average_rating = total_rating / count if count > 0 else 0

        return jsonify({
            'success': True,
            'reviews': all_reviews,
            'average_rating': average_rating
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed. Unexpected error occured.',
            'details': str(e)
        }), 200

# toggle review status
@app.route('/toggle-review', methods = ['POST'])
def toggle_review():
    try:
        review_id = request.form.get('review_id')

        fetched_review = Reviews.query.filter_by(review_id = review_id).first()

        if fetched_review.status == 'Active':
            fetched_review.status = 'Inactive'
        else: 
            fetched_review.status = 'Active'

        db.session.commit()
        return({
            'success': True,
            'message': 'Review status updated'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed. Unexpected error occured',
            'details': str(e)
        }), 200


# mark message as read
@app.route('/mark-as-read', methods = ['POST'])
def mark_as_read():
    try:
        message_id = request.form.get("id")
        existing_message = ContactUs.query.get(message_id)

        if not existing_message:
            return jsonify({
                'success': False,
                'error': 'Enquiry not found'
            }), 200
        
        else: 
            existing_message.status = 'Read'
            db.session.commit()


            return jsonify({
                'success': True,
                'message': "Enquiry marked as read"
            }), 200

    except Exception as e:
        print("Error marking message as read: ", str(e))
        return jsonify({
            'success': False,
            'error': "Failed. Unexpected error occured",
            'details': str(e)
        }), 500
    

# mark message as read
@app.route('/mark-enquiry-as-read', methods = ['POST'])
def mark_enquiry_as_read():
    try:
        message_id = request.form.get("id")
        existing_message = Enquiries.query.get(message_id)

        if not existing_message:
            return jsonify({
                'success': False,
                'error': 'Enquiry not found'
            }), 200
        
        else: 
            existing_message.status = 'Read'
            db.session.commit()


            return jsonify({
                'success': True,
                'message': "Enquiry marked as read"
            }), 200

    except Exception as e:
        print("Error marking message as read: ", str(e))
        return jsonify({
            'success': False,
            'error': "Failed. Unexpected error occured",
            'details': str(e)
        }), 500

# delete contact enquiry
@app.route('/del-contact-us', methods = ['POST'])
def del_contact_us():
    try:
        message_id = request.form.get('id')
        message = ContactUs.query.get(message_id)
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message not found'
            }), 200
        
        else:
            db.session.delete(message)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Enquiry deleted'
            }), 200

    except Exception as e:
        print("Error deleting contact enquiry: ", str(e))
        return jsonify({
            'success': False,
            'error': 'Failed. An unexpected error occured'
        }), 500


# delete contact enquiry
@app.route('/del-enquiry', methods = ['POST'])
def del_enquiry():
    try:
        message_id = request.form.get('id')
        message = Enquiries.query.get(message_id)
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Enquiry not found'
            }), 200
        
        else:
            db.session.delete(message)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Enquiry deleted'
            }), 200

    except Exception as e:
        print("Error deleting contact enquiry: ", str(e))
        return jsonify({
            'success': False,
            'error': 'Failed. An unexpected error occured'
        }), 500

# delete review
@app.route('/del-review', methods = ['POST'])
def del_review():
    try:
        review_id = request.form.get('id')

        if not review_id:
            return jsonify({'success': False, 'error': 'Review ID is required'}), 200
        
        else:
            review = Reviews.query.get(review_id)
            db.session.delete(review)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Review deleted',
            }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed. Unexpected error occured',
            'details': str(e)
        }), 200


# Add vehicle to sell
@app.route('/add-vehicle-to-sell', methods=['POST'])
def add_vehicle_to_sell():
    try:
        # Get form data
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        location = request.form.get('location')
        make_id = request.form.get('make_id')
        model_id = request.form.get('model_id')
        year = request.form.get('year')
        mileage = request.form.get('mileage')
        price = request.form.get('price')
        fuel_type = request.form.get('fuel_type')
        body_id = request.form.get('body_id')
        transmission = request.form.get('transmission')
        color = request.form.get('color')
        steering = request.form.get('steering')
        drive_type = request.form.get('drive_type')
        description = request.form.get('description', '')
        features_json = request.form.get('features')
        
        # Validate required fields
        required_fields = {
            'full_name': full_name,
            'phone': phone,
            'email': email,
            'location': location,
            'make_id': make_id,
            'model_id': model_id,
            'year': year,
            'price': price,
            'body_id': body_id
        }
        
        for field, value in required_fields.items():
            if not value:
                return jsonify({
                    'success': False,
                    'message': f'{field.replace("_", " ").title()} is required'
                }), 400
        
        # Get uploaded images
        images = request.files.getlist('images')
        
        if not images or len(images) == 0:
            return jsonify({
                'success': False,
                'message': 'At least one image is required'
            }), 400
        
        if len(images) > 6:
            return jsonify({
                'success': False,
                'message': 'Maximum 6 images allowed'
            }), 400
        
        # Validate image sizes (3MB each)
        max_size = 3 * 1024 * 1024  # 3MB in bytes
        for img in images:
            if img.filename == '':
                return jsonify({
                    'success': False,
                    'message': 'Invalid image file'
                }), 400
            
            # Check file size
            img.seek(0, 2)  # Seek to end
            size = img.tell()
            img.seek(0)  # Reset to beginning
            
            if size > max_size:
                return jsonify({
                    'success': False,
                    'message': f'Image {img.filename} exceeds 3MB size limit'
                }), 400
        
        # First, create a Selling record
        new_selling = Selling(
            seller=full_name,
            phone_number=phone,
            email=email,
            location=int(location),
            status='pending'
        )
        db.session.add(new_selling)
        db.session.flush()  # Get the ID without committing
        
        # Create car details record
        new_car_details = CarToSellDetails(
            selling_id=new_selling.sell_id,
            make=int(make_id),
            model=int(model_id),
            year=int(year),
            mileage=mileage,
            selling_price=float(price),
            fuel_type=fuel_type,
            body_type=int(body_id),
            transmission=transmission,
            steering=steering,
            drive_type=drive_type,
            description=description
        )
        db.session.add(new_car_details)
        db.session.flush()  # Get the ID without committing
        
        # Process and save images using your existing function
        try:
            processed_filenames = process_images(
                image_files=images,
                destination_folder=SELLING_FOLDER,
                max_width=1920,
                max_height=1080,
                quality=85
            )
            
            # Save image records to database
            for filename in processed_filenames:
                # Store relative path
                # relative_path = f"/uploads/selling_vehicles/{filename}"
                
                car_image = CarSellingImages(
                    car_to_sell_id=new_car_details.car_sell_id,
                    image=filename
                )
                db.session.add(car_image)
                
        except ValueError as ve:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(ve)
            }), 400
        except Exception as img_error:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': 'Failed to process images',
                'details': str(img_error)
            }), 500
        
        # Parse and save features
        if features_json:
            try:
                features_list = json.loads(features_json)
                if isinstance(features_list, list):
                    for feature_id in features_list:
                        if feature_id:  # Skip empty values
                            car_feature = CarSellingFeatures(
                                feature=int(feature_id),
                                car_to_sell_id=new_car_details.car_sell_id
                            )
                            db.session.add(car_feature)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error parsing features: {e}")
                # Continue without features rather than failing
        
        # Commit all changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Thank you. We will get back to you soon',
            'data': {
                'car_sell_id': new_car_details.car_sell_id,
                'selling_id': new_selling.sell_id
            }
        }), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Invalid data format',
            'details': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        print("Error at add_vehicle_to_sell(): ", str(e))
        return jsonify({
            'success': False,
            'message': 'Failed. An unexpected error occurred',
            'details': str(e)
        }), 500


# Get all selling vehicles
@app.route('/get-selling-vehicles', methods=['GET'])
def get_selling_vehicles():
    try:
        # Optional query parameters for filtering
        status = request.args.get('status')
        make_id = request.args.get('make_id')
        body_type = request.args.get('body_type')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        year_from = request.args.get('year_from')
        year_to = request.args.get('year_to')
        limit = request.args.get('limit', type=int)
        
        # Build query
        query = db.session.query(CarToSellDetails).join(Selling)
        
        # Apply filters if provided
        if status:
            query = query.filter(Selling.status == status)
        if make_id:
            query = query.filter(CarToSellDetails.make == int(make_id))
        if body_type:
            query = query.filter(CarToSellDetails.body_type == int(body_type))
        if min_price:
            query = query.filter(CarToSellDetails.selling_price >= float(min_price))
        if max_price:
            query = query.filter(CarToSellDetails.selling_price <= float(max_price))
        if year_from:
            query = query.filter(CarToSellDetails.year >= int(year_from))
        if year_to:
            query = query.filter(CarToSellDetails.year <= int(year_to))
        
        # Order by most recent
        query = query.order_by(CarToSellDetails.car_sell_id.desc())
        
        # Apply limit if provided
        if limit:
            query = query.limit(limit)
        
        # Execute query
        vehicles = query.all()
        
        # Convert to dict with seller info
        vehicles_data = []
        for vehicle in vehicles:
            vehicle_dict = vehicle.to_dict()
            
            # Add seller information from Selling table
            selling = Selling.query.get(vehicle.selling_id)
            if selling:
                vehicle_dict['seller'] = {
                    'full_name': selling.seller,
                    'phone': selling.phone_number,
                    'email': selling.email,
                    'location': selling.location,
                    'color': selling.color if hasattr(selling, 'color') else None,
                    'status': selling.status if hasattr(selling, 'status') else None
                }
            
            vehicles_data.append(vehicle_dict)
        
        return jsonify({
            'success': True,
            'count': len(vehicles_data),
            'vehicles': vehicles_data
        }), 200
        
    except Exception as e:
        print("Error at get_selling_vehicles(): ", str(e))
        return jsonify({
            'success': False,
            'message': 'Failed to fetch vehicles',
            'details': str(e)
        }), 500


# Get single selling vehicle by ID
@app.route('/get-selling-vehicle/<int:car_sell_id>', methods=['GET'])
def get_selling_vehicle(car_sell_id):
    try:
        vehicle = CarToSellDetails.query.get(car_sell_id)
        
        if not vehicle:
            return jsonify({
                'success': False,
                'message': 'Vehicle not found'
            }), 404
        
        vehicle_dict = vehicle.to_dict()
        
        # Add seller information
        selling = Selling.query.get(vehicle.selling_id)
        if selling:
            vehicle_dict['seller'] = {
                'full_name': selling.seller,
                'phone': selling.phone_number,
                'email': selling.email,
                'location': selling.location,
                'color': selling.color if hasattr(selling, 'color') else None,
                'status': selling.status if hasattr(selling, 'status') else None
            }
        
        return jsonify({
            'success': True,
            'vehicle': vehicle_dict
        }), 200
        
    except Exception as e:
        print("Error at get_selling_vehicle(): ", str(e))
        return jsonify({
            'success': False,
            'message': 'Failed to fetch vehicle',
            'details': str(e)
        }), 500


# update about us
@app.route('/update-about', methods=['POST'])
def update_about_us():
    try:
        statement = request.form.get("statement")
        image_1 = request.files.get("image_1")
        image_2 = request.files.get("image_2")
        image_1_alt = request.form.get("image_1_alt")
        image_2_alt = request.form.get("image_2_alt")

        about_us = AboutUs.query.first()
        if statement:
            about_us.statement = statement
            db.session.commit()
        
        if image_1_alt:
            about_us.image_1_alt = image_1_alt
            db.session.commit()
        
        if image_2_alt:
            about_us.image_2_alt = image_2_alt
            db.session.commit()

        if image_1:
            # delete previous image
            previous_image = about_us.image_1
            image_path = os.path.join(ABOUT_US_FOLDER, previous_image)
            if os.path.exists(image_path):
                os.remove(image_path)
            
            processed_image = process_images(image_1, ABOUT_US_FOLDER)
            about_us.image_1 = processed_image[0]
            db.session.commit()

        if image_2:
            # delete previous image
            previous_image = about_us.image_2
            image_path = os.path.join(ABOUT_US_FOLDER, previous_image)
            if os.path.exists(image_path):
                os.remove(image_path)

            processed_image = process_images(image_2, ABOUT_US_FOLDER)
            about_us.image_2 = processed_image[0]
            db.session.commit()

        return jsonify({
            'success': True,
            'message': 'About us updated'
        })
    except Exception as e:
        print("Error at update_about_us(): ", str(e))
        return jsonify({
            'success': False,
            'error': 'Failed. An unexpected error occured',
            'details': str(e)
        })

# update blog
@app.route('/update-blog', methods=['POST'])
def update_blog():
    try:
        content = request.form.get('content')
        title = request.form.get('title')
        image_alt = request.form.get('image_alt')
        excerpt = request.form.get('excerpt')
        category = request.form.get('category')
        image_filename = request.files.get('image')
        id=request.form.get("id")

        print("title", str(title))
        print("image_alt", str(image_alt))
        print("excerpt", str(excerpt))
        print("category", str(category))
        print("image_filename", str(image_filename))

        blog = Blogs.query.filter_by(blog_id = id).first()
       
        blog.content = content
        blog.title = title
        blog.image_alt = image_alt
        blog.excerpt = excerpt
        if category:
            blog.category = category
        
        if image_filename:
            # delete previous image
            previous_image = blog.image
            image_path = os.path.join(BLOGS_FOLDER, previous_image)
            if os.path.exists(image_path):
                os.remove(image_path)
            
            processed_image = process_images(image_filename, BLOGS_FOLDER)
            blog.image = processed_image[0]
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': "Blog updated"
        }), 200


    except Exception as e:
        print("Error at update_blog(): ", str(e))
        return jsonify({
            'success': False,
            'error': 'Failed. An unexpected error occured'
        }), 500
    
# delete blog
@app.route('/del-blog/<blog_id>', methods=['GET'])
def del_blog(blog_id):
    try:
        existing_blog = Blogs.query.filter_by(blog_id = blog_id).first()
        image_filename = existing_blog.image
        if image_filename:
                # delete previous image
                previous_image = existing_blog.image
                image_path = os.path.join(BLOGS_FOLDER, previous_image)
                if os.path.exists(image_path):
                    os.remove(image_path)

        db.session.delete(existing_blog)
        db.session.commit()
        db.session.commit()
        return jsonify({
            'success': True,
            'message': "Blog deleted"
        }), 200
    
    except Exception as e:
        print("Error at del_blog(): ", str(e))
        return jsonify({
            'success': False,
            'error': 'Failed. An unexpected error occured'
        }), 500

# update sell status
@app.route('/change-selling-status/<selling_id>', methods=['GET'])
def toggle_selling_status(selling_id):
    try:
        selling = Selling.query.filter_by(sell_id = selling_id).first()
        if selling.status == 'Pending':
            selling.status = 'Complete'
        else:
            selling.status = 'Pending'
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Status updated'
        }), 200
    
    except Exception as e:
        print('error in toggle_selling_status(): ', str(e))
        return jsonify({
            'success': False,
            'error': "Failed. An unexpected error occured"
        }), 500

@app.route('/del-sell/<selling_id>', methods=['GET'])
def del_sell(selling_id):
    try:
        selling = Selling.query.filter_by(sell_id=selling_id).first()
        
        if not selling:
            return jsonify({
                'success': False,
                'error': 'Selling record not found'
            }), 404
        
        # Get car details first (to access images and features through relationship)
        car_to_sell_details = CarToSellDetails.query.filter_by(selling_id=selling_id).first()
        
        if car_to_sell_details:
            # Delete all images from filesystem
            selling_images = CarSellingImages.query.filter_by(car_to_sell_id=car_to_sell_details.car_sell_id).all()
            for image in selling_images:
                image_to_delete = image.image
                if image_to_delete:
                    image_path = os.path.join(SELLING_FOLDER, image_to_delete)
                    if os.path.exists(image_path):
                        os.remove(image_path)
                # Delete image record from database
                db.session.delete(image)
            
            # Delete car selling features
            car_selling_features = CarSellingFeatures.query.filter_by(car_to_sell_id=car_to_sell_details.car_sell_id).all()
            for feature in car_selling_features:
                db.session.delete(feature)
            
            # Delete car details
            db.session.delete(car_to_sell_details)
        
        # Delete the main selling record
        db.session.delete(selling)
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Selling request deleted '
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print('error in del_sell(): ', str(e))
        return jsonify({
            'success': False,
            'error': "Failed. An unexpected error occurred"
        }), 500

# delete vehicle
@app.route('/del-vehicle/<int:car_id>', methods=['GET'])
def del_vehicle(car_id):
    try:
        # Find the car by ID
        car = Cars.query.get(car_id)
        
        # Check if car exists
        if not car:
            return jsonify({
                'success': False,
                'error': 'Vehicle not found'
            }), 404
        
        # Delete associated image files from filesystem
        for car_image in car.images:
            image_path = os.path.join('VEHICLE_IMAGES', car_image.image)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except OSError as e:
                    print(f"Error deleting image {image_path}: {str(e)}")
        
        # Delete the car from database
        # This will cascade delete CarImages and CarFeatures due to cascade='all, delete-orphan'
        db.session.delete(car)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vehicle deleted'
        }), 200

    except Exception as e:
        db.session.rollback()
        print("Error in del_vehicle(): ", str(e))
        return jsonify({
            'success': False,
            'error': 'Failed. An unexpected error occurred'
        }), 500



# edit data
@app.route('/save-vehicle/<int:car_id>', methods=['POST'])
def save_vehicle(car_id=None):
    try:
        data = request.form
        
        # Determine if this is an update or new vehicle
        if car_id:
            vehicle = Cars.query.get(car_id)
            if not vehicle:
                return jsonify({
                    'success': False,
                    'message': 'Vehicle not found'
                }), 404
        else:
            vehicle = Cars()
        
        # Update basic vehicle information
        vehicle.name = data.get('name')
        vehicle.price = data.get('price')
        vehicle.condition = data.get('condition')
        vehicle.model_id = data.get('model_id') if data.get('model_id') else None
        
        # Update existing fields
        vehicle.make = data.get('make')
        vehicle.body_style = data.get('body_style') if data.get('body_style') else None
        vehicle.mileage = data.get('mileage')
        vehicle.year = data.get('year')
        vehicle.engine = data.get('engine')
        vehicle.location = data.get('location') if data.get('location') else None
        vehicle.ref_no = data.get('ref_no')
        vehicle.model_code = data.get('model_code')
        vehicle.steering = data.get('steering')
        vehicle.exterior_color = data.get('exterior_color')
        vehicle.fuel = data.get('fuel')
        vehicle.seats = data.get('seats') if data.get('seats') else None
        vehicle.interior_color = data.get('interior_color')
        vehicle.seats_color = data.get('seats_color')
        vehicle.drive = data.get('drive')
        vehicle.doors = data.get('doors')
        vehicle.transmission = data.get('transmission')
        vehicle.weight = data.get('weight')
        
        # Add to session if new vehicle
        if not car_id:
            db.session.add(vehicle)
        
        # Commit to get the car_id
        db.session.commit()
        
        # Handle features (if provided)
        if 'features' in data:
            # Remove existing features if updating
            if car_id:
                CarFeatures.query.filter_by(car_id=vehicle.car_id).delete()
            
            # Add new features
            features = data.getlist('features') if hasattr(data.get('features'), '__iter__') else data.get('features', '').split(',')
            for feature_id in features:
                if feature_id:
                    car_feature = CarFeatures(
                        car_id=vehicle.car_id,
                        feature=int(feature_id)
                    )
                    db.session.add(car_feature)
        
        # Handle images (if provided)
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename:
                    # Save the file and get the path
                    filename = secure_filename(file.filename)
                    # Add your file saving logic here
                    # file_path = save_uploaded_file(file, filename)
                    
                    car_image = CarImages(
                        car=vehicle.car_id,
                        image=filename  # or file_path
                    )
                    db.session.add(car_image)
        
        # Handle image URLs (if provided as array)
        if 'image_urls' in data:
            image_urls = data.getlist('image_urls')
            for image_url in image_urls:
                if image_url:
                    car_image = CarImages(
                        car=vehicle.car_id,
                        image=image_url
                    )
                    db.session.add(car_image)
        
        db.session.commit()
        
        message = 'Vehicle updated ' if car_id else 'Vehicle added successfully!'
        
        return jsonify({
            'success': True,
            'message': message,
            'car_id': vehicle.car_id
        }), 200

    except Exception as e:
        db.session.rollback()
        print("Error in save_vehicle(): ", str(e))
        return jsonify({
            'success': False,
            'message': 'Failed to save vehicle. An unexpected error occurred'
        }), 500

# mark vehicle as sold
@app.route('/toggle-vehicle-status/<car_id>', methods=['GET'])
def mark_vehicle_as_sold(car_id):
    try:
        vehicle = Cars.query.filter_by(car_id = car_id).first()
        vehicle.status = 'Sold'

        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Vehicle status changed'
        }), 200
    except Exception as e:
        print("Error in mark_vehicle_as_sold(): ", str(e))
        return jsonify({
            'success': False,
            'error': 'Failed. An unexpected error occured',
            'details': str(e)
        }), 500

# filter vehicles
@app.route("/filter-vehicles", methods = ['POST'])
def filter_vehicles():
    try:
        # Get all filter parameters from form
        location = request.form.get("location")
        body = request.form.get("body")
        model = request.form.get("model")
        make = request.form.get("make")
        min_year = request.form.get("min_year")
        max_year = request.form.get("max_year")
        fuel = request.form.get("fuel")
        transmission = request.form.get("transmission")  # Fixed typo
        condition = request.form.get("condition")
        min_price = request.form.get("min_price")
        max_price = request.form.get("max_price")
        status = request.form.get("status")

        # Start with base query
        query = Cars.query
        
        # Apply filters directly to the query for better performance
        # Only apply filter if value exists and is not empty/placeholder
        if location and location.strip() and location.isdigit():
            query = query.filter(Cars.location == int(location))
        
        if body and body.strip() and body.isdigit():
            query = query.filter(Cars.body_style == int(body))
        
        if model and model.strip() and model.isdigit():
            query = query.filter(Cars.model_id == int(model))
        
        if make and make.strip() and make.isdigit():
            query = query.filter(Cars.make == int(make))
        
        if fuel and fuel.strip():
            query = query.filter(Cars.fuel == fuel)
        
        if transmission and transmission.strip():
            query = query.filter(Cars.transmission == transmission)
        
        if condition and condition.strip():
            query = query.filter(Cars.condition == condition)
        
        if status and status.strip():
            query = query.filter(Cars.status == status)
        
        # Year range filter
        if min_year and min_year.strip() and min_year.isdigit():
            query = query.filter(Cars.year >= int(min_year))
        
        if max_year and max_year.strip() and max_year.isdigit():
            query = query.filter(Cars.year <= int(max_year))
        
        # Price range filter
        if min_price and min_price.strip():
            try:
                query = query.filter(Cars.price >= float(min_price))
            except ValueError:
                pass  # Skip invalid price values
        
        if max_price and max_price.strip():
            try:
                query = query.filter(Cars.price <= float(max_price))
            except ValueError:
                pass  # Skip invalid price values
        
        # Execute query
        fetched_vehicles = query.all()
        
        # Build vehicle data
        vehicles = []
        for car in fetched_vehicles:
            vehicle_data = {
                "car_id": car.car_id,
                "name": car.name,
                "price": float(car.price) if car.price else None,
                "condition": car.condition,
                "year": car.year,
                "mileage": car.mileage,
                "ref_no": car.ref_no,
                "steering": car.steering,
                "engine": car.engine,
                "fuel": car.fuel,
                "transmission": car.transmission,
                "seats": car.seats,
                "status": car.status,
                
                # Make and model info
                "make": {
                    "make_id": car.make_ref.make_id if car.make_ref else None,
                    "name": car.make_ref.name if car.make_ref else None,
                    "logo_image": car.make_ref.logo_image if car.make_ref else None
                },
                "model": {
                    "model_id": car.model_ref.model_id if car.model_ref else None,
                    "model_name": car.model_ref.model_name if car.model_ref else None
                } if car.model_ref else None,
                
                # Body style
                "body_style": {
                    "style_id": car.body_style_ref.style_id if car.body_style_ref else None,
                    "name": car.body_style_ref.name if car.body_style_ref else None
                } if car.body_style_ref else None,
                
                # Location
                "location": {
                    "location_id": car.location_ref.location_id if car.location_ref else None,
                    "location_name": car.location_ref.location_name if car.location_ref else None
                } if car.location_ref else None,
                
                # All images
                "images": [
                    {
                        "car_image_id": img.car_image_id,
                        "image": img.image,
                        "image_url": url_for('static', filename=f'uploads/{img.image}', _external=True)
                    } for img in car.images
                ],

                # Primary image for backward compatibility
                "primary_image_url": url_for('static', filename=f'uploads/{car.images[0].image}', _external=True) if car.images else None,
                
                # Image count
                "image_count": len(car.images),
                
                # Timestamps
                "created_at": car.created_at.isoformat() if car.created_at else None,
                "updated_at": car.updated_at.isoformat() if car.updated_at else None
            }
            vehicles.append(vehicle_data)
        
        return jsonify({
            'success': True,
            'vehicles': vehicles,
            'total_count': len(vehicles)
        }), 200
        
    except ValueError as e:
        print("ValueError in filter_vehicles(): ", str(e))
        return jsonify({
            'success': False,
            'error': "Invalid filter parameters"
        }), 400
    except Exception as e:
        print("Error in filter_vehicles(): ", str(e))
        return jsonify({
            'success': False,
            'error': "Failed. An unexpected error occurred"
        }), 500
    

# filter blogs
@app.route('/filter-blogs/<blog_id>', methods=['GET'])
def filter_blogs(blog_id):
    """
    Fetch all blogs sorted by creation date (newest first)
    """
    try:
       
        # Get all blogs ordered by creation date (newest first)
        blogs = None

        if blog_id ==  "All":
            blogs = Blogs.query.order_by(Blogs.created_at.desc()).all()
        else:
            blogs = Blogs.query.filter_by(category = blog_id).order_by(Blogs.created_at.desc()).all()
        
        # Convert to dictionary format
        blogs_data = []
       
        for blog in blogs:
            blog_dict = blog.to_dict()
            
            # Add full image URL if image exists
            if blog_dict['image']:
                blog_dict['image_url'] =  url_for('static', filename=f'images/blogs/{blog_dict['image']}', _external=True)
            else:
                blog_dict['image_url'] = None

            if blog_dict['excerpt']:
                blog_dict['excerpt'] = blog.excerpt

            else:
                blog_dict['excerpt'] = ""

            if blog_dict['category']: 
                cat_id = blog_dict['category']
                category = Categories.query.filter_by(category_id = cat_id).first()
                blog_dict['category'] = category.category_name
            
            else:
                blog_dict['category'] = ""
                
            blogs_data.append(blog_dict)
        
        return jsonify({
            'success': True,
            'blogs': blogs_data,
            'count': len(blogs_data)
        }), 200
        
    except Exception as e:
        print(f"Error fetching blogs: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch blogs',
            'message': str(e)
        }), 500
    
# get user
@app.route('/get-user', methods = ['GET'])
def get_user():
    try:
    # Get all features from database
        fetched_user = Users.query.first()
        user_data = {
            'id': fetched_user.id,
            'email': fetched_user.email,
            'name': fetched_user.name
        }
        

        return jsonify({
            'success': True,
            'user': user_data,
        }), 200
    except Exception as e:
        print(f"Error in get_user: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch blogs',
            'message': str(e)
        }), 500

# update password
@app.route("/update-user", methods=['POST'])
def update_user():
    try:
        email = request.form.get('email')
        name = request.form.get('name')
        new_password = request.form.get('new_password')
        old_password = request.form.get('old_password')

        # Find user
        user = Users.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'sucess': False,
                'error': 'User not found'
            }), 200

        # If old_password provided, check before updating password
        if old_password:
            if not check_password_hash(user.password, old_password):
                return jsonify({
                    'success': False,
                    'error': 'Incorrect password'
                }), 200

        # Update details
        user.name = name if name else user.name
        user.email = email if email else user.email

        if new_password:
            user.password = generate_password_hash(new_password)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'User updated '
        }), 200

    except Exception as e:
        print("Error at update_user(): ", str(e))
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed. An unexpected error occured',
            'details': str(e)
        }), 200
    
 # filter reviews
@app.route('/filter-reviews/<review_status>', methods=['POST'])
def filter_reviews(review_status):
    try:
        model = request.form.get('model')
        make = request.form.get('make')
        body = request.form.get('body')

        all_reviews = []
        
        # Start with base query filtered by status
        reviews_query = Reviews.query.filter_by(status=review_status)
        
        # Get all reviews with the specified status
        reviews = reviews_query.all()
        
        total_rating = 0
        count = 0

        for review in reviews:
            vehicle = Cars.query.filter_by(car_id=review.car_id).first()
            
            # Skip if vehicle doesn't exist
            if not vehicle:
                continue
            
            # Apply filters - skip review if it doesn't match the criteria
            if make and str(vehicle.make) != str(make):
                continue
            
            if model and vehicle.model_id and str(vehicle.model_id) != str(model):
                continue
            
            if body and vehicle.body_style and str(vehicle.body_style) != str(body):
                continue
            
            car_name = vehicle.name if vehicle else None

            # review image
            review_image = url_for(
                'static',
                filename=f'images/reviews/{review.image}',
                _external=True
            )

            review_data = {
                'review_id': review.review_id,
                'title': review.title,
                'rating': review.rating,
                'reviewer': review.reviewer,
                'date': review.date.isoformat(),
                'review': review.text,
                'image': review_image,
                'status': review.status,
                'car_id': review.car_id,
                'car_name': car_name,
            }

            all_reviews.append(review_data)

            if review.rating is not None:
                total_rating += review.rating
                count += 1

        average_rating = total_rating / count if count > 0 else 0
        return jsonify({
            'success': True,
            'reviews': all_reviews,
            'average_rating': average_rating
        })

    except Exception as e:
        print("Error at filter_reviews(): ", str(e))
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed. An unexpected error occured',
            'details': str(e)
        }), 200

# search faq
@app.route('/search-faq/<search_input>', methods=['GET'])
def search_faq(search_input):
    try:
        # Filter FAQs where faq_question matches the search_input (case-insensitive)
        faqs = Faqs.query.filter(Faqs.question.ilike(f"%{search_input}%")).all()
        faqs_list = []

        for faq in faqs:
            faq_dict = {
                'faq_id': faq.faq_id,
                'faq_question': faq.question,
                'faq_answer': faq.answer,
                'category_id': faq.category_id,
                'category_name': faq.category_ref.category_name if faq.category_ref else None
            }
            faqs_list.append(faq_dict)

        return jsonify({'success': True, 'faqs': faqs_list})

    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to fetch faqs: {str(e)}'}), 500

# search blog
@app.route('/search-blog/<search_input>', methods=['GET'])
def search_blog(search_input):

    try:
        # Get all blogs ordered by creation date (newest first)
        blogs = Blogs.query.filter(Blogs.title.ilike(f"%{search_input}%")).all()
        
        # Convert to dictionary format
        blogs_data = []
       
        for blog in blogs:
            blog_dict = blog.to_dict()
            
            # Add full image URL if image exists
            if blog_dict['image']:
                blog_dict['image_url'] =  url_for('static', filename=f'images/blogs/{blog_dict['image']}', _external=True)
            else:
                blog_dict['image_url'] = None

            if blog_dict['excerpt']:
                blog_dict['excerpt'] = blog.excerpt

            else:
                blog_dict['excerpt'] = ""

            if blog_dict['category']: 
                cat_id = blog_dict['category']
                category = Categories.query.filter_by(category_id = cat_id).first()
                blog_dict['category'] = category.category_name
            
            else:
                blog_dict['category'] = ""
                
            blogs_data.append(blog_dict)
        
        return jsonify({
            'success': True,
            'blogs': blogs_data,
            'count': len(blogs_data)
        }), 200
        
    except Exception as e:
        print(f"Error fetching blogs: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch blogs',
            'message': str(e)
        }), 500

# forgot password
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    username = request.form.get('username')

    if not username:
        return jsonify({"message":"3"}), 200 # no credentials

    user = Users.query.filter_by(email=username).first()

    if user:
        # send OTP here
        otp = generate_otp()
        subject = "Your OTP Code"
        body = f"Your One-Time Password (OTP) is: {otp}\n\nIt is valid for 5 minutes."

        send_email(username, subject, body)

        # store in db
        new_otp = OTPStore(username=username, otp=otp)
        db.session.add(new_otp)
        db.session.commit()

        return jsonify({"message":"1"}), 200
    else:
        return jsonify({"message": "2"}), 200 # user does not exist


# generate otp
def generate_otp():
    return str(random.randint(100000, 999999))
# send OTP via email
def send_email(to_email, subject, body):
    try:
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)

        # Send
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()

        return jsonify({"message": "1"}), 200
    except Exception as e:
        return jsonify({"message": "Error"}), 403
        # return False, str(e)

# verify otp
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    try: 
        username = request.form.get('username')
        otp = request.form.get('otp')
        password = request.form.get('password')


        record = OTPStore.query.filter_by(username=username, otp=otp).first()

        if record:
            if record.is_expired:
                db.session.delete(record)  # cleanup expired OTP
                db.session.commit()
                return jsonify({"message": "2"}), 200
            
            # Valid OTP
            db.session.delete(record)  # remove after use
            db.session.commit()
            # save new password
            user = Users.query.filter_by(email=username).first()

            # Hash the password before saving
            hashed_password = generate_password_hash(password)

            user.password = hashed_password
            db.session.commit()

        # return response
        return jsonify({"message": "1"}), 200
    
    except Exception as e:
            print("Error is: ", str(e))
            db.session.rollback()
            return jsonify({"error": str(e)}), 400