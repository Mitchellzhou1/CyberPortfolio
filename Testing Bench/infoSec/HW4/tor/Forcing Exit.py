from stem.control import Controller
import requests
"""
I used https://sigmapie8.github.io/learning-stem/requests_with_tor.html
to obtain the syntax for sending requests and using the proxy via STEM 

I used https://stackoverflow.com/questions/40710588/choose-exit-node-of-tor-python-stem
to obtain the syntax set controller options
"""


def configure_tor_exit_nodes(country_code):
    with Controller.from_port(port=9051) as controller:
        controller.authenticate("i_like_this_class_alot")

        location = "{" + country_code + "}"
        controller.set_options({                        # got from stack overflow
            "ExitNodes": location,
            "StrictNodes": "1"
        })
        print(f"Exit node from: {country_code}")
        return controller


def ping_site(url):
    proxy_url = "socks5h://127.0.0.1:9050"
    try:
        response = requests.get(url, proxies={"https": proxy_url})      # got from sigmapie8.github.io
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"


def main():
    url = "https://arjunbrar.com/ctf?andrew_id=mitchelz"

    country_codes = ["gb"]

    for country_code in country_codes:
        print(f"Attempting with exit node in {country_code}...")
        controller = configure_tor_exit_nodes(country_code)


        result = ping_site(url)
        print(result)
        controller.close()


if __name__ == "__main__":
    main()
