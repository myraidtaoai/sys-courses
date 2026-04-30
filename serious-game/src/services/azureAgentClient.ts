import type { AIResponse, AIScenarioContext } from './azureAgent'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3001'

export class AzureAgentClient {
  private sessionId: string
  private backendUrl: string

  constructor() {
    this.sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    this.backendUrl = BACKEND_URL
  }

  async checkConfigured(): Promise<boolean> {
    try {
      const response = await fetch(`${this.backendUrl}/api/configured`)
      const data = await response.json()
      return data.configured
    } catch {
      return false
    }
  }

  async initializeAgent(
    agentRole?: 'genuine' | 'attacker'
  ): Promise<{ roleDescription: string; scenario: AIScenarioContext }> {
    const response = await fetch(`${this.backendUrl}/api/agent/init`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: this.sessionId,
        agentRole
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to initialize agent')
    }

    return response.json()
  }

  async sendMessage(message: string): Promise<AIResponse> {
    const response = await fetch(`${this.backendUrl}/api/agent/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: this.sessionId,
        message
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to send message')
    }

    const data = await response.json()
    return data.response
  }

  async reset(): Promise<void> {
    try {
      await fetch(`${this.backendUrl}/api/agent/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId: this.sessionId })
      })
    } catch {
      // Ignore errors on reset
    }
  }
}

export const agentClient = new AzureAgentClient()
