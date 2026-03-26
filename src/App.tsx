import { AlertTriangle, CheckCircle2, Mail, MessageSquare, MessageSquareWarning, Shield, X } from 'lucide-react'
import { AnimatePresence, motion } from 'motion/react'
import { useMemo, useState } from 'react'
import { ChatSimulation } from './components/ChatSimulation'
import { levels, type Level } from './data/scenarios'
import { chatScenarios, type ChatScenario } from './data/chatScenarios'

function App() {
  const [selectedLevel, setSelectedLevel] = useState<Level | null>(null)
  const [selectedChatScenario, setSelectedChatScenario] = useState<ChatScenario | null>(null)
  const [index, setIndex] = useState(0)
  const [score, setScore] = useState(0)
  const [feedback, setFeedback] = useState<string | null>(null)
  const [isComplete, setIsComplete] = useState(false)
  const [isScenarioModalOpen, setIsScenarioModalOpen] = useState(false)
  const [chatScore, setChatScore] = useState(0)
  const [chatCount, setChatCount] = useState(0)
  const [isInChatMode, setIsInChatMode] = useState(false)

  const currentScenario = selectedLevel?.scenarios[index]
  const isRiskyScenario = currentScenario ? !currentScenario.safe : false

  const accuracy = useMemo(() => {
    if (!selectedLevel) {
      return 0
    }
    return Math.round((score / selectedLevel.scenarios.length) * 100)
  }, [score, selectedLevel])

  const chatAccuracy = useMemo(() => {
    if (chatCount === 0) {
      return 0
    }
    return Math.round((chatScore / chatCount) * 100)
  }, [chatScore, chatCount])

  const progress = selectedLevel
    ? Math.min((index / selectedLevel.scenarios.length) * 100, 100)
    : 0

  const chooseLevel = (level: Level) => {
    setSelectedLevel(level)
    setIndex(0)
    setScore(0)
    setFeedback(null)
    setIsComplete(false)
    setIsScenarioModalOpen(false)
    setIsInChatMode(false)
  }

  const startChatDrill = () => {
    setIsInChatMode(true)
    const randomScenario = chatScenarios[Math.floor(Math.random() * chatScenarios.length)]
    setSelectedChatScenario(randomScenario)
    setChatCount(0)
    setChatScore(0)
  }

  const handleChatComplete = (_correct: boolean, points: number) => {
    setChatScore(chatScore + points)
    setChatCount(chatCount + 1)

    setTimeout(() => {
      if (chatCount + 1 >= 3) {
        setIsComplete(true)
        return
      }
      const randomScenario = chatScenarios[Math.floor(Math.random() * chatScenarios.length)]
      setSelectedChatScenario(randomScenario)
    }, 2500)
  }

  const closeChatScenario = () => {
    setSelectedChatScenario(null)
  }

  const handleAnswer = (userThinksSafe: boolean) => {
    if (!currentScenario || !selectedLevel) {
      return
    }

    const correct = userThinksSafe === currentScenario.safe
    if (correct) {
      setScore((value) => value + 1)
      setFeedback('Correct call. Threat pattern identified.')
    } else {
      setFeedback('Not quite. Review the social-engineering signals carefully.')
    }

    window.setTimeout(() => {
      const isLastScenario = index >= selectedLevel.scenarios.length - 1
      if (isLastScenario) {
        setIsComplete(true)
        setIsScenarioModalOpen(false)
        return
      }
      setIsScenarioModalOpen(false)
      setIndex((value) => value + 1)
      setFeedback(null)
    }, 900)
  }

  const restart = () => {
    setSelectedLevel(null)
    setSelectedChatScenario(null)
    setIndex(0)
    setScore(0)
    setChatScore(0)
    setChatCount(0)
    setFeedback(null)
    setIsComplete(false)
    setIsScenarioModalOpen(false)
    setIsInChatMode(false)
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.13),_transparent_45%),radial-gradient(circle_at_bottom_right,_rgba(20,184,166,0.14),_transparent_45%)]" />

      <div className="relative mx-auto flex min-h-screen w-full max-w-6xl flex-col px-5 py-8 sm:px-8">
        <header className="mb-8 flex items-center justify-between rounded-2xl border border-cyan-400/20 bg-slate-900/70 px-5 py-4 backdrop-blur">
          <div className="flex items-center gap-3">
            <Shield className="h-7 w-7 text-cyan-300" />
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-cyan-200/70">PhishGuard</p>
              <h1 className="text-lg font-semibold text-cyan-50">Threat Response Simulator</h1>
            </div>
          </div>
          <div className="rounded-xl border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-sm font-semibold text-emerald-200">
            Score: {score}
          </div>
        </header>

        <AnimatePresence mode="wait">
          {!selectedLevel && !isInChatMode && (
            <motion.section
              key="level-select"
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -24 }}
              transition={{ duration: 0.45 }}
              className="grid gap-4"
            >
              <p className="max-w-2xl text-balance text-lg text-slate-300">
                Train your instinct against phishing attempts by classifying live-style messages as safe or malicious.
              </p>
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
                <motion.button
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0 }}
                  onClick={startChatDrill}
                  className="group rounded-2xl border border-slate-700 bg-slate-900/70 p-5 text-left transition hover:-translate-y-1 hover:border-purple-300/60 hover:shadow-[0_20px_50px_-24px_rgba(168,85,247,0.7)]"
                >
                  <p className="text-sm font-semibold uppercase tracking-[0.2em] text-purple-300">AI Chat</p>
                  <h2 className="mt-2 text-xl font-semibold text-white">Live Conversation</h2>
                  <p className="mt-4 text-sm leading-6 text-slate-400">Chat with an AI contact and determine if they're legitimate or an attacker.</p>
                  <div className="mt-6 inline-flex items-center gap-2 text-sm text-purple-200">
                    <MessageSquare className="h-4 w-4" />
                    3 scenarios
                  </div>
                </motion.button>
                {levels.map((level, levelIndex) => (
                  <motion.button
                    key={level.key}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.08 * (levelIndex + 1) }}
                    onClick={() => chooseLevel(level)}
                    className="group rounded-2xl border border-slate-700 bg-slate-900/70 p-5 text-left transition hover:-translate-y-1 hover:border-cyan-300/60 hover:shadow-[0_20px_50px_-24px_rgba(34,211,238,0.7)]"
                  >
                    <p className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-300">{level.key}</p>
                    <h2 className="mt-2 text-xl font-semibold text-white">{level.subtitle}</h2>
                    <p className="mt-4 text-sm leading-6 text-slate-400">{level.hint}</p>
                    <div className="mt-6 inline-flex items-center gap-2 text-sm text-cyan-200">
                      <AlertTriangle className="h-4 w-4" />
                      {level.scenarios.length} scenarios
                    </div>
                  </motion.button>
                ))}
              </div>
            </motion.section>
          )}

          {selectedLevel && !isComplete && currentScenario && (
            <motion.section
              key={`scenario-${selectedLevel.key}-${currentScenario.id}`}
              initial={{ opacity: 0, x: 18 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -18 }}
              transition={{ duration: 0.3 }}
              className="flex flex-1 flex-col gap-5"
            >
              <div className="h-2 overflow-hidden rounded-full bg-slate-800">
                <motion.div
                  className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ type: 'spring', stiffness: 80, damping: 18 }}
                />
              </div>

              <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]">
                <div className="space-y-4">
                  <button
                    onClick={() => setIsScenarioModalOpen(true)}
                    className="w-full rounded-2xl border border-slate-700 bg-slate-900/80 p-6 text-left shadow-[0_20px_50px_-30px_rgba(15,23,42,0.9)] transition hover:border-cyan-300/60"
                  >
                    <div className="mb-4 flex items-center gap-2 text-xs uppercase tracking-[0.25em] text-slate-400">
                      {currentScenario.channel === 'Email' ? <Mail className="h-4 w-4" /> : <MessageSquareWarning className="h-4 w-4" />}
                      {currentScenario.channel}
                    </div>

                    <div className="mx-auto w-full max-w-[290px] rounded-[3rem] border border-slate-500/70 bg-slate-950 p-2.5 shadow-[0_30px_60px_-28px_rgba(15,23,42,0.9)]">
                      <div className="relative h-[590px] overflow-hidden rounded-[2.5rem] border border-slate-700 bg-gradient-to-b from-slate-800 to-slate-950 p-4">
                        <div className="absolute left-1/2 top-2 flex h-7 w-36 -translate-x-1/2 items-center justify-center rounded-b-2xl bg-black/90">
                          <div className="h-1.5 w-14 rounded-full bg-slate-700" />
                          <div className="ml-2 h-1.5 w-1.5 rounded-full bg-slate-600" />
                        </div>

                        <div className="mt-8 mb-4 flex items-center justify-between text-[11px] text-slate-300">
                          <span>{currentScenario.channel === 'Email' ? 'Inbox' : 'Messages'}</span>
                          <span>9:41</span>
                        </div>

                        <div className="rounded-2xl border border-slate-600/80 bg-slate-800/70 p-3">
                          <p className="text-[11px] uppercase tracking-[0.15em] text-slate-400">Notification</p>
                          <h2 className="mt-2 text-sm font-semibold text-white">{currentScenario.title}</h2>
                          <p className="mt-1 text-xs text-cyan-200">From: {currentScenario.sender}</p>
                        </div>

                        <div className="mt-3 rounded-2xl border border-cyan-400/20 bg-cyan-500/10 px-4 py-3">
                          <p className="text-xs text-slate-300">Tap notification to view full message details</p>
                        </div>

                        <div className="absolute bottom-2.5 left-1/2 h-1.5 w-24 -translate-x-1/2 rounded-full bg-slate-600" />
                      </div>
                    </div>
                  </button>

                  <div className="grid gap-3 sm:grid-cols-2">
                    <motion.button
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleAnswer(true)}
                      className="rounded-2xl border border-emerald-300/40 bg-emerald-400/10 px-4 py-4 font-semibold text-emerald-100 transition hover:bg-emerald-400/20"
                    >
                      Mark as Safe
                    </motion.button>
                    <motion.button
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleAnswer(false)}
                      className="rounded-2xl border border-rose-300/40 bg-rose-400/10 px-4 py-4 font-semibold text-rose-100 transition hover:bg-rose-400/20"
                    >
                      Mark as Phishing
                    </motion.button>
                  </div>
                </div>

                <aside className="rounded-2xl border border-slate-700 bg-slate-900/80 p-5 shadow-[0_20px_50px_-30px_rgba(15,23,42,0.9)]">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Tips and Alerts</p>
                  <div
                    className={`mt-4 rounded-xl border px-3 py-2 text-sm font-semibold ${
                      isRiskyScenario
                        ? 'border-rose-300/40 bg-rose-400/10 text-rose-100'
                        : 'border-emerald-300/40 bg-emerald-400/10 text-emerald-100'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" />
                      {isRiskyScenario ? 'High Alert Pattern Detected' : 'Low Immediate Risk Signals'}
                    </div>
                  </div>

                  <div className="mt-4 rounded-xl border border-amber-300/35 bg-amber-400/10 p-4">
                    <p className="text-xs uppercase tracking-[0.18em] text-amber-200">Notice</p>
                    <p className="mt-2 text-sm leading-6 text-cyan-100/90">{currentScenario.explanation}</p>
                  </div>

                  <ul className="mt-4 space-y-2 text-sm text-slate-300">
                    {currentScenario.clues.map((clue) => (
                      <li key={clue} className="flex items-start gap-2">
                        <AlertTriangle className="mt-0.5 h-4 w-4 text-amber-300" />
                        {clue}
                      </li>
                    ))}
                    <li className="flex items-start gap-2">
                      <Shield className="mt-0.5 h-4 w-4 text-cyan-300" />
                      Verify sender identity through a trusted channel.
                    </li>
                  </ul>
                </aside>
              </div>

              <AnimatePresence>
                {isScenarioModalOpen && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/75 px-4"
                    onClick={() => setIsScenarioModalOpen(false)}
                  >
                    <motion.div
                      initial={{ opacity: 0, y: 24, scale: 0.96 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 16, scale: 0.96 }}
                      transition={{ duration: 0.2 }}
                      className="w-full max-w-lg rounded-2xl border border-slate-700 bg-slate-900 p-5 shadow-2xl"
                      onClick={(event) => event.stopPropagation()}
                    >
                      <div className="mb-4 flex items-start justify-between gap-3">
                        <div>
                          <p className="text-xs uppercase tracking-[0.25em] text-slate-400">
                            {currentScenario.channel}
                          </p>
                          <h3 className="mt-2 text-xl font-semibold text-white">{currentScenario.title}</h3>
                          <p className="mt-2 text-sm text-cyan-200">From: {currentScenario.sender}</p>
                        </div>
                        <button
                          onClick={() => setIsScenarioModalOpen(false)}
                          className="rounded-lg border border-slate-600 p-2 text-slate-300 transition hover:border-cyan-300 hover:text-cyan-200"
                          aria-label="Close message details"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>

                      <div className="rounded-2xl border border-cyan-400/20 bg-cyan-500/10 px-4 py-3 text-sm leading-6 text-cyan-50">
                        {currentScenario.message}
                      </div>
                    </motion.div>
                  </motion.div>
                )}

                {feedback && (
                  <motion.p
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    className="rounded-xl border border-cyan-300/30 bg-cyan-400/10 px-4 py-3 text-sm text-cyan-100"
                  >
                    {feedback}
                  </motion.p>
                )}
              </AnimatePresence>
            </motion.section>
          )}

          {isInChatMode && selectedChatScenario && (
            <ChatSimulation
              scenario={selectedChatScenario}
              onComplete={handleChatComplete}
              onClose={closeChatScenario}
            />
          )}

          {selectedLevel && isComplete && (
            <motion.section
              key="complete"
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.35 }}
              className="mx-auto mt-10 w-full max-w-2xl rounded-3xl border border-cyan-300/30 bg-slate-900/80 p-8 text-center"
            >
              <CheckCircle2 className="mx-auto h-16 w-16 text-emerald-300" />
              <h2 className="mt-4 text-3xl font-semibold text-white">Simulation Complete</h2>
              <p className="mt-4 text-slate-300">
                You finished the <span className="font-semibold text-cyan-100">{selectedLevel.key}</span> track with
                an accuracy of <span className="font-semibold text-emerald-200">{accuracy}%</span>.
              </p>
              <button
                onClick={restart}
                className="mt-7 rounded-xl border border-cyan-300/50 bg-cyan-400/10 px-5 py-3 font-semibold text-cyan-100 transition hover:bg-cyan-400/20"
              >
                Run Another Drill
              </button>
            </motion.section>
          )}

          {isInChatMode && isComplete && (
            <motion.section
              key="chat-complete"
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.35 }}
              className="mx-auto mt-10 w-full max-w-2xl rounded-3xl border border-purple-300/30 bg-slate-900/80 p-8 text-center"
            >
              <CheckCircle2 className="mx-auto h-16 w-16 text-emerald-300" />
              <h2 className="mt-4 text-3xl font-semibold text-white">Drill Complete</h2>
              <p className="mt-4 text-slate-300">
                You completed 3 AI Chat scenarios with an accuracy of <span className="font-semibold text-emerald-200">{chatAccuracy}%</span>.
              </p>
              <button
                onClick={restart}
                className="mt-7 rounded-xl border border-cyan-300/50 bg-cyan-400/10 px-5 py-3 font-semibold text-cyan-100 transition hover:bg-cyan-400/20"
              >
                Run Another Drill
              </button>
            </motion.section>
          )}
        </AnimatePresence>
      </div>
    </main>
  )
}

export default App
