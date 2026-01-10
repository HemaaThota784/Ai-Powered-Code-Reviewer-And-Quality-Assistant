def generator_example(n):
    """
    Generates an example for demonstration purposes.

    No parameters are accepted by this function.

    :returns: None
    :rtype: None
    """
    for i in range(n):
        yield i


def raises_example(x):
    """
    Raises an example exception to demonstrate error handling.

    :raises ValueError: Raised when an example exception occurs to illustrate error handling. 
    :returns: None 
    :rtype: None
    """
    if x < 0:
        raise ValueError("negative")
    return x * 2
