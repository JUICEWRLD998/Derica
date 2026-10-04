# How to test Derica on your computer

Open a terminal in the `derica` folder. Every step below runs from there.

## 1. Run the checks (10 seconds)

```
uv run pytest -q
```

You should see `167 passed`. If a test fails, something is broken.

## 2. Start the app

The app needs your Tinker key. The server does not read `.env` by itself, so load it first.

Git Bash:
```
set -a; . ./.env; set +a
uv run uvicorn derica.server:app --port 8000
```

PowerShell:
```
Get-Content .env | Where-Object { $_ -match '^[A-Z_]+=' } | ForEach-Object { $k,$v = $_ -split '=',2; Set-Item "env:$k" $v }
uv run uvicorn derica.server:app --port 8000
```

Wait about 30 seconds for the model to warm up.

## 3. Check it is ready

Open http://localhost:8000/health

- `{"status":"ok","model":true}` means the model is connected.
- `"model":false` means the key was not loaded. Redo step 2.

## 4. Try the page

Open http://localhost:8000 in your browser.

1. Click **Try an example**. The prices should count up and settle in a few seconds.
2. Clear it. Paste: `abeg rice na seventy eight thousand for 50kg` and click **Read message**. Expect rice, 50 kg, ₦78,000.
3. Paste: `how far, I dey come`. Expect "Not a price. Nothing changed."
4. Paste: `how much be your rice?`. Expect a refusal, not a price.
5. Click **Make price card**. A picture should appear.

## 5. Things to try to break it

- Send an empty message.
- Paste a very long message.
- Click **Read message** twice quickly.
- Type a price with no item, like `92k`.

None of these should crash the page. Write down anything that does, with the exact words on screen.

## 6. Stop the app

Press `Ctrl+C` in the terminal.
