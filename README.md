# Yava Labs Stock Monitor

Monitors Shopify product variant stock status every 15 minutes and sends a Telegram notification when an item is restocked.

## How It Works

1. A GitHub Actions workflow runs every 15 minutes (cron: `*/15 * * * *`)
2. Fetches the product JSON via Shopify's `/products/{handle}.js` endpoint
3. Looks up the target variant by ID and checks `available`
4. Compares against the previous status stored in `state.json`
5. If status changed from `out_of_stock` → `in_stock`, sends a Telegram alert
6. Commits the updated `state.json` back to the repo

## Setup

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Save the bot token (looks like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 2. Get Your Chat ID

1. Start a chat with your new bot and send any message
2. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find the `chat.id` value in the JSON response

### 3. Add GitHub Secrets

In your repository on GitHub, go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|--------|-------|
| `TELEGRAM_BOT_TOKEN` | Your bot token from BotFather |
| `TELEGRAM_CHAT_ID` | Your chat ID |

### 4. Enable Workflows

Push to `main`. The workflow runs automatically every 15 minutes. You can also trigger it manually from the Actions tab.

## Run Locally

```bash
pip install -r requirements.txt

TELEGRAM_BOT_TOKEN="your-token" TELEGRAM_CHAT_ID="your-chat-id" python src/monitor.py
```

### Dry Run

```bash
python src/monitor.py --dry-run --verbose
```

## Customize for Another Product / Variant

Edit `src/products.py`:

```python
PRODUCTS = [
    {
        "name": "Pure ISO Whey 2 KG",
        "url": "https://www.yavalabs.ae/products/pure-iso-whey-2-kg",
        "variants": [
            {"name": "Banana", "id": 46692232495329},
            {"name": "Vanilla", "id": 46692232462561},
        ],
    },
    {
        "name": "Another Product",
        "url": "https://www.yavalabs.ae/products/another-product",
        "variants": [
            {"name": "Strawberry", "id": 123456789},
        ],
    },
]
```

You can add unlimited products, each with unlimited variants.

## Project Structure

```
├── .github/workflows/stock-check.yml   # GitHub Actions workflow
├── src/
│   ├── config.py    # Configuration dataclass
│   ├── monitor.py   # Entry point with CLI
│   ├── notifier.py  # Telegram sender
│   ├── products.py  # Product & variant definitions
│   ├── shopify.py   # Shopify API client
│   └── state.py     # Persistent state manager
├── tests/
│   ├── test_products.py
│   └── test_shopify.py
├── requirements.txt
├── state.json       # Tracks last known status
└── README.md
```

## Troubleshooting

- **Workflow not running**: Verify secrets are set and Actions are enabled
- **No notification received**: Check the workflow logs for errors
- **"Variant not found"**: Verify the variant ID and product URL in `src/products.py`
- **Rate limited**: The script retries with exponential backoff automatically
