import os
import pandas as pd


def load_data():
    csv_path = 'restaurants.csv'

    # Reads your CSV file if it exists, otherwise uses sample Indian restaurant data
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
        return pd.read_csv(csv_path)
    else:
        sample_data = {
            'id': [1, 2, 3, 4, 5],
            'name': ['Bukhara', 'Britannia & Co.', 'Mavalli Tiffin Room', 'Paradise Biryani', 'Toit Brewpub'],
            'city': ['Delhi', 'Mumbai', 'Bengaluru', 'Hyderabad', 'Bengaluru'],
            'address': [
                'ITC Maurya, Diplomatic Enclave, New Delhi',
                '11 Sprott Rd, Fort, Mumbai',
                '14 Lalbagh Fort Rd, Bengaluru',
                'MG Road, Secunderabad, Hyderabad',
                '100 Feet Rd, Indiranagar, Bengaluru'
            ],
            'cuisine': [
                'North Indian, Kebab',
                'Parsi, Berry Pulao',
                'South Indian, Dosa, Filter Coffee',
                'Hyderabadi Biryani, Kebabs',
                'Brewery, Continental, Pizza'
            ],
            'rating': [4.8, 4.6, 4.7, 4.5, 4.7],
            'image': [
                'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=500',
                'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500',
                'https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?w=500',
                'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500',
                'https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=500'
            ]
        }
        return pd.DataFrame(sample_data)


def get_recommendations_by_city(city_name):
    df = load_data()
    if not city_name:
        return []

    # Case-insensitive city search
    filtered = df[df['city'].astype(str).str.lower() == city_name.strip().lower()]

    if filtered.empty:
        return []

    # Sort highest rating first
    sorted_df = filtered.sort_values(by='rating', ascending=False)
    return sorted_df.to_dict(orient='records')