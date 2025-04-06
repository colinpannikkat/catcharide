from groq import Groq
import os
import base64
from dotenv import load_dotenv
import json
from thefuzz import fuzz
from deepface import DeepFace

load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

class IDVerification:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def check_base64_size(self, b64_string):
        """
        Checks if the size of a given Base64-encoded string exceeds the 4MB limit.

        Args:
            b64_string (str): The Base64-encoded string to check.

        Raises:
            ValueError: If the decoded size of the Base64-encoded data exceeds 4MB.

        Notes:
            The size is calculated approximately by decoding the Base64 string length,
            accounting for padding characters ('=').
        """
        max_size_bytes = 4 * 1024 * 1024  # 4MB in bytes
        size_in_bytes = (len(b64_string.rstrip('=')) * 3) // 4  # approximate decoded size, accounting for padding

        if size_in_bytes > max_size_bytes:
            raise ValueError("Base64-encoded data exceeds the 4MB limit.")

    # Function to encode the image
    def encode_image(self, image_path: str) -> bytes:
        """
        Encodes an image file into a Base64-encoded string.

        Args:
            image_path (str): The file path to the image to be encoded. 
                              The image file size must not exceed 4MB.

        Returns:
            bytes: The Base64-encoded representation of the image as a UTF-8 string.

        Raises:
            ValueError: If the Base64-encoded string exceeds the allowed size limit (4MB).
        """
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            self.check_base64_size(encoded)
            return encoded


    def parse_id(self, img_ref: str) -> dict | None:
        """
        Parses a student ID image to extract relevant information.

        This method takes an image reference, encodes it, and sends it to a Groq 
        to extract the student's name and university details. The AI model
        responds with a JSON object containing the extracted fields.

        Args:
            img_ref (str): A reference to the image (file path or URL) to be parsed.

        Returns:
            dict or None: A dictionary containing the extracted fields:
                - 'id' (str or None): The ID from the image, or None if not retrievable.
                - 'school' (str or None): The university or school name, or None if not retrievable.
                - 'last_name' (str or None): The student's last name, or None if not retrievable.
                - 'first_name' (str or None): The student's first name, or None if not retrievable.
            Returns None if the response cannot be parsed or an error occurs.
        """
        encoded_img = self.encode_image(img_ref)
        completion = self.client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f'''
                                    Parse the following image and retrieve a students name and university.
                                    Respond in JSON format with the fields, 'id' if ID in image,
                                    'school' from ID, and 'last_name' and 'first_name' from ID. If information 
                                    is not retrievable set json fields to null.
                                    '''
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_img}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.2,
            max_completion_tokens=256,
            top_p=1,
            stream=False,
            response_format={"type": "json_object"},
            stop=None,
        )

        try:
            response = json.loads(completion.choices[0].message.content)
        except Exception as e:
            print(e)
            raise(e)

        return response
    
    def verify_id(self, img_ref: str, first_name: str, last_name: str) -> dict | None:
        """
        Verifies the identity of a person by comparing their provided first and last names
        with the names extracted from an identification document image.
        Args:
            img_ref (str): The file path or reference to the image of the identification document.
            first_name (str): The first name of the person to verify.
            last_name (str): The last name of the person to verify.
        Returns:
            dict/None: A dictionary containing the parsed ID information with an added 
            'verified' key indicating whether the verification was successful. Returns None 
            if the ID could not be parsed, either due to model error or no ID in image.
        """
        id = self.parse_id(img_ref)
        
        # Checks if parsing failed or ID not in image
        if id is None or id['id'] is None:
            return None

        # Calculate Levenhstein distance between given names and names from ID
        first_fuzz = fuzz.partial_ratio(first_name, id['first_name'])
        second_fuzz = fuzz.partial_ratio(last_name, id['last_name'])
        total_fuzz = (first_fuzz + second_fuzz) / 200

        print(total_fuzz)

        # Add verified category
        id['verified'] = True if total_fuzz > 0.90 else False
        return id
    
    def verify_face(self, img_ref: str, face_ref: str) -> dict:
        """
        Verifies if two images represent the same face using DeepFace.

        Args:
            img_ref (str): The file path to the reference image.
            face_ref (str): The file path to the face image to be verified.

        Returns:
            dict: A dictionary containing the verification result, including 
                  similarity metrics and a boolean indicating if the faces match.
        """
        result = DeepFace.verify(
            img1_path = img_ref,
            img2_path = face_ref,
        )
        return result

    def verify(self, img_ref, face_ref, first_name, last_name) -> dict | None:
        """
        Verifies the identity and face of a user based on the provided references.

        Args:
            img_ref (Any): The reference image used for verification.
            face_ref (Any): The reference face data used for verification.
            first_name (str): The first name of the user.
            last_name (str): The last name of the user.

        Returns:
            dict | None: A dictionary containing the verification results if successful,
                         or None if verification fails.
        """
        id_res = self.verify_id(img_ref, first_name, last_name)
        if not id_res:
            return None
        face_res = self.verify_face(img_ref, face_ref)
        res = {
            'id_res' : id_res,
            'face_res' : face_res
        }
        return res