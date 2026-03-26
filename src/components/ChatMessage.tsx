import { motion } from 'motion/react'

type ChatMessageProps = {
  speaker: 'contact' | 'user'
  text: string
}

export function ChatMessage({ speaker, text }: ChatMessageProps) {
  const isUser = speaker === 'user'

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-xs rounded-2xl px-4 py-3 text-sm leading-6 ${
          isUser
            ? 'bg-cyan-500/20 text-cyan-50 border border-cyan-400/30'
            : 'bg-slate-700/60 text-slate-100 border border-slate-600/40'
        }`}
      >
        {text}
      </div>
    </motion.div>
  )
}
