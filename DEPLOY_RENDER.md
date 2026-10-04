# Deploy Derica on Render

About 10 minutes. The repo already has a `render.yaml`, so Render sets most things up for you.

## Before you start

1. **Rotate your Tinker key.** The old one appeared in a session transcript. Create a new one in your Tinker account, in the same account that trained the model. The model path in `runs/train_run_v2.json` only works with keys from that account.
2. Make sure the latest code is on GitHub: https://github.com/JUICEWRLD998/Derica (branch `main`).
3. You do not need the OpenRouter key. Do not put it on Render.

## Steps

1. Go to https://render.com and sign in with GitHub.
2. Click **New**, then **Blueprint**.
3. Pick the repo `JUICEWRLD998/Derica`. If it is not listed, click **Configure account** and give Render access to it.
4. Render reads `render.yaml` and shows one web service called `derica`. Click **Apply**.
5. When it asks for `TINKER_API_KEY`, paste the **new** key. (Later: service, **Environment** tab.)
6. Wait for the deploy to finish. The build takes a few minutes.
7. Open `https://<your-service-name>.onrender.com/health`.
   - `{"status":"ok","model":true}` means it works.
   - `"model":false` means the key is missing or empty. Fix it in the Environment tab and redeploy.
8. Open the main URL. Click **Try an example**. You should see ₦1,600, ₦3,150 and ₦13,650 in a few seconds.

## Things to know

- **Free plan sleeps** after 15 minutes of no visits. The first visit after sleep takes about a minute. Open the page once before any demo or recording.
- **First model call is slow** (about 20 seconds). After that it takes about 2 seconds. The app warms the model when it starts.
- **Your stall prices** are saved in the visitor's own browser. Nothing is stored on the server.
- **Page looks old after an update?** Press `Ctrl + Shift + R` to refresh without the cache.

## When something fails

| What you see | Fix |
|---|---|
| Build fails | Open the **Logs** tab. Check that `PYTHON_VERSION` is `3.12.7` in the Environment tab |
| `"model":false` on `/health` | Set `TINKER_API_KEY`, then **Manual Deploy**, **Deploy latest commit** |
| The page loads but reading a message fails | Check the key belongs to the account that trained the model. Check the Tinker credit balance |
| A 502 error right after deploy | Wait a minute. The service is still starting |

## After it works

Paste the URL into the README, `CLAIMS.md` and the post. Then do the phone check in `strategy/PHASE5_KIT.md`, section 2.
