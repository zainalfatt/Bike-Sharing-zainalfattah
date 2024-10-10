# Data Analytics Project: Bike Sharing Dataset

## About Bike Sharing Dataset

[**Bike Sharing Dataset**](https://www.kaggle.com/datasets/lakshmi25npathi/bike-sharing-dataset) is a dataset that contains the hourly and daily count of rental bikes between the years 2011 and 2012 in the [**Capital Bikeshare**](https://capitalbikeshare.com) system with the corresponding weather and seasonal information.

**Dataset Information**
- Date and Time: date, year, month, hour, and day of the week
- Season and Holidays: season, holiday status, and working day status
- Weather: weather situation, temperature, feeling temperature, humidity, and wind speed (all normalized)
- User Types: count of casual users, registered users, and total rental bikes

## How to Run This Project ?

1. Clone this repository

```
git clone https://github.com/Anashaneef/capital-bike-share-analysis.git
```

2. Install all library

```
pip install numpy pandas matplotlib seaborn jupyter streamlit babel
```

or

```
pip install -r requirements.txt
```

3. Go to dashboard folder

```
cd dashboard
```

4. Run with Streamlit

```
streamlit run dashboard.py
```