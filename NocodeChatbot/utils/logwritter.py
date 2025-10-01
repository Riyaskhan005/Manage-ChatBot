import os
import datetime
import traceback

class LogWriter:
    def __init__(self):
        # Base directory for logs
        self.base_log_dir = "NocodeChatBotLogs"

    def log_exception(self, module_name, function_name, e):
        """Logs exception details with module, function, file name, line number, and error message."""
        try:
            # Get current date
            now = datetime.datetime.now()
            year = now.strftime("%Y")
            month = now.strftime("%m")
            day = now.strftime("%d")

            # Define log directory structure: ControlPanelLogs/YYYY/MM/DD/
            log_dir = os.path.join(self.base_log_dir, year, month, day)
            os.makedirs(log_dir, exist_ok=True)

            # Define log file (exception.txt inside the day folder)
            log_file = os.path.join(log_dir, "exception.txt")

            # Extract exception details
            exc_type, exc_obj, exc_tb = traceback.sys.exc_info()
            file_name = exc_tb.tb_frame.f_code.co_filename  # Get file name
            line_no = exc_tb.tb_lineno  # Get line number
            error_message = str(e)  # Get error message

            # Prepare log entry with dashed line separator
            log_entry = (
                f"{'-' * 80}\n"  # 80 dashes for separator
                f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] ERROR in {module_name}.{function_name} "
                f"({file_name}, Line {line_no}): {error_message}\n"
            )

            # Check if exception contains SQL-related info
            if isinstance(e.args, tuple) and len(e.args) > 1:
                log_entry += f"[SQL: {str(e.args[0])}]\n"
                log_entry += f"[parameters: {str(e.args[1])}]\n"

            log_entry += f"{'-' * 80}\n"  # 80 dashes for separator

            # Write to log file
            with open(log_file, "a") as f:
                f.write(log_entry)

        except Exception as log_error:
            print(f"Failed to write log: {log_error}")  # Print error if logging fails
