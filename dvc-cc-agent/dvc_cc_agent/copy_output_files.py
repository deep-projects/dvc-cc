import threading
import time
import shutil
import os
import uuid

class Thread(object):

    def __init__(self, list_of_files_or_folders, destination_path, interval=60):
        """
        :param interval: Interval check in seconds
        :param list_of_files_or_folders: A list of files that should copied to the destination
        :param destination_path: The destination path to copy the files
        """
        self.interval = int(interval)
        self.files = list_of_files_or_folders
        self.destination_path = destination_path

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        thread_uuid = str(uuid.uuid4()).split('-')[0]
        while True:
            for f in self.files:
                if os.path.exists(f):
                    if os.path.isdir(f):
                        if os.path.exists(self.destination_path+f+'_'+thread_uuid):
                            shutil.rmtree(self.destination_path+f+'_'+thread_uuid)
                        shutil.copytree(f, self.destination_path+f+'_'+thread_uuid)
                    else:
                        shutil.copyfile(f, self.destination_path+f+'_'+thread_uuid)
            time.sleep(self.interval)