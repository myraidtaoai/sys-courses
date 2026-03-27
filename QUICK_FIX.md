# Quick Reference: Fixing "Azure OpenAI Configuration Error"

## Immediate Steps

### 1. Check if `.env.local` exists
```bash
ls -la .env.local
```

If it doesn't exist, create it:
```bash
cp .env.example .env.local
```

### 2. Edit `.env.local` with your credentials
```env
VITE_AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
VITE_AZURE_OPENAI_API_KEY=YOUR-32-CHAR-KEY-HERE
VITE_AZURE_OPENAI_DEPLOYMENT_NAME=YOUR-DEPLOYMENT-NAME
```

### 3. Find your credentials

**Endpoint & API Key:**
- Go to https://portal.azure.com
- Find your Azure OpenAI resource
- Click "Keys and Endpoint"
- Copy endpoint URL and KEY 1

**Deployment Name:**
- Go to https://oai.azure.com/
- Click "Deployments"
- Copy the exact deployment name (case-sensitive!)

### 4. Restart server
```bash
# Press Ctrl+C to stop
npm run dev
```

---

## Common Mistakes

| Problem | Wrong | Right |
|---------|-------|-------|
| Missing https:// | `myresource.openai.azure.com` | `https://myresource.openai.azure.com/` |
| Using model name | `gpt-4` | `gpt-4-deployment` (your deployment name) |
| Quotes in .env | `"https://..."` | `https://...` (no quotes) |
| Wrong file | `.env` | `.env.local` |
| Not restarting | Running old server | Stop and restart `npm run dev` |

---

## Error Messages Decoded

| Error | Meaning | Fix |
|-------|---------|-----|
| "not configured" | `.env.local` missing or empty | Create file with 3 variables |
| **"400" - Bad Request** | **Deployment name or format issue** | **See below for 400 error solutions** |
| "401/403" | Wrong API key | Check key in Azure Portal |
| "404" | Wrong deployment name | Verify exact name in Azure OpenAI Studio |
| "429" | Rate limit | Wait 60 seconds, try again |

---

## 🔴 400 Error: "Bad Request" - DETAILED SOLUTIONS

**This is the most common error.** Here's how to fix it:

### Check #1: Deployment Name
```bash
# WRONG - Using model name instead of deployment name:
VITE_AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
VITE_AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo

# RIGHT - Using deployment name:
VITE_AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-deployment
VITE_AZURE_OPENAI_DEPLOYMENT_NAME=my-gpt4
VITE_AZURE_OPENAI_DEPLOYMENT_NAME=phishing-sim
```

**To find correct deployment name:**
1. Go to https://oai.azure.com/
2. Click "Deployments" in left sidebar
3. Look at the "Deployment name" column
4. Copy EXACTLY as shown (case-sensitive!)

### Check #2: No Trailing Spaces
```bash
# WRONG:
VITE_AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4 

# RIGHT:
VITE_AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

Even one trailing space causes 400 error!

### Check #3: Endpoint Format
```bash
# Both work:
VITE_AZURE_OPENAI_ENDPOINT=https://myresource.openai.azure.com/
VITE_AZURE_OPENAI_ENDPOINT=https://myresource.openai.azure.com

# Wrong:
VITE_AZURE_OPENAI_ENDPOINT=myresource.openai.azure.com (missing https://)
VITE_AZURE_OPENAI_ENDPOINT=https://api.openai.com (wrong service!)
```

### Check #4: Verify in Azure

1. Go to https://oai.azure.com/
2. In left sidebar, click **"Deployments"**
3. Find your deployment
4. Check status is **"Succeeded"** (not "Creating" or "Failed")
5. Copy the exact **Deployment name** value
6. Paste into `.env.local`
7. Restart server: `npm run dev`

---

## Quick Test

After fixing configuration:

1. Open http://localhost:5173
2. Click "Live AI" tile (pink/purple gradient)
3. Should see chat interface with AI persona
4. Type "Hello" and press Enter
5. AI should respond within 5 seconds

---

## Still Not Working?

See detailed guides:
- **AZURE_AI_SETUP.md** - Complete setup instructions
- **TROUBLESHOOTING.md** - All error messages and solutions

Check browser console (F12 → Console) for specific error details.
