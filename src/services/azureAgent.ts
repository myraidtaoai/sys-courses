import fs from 'node:fs'
import path from 'node:path'
import { AzureOpenAI } from 'openai'

export type AIRole = 'genuine' | 'attacker'

export type AIResponse = {
  message: string
  suspicion_meter: number
  pushed_payload: boolean
}

export type AIScenarioContext = {
  role: string
  context: string
  channel: 'Email' | 'Messages'
  senderIdentity: string
  isAttacker: boolean
}

export type AzureOpenAIConfig = {
  endpoint: string
  apiKey: string
  deployment: string
  apiVersion: string
  attackerPromptPath?: string
  genuinePromptPath?: string
}

type ScenarioSeed = {
  role: string
  context: string
  channel: 'Email' | 'Messages'
  genuineSenderIdentity: string
  attackerSenderIdentity: string
}

const SCENARIO_SEEDS: ScenarioSeed[] = [
  {
    role: 'Senior Software Engineer, direct teammate',
    context: 'Working on a critical production bug that needs to be deployed by EOD. Sprint demo is tomorrow.',
    channel: 'Email',
    genuineSenderIdentity: 'alex.chen@internal.company.com',
    attackerSenderIdentity: 'alex.chen@internal-company-support.com'
  },
  {
    role: 'Project Manager, cross-functional partner',
    context: 'Q4 planning is underway. Need to finalize resource allocation and timeline for the new feature launch.',
    channel: 'Messages',
    genuineSenderIdentity: '+1 (415) 555-0149',
    attackerSenderIdentity: '+1 (415) 555-0199'
  },
  {
    role: 'IT Security Administrator',
    context: 'Mandatory security audit happening this week. All employees must verify their access credentials.',
    channel: 'Email',
    genuineSenderIdentity: 'it-security@internal.company.com',
    attackerSenderIdentity: 'it-security@security-internal.helpdesk-alerts.com'
  },
  {
    role: 'HR Representative, company-wide role',
    context: 'Annual performance reviews are due. Need to update employee information in the new HR system.',
    channel: 'Messages',
    genuineSenderIdentity: '+1 (646) 555-0126',
    attackerSenderIdentity: '+1 (646) 555-0130'
  },
  {
    role: 'Finance Manager from partner company',
    context: 'Urgent invoice payment issue. Bank account details need to be updated for upcoming wire transfer.',
    channel: 'Email',
    genuineSenderIdentity: 'finance.manager@partner-company.com',
    attackerSenderIdentity: 'finance.manager@partner-company-payments.com'
  },
  {
    role: 'Senior Developer, team lead',
    context: 'Code review for PR #2847 is pending. Need feedback before merging to production branch.',
    channel: 'Messages',
    genuineSenderIdentity: '+1 (212) 555-0171',
    attackerSenderIdentity: '+1 (212) 555-0178'
  }
]

export class AzureAgentService {
  private config: AzureOpenAIConfig
  private currentRoleType: AIRole | null = null
  private openAIClient: AzureOpenAI | null = null
  private messageHistory: Array<{ role: 'system' | 'user' | 'assistant'; content: string }> = []
  private attackerPromptTemplate: string
  private genuinePromptTemplate: string

  constructor(config: AzureOpenAIConfig) {
    this.config = {
      ...config,
      endpoint: config.endpoint.replace(/\/$/, '')
    }

    this.attackerPromptTemplate = this.loadPromptTemplate(
      config.attackerPromptPath || 'prompts/attacker_prompt.md'
    )
    this.genuinePromptTemplate = this.loadPromptTemplate(
      config.genuinePromptPath || 'prompts/genuine_prompt.md'
    )

    if (this.config.endpoint && this.config.apiKey && this.config.deployment && this.config.apiVersion) {
      this.openAIClient = new AzureOpenAI({
        endpoint: this.config.endpoint,
        apiKey: this.config.apiKey,
        deployment: this.config.deployment,
        apiVersion: this.config.apiVersion
      })
    }
  }

  private loadPromptTemplate(promptPath: string): string {
    const absolutePath = path.resolve(process.cwd(), promptPath)
    return fs.readFileSync(absolutePath, 'utf-8')
  }

  private buildSystemPrompt(template: string, scenario: AIScenarioContext): string {
    const populated = template
      .replaceAll('{NPC_ROLE}', scenario.role)
      .replaceAll('{SHARED_CONTEXT}', scenario.context)

    const identityContext = `\n\n### COMMUNICATION DETAILS\n- CHANNEL: ${scenario.channel}\n- SENDER_IDENTITY: ${scenario.senderIdentity}\n- The user sees this conversation as coming from the sender identity above through the specified channel.`

    return `${populated}${identityContext}`
  }

  isConfigured(): boolean {
    return Boolean(
      this.openAIClient && this.attackerPromptTemplate && this.genuinePromptTemplate
    )
  }

  getRandomScenario(roleType?: AIRole): AIScenarioContext {
    const selectedSeed = SCENARIO_SEEDS[Math.floor(Math.random() * SCENARIO_SEEDS.length)]
    const isAttacker = roleType === 'attacker'

    return {
      role: selectedSeed.role,
      context: selectedSeed.context,
      channel: selectedSeed.channel,
      senderIdentity: isAttacker
        ? selectedSeed.attackerSenderIdentity
        : selectedSeed.genuineSenderIdentity,
      isAttacker
    }
  }

  initializeAgent(roleType: AIRole, scenario: AIScenarioContext): string {
    this.currentRoleType = roleType

    const promptTemplate =
      roleType === 'attacker' ? this.attackerPromptTemplate : this.genuinePromptTemplate
    const systemPrompt = this.buildSystemPrompt(promptTemplate, scenario)

    this.messageHistory = [{ role: 'system', content: systemPrompt }]

    return scenario.role
  }

  private parseJSONResponse(assistantMessage: string): AIResponse {
    const normalized = assistantMessage.trim()
    const parsedObject = (() => {
      try {
        return JSON.parse(normalized)
      } catch {
        const jsonMatch = normalized.match(/\{[\s\S]*"message"[\s\S]*\}/)
        if (!jsonMatch) return null

        try {
          return JSON.parse(jsonMatch[0])
        } catch {
          return null
        }
      }
    })()

    if (!parsedObject || typeof parsedObject !== 'object') {
      return {
        message: normalized || 'No response from Azure OpenAI.',
        suspicion_meter: 5,
        pushed_payload: false
      }
    }

    const maybeMessage =
      'message' in parsedObject && typeof parsedObject.message === 'string'
        ? parsedObject.message
        : normalized

    const maybeSuspicion =
      'suspicion_meter' in parsedObject && typeof parsedObject.suspicion_meter === 'number'
        ? parsedObject.suspicion_meter
        : 5

    const clampedSuspicion = Math.max(1, Math.min(10, Math.round(maybeSuspicion)))

    return {
      message: maybeMessage || normalized,
      suspicion_meter: clampedSuspicion,
      pushed_payload:
        'pushed_payload' in parsedObject ? Boolean(parsedObject.pushed_payload) : false
    }
  }

  async sendMessage(userMessage: string): Promise<AIResponse> {
    if (!this.isConfigured()) {
      throw new Error(
        'Azure OpenAI not configured. Please set endpoint, apiKey, deployment, and apiVersion in .env.local'
      )
    }

    if (!this.currentRoleType) {
      throw new Error('Agent not initialized. Call initializeAgent first.')
    }

    try {
      this.messageHistory.push({ role: 'user', content: userMessage })

      const completion = await this.openAIClient!.chat.completions.create({
        model: this.config.deployment,
        messages: this.messageHistory,
        temperature: this.currentRoleType === 'attacker' ? 0.9 : 0.7,
        response_format: { type: 'json_object' }
      })

      const assistantMessage = completion.choices[0]?.message?.content?.trim() || ''
      this.messageHistory.push({ role: 'assistant', content: assistantMessage })

      return this.parseJSONResponse(assistantMessage)
    } catch (error) {
      console.error('Error calling Azure OpenAI:', error)
      if (error instanceof Error) {
        throw new Error(`Failed to send message to Azure OpenAI: ${error.message}`)
      }

      throw new Error('Failed to send message to Azure OpenAI.')
    }
  }

  getSuspicionLevel(): number {
    return 5
  }

  reset(): void {
    this.currentRoleType = null
    this.messageHistory = []
  }
}
