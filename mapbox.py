import requests
from constant import API_KEY

def get_coordinate(address):
   url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
   params = {'access_token': API_KEY, 'limit': 1}
   response = requests.get(url, params=params)
   data = response.json()
   if data['features']:
       coordinates = data['features'][0]['geometry']['coordinates']
       return coordinates
   return None

def get_distance(coords1, coords2):
   url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{coords1[0]},{coords1[1]};{coords2[0]},{coords2[1]}"
   params = {'access_token': API_KEY}
   response = requests.get(url, params=params)
   data = response.json()
   if 'routes' in data and data['routes']:
       distance = data['routes'][0]['distance'] / 1000  # расстояние в км
       duration = data['routes'][0]['duration'] / 60    # продолжительность в минутах
       return distance, duration
   return None