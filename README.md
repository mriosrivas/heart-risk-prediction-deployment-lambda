# Deploying Machine Learning models in Lambda AWS

In this short tutorial we will deploy a Machine Learning model into Lambda AWS. Our assumtion is that you already have a model trained and now you want to serve it.

## AWS lambda_handler

Lambda AWS uses a wraper function called `lambda_handler` to perform calculations,  the complete implementation is stored in `lambda_function.py` but the important part here is how we pass data.

```python
 def lambda_handler(event, context):
    user = event['user']
    #X = preprocessor.from_url(url)
    preds = predict(user)
    return preds
```

Wich in this case `user` is the data that we want to use to predict our heart risk. Note that our prediction must be returned in a JSON format.

## Docker container

We will create a Docker container with all dependencies needed for us to use AWS Lambda.

```dockerfile
FROM public.ecr.aws/lambda/python:3.7

RUN pip3 install --upgrade pip
RUN pip3 install numpy
RUN pip3 install scipy
RUN pip3 install sklearn

COPY ["lambda_function.py", "dict_vectorizer.bin", "logistic_regression.bin",  "./"]

CMD ["lambda_function.lambda_handler"]
```

Type `docker build -t model_name .` to build the container.

## Run Docker locally

```bash
docker run -it --rm -p 8080:8080 model_name:latest
```

## Test the container locally

To test the cointaner locally we will send a `data_url` from an image to the localhost `url` that AWS uses

```python
import requests
import json

user = {'bmi': 23.78,
 'smoking': "yes",
 'alcoholdrinking': "yes",
 'stroke': "yes",
 'physicalhealth': 0.0,
 'mentalhealth': 0.0,
 'diffwalking': "yes",
 'sex': "female",
 'agecategory': "80 or older",
 'race': "black",
 'diabetic': "yes",
 'physicalactivity': "no",
 'genhealth': "good",
 'sleeptime': 7.0,
 'asthma': "no",
 'kidneydisease': "no",
 'skincancer': "no"}
 
event = {"user":user}

url = 'http://localhost:8080/2015-03-31/functions/function/invocations'
response = requests.post(url, json=event)
result = response.json()

print(json.dumps(result, indent=2))
```

If the results are correct we expect to have a prediction of our model. The test file is stored in `test.py`.

## Create AWS ECR respository

```bash
aws ecr create-repository --repository-name model-repo
```

## Login to Docker account

```bash
$(aws ecr get-login --no-include-email)
```

## Tag Docker container

For this you will use the `respositoryUri` generated when you created your ECR repository.

```bash
ACCOUNT=*************
REGION=us-east-1
REGISTRY=model-repo
TAG=latest

PREFIX=$ACCOUNT.dkr.ecr.$REGION.amazonaws.com/$REGISTRY

REMOTE_URI=$PREFIX:$TAG

docker tag model_name:latest $REMOTE_URI
```

## Push container

```bash
docker push $REMOTE_URI
```

## Create AWS Lambda function

![Alt text](/media/manuel/storage/Courses/ml-zoomcamp/course-zoomcamp/09-serverless/homework/own/images/lambda.png "a title")

Be sure to edit it's preferences and add more memory and time for your Lambda function to execute.

## Create API Gateway

Go to AWS Console and create a REST API with a resource named `predict`. Be sure to select CORS.

![Alt text](/media/manuel/storage/Courses/ml-zoomcamp/course-zoomcamp/09-serverless/homework/own/images/api-gateway-resources.png "a title")

Make a POST method with your previously created lambda function

![Alt text](/media/manuel/storage/Courses/ml-zoomcamp/course-zoomcamp/09-serverless/homework/own/images/api-gateway-post.png "a title")

Deploy your API and give it a stage name, i.e. `production`.

You will get an IP  like this

```bash
https://*********.execute-api.us-east-1.amazonaws.com/production/predict
```

where you can make your API calls .

## Add an API Key

To protect you deployment from undisired requests, you can add an API Key to your service. To do so you first need to add an **Api Key Required** parameter to your POST method.

![Alt text](/media/manuel/storage/Courses/ml-zoomcamp/course-zoomcamp/09-serverless/homework/own/images/api-key.png "a title")

Then go to API Keys on the left panel and on Actions select Create API key and give a name to your API key.

![Alt text](/media/manuel/storage/Courses/ml-zoomcamp/course-zoomcamp/09-serverless/homework/own/images/api-key-create.png "a title")

Now go to Usage Plans on the left panel and create a usage plan. Set a Throttling and Quota that you prefer.

![Alt text](/media/manuel/storage/Courses/ml-zoomcamp/course-zoomcamp/09-serverless/homework/own/images/usage_plan.png "a title")

And then associate your Usage Plan with your API Key.

Deploy your API again. (Maybe you will need to wait a minute in order for your changes to take effect.)

## Test your deployment

To test your deployment you need to modify the `test.py` script and a header with the API Key as follows

```python
headers = {
  'X-API-KEY': api_key,
  'Content-Type': 'application/json'
}

result = requests.post(url, json={'url': data}, headers=headers).json()
```

**It is a good idea to store your API Key separately in another file to avoid malicious usage.**


