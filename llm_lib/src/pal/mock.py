def mock_streaming_query():
    """
    This function is a mock of the response_generator_helper function in chat_utils.py
    It will return a mock stream of responses from the vdb.
    """
    for i in range(10):
        yield f"Mock response {i} \n"
