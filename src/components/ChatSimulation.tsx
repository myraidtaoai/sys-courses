import { AlertTriangle, CheckCircle2, MessageSquare, Send, X } from 'lucide-react'
import { AnimatePresence, motion } from 'motion/react'
import { useEffect, useState } from 'react'
import { type ChatScenario, type UserChoice } from '../data/chatScenarios'
import { ChatMessage } from './ChatMessage'
import { JudgmentPanel } from './JudgmentPanel'

type ChatSimulationProps = {
  scenario: ChatScenario
  onComplete: (correct: boolean, score: number) => void
  onClose: () => void
}

export function ChatSimulation({ scenario, onComplete, onClose }: ChatSimulationProps) {
  const [messageIndex, setMessageIndex] = useState(0)
  const [userResponses, setUserResponses] = useState<string[]>([])
  const [isAwaitingJudgment, setIsAwaitingJudgment] = useState(false)
  const [judgmentMade, setJudgmentMade] = useState(false)
  const [userJudgmentWasPhishing, setUserJudgmentWasPhishing] = useState(false)
  const [inputText, setInputText] = useState('')

  const currentMessage = scenario.messages[messageIndex]
  const isComplete = messageIndex >= scenario.messages.length - 1

  const handleChoice = (choice: UserChoice) => {
    setUserResponses([...userResponses, choice.text])
    setMessageIndex(choice.nextMessageIndex)
  }

  const handleJudgment = (userThinkIsPhishing: boolean) => {
    const isCorrect = userThinkIsPhishing === scenario.isPhishing
    setUserJudgmentWasPhishing(userThinkIsPhishing)
    setJudgmentMade(true)
    setIsAwaitingJudgment(false)

    setTimeout(() => {
      onComplete(isCorrect, isCorrect ? 1 : 0)
    }, 2000)
  }

  useEffect(() => {
    if (isComplete && !judgmentMade) {
      setTimeout(() => {
        setIsAwaitingJudgment(true)
      }, 600)
    }
  }, [isComplete, judgmentMade])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="flex flex-1 flex-col gap-6"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-4 rounded-2xl border border-slate-700 bg-slate-900/80 p-5">
        <div>
          <div className="mb-2 flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-cyan-300" />
            <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Live Chat</p>
          </div>
          <h2 className="text-xl font-semibold text-white">{scenario.persona.name}</h2>
          <p className="mt-1 text-sm text-cyan-200">
            {scenario.persona.role}
            {scenario.persona.company && ` • ${scenario.persona.company}`}
          </p>
          <p className="mt-2 text-xs text-slate-400">{scenario.context}</p>
        </div>
        <button
          onClick={onClose}
          className="rounded-lg border border-slate-600 p-2 text-slate-300 transition hover:border-cyan-300 hover:text-cyan-200"
          aria-label="Close chat"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Chat Messages */}
      <div className="flex flex-1 flex-col rounded-2xl border border-slate-700 bg-slate-900/40">
        <div className="flex-1 space-y-4 overflow-y-auto p-5">
          <AnimatePresence mode="wait">
            {scenario.messages.slice(0, messageIndex + 1).map((msg) => (
              <ChatMessage
                key={msg.id}
                speaker={msg.speaker}
                text={msg.text}
              />
            ))}
          </AnimatePresence>
        </div>

        {/* User Choices */}
        {currentMessage?.choices && !isComplete && !judgmentMade && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-2 border-t border-slate-700/50 px-5 py-4"
          >
            <p className="text-xs uppercase tracking-[0.15em] text-slate-400">Quick responses:</p>
            <div className="space-y-2">
              {currentMessage.choices.map((choice) => (
                <motion.button
                  key={choice.id}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleChoice(choice)}
                  className="w-full rounded-lg border border-cyan-400/30 bg-cyan-500/10 px-3 py-2 text-left text-sm text-cyan-100 transition hover:bg-cyan-500/20"
                >
                  {choice.text}
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}

        {/* Text Input Box */}
        {!judgmentMade && !isAwaitingJudgment && (
          <div className="border-t border-slate-700/50 p-4">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Type a message..."
                disabled={!currentMessage?.choices || isComplete}
                className="flex-1 rounded-lg border border-slate-600 bg-slate-800/70 px-4 py-2 text-sm text-slate-100 placeholder-slate-400 outline-none transition focus:border-cyan-400/50 focus:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && inputText.trim()) {
                    e.preventDefault()
                  }
                }}
              />
              <motion.button
                whileTap={{ scale: 0.95 }}
                disabled={!inputText.trim() || !currentMessage?.choices || isComplete}
                className="rounded-lg border border-cyan-400/30 bg-cyan-500/10 p-2 text-cyan-200 transition hover:bg-cyan-500/20 disabled:opacity-30 disabled:cursor-not-allowed"
                aria-label="Send message"
              >
                <Send className="h-5 w-5" />
              </motion.button>
            </div>
            <p className="mt-2 text-xs text-slate-500">
              {currentMessage?.choices ? 'Use quick responses above to continue the conversation' : 'Waiting for response...'}
            </p>
          </div>
        )}
      </div>

      {/* Judgment or Results */}
      <AnimatePresence>
        {isAwaitingJudgment && !judgmentMade && (
          <JudgmentPanel
            isPhishing={scenario.isPhishing}
            userCorrect={false}
            onMakeJudgment={handleJudgment}
            isAwaitingJudgment={true}
          />
        )}

        {judgmentMade && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="rounded-2xl border border-slate-700 bg-slate-900/80 p-6"
          >
            <div className="mb-4 flex items-start gap-3">
              {userJudgmentWasPhishing === scenario.isPhishing ? (
                <>
                  <CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-300" />
                  <div>
                    <p className="font-semibold text-emerald-100">Correct Assessment!</p>
                    <p className="mt-1 text-sm text-emerald-100/80">
                      You correctly identified this as {scenario.isPhishing ? 'a phishing attempt' : 'legitimate'}.
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <AlertTriangle className="mt-0.5 h-5 w-5 text-rose-300" />
                  <div>
                    <p className="font-semibold text-rose-100">Missed This One</p>
                    <p className="mt-1 text-sm text-rose-100/80">
                      This was actually {scenario.isPhishing ? 'a phishing attempt' : 'legitimate contact'}. Review the clues below.
                    </p>
                  </div>
                </>
              )}
            </div>

            {/* Explanation and Clues */}
            <div className="mt-5 space-y-4 rounded-xl border border-amber-300/35 bg-amber-400/10 p-4">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-amber-200">Analysis</p>
                <p className="mt-2 text-sm leading-6 text-slate-100">{scenario.explanation}</p>
              </div>

              {scenario.isPhishing && scenario.redFlags.length > 0 && (
                <div>
                  <p className="text-xs uppercase tracking-[0.18em] text-rose-200">🚩 Red Flags</p>
                  <ul className="mt-2 space-y-1">
                    {scenario.redFlags.map((flag) => (
                      <li key={flag} className="text-sm text-slate-100 flex gap-2">
                        <span className="text-rose-300">•</span> {flag}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {!scenario.isPhishing && scenario.goodSigns.length > 0 && (
                <div>
                  <p className="text-xs uppercase tracking-[0.18em] text-emerald-200">✓ Good Signs</p>
                  <ul className="mt-2 space-y-1">
                    {scenario.goodSigns.map((sign) => (
                      <li key={sign} className="text-sm text-slate-100 flex gap-2">
                        <span className="text-emerald-300">•</span> {sign}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <p className="mt-4 text-xs text-slate-400">
              Assessing results...
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
