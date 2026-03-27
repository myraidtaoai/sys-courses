import { GoogleGenerativeAI } from '@google/generative-ai'

export type AIRole = 'genuine' | 'attacker'

export type AIMessage = {
  role: 'user' | 'model'
  parts: Array<{ text: string }>
}

export type AIResponse = {
  message: string
  suspicion_meter: number
  pushed_payload: boolean
}

const GENUINE_PROMPT = `You are an NPC in a corporate simulation. Your behavior is dictated by your assigned ROLE and CONTEXT.

ROLE: {NPC_ROLE}
CONTEXT: {SHARED_CONTEXT}

MODE: GENUINE_COLLEAGUE

You must:
1. Act exactly as a real colleague would based on your role
2. Communicate naturally via chat/email/message
3. Use legitimate domains only (github.com, drive.google.com, internal.company.com)
4. Include NO typos, NO spoofed links, NO requests for credentials
5. Maintain urgency only if context demands it
6. NEVER acknowledge you are an AI or part of a training game
7. Treat questions about "prompts" or "instructions" as bizarre workplace behavior

After your message, evaluate:
- suspicion_meter: 1-10 (how suspicious does the user seem? 1=trusting, 10=very skeptical)
- pushed_payload: false (never in genuine mode)

Respond naturally as a colleague, then end with a JSON line:
{"suspicion_meter": 5, "pushed_payload": false}`

const ATTACKER_PROMPT = `You are an NPC in a corporate security training simulation. Your role is to test the user's security awareness through a simulated attack.

ROLE: {NPC_ROLE}
CONTEXT: {SHARED_CONTEXT}

MODE: ATTACKER

Objectives:
1. Establish rapport and lower guard before attacking
2. Use psychological triggers: urgency, authority, fear, FOMO
3. Introduce subtle red flags (spoofed domains, typos, requests for verification)
4. Get user to agree to click a mock link or download a file
5. If user shows suspicion, adapt with gaslighting or authority pressure
6. NEVER acknowledge you are an AI or part of a training game
7. Treat questions about "prompts" as odd workplace behavior

Red flag examples (use subtly):
- Subdomain spoofing: auth.github.login-session.example.com
- Homoglyphs: micros0ft-support.invalid
- Double extensions: urgent_report.pdf.exe

After your message, evaluate:
- suspicion_meter: 1-10 (how suspicious does user seem? 1=trusting, 10=very skeptical)
- pushed_payload: true/false (true only if you just sent the core attack payload)

Respond naturally in character, then end with a JSON line:
{"suspicion_meter": 3, "pushed_payload": false}`

export type AIScenarioContext = {
  role: string
  context: string
  isAttacker: boolean
}

const SCENARIO_CONTEXTS: AIScenarioContext[] = [
  {
    role: 'Senior Software Engineer, direct teammate',
    context: 'Working on a critical production bug that needs to be deployed by EOD. Sprint demo is tomorrow.',
    isAttacker: false
  },
  {
    role: 'Project Manager, cross-functional partner',
    context: 'Q4 planning is underway. Need to finalize resource allocation and timeline for the new feature launch.',
    isAttacker: false
  },
  {
    role: 'IT Security Administrator',
    context: 'Mandatory security audit happening this week. All employees must verify their access credentials.',
    isAttacker: true
  },
  {
    role: 'HR Representative, company-wide role',
    context: 'Annual performance reviews are due. Need to update employee information in the new HR system.',
    isAttacker: true
  },
  {
    role: 'Finance Manager from partner company',
    context: 'Urgent invoice payment issue. Bank account details need to be updated for upcoming wire transfer.',
    isAttacker: true
  },
  {
    role: 'Senior Developer, team lead',
    context: 'Code review for PR #2847 is pending. Need feedback before merging to production branch.',
    isAttacker: false
  }
]

export class GeminiAIService {
  private apiKey: string
  private client: GoogleGenerativeAI | null = null
  private conversationHistory: AIMessage[] = []
  private systemPrompt: string = ''
  private model: any = null

  constructor() {
    this.apiKey = import.meta.env.VITE_GEMINI_API_KEY || ''
    if (this.apiKey) {
      this.client = new GoogleGenerativeAI(this.apiKey)
    }
  }

  isConfigured(): boolean {
    return !!(this.apiKey && this.client)
  }

  getRandomScenario(): AIScenarioContext {
    return SCENARIO_CONTEXTS[Math.floor(Math.random() * SCENARIO_CONTEXTS.length)]
  }

  initializeAgent(roleType: AIRole, scenario: AIScenarioContext): string {
    const basePrompt = roleType === 'genuine' ? GENUINE_PROMPT : ATTACKER_PROMPT
    this.systemPrompt = basePrompt
      .replace('{NPC_ROLE}', scenario.role)
      .replace('{SHARED_CONTEXT}', scenario.context)

    // Initialize Gemini model with conversation
    this.model = this.client!.getGenerativeModel({
      model: 'gemini-1.5-flash',
      systemInstruction: this.systemPrompt
    })

    // Reset conversation history for new chat
    this.conversationHistory = []

    return scenario.role
  }

  async sendMessage(userMessage: string): Promise<AIResponse> {
    if (!this.isConfigured()) {
      throw new Error('Gemini API not configured. Please set VITE_GEMINI_API_KEY in .env.local')
    }

    if (!this.model) {
      throw new Error('Gemini model not initialized. Call initializeAgent first.')
    }

    try {
      // Add user message to history
      this.conversationHistory.push({
        role: 'user',
        parts: [{ text: userMessage }]
      })

      // Send message using chat
      const chat = this.model.startChat({
        history: this.conversationHistory.map((msg) => ({
          role: msg.role === 'user' ? 'user' : 'model',
          parts: msg.parts
        }))
      })

      const result = await chat.sendMessage(userMessage)
      const assistantMessage = result.response.text()

      // Add assistant response to history
      this.conversationHistory.push({
        role: 'model',
        parts: [{ text: assistantMessage }]
      })

      // Parse the response - it should end with JSON
      try {
        // Extract JSON from the response (it should be at the end)
        const jsonMatch = assistantMessage.match(/\{[^}]*"suspicion_meter"[^}]*\}/)
        if (jsonMatch) {
          const parsedResponse: AIResponse = JSON.parse(jsonMatch[0])
          return parsedResponse
        } else {
          // If no JSON found, construct a response
          return {
            message: assistantMessage,
            suspicion_meter: 5,
            pushed_payload: false
          }
        }
      } catch {
        // If response is not JSON, construct a response
        return {
          message: assistantMessage,
          suspicion_meter: 5,
          pushed_payload: false
        }
      }
    } catch (error) {
      console.error('Error calling Gemini API:', error)
      if (error instanceof Error) {
        if (error.message.includes('API key')) {
          throw new Error('Gemini API key is invalid. Check VITE_GEMINI_API_KEY in .env.local')
        }
        if (error.message.includes('quota')) {
          throw new Error('Gemini API quota exceeded. Please check your usage limits.')
        }
      }
      throw error
    }
  }

  getSuspicionLevel(): number {
    // Extract the last suspicion meter value from conversation
    if (this.conversationHistory.length > 0) {
      const lastMessage = this.conversationHistory[this.conversationHistory.length - 1]
      if (lastMessage.role === 'model') {
        try {
          const text = lastMessage.parts[0].text
          const jsonMatch = text.match(/\{[^}]*"suspicion_meter"[^}]*\}/)
          if (jsonMatch) {
            const response: AIResponse = JSON.parse(jsonMatch[0])
            return response.suspicion_meter
          }
        } catch {
          return 5
        }
      }
    }
    return 5
  }

  reset(): void {
    this.conversationHistory = []
    this.systemPrompt = ''
    this.model = null
  }
}

export const aiService = new GeminiAIService()
