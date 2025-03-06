import requests
from stem.control import Controller

"""
The base of the code was taken from this website:
https://stem.torproject.org/tutorials/examples/list_circuits.html

I pinged the website https://ip-api.com/docs/api:json to get the geolocation of the IP
"""

location = ['ENTRY', 'MIDDLE', 'EXIT']

# Function to get geolocation (country) of an IP address
def get_country(ip):
    url = f"http://ip-api.com/json/{ip}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data["country"]
    else:
        return "Unknown"

with Controller.from_port(port=9051) as controller:
    controller.authenticate('i_like_this_class_alot')

    for circuit in sorted(controller.get_circuits()):
        if circuit.status == 'BUILT':
            print()
            print("Circuit %s (%s)" % (circuit.id, circuit.purpose))
            for i, node in enumerate(circuit.path):
                fingerprint, nickname = node

                curr = controller.get_network_status(fingerprint, None)
                address = curr.address if curr else 'unknown'
                bandwidth = curr.bandwidth if curr else 'unknown'
                country = get_country(address)

                print("| %s: \t %s (%s, %s, %s)" % (
                    location[i], nickname, address, country, bandwidth))
