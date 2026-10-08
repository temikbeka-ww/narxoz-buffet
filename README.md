# TEMIKBEK — Project One: Narxoz Buffet Rush

A **single-page interactive website written in Python with Streamlit**, covering Theory of Probability & Statistics Weeks 1–5 through a familiar campus question: can you buy food during a 15-minute break and still arrive at class on time?

## Start locally

**On Windows:** after installing Python, double-click `start_windows.bat` (or follow the terminal steps below). **On macOS / Linux:** run `bash start_mac_linux.sh`. An internet connection is required the first time to install Streamlit and the other dependencies.

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Install requirements:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Start the website:

   ```bash
   python -m streamlit run app.py
   ```

The app will open at `http://localhost:8501`.

## Deploy (Streamlit Community Cloud)

Upload the project to GitHub, then choose `app.py` as the main file in Streamlit Community Cloud. It installs packages listed in `requirements.txt`.

## Features

- RU/EN interface, three floor choices (previous class → buffet → next class)
- Walking down: 1.5 min/floor; walking up: 2.25 min/floor (adjustable via pace)
- Buffet queue, purchase time, **time to eat**, and a 15-minute break
- Floor 3: separate waiting-time examples for students coming from floor 3 and those coming from another floor
- Default 3 → 3 → 3 case: after the queue (4–6 minutes) and purchase (1 minute), **8–10 minutes remain for eating** within a 15-minute break
- Probability as relative frequency across observed/example queue times — **no Monte Carlo / no random numbers**
- Interactive graphs for floor comparison and waiting-time frequency
- Editable example waiting-time table, CSV download
- Course concepts: Week 1 sample space, events and counting; Week 2 probability; Week 3 conditional/total probability; Week 4 independence; Week 5 frequencies/data visualization

## Interpretation and limitations

Default numbers are **illustrative assumptions, not verified Narxoz measurements**. A percent represents the fraction of example wait times in which the selected trip, purchase and eating time fit into the break. It is **not an official forecast**. Enter your own anonymized timing data to get a more useful empirical estimate.

The number of possible unrestricted three-floor route combinations is `5 × 5 × 5 = 125`. This is a count of options, **not a claim that all routes are equally likely**. The probability of getting to class on time is instead estimated from waiting-time examples for the chosen situation.

The total-probability and independence examples assume specific buffet-selection weights; they are not an inference about actual student preferences.

## Run tests

```bash
python -m pip install pytest
python -m pytest -q
```

Core math is implemented in `model.py`, separate from the Streamlit interface in `app.py`.
