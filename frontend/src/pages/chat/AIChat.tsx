import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, CornerDownLeft, Copy, MoreHorizontal } from 'lucide-react';

const mockHistory = [
  { role: 'assistant', content: 'Hello Commander. I am your strategic AI liaison. I have access to all 13 departmental agents. How can I assist you today?' },
  { role: 'user', content: 'Can you summarize the impact of the current APAC supply chain disruption on our quarterly revenue?' },
  { role: 'assistant', content: 'Certainly. Based on live data from the Supply Chain and Financial Analysis agents:\n\n1. **Direct Impact**: -$4.2M in delayed recognitions.\n2. **Mitigation Cost**: Expedited shipping via EMEA will cost an estimated $850k.\n3. **Net Quarterly Adjust**: We project a 1.2% dip in Q3 net margins if mitigation begins immediately.\n\nWould you like me to draft the authorization order for the EMEA pivot?' },
];

export function AIChat() {
  const [messages, setMessages] = useState(mockHistory);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = () => {
    if (!input.trim()) return;
    
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setInput('');
    setIsTyping(true);

    setTimeout(() => {
      setIsTyping(false);
      setMessages(prev => [...prev, { role: 'assistant', content: 'This is a simulated response. In production, this will stream from the backend Commander AI API.' }]);
    }, 1500);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-card/50 backdrop-blur-sm border border-border rounded-xl overflow-hidden shadow-lg">
      <div className="border-b border-border p-4 bg-secondary/40 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center text-primary shadow-[0_0_15px_rgba(37,99,235,0.2)]">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-bold text-foreground">Commander Assistant</h2>
            <p className="text-xs text-muted-foreground">Orchestration & Strategy AI</p>
          </div>
        </div>
        <button className="p-2 text-muted-foreground hover:text-foreground hover:bg-secondary rounded-lg transition-colors">
          <MoreHorizontal className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar" ref={scrollRef}>
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-4 max-w-[85%] ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-secondary text-foreground' : 'bg-primary/20 border border-primary/30 text-primary'}`}>
              {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>
            
            <div className={`p-4 rounded-2xl text-sm leading-relaxed relative group ${
              msg.role === 'user' 
                ? 'bg-primary text-primary-foreground rounded-tr-sm' 
                : 'bg-secondary/50 border border-border text-foreground rounded-tl-sm'
            }`}>
              <div className="whitespace-pre-wrap">{msg.content}</div>
              
              {msg.role === 'assistant' && (
                <button className="absolute -right-10 top-2 p-1.5 text-muted-foreground hover:text-foreground hover:bg-secondary rounded opacity-0 group-hover:opacity-100 transition-all">
                  <Copy className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex gap-4 max-w-[85%]">
            <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center shrink-0 text-primary">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-4 rounded-2xl bg-secondary/50 border border-border rounded-tl-sm flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-primary animate-bounce"></span>
              <span className="w-2 h-2 rounded-full bg-primary animate-bounce delay-100"></span>
              <span className="w-2 h-2 rounded-full bg-primary animate-bounce delay-200"></span>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 bg-background border-t border-border shrink-0">
        <div className="relative flex items-end gap-2 bg-secondary/30 border border-border rounded-xl p-2 focus-within:ring-1 focus-within:ring-primary focus-within:border-primary transition-all">
          <textarea 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask the Commander AI..." 
            className="w-full bg-transparent border-none focus:outline-none resize-none max-h-32 p-2 text-sm text-foreground placeholder:text-muted-foreground custom-scrollbar"
            rows={input.split('\n').length > 3 ? 3 : 1}
          />
          <button 
            onClick={handleSend}
            disabled={!input.trim() || isTyping}
            className="p-2.5 bg-primary hover:bg-primary/90 disabled:bg-primary/50 text-primary-foreground rounded-lg transition-colors flex items-center justify-center shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <div className="flex items-center justify-between mt-2 px-2 text-[10px] text-muted-foreground">
          <span>AI can make mistakes. Verify critical business decisions.</span>
          <span className="flex items-center gap-1"><CornerDownLeft className="w-3 h-3" /> to send</span>
        </div>
      </div>
    </div>
  );
}
