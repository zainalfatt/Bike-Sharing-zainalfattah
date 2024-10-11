import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import matplotlib.patches as mpatches
from babel.numbers import format_currency
sns.set(style='dark')

# Helper functions
def create_by_season(df):
    sum_casual_user = df.groupby("season").casual.sum().sort_values(ascending=False).reset_index()
    sum_registered_user = df.groupby("season").registered.sum().sort_values(ascending=False).reset_index()

    daily_user = pd.merge(
        left=sum_casual_user,
        right=sum_registered_user,
        how="left",
        left_on="season",
        right_on="season"
    )
    daily_user_type = daily_user.melt(id_vars='season', var_name='tipePengguna', value_name='jumlahPengguna')
    return  daily_user_type


def create_sum_casual_user_df(df):
    sum_casual_user_df = df.groupby("season").casual.sum().sort_values(ascending=False).reset_index()
    return sum_casual_user_df

def create_sum_registered_user_df(df):
    sum_registered_user_df = df.groupby("season").registered.sum().sort_values(ascending=False).reset_index()
    return sum_registered_user_df

def create_byweather_df(df):
    byweather_df = df.groupby("weatherist").cnt.sum().sort_values(ascending=False).reset_index()
    return byweather_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="weekday", as_index=False).agg({
    "dteday": "max", 
    "instant": "nunique", 
    "cnt": "sum"
    })

    rfm_df.columns = ["weekday", "max_order_timestamp", "frequency", "monetary"]

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["dteday"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df


# Prepare dataframe
df = pd.read_csv("dashboard/data_clean.csv")

# Ensure the date column are of type datetime
datetime_columns = ["dteday"]
df.sort_values(by="dteday", inplace=True)
df.reset_index(inplace=True)
for column in datetime_columns:
    df[column] = pd.to_datetime(df[column])

# Create filter components
min_date = df["dteday"].min()
max_date = df["dteday"].max()

with st.sidebar:
    # Adding a company logo
    st.image("dashboard/logo.png", width=200)

    # Retrieve start_date & end_date from date_input
    start_date, end_date = st.date_input(
        label='Range of Time', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = df[(df["dteday"] >= str(start_date)) & (df["dteday"] <= str(end_date))]

createSeason = create_by_season(df)
sum_casual_user_df = create_sum_casual_user_df(main_df)
sum_registered_user_df = create_sum_registered_user_df(main_df)
rfm_df = create_rfm_df(main_df)

# Create dashboard
st.header('Capital Bike Share Dashboard :bicyclist:')

# Daily Users
st.subheader('Season Users')
col1, col2, col3 = st.columns(3)

with col1:
    total_casual = sum_casual_user_df.casual.sum()
    st.metric("Total Casual User", value=f'{total_casual:,}', delta_color="inverse")

with col2:
    total_registered =sum_registered_user_df.registered.sum()
    st.metric("Total Registered User", value=f'{total_registered:,}', delta_color="inverse")

with col3:
    total_users = sum_casual_user_df.casual.sum() + sum_registered_user_df.registered.sum()
    st.metric("Total Users", value=f'{total_users:,}', delta_color="inverse")

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x="season", y="jumlahPengguna", hue="tipePengguna", data=createSeason, palette="muted")
ax.set_ylabel("Total Pengguna", fontsize=12)
ax.set_xlabel("Musim", fontsize=12)
ax.set_title("Perbandingan Pengguna Casual and Registered Berdasarkan Musim", fontsize=16)

casual_patch = mpatches.Patch(color=sns.color_palette("muted")[0], label='Casual')
registered_patch = mpatches.Patch(color=sns.color_palette("muted")[1], label='Registered')
ax.legend(handles=[casual_patch, registered_patch], title="User Type")

plt.tight_layout()
st.pyplot(fig)

# Number of Casual Users and Registered Users by Season
st.subheader("Number of Casual Users and Registered Users by Season")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = sns.color_palette("coolwarm", 7)

sns.barplot(x="casual", y="season", data=sum_casual_user_df, palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Casual Users", loc="center", fontsize=40)
ax[0].tick_params(axis='y', labelsize=20)
ax[0].tick_params(axis='x', labelsize=20, rotation=45)

sns.barplot(x="registered", y="season", data=sum_registered_user_df, palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("Registered Users", loc="center", fontsize=40)
ax[1].tick_params(axis='y', labelsize=20)
ax[1].tick_params(axis='x', labelsize=20, rotation=-45)

st.pyplot(fig)

# Productivity Bike Sharing in season
def plot_season_data(df, season_name, season_label):
    season_df = df[df['season'] == season_name]
    
    if not season_df.empty:
        fig, ax = plt.subplots(figsize=(20, 5))
        sub = f"Bike Sharing productivity based on time during the {season_label} season"
        st.subheader(sub.title())
        sns.pointplot(data=season_df, x='hr', y='cnt', hue='daystatus', errorbar=None, ax=ax)
        ax.set_title(f'Produktivitas Bike Sharing Berdasarkan Waktu pada Musim {season_label}')
        ax.set_ylabel('Total Pengguna')
        ax.set_xlabel('Hour')
        st.pyplot(fig)
    else:
        st.write(f"No data available for the {season_label} season.")

# Identifikasi musim yang ada dalam rentang tanggal tersebut
seasons_available = main_df['season'].unique()

# Tampilkan visualisasi untuk setiap musim yang ada
if 'Winter' in seasons_available:
    plot_season_data(main_df, 'Winter', 'Winter')

if 'Fall' in seasons_available:
    plot_season_data(main_df, 'Fall', 'Fall')

if 'Spring' in seasons_available:
    plot_season_data(main_df, 'Spring', 'Spring')

if 'Summer' in seasons_available:
    plot_season_data(main_df, 'Summer', 'Summer')


# Jumlah pengguna berdasarkan kondisi cuaca
st.subheader("Number of Users Based on Weather Conditions")

# Mengelompokkan data berdasarkan kondisi cuaca dan menjumlahkan total pengguna
byweather = main_df.groupby("weathersit")["cnt"].sum().sort_values(ascending=False).reset_index()

level_labels = byweather['weathersit'].tolist()  
level_counts = byweather['cnt'].tolist()       
cols = st.columns(len(level_labels))

for i in range(len(level_labels)):
    with cols[i]:
        st.metric(label=level_labels[i], value=level_counts[i])

max_count = byweather['cnt'].max()
colors = ["#72BCD4" if count >= max_count else "#D3D3D3" for count in byweather['cnt']]  # Warna default dan warna untuk tertinggi
# Membuat figure dan plot
fig, ax = plt.subplots(figsize=(12, 6))  # Menggunakan subplots agar lebih fleksibel
sns.barplot(y="cnt", x="weathersit", data=byweather, palette=colors, ax=ax)

# Menambahkan judul dan label
ax.set_title("Jumlah Pengguna Berdasarkan Kondisi Cuaca", loc="center", fontsize=15)
ax.set_ylabel("Total Pengguna")
ax.set_xlabel("Kondisi Cuaca")
ax.ticklabel_format(style='plain', axis='y')  # Mengatur format sumbu y agar tidak dalam notasi ilmiah

# Menampilkan plot di Streamlit
st.pyplot(fig)

# RFM Analysis
st.subheader("Best Customer Based on RFM Parameters (day)")
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Avg Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Avg Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "USD", locale='en_US')
    st.metric("Avg Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))

colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="recency", x="weekday", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15)

sns.barplot(y="frequency", x="weekday", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)

sns.barplot(y="monetary", x="weekday", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader("Jumlah Level Volume Users")
total_level_pengguna = main_df.groupby("level_pengguna")['level_pengguna'].count().sort_values(ascending=False).reset_index(name='count')

level_labels = total_level_pengguna['level_pengguna'].tolist()  
level_counts = total_level_pengguna['count'].tolist()       
cols = st.columns(len(level_labels))

for i in range(len(level_labels)):
    with cols[i]:
        st.metric(label=level_labels[i], value=level_counts[i])
    
fig, ax = plt.subplots(figsize=(10, 6))
max_count = total_level_pengguna['count'].max()
colors = ["#72BCD4" if c == max_count else "#D3D3D3" for c in total_level_pengguna['count']]
sns.barplot(x='level_pengguna', y='count', data=total_level_pengguna, ax=ax, color="#D3D3D3")  # Set warna default
for i, count in enumerate(total_level_pengguna['count']):
    if count == max_count:
        ax.patches[i].set_facecolor("#72BCD4")  # Mengubah warna batang tertinggi
ax.set_ylabel('Jumlah Volume')
ax.set_xlabel('Level Volume Pengguna/Penyewa')
st.pyplot(fig)

st.caption(f"Copyright © 2024 All Rights Reserved Zainal Fattah (www.linkedin.com/in/zainalfattah)")
