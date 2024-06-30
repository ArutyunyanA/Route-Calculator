from flask import Flask, render_template, request
from constant import API_KEY  # Предполагается, что API_KEY определен в constant.py
import requests
import folium

app = Flask(__name__, template_folder='templates')

# Функции для работы с API Mapbox и визуализации маршрутов

def get_coordinate(address):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
    params = {
        'access_token': API_KEY,
        'limit': 1  # Ограничить результат одним ответом
    }
    response = requests.get(url, params=params)
    try:
        data = response.json()
        if data['features']:
            coordinates = data['features'][0]['geometry']['coordinates']
            return coordinates
        else:
            return None
    except requests.exceptions.ConnectionError as error:
        print(f"Не удалось подключиться к серверу: {error}")
        return None

def get_routes(coords1, coords2):
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{coords1[0]},{coords1[1]};{coords2[0]},{coords2[1]}"
    params = {
        'access_token': API_KEY,
        'alternatives': 'true',  # Запрос альтернативных маршрутов
        'geometries': 'geojson'  # Получение геометрии маршрутов в формате GeoJSON
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        if 'routes' in data and data['routes']:
            return data['routes']
        else:
            return None
    except requests.exceptions.ConnectionError as error:
        print(f"Не удалось подключиться к серверу: {error}")
        return None

def find_best_routes(routes):
    if not routes:
        return None, None
    
    shortest_route = min(routes, key=lambda x: x['distance'])
    fastest_route = min(routes, key=lambda x: x['duration'])
    
    return shortest_route, fastest_route

def visualize_routes(routes, coords_a, coords_b):
    map_ = folium.Map(location=[(coords_a[1] + coords_b[1]) / 2, (coords_a[0] + coords_b[0]) / 2], zoom_start=13)
    colors = ['blue', 'green', 'red']

    for i, route in enumerate(routes):
        points = route['geometry']['coordinates']
        points = [(point[1], point[0]) for point in points]  # Переставить координаты местами (lat, lon)
        
        folium.PolyLine(points, color=colors[i % len(colors)], weight=5, opacity=0.8).add_to(map_)
    
    folium.Marker(location=[coords_a[1], coords_a[0]], popup='Start').add_to(map_)
    folium.Marker(location=[coords_b[1], coords_b[0]], popup='End').add_to(map_)

    return map_._repr_html_()

# Определение маршрутов в Flask

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        origin_address = request.form['origin']
        destination_address = request.form['destination']
        
        coords_a = get_coordinate(origin_address)
        coords_b = get_coordinate(destination_address)
        
        if coords_a and coords_b:
            routes = get_routes(coords_a, coords_b)
            if routes:
                shortest_route, fastest_route = find_best_routes(routes)
                
                if shortest_route:
                    shortest_route_info = {
                        'distance': round(shortest_route['distance'] / 1000),
                        'duration': round(shortest_route['duration'] / 60)
                    }
                else:
                    shortest_route_info = None
                
                if fastest_route:
                    fastest_route_info = {
                        'distance': round(fastest_route['distance'] / 1000),
                        'duration': round(fastest_route['duration'] / 60)
                    }
                else:
                    fastest_route_info = None
                
                # Визуализация маршрутов на карте
                map_html = visualize_routes(routes, coords_a, coords_b)
                
                return render_template('result.html', 
                                       shortest_route=shortest_route_info, 
                                       fastest_route=fastest_route_info,
                                       map_html=map_html)
            else:
                return "Не удалось получить маршруты."
        else:
            return "Не удалось получить координаты для одного из адресов."
    
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
