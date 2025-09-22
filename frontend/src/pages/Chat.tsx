import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { useToast } from "@/hooks/use-toast";
import { 
  Send, 
  Code2, 
  History, 
  Settings, 
  BarChart3,
  Shield,
  Loader2,
  CheckCircle,
  AlertTriangle,
  Info,
  ArrowLeft
} from "lucide-react";
import { useNavigate } from "react-router-dom";

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  analysisData?: any;
}

interface AnalysisSettings {
  includePerformance: boolean;
  includeSecurity: boolean;
  maxSuggestions: number;
}

const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: 'Welcome to Python Review! Send me your Python code and I\'ll provide comprehensive analysis including security checks, performance optimization, and code quality improvements.',
      timestamp: new Date()
    }
  ]);
  const [isPageLoaded, setIsPageLoaded] = useState(false);
  
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [settings, setSettings] = useState<AnalysisSettings>({
    includePerformance: true,
    includeSecurity: true,
    maxSuggestions: 20
  });
  const [showSettings, setShowSettings] = useState(false);
  const [apiStatus, setApiStatus] = useState<'unknown' | 'healthy' | 'error'>('unknown');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    checkApiHealth();
    setIsPageLoaded(true);
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      const data = await response.json();
      if (data.status === 'ok') {
        setApiStatus('healthy');
      } else {
        setApiStatus('error');
      }
    } catch (error) {
      setApiStatus('error');
      console.error('API health check failed:', error);
    }
  };

  const analyzeCode = async (codeSnippet: string) => {
    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/analyze-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code_snippet: codeSnippet,
          include_performance_analysis: settings.includePerformance,
          include_security_analysis: settings.includeSecurity,
          max_suggestions: settings.maxSuggestions
        })
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const analysisData = await response.json();

      const assistantMessage: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        content: formatAnalysisResponse(analysisData),
        timestamp: new Date(),
        analysisData
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      toast({
        title: "Analysis Complete",
        description: `Found ${analysisData.suggestions?.length || 0} suggestions`,
      });

    } catch (error) {
      console.error('Analysis error:', error);
      toast({
        title: "Analysis Failed",
        description: "Could not analyze code. Please check your connection and try again.",
        variant: "destructive"
      });
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'system',
        content: 'Analysis failed. Please check your connection and try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatAnalysisResponse = (data: any) => {
    let response = `## Analysis Complete ✅\n\n`;
    
    if (data.summary) {
      response += `**Summary:** ${data.summary}\n\n`;
    }

    if (data.metrics) {
      response += `Métricas do Código 📊\n`;
      response += `- Linhas de Código: ${data.metrics.lines_of_code}\n`;
      response += `- Complexidade Ciclomática: ${data.metrics.cyclomatic_complexity}\n`;
      response += `- Índice de Manutenibilidade: ${data.metrics.maintainability_index?.toFixed(1)}\n`;
      response += `- Estimativa de Cobertura de Código: ${data.metrics.code_coverage_estimate}%\n\n`;
    }

    if (data.suggestions && data.suggestions.length > 0) {
      response += `### Suggestions (${data.suggestions.length}) 💡\n`;
      data.suggestions.forEach((suggestion: any, index: number) => {
        response += `${index + 1}. ${suggestion}\n`;
      });
      response += `\n`;
    }

    if (data.processing_time_ms !== undefined) {
      response += `*Analysis completed in ${data.processing_time_ms}ms*`;
    }

    return response;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    
    // Analyze the code
    analyzeCode(input);
    setInput('');
  };

  const loadHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/analysis-history?limit=10&offset=0');
      const data = await response.json();
      
      if (data.history) {
        const historyMessage: Message = {
          id: Date.now().toString(),
          type: 'system',
          content: `## Analysis History 📋\n\nShowing ${data.history.length} recent analyses:\n\n` +
            data.history.map((item: any, index: number) => 
              `**${index + 1}.** ID: ${item.id} | ${item.suggestions_count} suggestions | ${item.summary}\n` +
              `   *${new Date(item.created_at).toLocaleDateString()} | ${item.processing_time}ms*`
            ).join('\n\n'),
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, historyMessage]);
        
        toast({
          title: "History Loaded",
          description: `Found ${data.history.length} previous analyses`
        });
      }
    } catch (error) {
      console.error('Failed to load history:', error);
      toast({
        title: "Failed to Load History",
        description: "Could not retrieve analysis history",
        variant: "destructive"
      });
    }
  };

  const getApiStatusIcon = () => {
    switch (apiStatus) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-accent" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-destructive" />;
      default:
        return <Info className="h-4 w-4 text-muted-foreground" />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <div className={`border-b border-border/50 bg-card/80 backdrop-blur-sm sticky top-0 z-10 transition-all duration-700 ${isPageLoaded ? 'animate-slide-in-left' : 'opacity-0 -translate-x-full'}`}>
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/')}
                className="text-muted-foreground hover:text-foreground hover:scale-105 transition-all duration-300"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              
              <div className="flex items-center space-x-3">
                <div className="tech-gradient p-2 rounded-lg animate-float">
                  <Code2 className="h-5 w-5 text-primary-foreground" />
                </div>
                <h1 className="text-xl font-semibold">Python Review Chat</h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 text-sm">
                {getApiStatusIcon()}
                <span className={apiStatus === 'healthy' ? 'text-accent' : 'text-muted-foreground'}>
                  API {apiStatus === 'healthy' ? 'Online' : 'Offline'}
                </span>
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={loadHistory}
                className="flex items-center space-x-2 hover:scale-105 transition-all duration-300"
              >
                <History className="h-4 w-4" />
                <span>History</span>
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowSettings(!showSettings)}
                className="flex items-center space-x-2 hover:scale-105 transition-all duration-300"
              >
                <Settings className="h-4 w-4" />
                <span>Settings</span>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="border-b border-border/50 bg-muted/50 animate-slide-in-left">
          <div className="max-w-6xl mx-auto px-4 py-6">
            <h3 className="text-lg font-semibold mb-4 animate-fade-in">Analysis Settings</h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium">Performance Analysis</label>
                  <p className="text-xs text-muted-foreground">Include performance optimization suggestions</p>
                </div>
                <Switch
                  checked={settings.includePerformance}
                  onCheckedChange={(checked) => setSettings(prev => ({ ...prev, includePerformance: checked }))}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium">Security Analysis</label>
                  <p className="text-xs text-muted-foreground">Include security vulnerability checks</p>
                </div>
                <Switch
                  checked={settings.includeSecurity}
                  onCheckedChange={(checked) => setSettings(prev => ({ ...prev, includeSecurity: checked }))}
                />
              </div>
              
              <div>
                <label className="text-sm font-medium mb-2 block">Max Suggestions: {settings.maxSuggestions}</label>
                <Slider
                  value={[settings.maxSuggestions]}
                  onValueChange={(value) => setSettings(prev => ({ ...prev, maxSuggestions: value[0] }))}
                  max={50}
                  min={1}
                  step={1}
                  className="w-full"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chat Messages */}
      <div className={`flex-1 max-w-6xl mx-auto w-full px-4 py-6 transition-all duration-700 ${isPageLoaded ? 'animate-fade-in' : 'opacity-0'}`}>
        <div className="space-y-6">
          {messages.map((message, index) => (
            <div 
              key={message.id} 
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <Card className={`max-w-4xl p-4 transition-all duration-300 hover:scale-[1.02] ${
                message.type === 'user' 
                  ? 'tech-gradient text-primary-foreground tech-glow' 
                  : message.type === 'system'
                  ? 'bg-muted border-accent/20'
                  : 'tech-card'
              }`}>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    {message.type === 'user' && <div className="w-6 h-6 rounded-full bg-primary-foreground/20 flex items-center justify-center text-xs font-bold">U</div>}
                    {message.type === 'assistant' && <Code2 className="h-5 w-5 text-primary" />}
                    {message.type === 'system' && <Info className="h-5 w-5 text-accent" />}
                    <span className="text-sm text-muted-foreground">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                  
                  <div className={`whitespace-pre-wrap ${message.type === 'user' ? 'code-snippet p-3 rounded-lg' : ''}`}>
                    {message.content}
                  </div>
                  
                  {message.analysisData && (
                    <div className="mt-4 p-3 bg-muted/50 rounded-lg">
                      <div className="flex items-center space-x-4 text-sm">
                        {settings.includePerformance && (
                          <Badge variant="secondary">
                            <BarChart3 className="h-3 w-3 mr-1" />
                            Performance
                          </Badge>
                        )}
                        {settings.includeSecurity && (
                          <Badge variant="secondary">
                            <Shield className="h-3 w-3 mr-1" />
                            Security
                          </Badge>
                        )}
                        <span className="text-muted-foreground">
                          Analysis ID: {message.analysisData.analysis_id}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </Card>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start animate-fade-in">
              <Card className="tech-card p-4 max-w-sm animate-pulse-glow">
                <div className="flex items-center space-x-3">
                  <Loader2 className="h-5 w-5 animate-spin text-primary" />
                  <span className="animate-shimmer">Analyzing your code...</span>
                </div>
              </Card>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Form */}
      <div className={`border-t border-border/50 bg-card/80 backdrop-blur-sm sticky bottom-0 transition-all duration-700 ${isPageLoaded ? 'animate-slide-in-right' : 'opacity-0 translate-x-full'}`}>
        <div className="max-w-6xl mx-auto px-4 py-4">
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Paste your Python code here for analysis..."
              className="flex-1 min-h-[100px] resize-none code-snippet transition-all duration-300 focus:scale-[1.02]"
              disabled={isLoading}
            />
            <Button
              type="submit"
              size="lg"
              disabled={!input.trim() || isLoading || apiStatus !== 'healthy'}
              className="tech-gradient px-6 tech-glow hover:scale-105 transition-all duration-300 animate-pulse-glow"
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Send className="h-5 w-5" />
              )}
            </Button>
          </form>
          
          <div className="mt-2 text-xs text-muted-foreground">
            Press Enter to submit • Supports multi-line Python code
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;