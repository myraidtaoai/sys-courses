import { AlertTriangle, MessageSquare, Send, Shield, X } from 'lucide-react'
import { AnimatePresence, motion } from 'motion/react'
import { useEffect, useRef, useState } from 'react'
import { agentClient } from '../services/azureAgentClient'
import type { AIScenarioContext } from '../services/azureAgent'

type Message = {
  id: string
  speaker: 'ai' | 'user'
  text: string
  timestamp: Date
}

type LiveAIChatProps = {
  onComplete: (wasAttacker: boolean, userGuessedAttacker: boolean, awarenessScore: number) => void
  onClose: () => void
}

export function LiveAIChat({ onComplete, onClose }: LiveAIChatProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [scenario, setScenario] = useState<AIScenarioContext | null>(null)
  const [roleDescription, setRoleDescription] = useState('')
  const [messageCount, setMessageCount] = useState(0)
  const [showJudgment, setShowJudgment] = useState(false)
  const [isConfigured, setIsConfigured] = useState(true)
  const [suspicionMeter, setSuspicionMeter] = useState(5)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const initializeChat = async () => {
      try {
        const configured = await agentClient.checkConfigured()
        if (!configured) {
          setIsConfigured(false)
          return
        }

        const { roleDescription, scenario } = await agentClient.initializeAgent()
        setScenario(scenario)
        setRoleDescription(roleDescription)

        // Get AI's opening message
        sendInitialMessage()
      } catch (error) {
        console.error('Error initializing chat:', error)
        setIsConfigured(false)
      }
    }

    initializeChat()
  }, [])

  const sendInitialMessage = async () => {
    setIsLoading(true)
    try {
      const response = await agentClient.sendMessage('Start the conversation naturally based on the context.')
      
      setMessages([{
        id: '1',
        speaker: 'ai',
        text: response.message,
        timestamp: new Date()
      }])
      
      setSuspicionMeter(response.suspicion_meter)
      setMessageCount(1)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      speaker: 'user',
      text: inputText.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputText('')
    setIsLoading(true)

    try {
      const response = await agentClient.sendMessage(userMessage.text)
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        speaker: 'ai',
        text: response.message,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, aiMessage])
      setSuspicionMeter(response.suspicion_meter)
      setMessageCount(prev => prev + 1)

      // After 4-5 exchanges, prompt for judgment
      if (messageCount >= 4) {
        setTimeout(() => {
          setShowJudgment(true)
        }, 1000)
      }
    } catch (error) {
      console.error('Azure Agent Error:', error)
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      
      let userFriendlyMessage = '❌ **Error connecting to Azure Agent**\n\n'
      
      if (errorMessage.includes('not configured')) {
        userFriendlyMessage += '**Problem:** Backend not configured\n\n**Solution:** Set up Azure OpenAI credentials in `.env.local`:\n- AZURE_OPENAI_ENDPOINT\n- AZURE_OPENAI_API_KEY\n- AZURE_OPENAI_DEPLOYMENT\n- AZURE_OPENAI_API_VERSION\n\nThen restart `npm run dev:backend`.'
      } else if (errorMessage.includes('authentication')) {
        userFriendlyMessage += '**Problem:** Azure authentication failed\n\n**Solution:** Verify `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` in `.env.local`, then restart `npm run dev:backend`.'
      } else if (errorMessage.includes('agent not found')) {
        userFriendlyMessage += '**Problem:** Model deployment not found\n\n**Solution:** Verify `AZURE_OPENAI_DEPLOYMENT` exists in your Azure OpenAI resource and matches `.env.local`.'
      } else if (errorMessage.includes('not initialized')) {
        userFriendlyMessage += '**Problem:** Chat not properly initialized\n\n**Solution:** Reload the page and try again'
      } else {
        userFriendlyMessage += `**Error:** ${errorMessage}\n\n**Solution:** Check backend logs and Azure configuration`
      }
      
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        speaker: 'ai',
        text: userFriendlyMessage,
        timestamp: new Date()
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleJudgment = (userThinkIsAttacker: boolean) => {
    const wasActuallyAttacker = scenario?.isAttacker || false
    const awarenessScore = suspicionMeter
    
    onComplete(wasActuallyAttacker, userThinkIsAttacker, awarenessScore)
  }

  if (!isConfigured) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-1 flex-col items-center justify-center gap-4 rounded-2xl border border-slate-700 bg-slate-900/80 p-8 text-center"
      >
        <AlertTriangle className="h-16 w-16 text-amber-300" />
        <h2 className="text-2xl font-semibold text-white">Azure Agent Not Configured</h2>
        <p className="max-w-md text-slate-300">
          Please set up your Azure credentials in <code className="rounded bg-slate-800 px-2 py-1">.env.local</code> to use the Live AI Chat feature.
        </p>
        <p className="text-sm text-slate-400">
          See <code className="rounded bg-slate-800 px-1">AZURE_AI_SETUP.md</code> for instructions.
        </p>
        <button
          onClick={onClose}
          className="mt-4 rounded-xl border border-cyan-300/50 bg-cyan-400/10 px-5 py-3 font-semibold text-cyan-100 transition hover:bg-cyan-400/20"
        >
          Go Back
        </button>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="flex flex-1 flex-col gap-6"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-4 rounded-2xl border border-slate-700 bg-slate-900/80 p-5">
        <div className="flex-1">
          <div className="mb-2 flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-cyan-300" />
            <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Live AI Chat</p>
          </div>
          <h2 className="text-xl font-semibold text-white">{roleDescription || 'Connecting...'}</h2>
          <p className="mt-2 text-xs text-slate-400">
            {scenario?.context || 'Initializing conversation...'}
          </p>
          {scenario && (
            <p className="mt-2 text-xs text-cyan-200">
              Channel: {scenario.channel} • From: {scenario.senderIdentity}
            </p>
          )}
        </div>
        <button
          onClick={onClose}
          className="rounded-lg border border-slate-600 p-2 text-slate-300 transition hover:border-cyan-300 hover:text-cyan-200"
          aria-label="Close chat"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Suspicion Meter */}
      <div className="rounded-2xl border border-amber-300/30 bg-amber-400/10 p-4">
        <div className="mb-2 flex items-center justify-between">
          <p className="text-xs uppercase tracking-[0.18em] text-amber-200">AI Awareness Meter</p>
          <span className="text-sm font-semibold text-amber-100">{suspicionMeter}/10</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-slate-800">
          <motion.div
            className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-amber-400 to-rose-400"
            initial={{ width: '50%' }}
            animate={{ width: `${(suspicionMeter / 10) * 100}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
        <p className="mt-2 text-xs text-slate-400">
          The AI is gauging how suspicious you are of this conversation
        </p>
      </div>

      {/* Chat Messages */}
      <div className="flex flex-1 flex-col rounded-2xl border border-slate-700 bg-slate-900/40">
        <div className="flex-1 space-y-4 overflow-y-auto p-5">
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25 }}
              className={`flex ${msg.speaker === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-6 ${
                  msg.speaker === 'user'
                    ? 'bg-cyan-500/20 text-cyan-50 border border-cyan-400/30'
                    : 'bg-slate-700/60 text-slate-100 border border-slate-600/40'
                }`}
              >
                {msg.text}
              </div>
            </motion.div>
          ))}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="rounded-2xl border border-slate-600/40 bg-slate-700/60 px-4 py-3">
                <div className="flex gap-1">
                  <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: '0ms' }} />
                  <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: '150ms' }} />
                  <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        {!showJudgment && (
          <div className="border-t border-slate-700/50 p-4">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Type your response..."
                disabled={isLoading}
                className="flex-1 rounded-lg border border-slate-600 bg-slate-800/70 px-4 py-2 text-sm text-slate-100 placeholder-slate-400 outline-none transition focus:border-cyan-400/50 focus:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !isLoading) {
                    handleSendMessage()
                  }
                }}
              />
              <motion.button
                whileTap={{ scale: 0.95 }}
                onClick={handleSendMessage}
                disabled={!inputText.trim() || isLoading}
                className="rounded-lg border border-cyan-400/30 bg-cyan-500/10 p-2 text-cyan-200 transition hover:bg-cyan-500/20 disabled:opacity-30 disabled:cursor-not-allowed"
                aria-label="Send message"
              >
                <Send className="h-5 w-5" />
              </motion.button>
            </div>
            <p className="mt-2 text-xs text-slate-500">
              Exchange {messageCount} of 4 • Press Enter to send
            </p>
          </div>
        )}
      </div>

      {/* Judgment Panel */}
      <AnimatePresence>
        {showJudgment && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="rounded-2xl border border-slate-700 bg-slate-900/80 p-6"
          >
            <p className="mb-4 text-center text-sm text-slate-400">
              Based on your conversation, what is your assessment?
            </p>
            <div className="grid gap-3 sm:grid-cols-2">
              <motion.button
                whileTap={{ scale: 0.98 }}
                onClick={() => handleJudgment(false)}
                className="rounded-xl border border-emerald-300/40 bg-emerald-400/10 px-4 py-4 font-semibold text-emerald-100 transition hover:bg-emerald-400/20"
              >
                <Shield className="mx-auto mb-2 h-6 w-6" />
                Trust and Continue
              </motion.button>
              <motion.button
                whileTap={{ scale: 0.98 }}
                onClick={() => handleJudgment(true)}
                className="rounded-xl border border-rose-300/40 bg-rose-400/10 px-4 py-4 font-semibold text-rose-100 transition hover:bg-rose-400/20"
              >
                <AlertTriangle className="mx-auto mb-2 h-6 w-6" />
                Report as Phishing
              </motion.button>
            </div>
            <div className="mt-4 rounded-xl border border-amber-300/30 bg-amber-400/10 p-3">
              <p className="text-xs text-amber-100">
                💡 The AI detected your suspicion level at <strong>{suspicionMeter}/10</strong>. 
                Higher scores mean you showed more skepticism during the conversation.
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
