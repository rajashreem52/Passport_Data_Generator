from PIL import Image, ImageDraw, ImageFont
import json
import os
import argparse
import numpy as np
import cv2

    
def draw_text_with_box(draw, position, text, font, color=(0, 0, 0)):
    # Draw the text on the image
    #print('============================================================================')
    #draw.text(position, text, color, font=font)
    spacing=5
    x, y = position
    for s in text:
        # Draw the current character
        draw.text((x, y), s, font=font, fill='black')

        # Calculate bounding box for the current character
        bb = draw.textbbox((x, y), s, font=font)

        # Draw a rectangle around the current character
        #draw.rectangle(bb, outline=color)
        #print(bb)

        # Update x-coordinate for the next character with spacing
        x = bb[2] - spacing
    # Get the bounding box coordinates for the drawn text
    bbox = (position[0], position[1], x, bb[3])

    
    # Draw a rectangle around the text
    #draw.rectangle(bbox, outline=color)
    
    
    return bbox
    
def draw_polygon_after_transformation(draw, bbox, transformation_matrix):
    # Convert the bounding box to four points
    points = np.array(convert_bbox_to_four_points(bbox), dtype=np.float32)
    
    # Apply the perspective transformation to the points
    transformed_points = cv2.perspectiveTransform(points.reshape(-1, 1, 2), transformation_matrix)

    # Convert transformed points back to integer coordinates
    transformed_points_int = transformed_points.reshape(-1, 2).astype(int).tolist()

    # Flatten the list of points
    flattened_points = [coord for sublist in transformed_points_int for coord in sublist]

    # Draw a polygon around the transformed bounding box
    draw.polygon(flattened_points, outline='red')


def convert_bbox_to_four_points(bbox):
    x1, y1, x2, y2 = bbox
    return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

def convert_bbox_to_string(bbox):
    x1, y1, x2, y2 = bbox
    return f"{x1},{y1},{x2},{y1},{x2},{y2},{x1},{y2}"
    

def adjust_bbox_after_transformation(bbox, transformation_matrix=None):
    points = np.array(convert_bbox_to_four_points(bbox), dtype=np.float32)
    x1, y1, x2, y2 = bbox
    
    # Convert the bounding box corners to homogeneous coordinates
    corners = np.array([[x1, y1, 1], [x2, y1, 1], [x2, y2, 1], [x1, y2, 1]])
    
    # Apply the perspective transformation to the corners
    transformed_corners = np.dot(transformation_matrix, corners.T).T
    
    # Normalize the transformed coordinates (divide by the homogeneous coordinate)
    normalized_corners = transformed_corners[:, :2] / transformed_corners[:, 2:]

    # Calculate the minimum and maximum coordinates of the transformed points
    min_x, min_y = np.min(normalized_corners, axis=0)
    max_x, max_y = np.max(normalized_corners, axis=0)
    
    # Create the adjusted bounding box
    adjusted_bbox = (int(min_x), int(min_y), int(max_x), int(max_y))
    
    return adjusted_bbox
    

def save_box_information(image_id, filename, boxes, output_folder,transformation_matrix=None):
    # Create the 'boxes_trans' directory if it doesn't exist
   

    boxes_trans_folder = os.path.join(output_folder, 'boxes_trans')
    if not os.path.exists(boxes_trans_folder):
        os.makedirs(boxes_trans_folder)

    tsv_filename = os.path.join(boxes_trans_folder, f"{os.path.splitext(os.path.basename(filename))[0]}.tsv")

    with open(tsv_filename, 'w') as tsv_file:
        
        i=0
        for box in boxes:
            bbox = box['bbox']
            if transformation_matrix is not None:
                adjusted_bbox = adjust_bbox_after_transformation(bbox, transformation_matrix)
                box_coords = convert_bbox_to_string(adjusted_bbox)
            else:
                box_coords = convert_bbox_to_string(bbox)
            tsv_file.write(f"{i},{box_coords},{box['text']},{box['data_type']}\n")
            i += 1
            
def generate_passports_and_save_images(num_passports, output_folder,do_perspective_transform):
    # Load the fake passport data
    with open("fake_passports.json", "r") as json_file:
        passports = json.load(json_file)

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for j in range(num_passports):
        passport = passports[j]

        # Load the base image
        base_image = Image.open('passport_template.png')
        draw = ImageDraw.Draw(base_image)

        # Use an OCR-B font
        ocrb_font_path = 'OCRB.otf'
        font = ImageFont.truetype(ocrb_font_path, 27)

        type_bbox = draw_text_with_box(draw, (418, 102),passport['Type'], font)

        code_bbox = draw_text_with_box(draw, (560, 102),passport['Code'], font)
        
        passport_number_text = str(passport['PassportNumber'])
        passport_number_bbox = draw_text_with_box(draw, (800, 102), passport_number_text, font)
 
        surname_text = passport['Surname']
        surname_bbox = draw_text_with_box(draw, (365, 155), surname_text, font)

        given_name_text = ' '.join(passport['GivenName'])
        given_name_bbox = draw_text_with_box(draw, (365, 215), given_name_text, font)
        
        nationality_bbox = draw_text_with_box(draw, (365, 270), passport['Nationality'], font)
        
        dob_text = passport['DateOfBirth']
        dob_bbox = draw_text_with_box(draw, (365, 325), dob_text, font)

        #PlaceOfBirth_bbox = draw_text_with_box(draw, (365, 380),passport['PlaceOfBirth'], font)
        #print(f"PlaceOfBirth Bounding Box: {PlaceOfBirth_bbox}")

        place_of_birth_parts = passport['PlaceOfBirth'].split(', ')
        place_of_birth_city_text = place_of_birth_parts[0]
        place_of_birth_country_text = place_of_birth_parts[1]

        # Draw bounding boxes for city and country
        place_of_birth_city_bbox = draw_text_with_box(draw, (365, 380), place_of_birth_city_text, font)
        comma_box = draw_text_with_box(draw, (place_of_birth_city_bbox[2], 380),', ', font)
        place_of_birth_country_bbox = draw_text_with_box(draw, (comma_box[2], 380), place_of_birth_country_text, font)

        
        sex_bbox = draw_text_with_box(draw, (900, 380),passport['Sex'], font)
        #print(f"Sex Bounding Box: {sex_bbox}")

        issue_date_text = passport['DateOfIssue']
        issue_date_bbox = draw_text_with_box(draw, (365, 435), issue_date_text, font)
        #print(f"Date of Issue Bounding Box: {issue_date_bbox}")

        Authority_bbox = draw_text_with_box(draw, (820, 435),passport['Authority'], font)
        #print(f"Authority Bounding Box: {Authority_bbox}")
        
        expire_date_bbox = draw_text_with_box(draw, (365, 490), passport['DateOfExpiration'], font)
        #print(f"Date of Expiry Bounding Box: { expire_date_bbox}")
        
        Endorsements_bbox = draw_text_with_box(draw, (365, 545),passport['Endorsements'], font)
        #print(f"Endorsements Bounding Box: {Endorsements_bbox}")

        # Save the image with a unique filename in the specified output folder
        images_folder = os.path.join(output_folder, 'images')
        if not os.path.exists(images_folder):
            os.makedirs(images_folder)
        filename = os.path.join(images_folder, f"image_{j}.png")
        base_image.save(filename)
        
        
        boxes = [
            {'bbox': type_bbox, 'text': passport['Type'], 'data_type': 'type'},
            {'bbox': code_bbox, 'text': passport['Code'], 'data_type': 'code'},
            {'bbox': passport_number_bbox, 'text': passport['PassportNumber'], 'data_type': 'passport_number'},
            {'bbox': surname_bbox, 'text': surname_text, 'data_type': 'Surname'},
            {'bbox': given_name_bbox, 'text': given_name_text, 'data_type': 'GivenName'},
            {'bbox': nationality_bbox, 'text': passport['Nationality'], 'data_type': 'nationality'},
            {'bbox': dob_bbox, 'text': passport['DateOfBirth'], 'data_type': 'date_of_birth'},
            {'bbox': place_of_birth_city_bbox, 'text': place_of_birth_city_text, 'data_type': 'place_of_birth_city'},
            {'bbox': place_of_birth_country_bbox, 'text': place_of_birth_country_text, 'data_type': 'place_of_birth_country'},
            {'bbox': sex_bbox, 'text': passport['Sex'], 'data_type': 'sex'},
            {'bbox': issue_date_bbox, 'text': passport['DateOfIssue'], 'data_type': 'date_of_issue'},
            {'bbox': Authority_bbox, 'text': passport['Authority'], 'data_type': 'authority'},
            {'bbox': expire_date_bbox, 'text': passport['DateOfExpiration'], 'data_type': 'date_of_expiration'},
            {'bbox': Endorsements_bbox, 'text': passport['Endorsements'], 'data_type': 'endorsements'},
        ]
        
        image_file_name=f"image_{j}.png"
        save_box_information(j, image_file_name, boxes,output_folder)
        if do_perspective_transform:
            rows, cols = base_image.size

            base_image_np = np.array(base_image)

            # Calculate the coordinates of the four corners
            src_points = np.float32([[0, 0], [cols-1, 0], [0, rows-1], [cols-1, rows-1]])
            start_index_x = 100
            start_index_y = 200
            dst_points = np.float32([[100,200], [cols-100,200], [0,rows-1], [cols-1,rows-1]])

            # Calculate the perspective transformation matrix
            perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)

            # Apply the perspective transformation
            perspective_image = cv2.warpPerspective(base_image_np, perspective_matrix, (rows, cols))

            # Convert the result back to a PIL Image if needed
            perspective_image_pil = Image.fromarray(perspective_image)
            filename2 = os.path.join(images_folder, f"perspective_image_{j}.png")
            
            draw_perspective = ImageDraw.Draw(perspective_image_pil)
            
            for box in boxes:
                bbox = box['bbox']
                print("hhhh")
                print(bbox)
                
                adjusted_bbox = adjust_bbox_after_transformation(bbox, perspective_matrix)
                
                print(adjusted_bbox)
                draw_polygon_after_transformation(draw_perspective, adjusted_bbox, perspective_matrix)

                



            # Save the perspective-transformed image
            perspective_image_pil.save(filename2)
            save_box_information(j, filename2, boxes, output_folder, perspective_matrix)

             
           
            
        



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate fake passports and save images with bounding boxes.")
    parser.add_argument("-n", "--number_of_passports", type=int, required=True, help="Number of fake passports to generate images for.")
    parser.add_argument("-o", "--output_folder", required=True, help="Output folder for saving images.")
    parser.add_argument("-t", "--yes", action='store_true', help="Do Perspective transformations")

    args = parser.parse_args()

    generate_passports_and_save_images(args.number_of_passports, args.output_folder, args.yes)
