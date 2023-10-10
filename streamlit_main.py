import os
import streamlit as st
from dotenv import load_dotenv
from ticket_master_utils import search_events, parse_event, group_events_by_artist
from spotify_utils import authenticate_to_spotify, get_current_user_top_artists
from streamlit_card import card
from collections import defaultdict
import datetime

import uuid


def eevent_card(event):
    text = [f'Band: {event["band_name"]}', f'Date and Time: {event["date_and_time"]}', f'Venue: {event["venue_name"]}', f'Address: {event["venue_address"]}']                
    card_id = uuid.uuid4().hex
    
    card(title=event["event_name"],
        text= text,
        url=f"{event['event_url']}",
        styles= {
            "card": {
                "width": "700px",
                "height": "450px",
                "fornt-size": "80px",
                }
            },
        image=event["image"], 
        key=card_id,
        )


def event_card(event):
    st.write(f"""
        **Event:** {event['event_name']}\n
        **Date and Time:** {event['date_and_time']}\n
        **Venue:** {event['venue_name']}\n
        **Address:** {event['venue_address']}\n
        **URL:** {event['event_url']}"""),
    st.image(image=event["image"])
    st.write("----")

# [theme]
# primaryColor="#b19cd9"
# backgroundColor="#f0f0f0"
# secondaryBackgroundColor="#b4bcde"
# textColor="#333333"


load_dotenv()
ticketmaster_api_key = os.getenv('TICKETMASTER_API_KEY')
ticketmaster_api_url = os.getenv('TICKETMASTER_API_URL')

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
scope = os.getenv('SPOTIFY_APP_SCOPE')

sp = None
all_artists = []

st.title('Content Finder')
st.markdown(body='Please connect to your Spotify account')
sp_connect_button = st.button(label='Connect', key='connect_spotify_button')
events_to_get = st.slider(min_value=1, max_value=10, value=1, step=1, label='events_to_get')

start_date = None
end_date = None

# start_date = st.date_input("Enter start date", key=f'start_input {uuid.uuid4().hex}')
# end_date = st.date_input("Enter end date", key=f'end_input {uuid.uuid4().hex}')

if sp_connect_button:
    try:
        sp = authenticate_to_spotify(client_id, client_secret, redirect_uri, scope)
    
    except Exception as e:
        st.error(e)
    
    finally:
        top_artists = get_current_user_top_artists(sp, limit=100)
        for artist in top_artists:
            artist_events = []
            events = search_events(artist_name=artist, ticketmaster_api_key=ticketmaster_api_key, ticketmaster_api_url=ticketmaster_api_url, 
                                   start_date=start_date, end_date=end_date, events_to_get=events_to_get)
            if events:
                for event in events:
                    if event is not None:
                            event = parse_event(band_name=artist, event=event)
                            artist_events.append(event)

            with st.expander(f"{artist}, {len(artist_events)}  events found", expanded=False):
                for event in artist_events:
                    event_card(event=event)
                        