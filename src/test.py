

from geminiInterface import 


API = "AIzaSyDvDFuAeeixpHlwyoKX5vO8g6C11xwPAwg"
    
    
    


# #from google import genai
# import google.generativeai as genai
# from google.generativeai import GenerativeModel

# #client = genai.Client(api_key=API)

# genai.configure(api_key=API)

# # response = client.models.generate_content(
# #     model="gemini-2.0-flash", contents="Explain how AI works in a few words"
# # )
# # print(response.text)

# # Crea il prompt
# prompt = "Genera un'immagine di un gatto che gioca con un gomitolo di lana su un prato verde."
# model = GenerativeModel("gemini-2.0-flash")
# # Genera l'immagine
# response = model.generate_content(prompt)

# # Accedi all'immagine generata
# # if response.blob:
# #     with open("generated_image.png", "wb") as f:
# #         f.write(response.blob)
# #     print("Immagine generata e salvata come generated_image.png")
# # else:
# #     print("Impossibile generare l'immagine.")

# if response.parts:
#     print(response)
#     image_part = response.parts[0]  # Potrebbe esserci una lista di parti
#     if image_part.mime_type.startswith("image/"):
#         image_bytes = image_part.blob
#         with open("generated_image.png", "wb") as f:
#             f.write(image_bytes)
#         print("Immagine generata e salvata come generated_image.png")
#     else:
#         print("La risposta non contiene un'immagine.")
# else:
#     print("Impossibile generare l'immagine o la risposta è vuota.")
    