FROM public.ecr.aws/lambda/python:3.7

RUN pip3 install --upgrade pip
RUN pip3 install numpy
RUN pip3 install scipy
RUN pip3 install sklearn

COPY ["lambda_function.py", "dict_vectorizer.bin", "logistic_regression.bin",  "./"]

CMD ["lambda_function.lambda_handler"]

