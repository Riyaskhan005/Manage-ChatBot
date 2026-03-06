import os
import shutil
from flask import current_app
from NocodeChatbot.models.projects import Projects
from NocodeChatbot.chatbotbuilder.fileManager import FileManager
file_manager_ = FileManager()
from NocodeChatbot.utils.logwritter import LogWriter
log_writer_ = LogWriter()

class ChatbotGenerator:
    def __init__(self, customer_id, project_id, builder_id, model_id,dataextractor_id,chatbot_id):
        self.customer_id = customer_id
        self.project_id = project_id
        self.builder_id = builder_id
        self.model_id = model_id
        self.dataextractor_id = dataextractor_id
        self.chatbot_id = chatbot_id

    def generate_chatbot(self):
        try:
            project = Projects.query.filter_by(id=self.project_id).first()
            project_name = project.project_name if project else f"project_{self.project_id}"
            project_name = project_name.replace(" ", "_")

            base_path = os.path.join(current_app.root_path, "static", "wrk")

            main_folder = f"{self.customer_id}_{self.project_id}_{self.builder_id}"
            main_path = os.path.join(base_path, main_folder)
            if os.path.isdir(main_path):
                shutil.rmtree(main_path)
            os.makedirs(main_path, exist_ok=True)

            project_path = os.path.join(main_path, project_name)
            os.makedirs(project_path, exist_ok=True)

            source_model_app = os.path.join(current_app.root_path, "model_app")


            shutil.copytree(source_model_app, project_path, dirs_exist_ok=True)
            file_manager_.building_chatbot(self.customer_id,self.project_id,self.builder_id,self.model_id,self.dataextractor_id,self.chatbot_id,project_path)

        except Exception as e:
            log_writer_.log_exception("chatbotGenerator", "generate_chatbot", e)
