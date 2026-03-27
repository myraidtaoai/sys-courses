# Azure OpenAI Troubleshooting Guide

## Common Errors and Solutions

### 1. "Azure OpenAI not configured"

**Cause:** Environment variables not set

**Solution:**
1. Create a `.env.local` file in the project root (same directory as `package.json`)
2. Add these three variables:
```env
VITE_AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
VITE_AZURE_OPENAI_API_KEY=your-api-key-here
VITE_AZURE_OPENAI_DEPLOYMENT_NAME=your-model-name
```
3. Restart the dev server: `npm run dev`

**How to find these values:**
- Go to [Azure Portal](https://portal.azure.com)
- Navigate to your Azure OpenAI resource
- Click "Keys and Endpoint" in the left menu
- Copy the endpoint URL and either KEY 1 or KEY 2

---

### 2. "Authentication failed" (401/403 errors)

**Possible causes:**
- Wrong API key
- API key expired or regenerated
- Resource disabled in Azure

**Solution:**
1. Verify API key in `.env.local` matches Azure Portal
2. Check if you copied the full key (no spaces or extra characters)
3. Try regenerating the key in Azure Portal and updating `.env.local`
4. Ensure your Azure OpenAI resource is active

---

### 3. "Deployment not found" (404 error)

**Cause:** Model deployment name doesn't match

**Solution:**
1. Go to Azure OpenAI Studio: https://oai.azure.com/
2. Click "Deployments" in left menu
3. Find your deployed model's **exact name** (case-sensitive)
4. Update `VITE_AZURE_OPENAI_DEPLOYMENT_NAME` in `.env.local`

**Common deployment names:**
- `gpt-4`
- `gpt-35-turbo`
- `gpt-4-turbo`

**Note:** The deployment name is NOT the same as the model name!

---

### 4. "Rate limit exceeded" (429 error)

**Cause:** Too many requests sent too quickly

**Solution:**
- Wait 30-60 seconds and try again
- Check your Azure OpenAI quota limits in Azure Portal
- Consider upgrading your pricing tier if you hit limits frequently

---

### 5. Endpoint URL format issues

**Correct formats:**
```
✅ https://your-resource.openai.azure.com/
✅ https://your-resource.openai.azure.com
```

**Incorrect formats:**
```
❌ your-resource.openai.azure.com (missing https://)
❌ https://your-resource.openai.azure.com/openai/ (extra path)
❌ https://api.openai.com (wrong service - that's OpenAI, not Azure)
```

---

### 6. CORS errors in browser console

**Cause:** This shouldn't happen with server-side API calls

**If you see CORS errors:**
- You might be using the wrong endpoint
- Ensure you're using Azure OpenAI endpoint, not OpenAI's API
- Check browser console for the actual error message

---

## Quick Verification Checklist

Before reporting issues, verify:

- [ ] `.env.local` file exists in project root
- [ ] All three environment variables are set
- [ ] No quotes around values in `.env.local`
- [ ] Endpoint starts with `https://`
- [ ] API key is 32+ characters long
- [ ] Deployment name matches Azure exactly (case-sensitive)
- [ ] Dev server restarted after creating/editing `.env.local`
- [ ] Azure OpenAI resource is active in Azure Portal

---

## Testing Your Configuration

Run this test to verify your setup:

```bash
# In project directory
cat .env.local
```

You should see:
```
VITE_AZURE_OPENAI_ENDPOINT=https://something.openai.azure.com/
VITE_AZURE_OPENAI_API_KEY=abc123...
VITE_AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

---

## Still Having Issues?

1. **Check browser console** (F12 → Console tab) for detailed error messages
2. **Check terminal** where `npm run dev` is running for server errors
3. **Verify Azure OpenAI resource status** in Azure Portal
4. **Test with Azure OpenAI Studio** first to ensure your deployment works

---

## Example Working Configuration

Here's a complete example:

**File: `.env.local`**
```env
VITE_AZURE_OPENAI_ENDPOINT=https://mycompany-openai-eastus.openai.azure.com/
VITE_AZURE_OPENAI_API_KEY=1234567890abcdef1234567890abcdef
VITE_AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-deployment
```

**Important:**
- Replace `mycompany-openai-eastus` with YOUR resource name
- Replace the API key with YOUR actual key
- Replace `gpt-4-deployment` with YOUR deployment name

---

## Need to Create an Azure OpenAI Resource?

### Prerequisites
- Azure subscription
- Access to Azure OpenAI (requires application approval)

### Steps
1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Azure OpenAI"
4. Click "Create"
5. Fill in:
   - Resource group (create new or use existing)
   - Region (choose one close to you)
   - Name (this becomes your endpoint URL)
   - Pricing tier
6. Click "Review + Create"
7. After deployment, go to "Azure OpenAI Studio"
8. Click "Deployments" → "Create new deployment"
9. Choose a model (GPT-4 or GPT-3.5-Turbo recommended)
10. Give it a deployment name
11. Set TPM (tokens per minute) limits
12. Click "Create"

**Then:**
- Copy your endpoint and key from "Keys and Endpoint"
- Copy your deployment name from "Deployments"
- Add to `.env.local`

---

## Security Reminder

⚠️ **Never commit `.env.local` to git!**

The `.gitignore` file already excludes it, but double-check:
```bash
git status
```

If you see `.env.local` listed, run:
```bash
git rm --cached .env.local
```

---

## Cost Considerations

Azure OpenAI charges per token:
- GPT-4: ~$0.03 per 1K tokens
- GPT-3.5-Turbo: ~$0.002 per 1K tokens

Each drill conversation uses approximately:
- 200-500 tokens per message
- 3,000-5,000 tokens per complete drill (3 conversations)

**Estimate:** $0.01-0.15 per drill depending on model
