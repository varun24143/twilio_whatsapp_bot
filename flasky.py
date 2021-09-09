from flask import Flask, request
import requests
import collections
import json
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
# Stores entries
Users = []
# Previous Stage
prev = ""

#Current Patient
patient = {}
#Store details
new = []

@app.route('/bot', methods=["POST","GET"])
def bot():
    global patient,prev,new,Users
    incoming_msg = request.values.get('Body', '').lower()
    waid = request.values.get("WaId")
    patient["User_ID"] = waid
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg == "raise new query":
        prev = "raise"
        patient = {}
        new = []
        print(new)
        msg.body("Raising for yourself?")
        return str(resp)
    
    if prev=="raise":
        if incoming_msg=="yes":
            prev = "name"
            msg.body("Enter patient name")
            return str(resp)
        else:
            prev = "np"
            msg.body("Enter your name")
            return str(resp)
    
    if prev=="np":
        new.append(("Raising on behalf",incoming_msg))
        prev = "pname"
        msg.body("Enter patient name")
        return str(resp)
    
    if prev=="pname":
        new.append(("Patient name",incoming_msg))
        prev = "mn"
        msg.body("Enter patient mobile number")
        return str(resp)

    if prev=="name" or prev=="mn":
        if incoming_msg:
            if prev=="mn":
                new.append(("Mobile Number",incoming_msg))
            else:
                new.append(("Patient name",incoming_msg))
            prev = "query"
            msg.body("Enter your Query")
            return str(resp)
        
        else:
            prev = "name"
            msg.body("Enter a valid name")
            return str(resp)
    
    if prev=="query":
        if incoming_msg:
            new.append(("Query",incoming_msg))
            prev = "docs"
            msg.body("Upload documents (Optional)")
            return str(resp)
        
        else:
            prev = "query"
            msg.body("Enter a valid Query")
            return str(resp)
    
    if prev=="docs":
        q = new[-1][1]
        prev = "equery"
        msg.body(f"Do you want to edit your query? \nYour query: {q}")
        return str(resp)
    
    if prev=="equery":
        if incoming_msg=="yes":
            prev = "query"
            msg.body("Enter your Query")
            return str(resp)
        
        else:
            prev = "mdocs"
            msg.body("Do you want to add more docs?")
            return str(resp)
        
    if prev=="mdocs":
        if incoming_msg=='yes':
            prev = 'docs'
            msg.body("Upload Documents")
            return str(resp)
        else:
            prev="submit"
            msg.body("Submit query")
            return str(resp)
    
    if prev=="submit":
        if incoming_msg == "yes":
            patient["details"] = new
            Users.append(patient)
            check = ''
            for i in new:
                check+=i[0]+": "+i[1]+"\n"
            msg.body(f"Query submited \n{check}")
            print()
        else:
            msg.body(f"Query not submited")
        return str(resp)

@app.route("/response",methods=["POST","GET"])
def responses():
    global Users
    with open('data.json', 'w') as f:
        json.dump(Users, f)
    return json.dumps(Users)

if __name__ == '__main__':
    app.run()
