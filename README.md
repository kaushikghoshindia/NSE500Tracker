# NSE 500 Tracker — Setup Guide (No Coding Required)

This project pulls daily historical price data for NSE 500 stocks and Nifty
indices automatically, and shows it on a webpage. Everything below is done
by clicking buttons in your browser — nothing to install, nothing to type
as code.

## What you're setting up

- A **repository** (a project folder) on GitHub holding this project.
- An **automatic daily job** (GitHub Actions) that fetches fresh data every
  weekday evening — runs on GitHub's computers, not yours.
- A **webpage** (GitHub Pages) that displays the data with charts.

## Step 1 — Create the repository

1. Go to **github.com**, make sure you're signed in.
2. Click the **+** icon (top right) → **New repository**.
3. Name it something like `nse500-tracker`.
4. Make sure it's set to **Public** (required for the free webpage hosting).
5. Do **not** check "Add a README" — leave it empty.
6. Click **Create repository**.

## Step 2 — Upload the project files

1. Unzip the `nse500-tracker.zip` file I gave you (double-click it — most
   computers extract zip files automatically; on Windows right-click →
   "Extract All").
2. On your new empty repository's GitHub page, click **"uploading an
   existing file"** (or **Add file → Upload files**).
3. Open the unzipped `nse500-tracker` folder on your computer, select
   *everything inside it* (all files and folders), and **drag them all**
   into the GitHub upload box in your browser. GitHub preserves the folder
   structure automatically.
4. Scroll down, click **Commit changes**.

If drag-and-drop doesn't pick up the `.github` folder (some browsers hide
it since it starts with a dot), that's the one thing to check — click into
the uploaded repo afterward and confirm you see a `.github` folder listed
alongside `data`, `scripts`, and `index.html`. If it's missing, use
**Add file → Create new file**, and for the filename type exactly
`.github/workflows/daily-sync.yml` (GitHub creates the folders for you),
then paste in the contents of that file from the zip.

## Step 3 — Turn on the daily automatic updates

1. In your repository, click the **Actions** tab.
2. If prompted with a message about workflows, click **"I understand my
   workflows, go ahead and enable them"**.
3. You should see **"Daily NSE 500 Data Sync"** listed on the left. Click it.
4. Click the **Run workflow** button (top right of that page) → **Run
   workflow** again to confirm.
5. Wait a few minutes and refresh — you'll see a run appear with a spinning
   or checkmark icon. A checkmark means it worked and your data is now in
   the `data` folder. From now on, this runs by itself every weekday evening.

## Step 4 — Turn on the webpage

1. In your repository, click **Settings** (top menu).
2. In the left sidebar, click **Pages**.
3. Under "Build and deployment" → "Source", choose **Deploy from a branch**.
4. Under "Branch", choose **main** and folder **/ (root)**, then **Save**.
5. Wait a minute, then refresh the page — GitHub will show you a link like
   `https://yourusername.github.io/nse500-tracker/`. That's your live
   webpage, and it updates automatically every time the daily data sync runs.

## Troubleshooting

- **Webpage shows an error about manifest.json**: the daily sync hasn't run
  yet — go do Step 3.
- **A stock symbol is missing from the list**: NSE 500 membership changes
  periodically (around March/September). It'll pick up newly added stocks
  automatically on the next scheduled run, as long as EOD2's data covers them.
- **Something looks broken and you're not sure why**: come back here and
  describe what you see — you won't need to read any code, just tell me
  what's on the screen.
