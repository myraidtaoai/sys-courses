# Gemini API Setup Guide

This guide shows how to set up Google Gemini API for the phishing simulation.

## Overview

The app now uses **Google's Gemini API** instead of Azure OpenAI. Gemini is free for personal use with rate limits.

- **Cost:** Free (5 requests per minute, 1,500 requests per day)
- **Setup time:** 2 minutes
- **Model:** Gemini 1.5 Flash (fast and capable)

## Step 1: Create a Google Account

If you don't have one:
1. Go to https://accounts.google.com
2. Click "Create account"
3. Follow the prompts

## Step 2: Get Your API Key

### Option 1: Quick Setup (Recommended)

1. Go to **https://aistudio.google.com/**
2. Sign in with your Google account
3. Click **"Get API Key"** in the left sidebar
4. Click **"Create API Key"** button
5. Copy the key from the dialog box
6. Paste it into `.env.local`

### Option 2: Google Cloud Console

1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable "Generative Language API"
4. Create an API key
5. Use the key in `.env.local`

## Step 3: Configure `.env.local`

Create a `.env.local` file in the project root with:

```
VITE_GEMINI_API_KEY=your-key-here
```

Replace `your-key-here` with the actual key from Step 2.

### Example:
```
VITE_GEMINI_API_KEY=AIzaSyC1234567890abcdefghijklmnopqrst
```

## Step 4: Start the App

```bash
npm run dev
```

Open http://localhost:5175 and click **"Live AI"** button.

## Verify It Works

1. Open the app
2. Click "Live AI" button
3. See a chat interface with a role description
4. Type a response
5. AI should reply (give it a few seconds)
6. After 4-5 exchanges, decide if it's genuine or attacking

## Troubleshooting

### Error: "not configured"
**Problem:** API key not set or wrong variable name

**Solution:**
```bash
# Check that .env.local exists in the project root (same level as package.json)
ls -la .env.local

# File should contain:
# VITE_GEMINI_API_KEY=your-key-here
```

### Error: "API key is invalid"
**Problem:** Key is expired, wrong, or doesn't have access

**Solution:**
1. Get a new key: https://aistudio.google.com/ → Get API Key
2. Copy the entire key (including all characters)
3. Update `.env.local`
4. Restart: Press Ctrl+C, then `npm run dev`

### Error: "quota exceeded"
**Problem:** Free tier rate limit hit (5 req/min, 1,500 req/day)

**Solution:**
- Wait 24 hours and quota resets
- OR upgrade to paid tier: https://cloud.google.com/generative-ai/pricing

### Chat not responding
**Problem:** Network issue or API overloaded

**Solution:**
1. Check internet connection
2. Wait a few seconds and try again
3. Restart dev server (Ctrl+C, `npm run dev`)
4. Check browser console (F12) for error details

### How to view detailed errors

1. Open http://localhost:5175
2. Press F12 to open Developer Tools
3. Click "Console" tab
4. Try using Live AI again
5. Look for error messages in red
6. Copy the error and check solution below

## API Details

| Parameter | Value |
|-----------|-------|
| **Provider** | Google AI Studio |
| **Model** | gemini-1.5-flash |
| **Free tier limit** | 5 requests/min, 1,500/day |
| **API Key location** | https://aistudio.google.com/ |
| **Environment var** | VITE_GEMINI_API_KEY |

## Upgrade to Paid (Optional)

If you hit the free tier limit:

1. Go to https://console.cloud.google.com/
2. Enable billing
3. Go to Generative AI → Quotas
4. Increase your quota

After that, you get higher limits:
- Up to 1,500 requests per minute
- Pay per token usage (very cheap)

## Security Notes

- **Never commit `.env.local`** to git (it's in `.gitignore`)
- **Keep your API key secret** (like a password)
- If you accidentally commit it, regenerate immediately
- Don't share your key in chat, forums, or screenshots

## Pre-scripted Chat (No Setup Needed)

Even without API key, you can use:
- Pre-scripted chat with 8 scenarios (pick difficulty level)
- This doesn't require any setup or API credentials
- Good for testing without internet access

## Next Steps

1. [x] Get API key from https://aistudio.google.com/
2. [x] Create `.env.local` file
3. [x] Paste key as `VITE_GEMINI_API_KEY=...`
4. [x] Run `npm run dev`
5. [x] Click "Live AI" and start chat

## Need Help?

- **Setup issues:** Check the troubleshooting table above
- **API key not working:** Regenerate at https://aistudio.google.com/
- **Rate limit hit:** Wait or upgrade to paid
- **Other issues:** Check browser console (F12) for error details

## Reference

- Gemini AI Studio: https://aistudio.google.com/
- Gemini API docs: https://ai.google.dev/
- Google Cloud pricing: https://cloud.google.com/generative-ai/pricing
