import os
from NocodeChatbot.models.models import ManageModels
from NocodeChatbot.models.chatbot import ManageChatbot
from NocodeChatbot.utils.logwritter import LogWriter
log_writer_ = LogWriter()


class FileManager:
    """
    Handles post-copy file operations for chatbot builds
    Must be STATELESS (safe for multiple requests)
    """

    def building_chatbot(self, customer_id, project_id, builder_id, model_id, dataextractor_id, chatbot_id, app_folder_path):
        try:
            """
            Called once AFTER model_app is copied successfully
            app_folder_path already points to: .../project_name/ncapp
            """

            model_data = ManageModels.query.filter_by(id=model_id,status="Active").first()

            if not model_data:
                raise Exception("Model not found or inactive")

            # Get chatbot details
            chatbot_data = ManageChatbot.query.filter_by(id=chatbot_id,status="Active").first()

            if not chatbot_data:
                raise Exception("Chatbot not found or inactive")

            api_key = model_data.model_key
            model_name = model_data.model_name
            model_type = model_data.model_config
            language = chatbot_data.chatbot_language
            tone = chatbot_data.chatbot_tone
            instructions = chatbot_data.chatbot_instructions or "Be helpful, polite, and clear"
            chatbot_color_code = chatbot_data.chatbot_color_code or "#4b38b3"

            chatbot_logic_path = os.path.join(app_folder_path,"ncapp","chatbot","chatbot_logic.py")
            chatbot_routes_path = os.path.join(app_folder_path,"ncapp","chatbot","routes.py")
            chatbot_css_path = os.path.join(app_folder_path,"ncapp","static","css","chatbot.css")
            chatbot_html_path = os.path.join(app_folder_path,"ncapp","templates","chat.html")

            if not os.path.exists(chatbot_logic_path):
                raise Exception("chatbot_logic.py not found in cloned project")
            
            if not os.path.exists(chatbot_routes_path):
                raise Exception("routes.py not found in cloned project")
            
            if not os.path.exists(chatbot_css_path):
                raise Exception("chatbot.css not found in cloned project")
            
            if not os.path.exists(chatbot_html_path):
                raise Exception("chat.html not found in cloned project")

            with open(chatbot_logic_path, "r", encoding="utf-8") as f:
                content = f.read()

            content = content.replace("REPLACE_YOUR_API_KEY_HERE", api_key)
            content = content.replace("REPLACE_MODEL_NAME", model_name)
            content = content.replace("REPLACE_LANGUAGE", language)
            content = content.replace("REPLACE_TONE", tone)
            content = content.replace("Be helpful, polite, and clear", instructions)

            with open(chatbot_css_path, "r", encoding="utf-8") as f:
                css_content = f.read()

            css_content = css_content.replace("REPLACE_CHATBOT_COLOR", chatbot_color_code)

            with open(chatbot_css_path, "w", encoding="utf-8") as f:
                f.write(css_content)

            with open(chatbot_html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            html_content = html_content.replace("REPLACE_CHATBOT_NAME", chatbot_data.chatbot_name)
            html_content = html_content.replace("REPLACE_CHATBOT_COLOR", chatbot_color_code)

            with open(chatbot_html_path, "w", encoding="utf-8") as f:
                f.write(html_content)


            with open(chatbot_logic_path, "w", encoding="utf-8") as f:
                f.write(content)

            api_call_code, api_import_package = self.generate_api_call_code(model_type)

            with open(chatbot_routes_path, "r", encoding="utf-8") as f:
                main_content = f.read()

            main_content = main_content.replace("# REPLACE IMPORT", api_import_package)
            main_content = main_content.replace("# REPLACE API CALL", api_call_code)
            main_content = main_content.replace("REPLACE_CHATBOT_NAME", chatbot_data.chatbot_name)
            main_content = main_content.replace("REPLACE_CHATBOT_DOMAIN", chatbot_data.chatbot_domain)

            with open(chatbot_routes_path, "w", encoding="utf-8") as f:
                f.write(main_content)

            extractor_folder = os.path.join(os.getcwd(),"NocodeChatbot","static","dataextractor",f"{customer_id}_{dataextractor_id}")

            if os.path.exists(extractor_folder):
                    combined_text = ""
                    for file_name in os.listdir(extractor_folder):
                        if file_name.endswith(".txt"):
                            file_path = os.path.join(extractor_folder, file_name)
                            with open(file_path, "r", encoding="utf-8") as f:
                                combined_text += f.read() + "\n\n"
                    if combined_text.strip():
                        rag_folder_path = os.path.join(app_folder_path,"ncapp","chatbot", "rag_data")
                        if not os.path.exists(rag_folder_path):
                            os.makedirs(rag_folder_path)
                        rag_file_path = os.path.join(rag_folder_path, "rag_data.txt")
                        with open(rag_file_path, "w", encoding="utf-8") as f:
                            f.write(combined_text)
                        print("RAG data copied successfully")
            else:
                print("No data extractor folder found, skipping RAG setup")

            print("Chatbot configured successfully")

        
        except Exception as e:
            log_writer_.log_exception("fileManager", "building_chatbot", e)

    def generate_api_call_code(self, model_type):

        if model_type == "OpenAI":

            api_import_package = """from openai import OpenAI"""

            api_call_code = """
        client = OpenAI(api_key=API_KEY)

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": final_prompt}
            ]
        )

        if hasattr(response, "choices") and response.choices:
            bot_reply = response.choices[0].message.content
        elif hasattr(response, "output_text") and response.output_text:
            bot_reply = response.output_text
        elif hasattr(response, "text") and response.text:
            bot_reply = response.text
        else:
            bot_reply = "Sorry, I could not generate a reply."
    """

        elif model_type == "Gemini":

            api_import_package = """import google.generativeai as genai"""

            api_call_code = """
        genai.configure(api_key=API_KEY)

        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(final_prompt)

        if hasattr(response, "text") and response.text:
            bot_reply = response.text
        elif hasattr(response, "output_text") and response.output_text:
            bot_reply = response.output_text
        else:
            bot_reply = "Sorry, I could not generate a reply."
    """

        else:

            api_import_package = "# Unsupported model"
            api_call_code = "bot_reply = 'Hi there! This is a Dummy Response from the Chatbot.'"

        return api_call_code, api_import_package

