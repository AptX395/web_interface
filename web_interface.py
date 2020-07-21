# coding: utf-8

import json, time, threading
from urllib.request import Request, urlopen
from pynvml import nvmlInit, nvmlDeviceGetCount, nvmlDeviceGetMemoryInfo, nvmlDeviceGetHandleByIndex, nvmlDeviceGetName, nvmlShutdown, nvmlDeviceGetUtilizationRates

class WebInterface():
    """ The interface of the website.

    Attributes:
        None

    Example Usage:
        web_interface = WebInterface(training_name = "test")
        used_gpu_indexes = list()
        used_gpu_indexes.append(0)
        is_successful = web_interface.register(used_gpu_indexes)

        if is_successful is False:
            print("Failed to register.")
        
        data = {"loss": 0.01, "accuracy": 0.99, "val_loss": 0.01, "val_accuracy": 0.99}
        is_successful = web_interface.publish(data)

        if is_successful is False:
            print("Failed to publish.")

        is_successful = web_interface.logout()

        if is_successful is False:
            print("Failed to logout.")

    """
    def __init__(self, training_name, host = "210.38.224.107"):
        self._training_name = training_name
        self._root = f"http://{host}/interface"
        self._is_running = None

    def register(self, used_gpu_indexes):
        """ Register the information of the training program. And start a new thread to get the status of GPUs in loop.

        Args:
            used_gpu_indexes: (list)

        Returns:
            is_successful: (bool)

        """
        is_successful = False
        url = f"{self._root}/register/{self._training_name}"
        is_successful = self._send_data(url)

        if is_successful:
            self._is_running = True
            thread = threading.Thread(target = self._publish_gpu_status, name = "publist_gpu_status", args = [used_gpu_indexes])
            thread.start()

        return is_successful

    def publish(self, data):
        """ Publish the training data to the backend of the website.

        Args:
            data: (dictionary) For example, `{"loss": 0.01, "accuracy": 0.99, "val_loss": 0.01, "val_accuracy": 0.99}`.

        Returns:
            is_successful: (bool)

        """
        is_successful = False
        url = f"{self._root}/publish_training_data/{self._training_name}"
        is_successful = self._send_data(url, data)
        return is_successful

    def logout(self):
        """ Logout the training program.

        Args:
            None

        Returns:
            is_successful: (bool)

        """
        is_successful = False
        url = f"{self._root}/logout/{self._training_name}"
        is_successful = self._send_data(url)

        if is_successful:
            self._is_running = False

        return is_successful

    # ----------------------------------------------------------------

    def _send_data(self, url, data = None):
        """ Send data to the backend of the website through a network request.

        Args:
            url: (string)
            data: (dictionary)

        Returns:
            is_successful: (bool)

        """
        is_successful = False

        if data is None:
            request = Request(url, method = "GET")
        else:
            json_data = json.dumps(data)
            byte_data = bytes(json_data, encoding = "utf-8")
            request = Request(url, data = byte_data, headers = {"Content-Type": "application/json"}, method = "POST")

        try:
            response = urlopen(request)
        except Exception as e:
            is_successful = False
            print(f"Failed to send data. [Exception]: `{e}`.")
        else:
            if response.status == 200:
                is_successful = True

        return is_successful

    def _get_gpu_status(self, used_gpu_indexes):
        """ Get the status of the currently used GPUs.

        Args:
            used_gpu_indexes: (list)

        Returns:
            gpu_status: (list)

        """        
        gpu_status = list()
        nvmlInit()
        
        for index in used_gpu_indexes:
            handle = nvmlDeviceGetHandleByIndex(index)
            utilization_rates = nvmlDeviceGetUtilizationRates(handle)
            mem_info = nvmlDeviceGetMemoryInfo(handle)
            mem_usage = mem_info.used / mem_info.total
            status = {"index": index, "gpu_util": utilization_rates.gpu, "mem_usage": mem_usage}
            gpu_status.append(status)

        nvmlShutdown()
        return gpu_status

    def _publish_gpu_status(self, used_gpu_indexes):
        """ Publish the status of the currently used GPUs to the backend of the website.

        Args:
            used_gpu_indexes: (list)

        Returns:
            None

        """
        while self._is_running:
            gpu_status = self._get_gpu_status(used_gpu_indexes)
            url = f"{self._root}/publish_gpu_status/{self._training_name}"
            self._send_data(url, gpu_status)
            time.sleep(10)
