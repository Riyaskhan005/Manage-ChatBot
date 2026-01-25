import os
import datetime
import traceback

class LogWriter:
    def __init__(self):
        self.base_log_dir = "ChatBotLogs"

    def log_exception(self, module_name, function_name, e):
        """Logs exception details with module, function, file name, line number, and error message."""
        try:
            now = datetime.datetime.now()
            year = now.strftime("%Y")
            month = now.strftime("%m")
            day = now.strftime("%d")

            # Log directory: NocodeChatBotLogs/YYYY/MM/DD/
            log_dir = os.path.join(self.base_log_dir, year, month, day)
            os.makedirs(log_dir, exist_ok=True)

            # Log file
            log_file = os.path.join(log_dir, "exception.txt")

            # Extract exception info
            exc_type, exc_obj, exc_tb = traceback.sys.exc_info()
            file_name = exc_tb.tb_frame.f_code.co_filename
            line_no = exc_tb.tb_lineno
            error_message = str(e)

            # Build log entry with clear separators and line breaks
            log_entry = (
                f"{'-'*80}\n"
                f"Timestamp : {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Module    : {module_name}\n"
                f"Function  : {function_name}\n"
                f"File      : {file_name}\n"
                f"Line      : {line_no}\n"
                f"Error     : {error_message}\n"
            )

            # Include SQL details if present
            if isinstance(e.args, tuple) and len(e.args) > 1:
                log_entry += f"SQL       : {str(e.args[0])}\n"
                log_entry += f"Params    : {str(e.args[1])}\n"

            log_entry += f"{'-'*80}\n\n"

            # Append to log file
            with open(log_file, "a") as f:
                f.write(log_entry)

        except Exception as log_error:
            print(f"Failed to write log: {log_error}")
