name: 4-Hour News Fetcher

on:
  schedule:
    - cron: '0 */4 * * *'
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install requests google-genai pymongo

      - name: Run news fetcher
        env:
          NEWSDATA_API_KEY: ${{ secrets.NEWSDATA_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          MONGO_URI: ${{ secrets.MONGO_URI }}
        run: python main.py
