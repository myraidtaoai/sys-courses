# Understanding the 400 Error & How to Fix It

## What Does "400 Bad Request" Mean?

The Azure OpenAI API is saying: "Your request is malformed or has wrong parameters."

This usually means ONE of these:
1. **Deployment name is incorrect** (most common)
2. **Extra spaces in configuration**
3. **Endpoint format is wrong**
4. **Model doesn't support the request parameters**

---

## The 99% Fix: Deployment Name

### The Problem

Most users copy their **model name** instead of their **deployment name**.

```
When you deployed a model in Azure OpenAI, you:
1. Chose a model: "gpt-4" or "gpt-35-turbo" (this is the MODEL NAME)
2. Named the deployment: "my-phishing-bot" (this is the DEPLOYMENT NAME)

You need to use the DEPLOYMENT NAME, not the MODEL NAME.
```

### How to Get the Right Deployment Name

**Option 1: Using Azure OpenAI Studio** (easiest)

1. Go to https://oai.azure.com/
2. Click **"Deployments"** in the left sidebar
3. You'll see a table with these columns:
   - Deployment name
   - Model
   - Model version
   - Status
4. Copy the value from the **"Deployment name"** column exactly as shown
5. Paste into `.env.local`
6. Restart server

**Option 2: Using Azure Portal**

1. Go to https://portal.azure.com
2. Find your Azure OpenAI resource
3. Click on it
4. Go to **Model deployments** (might be under "Deployments")
5. Find your deployment in the list
6. Copy its name

### Example

```
Azure OpenAI Studio shows:

Deployment name      | Model        | Status
---------------------|--------------|----------
gpt-4-phishing      | gpt-4        | Succeeded
research-bot        | gpt-35-turbo  | Succeeded
my-deployment       | gpt-4        | Succeeded

You should use: "gpt-4-phishing" or "research-bot" or "my-deployment"
NOT: "gpt-4" or "gpt-35-turbo"
```

---

## Step-by-Step Fix

### 1. Stop your dev server
```bash
# Press Ctrl+C if it's running
```

### 2. Open Azure OpenAI Studio
- Go to https://oai.azure.com/
- Log in with your Azure account

### 3. Click "Deployments"
- Left sidebar → Deployments
- You should see a list of your deployments

### 4. Find your deployment
- Look for status "Succeeded"
- Read the exact **Deployment name** value

### 5. Update `.env.local`
```bash
# Open the file
nano .env.local

# Change this line to match your deployment name:
VITE_AZURE_OPENAI_DEPLOYMENT_NAME=exact-deployment-name-from-step-4
```

### 6. Check for mistakes
```bash
# Make sure the file looks like:
VITE_AZURE_OPENAI_ENDPOINT=https://yourresource.openai.azure.com/
VITE_AZURE_OPENAI_API_KEY=your-32-character-key
VITE_AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-phishing

# NOT like:
VITE_AZURE_OPENAI_ENDPOINT=https://yourresource.openai.azure.com/ 
# ^ notice trailing space above - that's wrong!
```

### 7. Save and restart
```bash
# Save your .env.local
# Then restart server:
npm run dev
```

### 8. Test
- Open http://localhost:5173
- Click "Live AI" button
- Should start chat (no 400 error)

---

## Why This Happens

When you deploy a model in Azure OpenAI Studio, you're given 2 names:

```
Step 1: "Which model do you want to deploy?"
        Answer: GPT-4 (the MODEL NAME)

Step 2: "What should we name this deployment?"
        Answer: gpt-4-phishing (the DEPLOYMENT NAME)

Azure stores your deployment as:
{
  "model": "gpt-4",
  "deployment_name": "gpt-4-phishing"
}

The API endpoint uses the deployment_name:
/deployments/gpt-4-phishing/chat/completions

So we must use "gpt-4-phishing", not "gpt-4"!
```

---

## Troubleshooting the Troubleshooting

### I can't find the Deployments page

Try these URLs:
- https://oai.azure.com/ (main URL)
- https://oai.azure.com/deployments (direct to deployments)
- Azure Portal → Search "Azure OpenAI" → Click your resource → Deployments

### It says "Status: Creating"

Wait for status to become "Succeeded" before trying to use it.

### I don't see any deployments

You need to deploy a model first:
1. In Azure OpenAI Studio → **Deployments** → **Create new deployment**
2. Choose model (GPT-4 recommended)
3. Give it a deployment name
4. Set TPM limits
5. Click Create

### The deployment says "Failed"

Delete it and create a new one:
1. Click the deployment
2. Click Delete
3. Create a new deployment with same settings

---

## Prevention

To avoid this in the future:

1. **Write down your deployment name** when you create it
2. **Don't assume** the deployment name is the same as the model name
3. **Always copy-paste** from Azure OpenAI Studio (don't type manually)
4. **No trailing spaces** in `.env.local` - they matter!

---

## Still Stuck?

If the 400 error persists after trying the above:

1. **Check browser console** (F12 → Console)
   - Look for detailed error messages
   - Copy the exact error text

2. **Check server logs**
   - Terminal running `npm run dev`
   - Should show Azure API response

3. **Verify API key works**
   - Endpoint and key must be from the SAME Azure OpenAI resource
   - Try regenerating the key in Azure Portal

4. **Try a different model**
   - If you have multiple deployments, try another one
   - Verify its status is "Succeeded"

5. **See TROUBLESHOOTING.md** for other error types
