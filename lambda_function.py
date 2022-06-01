import pickle as pkl
import json


file_dictVect = 'dict_vectorizer.bin'
with open(file_dictVect, 'rb') as dictVect:
    dv = pkl.load(dictVect)

file_model = 'logistic_regression.bin'
with open(file_model, 'rb') as model:
    lr = pkl.load(model)


def predict(user):
    #user = request.get_json()
    X = dv.transform([user])
    y = lr.predict_proba(X)[0][1]
    danger = y >= 0.5

    result = {'danger': bool(danger),
              'probability':float(y)}
    #return jsonify(result)
    return result
    
    
def lambda_handler(event, context):
    user = event['user']
    #X = preprocessor.from_url(url)
    preds = predict(user)
    return preds
    
    
#if __name__ == "__main__":
#    app.run(debug=True, host='localhost', port=9696)
