# Dofus KIKI Meter

A damage-meter for the game Dofus.

## Installation

Make sure to install the required packages : 
- pandas
- streamlit
- plotly
- numpy
- re

## Run the App:

`streamlit run chat_stat_app.py`

## Get dofus chat in .txt format:

 - In game: click the star at the bottom left corner of the chat  
 - Select `ouvrir le chat externe`, this will open a new window
 - On the new window use the star icon to select only the `combat` channel
 - Click the eraser to clear the old messages
 - Once you have done some combats you can Download the chat as txt file by clicking the download icon

 ## misc:

- All asynchronous events will be wrongly attributed to the last action before their triggering this includes *poisons*, shield from *dofus emeraude* or *prytek*, damage from *bombs wall*, etc.
- If the file contains logs from multiple combats you can select the one you want to show in the side panel.
- If multiples entity have the same name they wil be counted as one and their stats will be aggregated because we can't differentiate them with only the chat informations.
