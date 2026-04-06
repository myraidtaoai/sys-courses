import express, { Request, Response } from 'express'
import cors from 'cors'
import dotenv from 'dotenv'
import { AzureAgentService, type AIResponse, type AzureOpenAIConfig } from './src/services/azureAgent'

dotenv.config({ path: '.env.local' })

const app = express()
const port = process.env.VITE_BACKEND_PORT || 3001

// Middleware
app.use(cors())
app.use(express.json())

// Initialize Azure OpenAI service using .env.local values
const azureOpenAIConfig: AzureOpenAIConfig = {
  endpoint: process.env.AZURE_OPENAI_ENDPOINT || process.env.endpoint || '',
  apiKey: process.env.AZURE_OPENAI_API_KEY || process.env.apiKey || '',
  deployment:
    process.env.AZURE_OPENAI_DEPLOYMENT || process.env.deployment || process.env.modelName || '',
  apiVersion: process.env.AZURE_OPENAI_API_VERSION || process.env.apiVersion || '2024-04-01-preview',
  attackerPromptPath: process.env.ATTACKER_PROMPT_PATH || 'prompts/attacker_prompt.md',
  genuinePromptPath: process.env.GENUINE_PROMPT_PATH || 'prompts/genuine_prompt.md'
}
const azureAgent = new AzureAgentService(azureOpenAIConfig)

// Store active agents per session
const sessions = new Map<string, { agent: AzureAgentService; roleType: 'genuine' | 'attacker' }>()

// Health check
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', backend: 'azure-agent' })
})

// Check configuration
app.get('/api/configured', (req: Request, res: Response) => {
  res.json({ configured: azureAgent.isConfigured() })
})

// Initialize agent for a session
app.post('/api/agent/init', (req: Request, res: Response) => {
  try {
    const { sessionId, agentRole } = req.body

    if (!sessionId) {
      return res.status(400).json({ error: 'Missing sessionId' })
    }

    const selectedRole: 'genuine' | 'attacker' =
      agentRole === 'genuine' || agentRole === 'attacker'
        ? agentRole
        : Math.random() > 0.5
          ? 'attacker'
          : 'genuine'

    // Create new agent instance for this session
    const sessionAgent = new AzureAgentService(azureOpenAIConfig)

    if (!sessionAgent.isConfigured()) {
      return res.status(500).json({ error: 'Azure Agent not configured' })
    }

    // Get random scenario
    const scenario = sessionAgent.getRandomScenario(selectedRole)

    // Initialize agent with role and scenario
    const roleDescription = sessionAgent.initializeAgent(selectedRole, scenario)

    // Store session
    sessions.set(sessionId, { agent: sessionAgent, roleType: selectedRole })

    res.json({
      success: true,
      roleType: selectedRole,
      roleDescription,
      scenario
    })
  } catch (error) {
    console.error('Error initializing agent:', error)
    res.status(500).json({ error: error instanceof Error ? error.message : 'Unknown error' })
  }
})

// Send message to agent
app.post('/api/agent/message', async (req: Request, res: Response) => {
  try {
    const { sessionId, message } = req.body

    if (!sessionId || !message) {
      return res.status(400).json({ error: 'Missing sessionId or message' })
    }

    const session = sessions.get(sessionId)
    if (!session) {
      return res.status(404).json({ error: 'Session not found' })
    }

    const response: AIResponse = await session.agent.sendMessage(message)

    res.json({
      success: true,
      response
    })
  } catch (error) {
    console.error('Error sending message:', error)
    res.status(500).json({ error: error instanceof Error ? error.message : 'Unknown error' })
  }
})

// Reset session
app.post('/api/agent/reset', (req: Request, res: Response) => {
  try {
    const { sessionId } = req.body

    if (!sessionId) {
      return res.status(400).json({ error: 'Missing sessionId' })
    }

    const session = sessions.get(sessionId)
    if (session) {
      session.agent.reset()
      sessions.delete(sessionId)
    }

    res.json({ success: true })
  } catch (error) {
    console.error('Error resetting session:', error)
    res.status(500).json({ error: error instanceof Error ? error.message : 'Unknown error' })
  }
})

// Start server
app.listen(port, () => {
  console.log(`Azure Agent backend running on http://localhost:${port}`)
  console.log(`Azure OpenAI: ${azureAgent.isConfigured() ? 'configured' : 'not configured'}`)
})
