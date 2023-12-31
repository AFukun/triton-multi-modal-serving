import json
import torch
import triton_python_backend_utils as pb_utils

from models import blip_nlvr

# ENABLE_MODAL_LEVEL_BATCH = True


class TritonPythonModel:
    """Your Python model must use the same class name. Every Python model
    that is created must have "TritonPythonModel" as the class name.
    """

    def initialize(self, args):
        """`initialize` is called only once when the model is being loaded.
        Implementing `initialize` function is optional. This function allows
        the model to intialize any state associated with this model.

        Parameters
        ----------
        args : dict
          Both keys and values are strings. The dictionary keys and values are:
          * model_config: A JSON string containing the model configuration
          * model_instance_kind: A string containing model instance kind
          * model_instance_device_id: A string containing model instance device ID
          * model_repository: Model repository path
          * model_version: Model version
          * model_name: Model name
        """

        # You must parse model_config. JSON string is not parsed here
        self.model_config = json.loads(args["model_config"])

        # Instantiate the PyTorch model
        model_url = "/pretrained/model_base_nlvr.pth"
        self.model = blip_nlvr(pretrained=model_url)
        self.model.eval()
        self.model = self.model.to(
            "cuda" if torch.cuda.is_available() else "cpu")

    def execute(self, requests):
        """`execute` must be implemented in every Python model. `execute`
        function receives a list of pb_utils.InferenceRequest as the only
        argument. This function is called when an inference is requested
        for this model. Depending on the batching configuration (e.g. Dynamic
        Batching) used, `requests` may contain multiple requests. Every
        Python model, must create one pb_utils.InferenceResponse for every
        pb_utils.InferenceRequest in `requests`. If there is an error, you can
        set the error argument when creating a pb_utils.InferenceResponse.

        Parameters
        ----------
        requests : list
          A list of pb_utils.InferenceRequest

        Returns
        -----.--
        list
          A list of pb_utils.InferenceResponse. The length of this list must
          be the same as `requests`
        """

        output_dtype = pb_utils.triton_string_to_numpy(
            pb_utils.get_output_config_by_name(self.model_config,
                                               "ANSWER")["data_type"])

        responses = []

        # Every Python backend must iterate over everyone of the requests
        # and create a pb_utils.InferenceResponse for each of them.
        for request in requests:
            # Get INPUT0
            image0s = pb_utils.get_input_tensor_by_name(request, "IMAGE0")
            # Get INPUT1
            image1s = pb_utils.get_input_tensor_by_name(request, "IMAGE1")
            # Get INPUT2
            texts = pb_utils.get_input_tensor_by_name(request, "TEXT")

            with torch.no_grad():
                answer = self.model(
                    image0s.as_numpy(),
                    image1s.as_numpy(),
                    texts.as_numpy(),
                    # enable_modal_level_batch=ENABLE_MODAL_LEVEL_BATCH,
                )

            answer_tensor = pb_utils.Tensor("ANSWER",
                                            answer.astype(output_dtype))

            inference_response = pb_utils.InferenceResponse(
                output_tensors=[answer_tensor])
            responses.append(inference_response)

        # You should return a list of pb_utils.InferenceResponse. Length
        # of this list must match the length of `requests` list.
        return responses

    def finalize(self):
        """`finalize` is called only once when the model is being unloaded.
        Implementing `finalize` function is optional. This function allows
        """
        print("Cleaning up...")
