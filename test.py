import requests
base="http://127.0.0.1:5000"
res=requests.post(base+"/2/trackers", json={'tracker_type': "numerical", 'tracker_name': "tracker_name", 'description': "tracker_description"})
print(res)