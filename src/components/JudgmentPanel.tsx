import { AlertTriangle, CheckCircle2, Shield } from 'lucide-react'
import { motion } from 'motion/react'

type JudgmentPanelProps = {
  isPhishing: boolean
  userCorrect: boolean
  onMakeJudgment: (isPhishing: boolean) => void
  isAwaitingJudgment: boolean
}

export function JudgmentPanel({
  isPhishing,
  userCorrect,
  onMakeJudgment,
  isAwaitingJudgment
}: JudgmentPanelProps) {
  if (isAwaitingJudgment) {
    return (
      <div className="rounded-2xl border border-slate-700 bg-slate-900/80 p-6">
        <p className="mb-4 text-sm text-slate-400">What is your judgment?</p>
        <div className="grid gap-3 sm:grid-cols-2">
          <motion.button
            whileTap={{ scale: 0.98 }}
            onClick={() => onMakeJudgment(false)}
            className="rounded-xl border border-emerald-300/40 bg-emerald-400/10 px-4 py-3 font-semibold text-emerald-100 transition hover:bg-emerald-400/20"
          >
            <Shield className="mb-2 inline h-5 w-5" />
            <span className="ml-2">Trust & Continue</span>
          </motion.button>
          <motion.button
            whileTap={{ scale: 0.98 }}
            onClick={() => onMakeJudgment(true)}
            className="rounded-xl border border-rose-300/40 bg-rose-400/10 px-4 py-3 font-semibold text-rose-100 transition hover:bg-rose-400/20"
          >
            <AlertTriangle className="mb-2 inline h-5 w-5" />
            <span className="ml-2">Report as Phishing</span>
          </motion.button>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className={`rounded-2xl border px-6 py-5 ${
        userCorrect
          ? 'border-emerald-300/40 bg-emerald-400/10'
          : 'border-rose-300/40 bg-rose-400/10'
      }`}
    >
      <div className="mb-3 flex items-start gap-3">
        {userCorrect ? (
          <CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-300" />
        ) : (
          <AlertTriangle className="mt-0.5 h-5 w-5 text-rose-300" />
        )}
        <div>
          <p className={`font-semibold ${userCorrect ? 'text-emerald-100' : 'text-rose-100'}`}>
            {userCorrect ? 'Correct!' : 'Not quite.'}
          </p>
          <p className={`mt-1 text-sm ${userCorrect ? 'text-emerald-100/90' : 'text-rose-100/90'}`}>
            {isPhishing
              ? 'This was indeed a phishing attempt.'
              : 'This was actually a legitimate contact.'}
          </p>
        </div>
      </div>
    </motion.div>
  )
}
