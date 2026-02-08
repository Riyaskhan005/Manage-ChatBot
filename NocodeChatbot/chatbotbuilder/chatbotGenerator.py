import os
import shutil
from flask import current_app
from NocodeChatbot.models.projects import Projects  # adjust import if needed


class ChatbotGenerator:
    def __init__(self, customer_id, project_id, builder_id, model_id):
        self.customer_id = customer_id
        self.project_id = project_id
        self.builder_id = builder_id
        self.model_id = model_id

    def generate_chatbot(self):
        # 1️⃣ Get project name
        project = Projects.query.filter_by(id=self.project_id).first()
        project_name = project.project_name if project else f"project_{self.project_id}"
        project_name = project_name.replace(" ", "_")

        # 2️⃣ static/wrk path
        base_path = os.path.join(
            current_app.root_path,
            "static",
            "wrk"
        )

        # 3️⃣ customerid_projectid_builderid
        main_folder = f"{self.customer_id}_{self.project_id}_{self.builder_id}"
        main_path = os.path.join(base_path, main_folder)
        os.makedirs(main_path, exist_ok=True)

        # 4️⃣ project folder
        project_path = os.path.join(main_path, project_name)
        os.makedirs(project_path, exist_ok=True)

        # 5️⃣ COPY model_app (not move, not delete)
        source_model_app = os.path.join(
            current_app.root_path,
            "model_app"
        )

        destination_model_app = os.path.join(
            project_path,
            "model_app"
        )

        # copy only if not already copied
        if not os.path.exists(destination_model_app):
            shutil.copytree(source_model_app, destination_model_app)
