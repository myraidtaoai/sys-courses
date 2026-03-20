import { AlertTriangle, CheckCircle2, Mail, MessageSquareWarning, Shield } from 'lucide-react'
import { AnimatePresence, motion } from 'motion/react'
import { useMemo, useState } from 'react'

type Difficulty = 'Beginner' | 'Analyst' | 'Expert'

type Scenario = {
  id: number
  title: string
  channel: 'Email' | 'SMS'
  message: string
  explanation: string
  safe: boolean
}

type Level = {
  key: Difficulty
  subtitle: string
  hint: string
  scenarios: Scenario[]
}

const levels: Level[] = [
  {
    key: 'Beginner',
    subtitle: 'Clear red flags and obvious bait',
    hint: 'Check urgency language, suspicious links, and unusual payment requests.',
    scenarios: [
      {
        id: 1,
        title: 'Payroll Account Alert',
        channel: 'Email',
        message:
          'Your salary deposit failed. Verify your account now at payrol-secure-update.com in 30 minutes to avoid suspension.',
        explanation: 'Misspelled domain and artificial urgency are common phishing tactics.',
        safe: false,
      },
      {
        id: 2,
        title: 'Calendar Invite',
        channel: 'Email',
        message:
          'Quarterly planning meeting moved to 2:00 PM. Please confirm attendance in the company calendar.',
        explanation: 'No pressure, no suspicious link, and normal internal context.',
        safe: true,
      },
    ],
  },
  {
    key: 'Analyst',
    subtitle: 'Mixed signals and social engineering',
    hint: 'Verify sender identity and cross-check links before you click.',
    scenarios: [
      {
        id: 1,
        title: 'Vendor Invoice Follow-up',
        channel: 'Email',
        message:
          'Hi, this is accounting. We updated banking details for this month. Use the attached sheet before processing pending invoices.',
        explanation: 'Unexpected bank detail change requests should always be validated out of band.',
        safe: false,
      },
      {
        id: 2,
        title: 'HR Benefits Reminder',
        channel: 'Email',
        message:
          'Open enrollment closes Friday. Review options in the official HR portal from the employee intranet homepage.',
        explanation: 'Refers to official access path and avoids suspicious redirection.',
        safe: true,
      },
    ],
  },
  {
    key: 'Expert',
    subtitle: 'Advanced impersonation attempts',
    hint: 'Assume compromise unless sender, tone, and destination are all verifiable.',
    scenarios: [
      {
        id: 1,
        title: 'Executive Wire Request',
        channel: 'SMS',
        message:
          'Need immediate confidential transfer before board call. Keep this private and send confirmation once done.',
        explanation: 'Authority pressure + secrecy + money transfer is high-risk business email compromise behavior.',
        safe: false,
      },
      {
        id: 2,
        title: 'Security Training Prompt',
        channel: 'SMS',
        message:
          'Reminder: complete this month training through your usual SSO dashboard. IT will never ask for your password by message.',
        explanation: 'Matches good security guidance and points users to trusted access workflow.',
        safe: true,
      },
    ],
  },
]

function App() {
  const [selectedLevel, setSelectedLevel] = useState<Level | null>(null)
  const [index, setIndex] = useState(0)
  const [score, setScore] = useState(0)
  const [feedback, setFeedback] = useState<string | null>(null)
  const [isComplete, setIsComplete] = useState(false)

  const currentScenario = selectedLevel?.scenarios[index]

  const accuracy = useMemo(() => {
    if (!selectedLevel) {
      return 0
    }
    return Math.round((score / selectedLevel.scenarios.length) * 100)
  }, [score, selectedLevel])

  const progress = selectedLevel
    ? Math.min((index / selectedLevel.scenarios.length) * 100, 100)
    : 0

  const chooseLevel = (level: Level) => {
    setSelectedLevel(level)
    setIndex(0)
    setScore(0)
    setFeedback(null)
    setIsComplete(false)
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
        return
      }
      setIndex((value) => value + 1)
      setFeedback(null)
    }, 900)
  }

  const restart = () => {
    setSelectedLevel(null)
    setIndex(0)
    setScore(0)
    setFeedback(null)
    setIsComplete(false)
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
          {!selectedLevel && (
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
              <div className="grid gap-4 md:grid-cols-3">
                {levels.map((level, levelIndex) => (
                  <motion.button
                    key={level.key}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.08 * levelIndex }}
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

              <article className="rounded-2xl border border-slate-700 bg-slate-900/80 p-6 shadow-[0_20px_50px_-30px_rgba(15,23,42,0.9)]">
                <div className="mb-5 flex items-center gap-2 text-xs uppercase tracking-[0.25em] text-slate-400">
                  {currentScenario.channel === 'Email' ? <Mail className="h-4 w-4" /> : <MessageSquareWarning className="h-4 w-4" />}
                  {currentScenario.channel}
                </div>
                <h2 className="text-2xl font-semibold text-white">{currentScenario.title}</h2>
                <p className="mt-4 text-base leading-7 text-slate-200">{currentScenario.message}</p>
                <p className="mt-6 rounded-xl border border-cyan-400/20 bg-cyan-400/5 p-4 text-sm leading-6 text-cyan-100/90">
                  {currentScenario.explanation}
                </p>
              </article>

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

              <AnimatePresence>
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
        </AnimatePresence>
      </div>
    </main>
  )
}

export default App
