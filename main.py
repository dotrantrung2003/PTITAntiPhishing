import json
import re
import joblib
import features_extraction
import sys
import numpy as np
import whois
from collections import Counter
from features_extraction import *


def main():
    url = sys.argv[1]
    features_test = features_extraction.main(url)
    
    if len(features_test) != 21:
        respond_data = {"error": "SOMETHING_WENT_WRONG"}
        json_respond_data = json.dumps(respond_data)
        print(json_respond_data)
        return
    features_test = np.array(features_test).reshape((1, -1))
    clf = joblib.load('classifier/27_11_25k_RF_Model.pkl')

    prediction = clf.predict(features_test)
    prediction_int = int(prediction[0])
    probability = clf.predict_proba(features_test)

    respond_data = {"features": features_test.tolist(), "probability": probability.tolist(),
                    "prediction": prediction_int, "url": url}
   
    json_respond_data = json.dumps(respond_data)
    print(json_respond_data)
    
if __name__ == "__main__":
    main()
